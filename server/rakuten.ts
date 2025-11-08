// Rakuten Travel API Client

const RAKUTEN_APPLICATION_ID = process.env.RAKUTEN_APPLICATION_ID || '1029472204308393704';
const RAKUTEN_AFFILIATE_ID = process.env.RAKUTEN_AFFILIATE_ID || '12426598.beaffa49.12426599.e0b47e86';

export interface RakutenHotel {
  hotelNo: number;
  hotelName: string;
  hotelInformationUrl: string;
  planListUrl: string;
  dpPlanListUrl: string;
  reviewUrl: string;
  hotelKanaName: string;
  hotelSpecial: string;
  hotelMinCharge: number;
  latitude: number;
  longitude: number;
  postalCode: string;
  address1: string;
  address2: string;
  telephoneNo: string;
  faxNo: string;
  access: string;
  parkingInformation: string;
  nearestStation: string;
  hotelImageUrl: string;
  hotelThumbnailUrl: string;
  roomImageUrl?: string;
  hotelMapImageUrl?: string;
  reviewCount: number;
  reviewAverage: number;
  userReview: string;
}

/**
 * 地域名から楽天トラベルAPIのエリアコードを取得
 */
export function getRegionCodes(regionName: string): {
  largeClassCode: string;
  middleClassCode: string;
  smallClassCode: string;
} | null {
  const regions: Record<string, { largeClassCode: string; middleClassCode: string; smallClassCode: string }> = {
    '箱根温泉': { largeClassCode: 'japan', middleClassCode: 'kanagawa', smallClassCode: 'hakone' },
    '箱根': { largeClassCode: 'japan', middleClassCode: 'kanagawa', smallClassCode: 'hakone' },
    // 他の温泉地も追加可能
  };

  return regions[regionName] || null;
}

/**
 * 楽天トラベル Simple Hotel Search API
 */
export async function searchHotels(regionName: string, limit: number = 5): Promise<RakutenHotel[]> {
  const codes = getRegionCodes(regionName);
  
  if (!codes) {
    throw new Error(`Unknown region: ${regionName}`);
  }

  const params = new URLSearchParams({
    applicationId: RAKUTEN_APPLICATION_ID,
    affiliateId: RAKUTEN_AFFILIATE_ID,
    largeClassCode: codes.largeClassCode,
    middleClassCode: codes.middleClassCode,
    smallClassCode: codes.smallClassCode,
    hits: limit.toString(),
    responseType: 'small',
    datumType: '1',
    formatVersion: '2',
  });

  const url = `https://app.rakuten.co.jp/services/api/Travel/SimpleHotelSearch/20170426?${params}`;

  try {
    const response = await fetch(url);
    
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Rakuten API error: ${response.status} ${response.statusText} - ${errorText}`);
    }

    const data = await response.json();

    if (!data.hotels || data.hotels.length === 0) {
      console.warn(`No hotels found for region: ${regionName}`);
      return [];
    }

    return data.hotels.map((item: any) => {
      const hotel = item[0].hotelBasicInfo;
      return {
        hotelNo: hotel.hotelNo,
        hotelName: hotel.hotelName,
        hotelInformationUrl: hotel.hotelInformationUrl,
        planListUrl: hotel.planListUrl,
        dpPlanListUrl: hotel.dpPlanListUrl,
        reviewUrl: hotel.reviewUrl,
        hotelKanaName: hotel.hotelKanaName,
        hotelSpecial: hotel.hotelSpecial,
        hotelMinCharge: hotel.hotelMinCharge,
        latitude: hotel.latitude,
        longitude: hotel.longitude,
        postalCode: hotel.postalCode,
        address1: hotel.address1,
        address2: hotel.address2,
        telephoneNo: hotel.telephoneNo,
        faxNo: hotel.faxNo,
        access: hotel.access,
        parkingInformation: hotel.parkingInformation,
        nearestStation: hotel.nearestStation,
        hotelImageUrl: hotel.hotelImageUrl,
        hotelThumbnailUrl: hotel.hotelThumbnailUrl,
        roomImageUrl: hotel.roomImageUrl,
        hotelMapImageUrl: hotel.hotelMapImageUrl,
        reviewCount: hotel.reviewCount,
        reviewAverage: hotel.reviewAverage,
        userReview: hotel.userReview,
      };
    });
  } catch (error) {
    console.error('Rakuten API error:', error);
    throw error;
  }
}
