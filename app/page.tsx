import Link from 'next/link'
import { getActiveThemes, Theme } from '@/lib/tidb'

// 動的レンダリングを強制（ビルド時にデータ取得しない）
export const dynamic = 'force-dynamic'

export default async function Home() {
  let themes: Theme[] = []
  try {
    themes = await getActiveThemes()
  } catch (error) {
    console.error('Failed to fetch themes:', error)
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <section className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          プレミアム温泉旅行
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto">
          40代・50代夫婦のための、人生の節目を祝う特別な温泉体験をご提案します
        </p>
      </section>

      <section>
        <h2 className="text-2xl font-bold text-gray-800 mb-6">テーマから探す</h2>
        {themes.length > 0 ? (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {themes.slice(0, 12).map((theme) => (
              <Link
                key={theme.theme_id}
                href={`/theme/${theme.theme_id}`}
                className="block p-6 bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow border"
              >
                <h3 className="text-lg font-semibold text-gray-800 mb-2">
                  {theme.theme_title}
                </h3>
                <p className="text-sm text-gray-500">
                  {theme.pages}件の温泉地
                </p>
              </Link>
            ))}
          </div>
        ) : (
          <p className="text-gray-500">テーマを読み込み中...</p>
        )}
      </section>
    </div>
  )
}
