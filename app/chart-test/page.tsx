import { RadarChart } from '@/components/RadarChart';
import Link from 'next/link';

export default function ChartTestPage() {
    // Gemini 2.0 Flashが分析した「シェラトン・グランデ・トーキョーベイ・ホテル」の実データ
    const analysisData = {
        overall_summary: "シェラトン・グランデ・トーキョーベイ・ホテルは、東京ディズニーリゾート至近という最高のロケーションに加え、パークの眺望や充実した施設が魅力のホテルです。特に、朝食ブッフェは品揃え豊富で人気が高く、家族連れからカップルまで幅広い層に支持されています。記念日や特別な日の滞在を、思い出深いものにしてくれるでしょう。ただし、混雑や一部設備に関する改善の余地も。",
        positive_keywords: [
            { word: "朝食", count: 12, context: "品揃え豊富で美味しい朝食ブッフェが人気。特に子供連れに嬉しいメニューも。" },
            { word: "眺望", count: 8, context: "ディズニーシーやスカイツリーが見える部屋があり、景観を楽しめる。" },
            { word: "便利", count: 5, context: "ディズニーリゾートへのアクセスが良く、空港へのバスも出ていて移動が楽。" },
            { word: "記念日", count: 4, context: "誕生日や記念日に利用し、サプライズや丁寧な対応が嬉しかった。" },
            { word: "プール", count: 3, context: "夏場はガーデンプールが利用でき、リゾート気分を満喫できる。" }
        ],
        radar_chart_data: {
            atmosphere: 4.6,
            cleanliness: 4.4,
            hospitality: 4.5,
            meals: 4.4,
            onsen_quality: 4.0 // 温泉がないため低めだが、サウナ等の評価含む
        },
        persona_match: {
            couple: { score: 90, reason: "記念日プランの充実度や夜景の美しさが高評価" },
            family: { score: 85, reason: "キッズエリアやプールなど子供向け施設が豊富" },
            solo: { score: 70, reason: "一人でも快適だが、ファミリー層が多く賑やか" }
        }
    };

    return (
        <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-4xl mx-auto bg-white rounded-xl shadow-lg overflow-hidden">

                {/* ヘッダー画像エリア（仮） */}
                <div className="h-48 bg-gray-200 relative">
                    <div className="absolute inset-0 bg-gradient-to-t from-black/60 to-transparent flex items-end p-6">
                        <h1 className="text-3xl font-bold text-white">シェラトン・グランデ・トーキョーベイ・ホテル</h1>
                    </div>
                </div>

                <div className="p-8">
                    {/* AI要約 */}
                    <div className="mb-8 bg-teal-50 border-l-4 border-teal-500 p-4 rounded-r">
                        <h2 className="text-lg font-bold text-teal-800 mb-2 flex items-center">
                            <span className="mr-2">✨</span> AIによる分析要約
                        </h2>
                        <p className="text-gray-700 leading-relaxed">
                            {analysisData.overall_summary}
                        </p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">
                        {/* レーダーチャート */}
                        <div className="bg-white p-4 rounded-lg border border-gray-100 shadow-sm">
                            <h3 className="text-lg font-bold text-gray-800 mb-4 text-center">評価バランス</h3>
                            <RadarChart
                                data={analysisData.radar_chart_data}
                                hotelName="シェラトン・グランデ・トーキョーベイ"
                            />
                            <p className="text-xs text-center text-gray-400 mt-2">※ 口コミ分析による推定スコア</p>
                        </div>

                        {/* ペルソナ分析 */}
                        <div className="space-y-4">
                            <h3 className="text-lg font-bold text-gray-800 mb-4">こんな人におすすめ</h3>

                            <div className="flex items-center justify-between p-3 bg-pink-50 rounded-lg">
                                <div className="flex items-center">
                                    <span className="text-2xl mr-3">💑</span>
                                    <div>
                                        <div className="font-bold text-gray-800">カップル・記念日</div>
                                        <div className="text-xs text-gray-500">{analysisData.persona_match.couple.reason}</div>
                                    </div>
                                </div>
                                <div className="text-xl font-bold text-pink-600">{analysisData.persona_match.couple.score}点</div>
                            </div>

                            <div className="flex items-center justify-between p-3 bg-orange-50 rounded-lg">
                                <div className="flex items-center">
                                    <span className="text-2xl mr-3">👨‍👩‍👧</span>
                                    <div>
                                        <div className="font-bold text-gray-800">ファミリー・子連れ</div>
                                        <div className="text-xs text-gray-500">{analysisData.persona_match.family.reason}</div>
                                    </div>
                                </div>
                                <div className="text-xl font-bold text-orange-600">{analysisData.persona_match.family.score}点</div>
                            </div>

                            <div className="flex items-center justify-between p-3 bg-blue-50 rounded-lg">
                                <div className="flex items-center">
                                    <span className="text-2xl mr-3">👤</span>
                                    <div>
                                        <div className="font-bold text-gray-800">一人旅・ビジネス</div>
                                        <div className="text-xs text-gray-500">{analysisData.persona_match.solo.reason}</div>
                                    </div>
                                </div>
                                <div className="text-xl font-bold text-blue-600">{analysisData.persona_match.solo.score}点</div>
                            </div>
                        </div>
                    </div>

                    {/* ポジティブキーワード */}
                    <div className="mb-8">
                        <h3 className="text-lg font-bold text-gray-800 mb-4">宿泊者の生の声（高評価ポイント）</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {analysisData.positive_keywords.map((kw, i) => (
                                <div key={i} className="flex items-start p-3 border border-gray-100 rounded-lg hover:shadow-md transition-shadow">
                                    <span className="bg-teal-100 text-teal-800 text-xs font-bold px-2 py-1 rounded mr-3 mt-1">
                                        {kw.word} ({kw.count}件)
                                    </span>
                                    <p className="text-sm text-gray-600">{kw.context}</p>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="text-center mt-8">
                        <Link href="/" className="text-teal-600 hover:underline">
                            ← トップページへ戻る
                        </Link>
                    </div>

                </div>
            </div>
        </div>
    );
}
