import Link from 'next/link';

export default function Footer() {
    const currentYear = new Date().getFullYear();

    return (
        <footer className="bg-gray-900 text-gray-300 mt-auto">
            <div className="max-w-7xl mx-auto px-4 py-12">
                {/* メインフッターコンテンツ */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
                    {/* サイト情報 */}
                    <div>
                        <h3 className="text-white font-bold text-lg mb-4">Premium Travel Japan</h3>
                        <p className="text-sm text-gray-400 leading-relaxed">
                            高級温泉旅館の厳選ガイド。口コミデータを徹底分析し、本当におすすめできる温泉旅館をご紹介します。
                        </p>
                    </div>

                    {/* サイトマップ */}
                    <div>
                        <h4 className="text-white font-semibold mb-4">サイトマップ</h4>
                        <ul className="space-y-2 text-sm">
                            <li>
                                <Link href="/" className="hover:text-white transition-colors">
                                    トップページ
                                </Link>
                            </li>
                            <li>
                                <Link href="/about" className="hover:text-white transition-colors">
                                    このサイトについて
                                </Link>
                            </li>
                            <li>
                                <Link href="/contact" className="hover:text-white transition-colors">
                                    お問い合わせ
                                </Link>
                            </li>
                        </ul>
                    </div>

                    {/* カテゴリー */}
                    <div>
                        <h4 className="text-white font-semibold mb-4">カテゴリー</h4>
                        <ul className="space-y-2 text-sm">
                            <li>
                                <Link href="/luxury" className="hover:text-white transition-colors">
                                    高級温泉旅館
                                </Link>
                            </li>
                            <li>
                                <Link href="/private-bath" className="hover:text-white transition-colors">
                                    客室露天風呂
                                </Link>
                            </li>
                            <li>
                                <Link href="/ryokan" className="hover:text-white transition-colors">
                                    温泉旅館ランキング
                                </Link>
                            </li>
                        </ul>
                    </div>

                    {/* 法的情報 */}
                    <div>
                        <h4 className="text-white font-semibold mb-4">法的情報</h4>
                        <ul className="space-y-2 text-sm">
                            <li>
                                <Link href="/company" className="hover:text-white transition-colors">
                                    特定商取引法に基づく表記
                                </Link>
                            </li>
                            <li>
                                <Link href="/privacy" className="hover:text-white transition-colors">
                                    プライバシーポリシー
                                </Link>
                            </li>
                        </ul>
                    </div>
                </div>

                {/* ボーダーライン */}
                <div className="border-t border-gray-800 pt-8">
                    <div className="flex flex-col md:flex-row justify-between items-center text-sm text-gray-500">
                        <p>© {currentYear} KIZUNA合同会社. All rights reserved.</p>
                        <p className="mt-2 md:mt-0">
                            運営統括責任者: 山内匠
                        </p>
                    </div>
                </div>
            </div>
        </footer>
    );
}
