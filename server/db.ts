import { eq, and } from "drizzle-orm";
import { drizzle } from "drizzle-orm/mysql2";
import { InsertUser, users, generatedContents, InsertGeneratedContent, hotels, InsertHotel } from "../drizzle/schema";
import { ENV } from './_core/env';

let _db: ReturnType<typeof drizzle> | null = null;

// Lazily create the drizzle instance so local tooling can run without a DB.
export async function getDb() {
  if (!_db && process.env.DATABASE_URL) {
    try {
      _db = drizzle(process.env.DATABASE_URL);
    } catch (error) {
      console.warn("[Database] Failed to connect:", error);
      _db = null;
    }
  }
  return _db;
}

export async function upsertUser(user: InsertUser): Promise<void> {
  if (!user.openId) {
    throw new Error("User openId is required for upsert");
  }

  const db = await getDb();
  if (!db) {
    console.warn("[Database] Cannot upsert user: database not available");
    return;
  }

  try {
    const values: InsertUser = {
      openId: user.openId,
    };
    const updateSet: Record<string, unknown> = {};

    const textFields = ["name", "email", "loginMethod"] as const;
    type TextField = (typeof textFields)[number];

    const assignNullable = (field: TextField) => {
      const value = user[field];
      if (value === undefined) return;
      const normalized = value ?? null;
      values[field] = normalized;
      updateSet[field] = normalized;
    };

    textFields.forEach(assignNullable);

    if (user.lastSignedIn !== undefined) {
      values.lastSignedIn = user.lastSignedIn;
      updateSet.lastSignedIn = user.lastSignedIn;
    }
    if (user.role !== undefined) {
      values.role = user.role;
      updateSet.role = user.role;
    } else if (user.openId === ENV.ownerOpenId) {
      values.role = 'admin';
      updateSet.role = 'admin';
    }

    if (!values.lastSignedIn) {
      values.lastSignedIn = new Date();
    }

    if (Object.keys(updateSet).length === 0) {
      updateSet.lastSignedIn = new Date();
    }

    await db.insert(users).values(values).onDuplicateKeyUpdate({
      set: updateSet,
    });
  } catch (error) {
    console.error("[Database] Failed to upsert user:", error);
    throw error;
  }
}

export async function getUserByOpenId(openId: string) {
  const db = await getDb();
  if (!db) {
    console.warn("[Database] Cannot get user: database not available");
    return undefined;
  }

  const result = await db.select().from(users).where(eq(users.openId, openId)).limit(1);

  return result.length > 0 ? result[0] : undefined;
}

/**
 * Generated Content Operations
 */

// Save generated content to database
export async function saveGeneratedContent(content: InsertGeneratedContent) {
  const db = await getDb();
  if (!db) {
    console.warn("[Database] Cannot save generated content: database not available");
    return null;
  }

  try {
    const result = await db.insert(generatedContents).values(content);
    return result;
  } catch (error) {
    console.error("[Database] Failed to save generated content:", error);
    throw error;
  }
}

// Get generated content by region, theme, hotel, and template
export async function getGeneratedContent(
  regionName: string,
  themeName: string,
  templateId: string,
  hotelNo?: number
) {
  const db = await getDb();
  if (!db) {
    console.warn("[Database] Cannot get generated content: database not available");
    return null;
  }

  try {
    const conditions = [
      eq(generatedContents.regionName, regionName),
      eq(generatedContents.themeName, themeName),
      eq(generatedContents.templateId, templateId),
    ];

    if (hotelNo !== undefined) {
      conditions.push(eq(generatedContents.hotelNo, hotelNo));
    }

    const result = await db
      .select()
      .from(generatedContents)
      .where(and(...conditions))
      .limit(1);

    return result.length > 0 ? result[0] : null;
  } catch (error) {
    console.error("[Database] Failed to get generated content:", error);
    return null;
  }
}

// Get all generated contents for a page (region + theme)
export async function getAllGeneratedContentsForPage(
  regionName: string,
  themeName: string
) {
  const db = await getDb();
  if (!db) {
    console.warn("[Database] Cannot get generated contents: database not available");
    return [];
  }

  try {
    const result = await db
      .select()
      .from(generatedContents)
      .where(
        and(
          eq(generatedContents.regionName, regionName),
          eq(generatedContents.themeName, themeName)
        )
      );

    return result;
  } catch (error) {
    console.error("[Database] Failed to get generated contents:", error);
    return [];
  }
}

/**
 * Hotel Operations
 */

// Save hotel information
export async function saveHotel(hotel: InsertHotel) {
  const db = await getDb();
  if (!db) {
    console.warn("[Database] Cannot save hotel: database not available");
    return null;
  }

  try {
    const result = await db.insert(hotels).values(hotel).onDuplicateKeyUpdate({
      set: {
        hotelName: hotel.hotelName,
        hotelImageUrl: hotel.hotelImageUrl,
        hotelMinCharge: hotel.hotelMinCharge,
        address1: hotel.address1,
        address2: hotel.address2,
        access: hotel.access,
        hotelInformationUrl: hotel.hotelInformationUrl,
        reviewAverage: hotel.reviewAverage,
        reviewCount: hotel.reviewCount,
        hotelSpecial: hotel.hotelSpecial,
        updatedAt: new Date(),
      },
    });
    return result;
  } catch (error) {
    console.error("[Database] Failed to save hotel:", error);
    throw error;
  }
}

// Get hotels by region
export async function getHotelsByRegion(regionName: string) {
  const db = await getDb();
  if (!db) {
    console.warn("[Database] Cannot get hotels: database not available");
    return [];
  }

  try {
    const result = await db
      .select()
      .from(hotels)
      .where(eq(hotels.regionName, regionName));

    return result;
  } catch (error) {
    console.error("[Database] Failed to get hotels:", error);
    return [];
  }
}
