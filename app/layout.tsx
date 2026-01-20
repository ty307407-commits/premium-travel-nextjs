import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'プレミアム温泉旅行 | 40代・50代夫婦のための特別な温泉体験',
  description: '人生の節目を祝う、40代・50代夫婦のための厳選温泉旅行プラン。記念日、健康回復、リフレッシュなど、テーマ別におすすめの温泉地とホテルをご紹介。',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ja">
      <body className="min-h-screen bg-white antialiased">
        <header className="border-b">
          <div className="container mx-auto px-4 py-4">
            <a href="/" className="text-xl font-bold text-gray-900">
              プレミアム温泉旅行
            </a>
          </div>
        </header>
        <main>{children}</main>
        <footer className="border-t mt-12 py-8 bg-gray-50">
          <div className="container mx-auto px-4 text-center text-gray-600">
            <p>&copy; 2026 プレミアム温泉旅行. All rights reserved.</p>
          </div>
        </footer>
      </body>
    </html>
  )
}
