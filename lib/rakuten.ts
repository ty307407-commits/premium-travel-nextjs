const RAKUTEN_APP_ID = '1029472204308393704'
const RAKUTEN_AFFILIATE_ID = '12426598.beaffa49.12426599.e0b47e86'

export interface Hotel {
  hotelName: string
  hotelImageUrl: string
  hotelInformationUrl: string
  address1: string
  address2: string
  access: string
  hotelMinCharge?: number
  reviewAverage?: number
  reviewCount?: number
}

export async function searchHotels(
  prefectureCode: string,
  areaCode: string,
  hits: number = 5
): Promise<Hotel[]> {
  const url = new URL('https://app.rakuten.co.jp/services/api/Travel/SimpleHotelSearch/20170426')
  url.searchParams.append('applicationId', RAKUTEN_APP_ID)
  url.searchParams.append('affiliateId', RAKUTEN_AFFILIATE_ID)
  url.searchParams.append('format', 'json')
  url.searchParams.append('largeClassCode', 'japan')
  url.searchParams.append('middleClassCode', prefectureCode)
  url.searchParams.append('smallClassCode', areaCode)
  url.searchParams.append('hits', String(hits))

  try {
    const response = await fetch(url.toString(), {
      next: { revalidate: 86400 }, // 24時間キャッシュ
    })

    if (!response.ok) {
      console.error('Rakuten API error:', response.status)
      return []
    }

    const data = await response.json()

    if (!data.hotels || data.hotels.length === 0) {
      return []
    }

    return data.hotels.map((h: any) => {
      const info = h.hotel[0].hotelBasicInfo
      return {
        hotelName: info.hotelName,
        hotelImageUrl: info.hotelImageUrl,
        hotelInformationUrl: info.hotelInformationUrl,
        address1: info.address1,
        address2: info.address2,
        access: info.access,
        hotelMinCharge: info.hotelMinCharge,
        reviewAverage: info.reviewAverage,
        reviewCount: info.reviewCount,
      }
    })
  } catch (error) {
    console.error('Failed to fetch hotels:', error)
    return []
  }
}
