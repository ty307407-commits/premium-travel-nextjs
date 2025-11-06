import { int, mysqlEnum, mysqlTable, text, timestamp, varchar } from "drizzle-orm/mysql-core";

/**
 * Core user table backing auth flow.
 * Extend this file with additional tables as your product grows.
 * Columns use camelCase to match both database fields and generated types.
 */
export const users = mysqlTable("users", {
  /**
   * Surrogate primary key. Auto-incremented numeric value managed by the database.
   * Use this for relations between tables.
   */
  id: int("id").autoincrement().primaryKey(),
  /** Manus OAuth identifier (openId) returned from the OAuth callback. Unique per user. */
  openId: varchar("openId", { length: 64 }).notNull().unique(),
  name: text("name"),
  email: varchar("email", { length: 320 }),
  loginMethod: varchar("loginMethod", { length: 64 }),
  role: mysqlEnum("role", ["user", "admin"]).default("user").notNull(),
  createdAt: timestamp("createdAt").defaultNow().notNull(),
  updatedAt: timestamp("updatedAt").defaultNow().onUpdateNow().notNull(),
  lastSignedIn: timestamp("lastSignedIn").defaultNow().notNull(),
});

export type User = typeof users.$inferSelect;
export type InsertUser = typeof users.$inferInsert;

/**
 * Generated contents table
 * Stores LLM-generated content for each page/hotel/template combination
 */
export const generatedContents = mysqlTable("generated_contents", {
  id: int("id").autoincrement().primaryKey(),
  
  // Page identification
  regionName: varchar("region_name", { length: 100 }).notNull(), // e.g., "箱根温泉"
  themeName: varchar("theme_name", { length: 100 }).notNull(), // e.g., "結婚5周年記念"
  
  // Hotel identification (nullable for page-level content)
  hotelNo: int("hotel_no"), // Rakuten hotel ID, null for page-level content
  hotelName: varchar("hotel_name", { length: 200 }), // Hotel name for reference
  
  // Template identification
  templateId: varchar("template_id", { length: 10 }).notNull(), // e.g., "1", "2", "4"
  templateName: varchar("template_name", { length: 100 }).notNull(), // e.g., "宿見出し", "おすすめポイント"
  
  // Generated content
  content: text("content").notNull(), // The actual generated text
  wordCount: int("word_count").notNull(), // Actual character count
  
  // Metadata
  generatedAt: timestamp("generated_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().onUpdateNow().notNull(),
});

export type GeneratedContent = typeof generatedContents.$inferSelect;
export type InsertGeneratedContent = typeof generatedContents.$inferInsert;

/**
 * Hotels table
 * Stores hotel information from Rakuten Travel API
 */
export const hotels = mysqlTable("hotels", {
  id: int("id").autoincrement().primaryKey(),
  
  // Rakuten hotel data
  hotelNo: int("hotel_no").notNull().unique(), // Rakuten hotel ID
  hotelName: varchar("hotel_name", { length: 200 }).notNull(),
  hotelImageUrl: varchar("hotel_image_url", { length: 500 }),
  hotelMinCharge: int("hotel_min_charge"),
  address1: varchar("address1", { length: 100 }),
  address2: varchar("address2", { length: 200 }),
  access: text("access"),
  hotelInformationUrl: varchar("hotel_information_url", { length: 500 }),
  reviewAverage: int("review_average"), // Stored as integer (e.g., 450 = 4.50)
  reviewCount: int("review_count"),
  hotelSpecial: text("hotel_special"),
  
  // Region association
  regionName: varchar("region_name", { length: 100 }).notNull(),
  
  // Metadata
  createdAt: timestamp("created_at").defaultNow().notNull(),
  updatedAt: timestamp("updated_at").defaultNow().onUpdateNow().notNull(),
});

export type Hotel = typeof hotels.$inferSelect;
export type InsertHotel = typeof hotels.$inferInsert;