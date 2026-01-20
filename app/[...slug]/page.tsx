import { Metadata } from 'next'
import Image from 'next/image'
import { notFound } from 'next/navigation'
import { getPageBySlug } from '@/lib/tidb'
import { searchHotels, Hotel } from '@/lib/rakuten'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

// 動的レンダリングを強制
export const dynamic = 'force-dynamic'

interface PageProps {
  params: {
    slug: string[]
  }
}

// URLパスからスラッグを構築
function buildSlug(slugParts: string[]): string {
  return '/' + slugParts.join('/') + '/'
}

// 動的メタデータ生成（SEO用）
export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const slug = buildSlug(params.slug)
  const page = await getPageBySlug(slug)

  if (!page) {
    return { title: 'ページが見つかりません' }
  }

  return {
    title: `${page.page_title} | プレミアム温泉旅行`,
    description: page.meta_description || `${page.region_name}の${page.theme_title}。おすすめの温泉宿泊施設をご紹介。`,
    openGraph: {
      title: page.page_title,
      description: page.meta_description || `${page.region_name}の${page.theme_title}`,
      images: page.hero_image_url ? [page.hero_image_url] : [],
    },
  }
}

function HotelCard({ hotel }: { hotel: Hotel }) {
  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden border">
      {hotel.hotelImageUrl && (
        <div className="relative h-48">
          <Image
            src={hotel.hotelImageUrl}
            alt={hotel.hotelName}
            fill
            className="object-cover"
          />
        </div>
      )}
      <div className="p-4">
        <h3 className="text-lg font-semibold text-gray-800 mb-2">
          {hotel.hotelName}
        </h3>
        <p className="text-sm text-gray-600 mb-2">
          {hotel.address1}{hotel.address2}
        </p>
        <p className="text-sm text-gray-500 mb-3">
          {hotel.access}
        </p>
        {hotel.reviewAverage && (
          <div className="flex items-center gap-2 mb-3">
            <span className="text-yellow-500">★</span>
            <span className="font-medium">{hotel.reviewAverage}</span>
            <span className="text-gray-400 text-sm">({hotel.reviewCount}件)</span>
          </div>
        )}
        <a
          href={hotel.hotelInformationUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-block bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition-colors text-sm"
        >
          詳細を見る
        </a>
      </div>
    </div>
  )
}

export default async function ContentPage({ params }: PageProps) {
  const slug = buildSlug(params.slug)
  const page = await getPageBySlug(slug)

  if (!page) {
    notFound()
  }

  // ホテル情報を取得
  let hotels: Hotel[] = []
  if (page.prefecture_code && page.area_code) {
    hotels = await searchHotels(page.prefecture_code, page.area_code, 6)
  }

  return (
    <article className="container mx-auto px-4 py-8 max-w-4xl">
      {/* ヒーロー画像 */}
      {page.hero_image_url && (
        <div className="relative h-64 md:h-96 rounded-xl overflow-hidden mb-8">
          <Image
            src={page.hero_image_url}
            alt={page.page_title}
            fill
            className="object-cover"
            priority
          />
          <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent" />
          <div className="absolute bottom-0 left-0 right-0 p-6 text-white">
            <p className="text-sm opacity-90 mb-2">{page.theme_title}</p>
            <h1 className="text-2xl md:text-4xl font-bold">{page.page_title}</h1>
          </div>
        </div>
      )}

      {/* タイトル（画像がない場合） */}
      {!page.hero_image_url && (
        <header className="mb-8">
          <p className="text-blue-600 mb-2">{page.theme_title}</p>
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900">
            {page.page_title}
          </h1>
        </header>
      )}

      {/* エリア情報 */}
      <div className="bg-blue-50 rounded-lg p-4 mb-8">
        <div className="flex items-center gap-4">
          <span className="text-2xl">♨️</span>
          <div>
            <p className="font-semibold text-gray-800">{page.region_name}</p>
            <p className="text-sm text-gray-600">{page.prefecture_name}</p>
          </div>
        </div>
      </div>

      {/* 記事本文（Markdownがある場合） */}
      {page.temp_full_markdown && (
        <div className="article-content mb-12">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {page.temp_full_markdown}
          </ReactMarkdown>
        </div>
      )}

      {/* おすすめホテル */}
      {hotels.length > 0 && (
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">
            おすすめの宿泊施設
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {hotels.map((hotel, index) => (
              <HotelCard key={index} hotel={hotel} />
            ))}
          </div>
        </section>
      )}
    </article>
  )
}
