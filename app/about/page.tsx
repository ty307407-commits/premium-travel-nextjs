import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";

export const metadata: Metadata = {
  title: "編集部について | Premium Travel Japan",
  description:
    "Premium Travel Japan編集部について。日本の温泉文化の魅力を伝えるため、実際の宿泊者の声を分析し、本当におすすめできる温泉旅館だけを厳選して紹介しています。",
};

// 編集部メンバー情報
const editors = [
  {
    id: 1,
    name: "ゆり",
    image: "https://pub-b953f613e39f4e5ea2f7b7a0e48c659b.r2.dev/authors/yuri.webp",
    bio: "夫婦の記念日旅行がきっかけで温泉旅館にハマりました。部屋に露天風呂があって、夜は美味しいお料理とお酒…そんな「非日常」を味わえる宿を探すのが好きです。",
    specialty: "カップル・夫婦向けコンテンツ",
  },
  {
    id: 2,
    name: "けんた",
    image: "https://pub-b953f613e39f4e5ea2f7b7a0e48c659b.r2.dev/authors/kenta.webp",
    bio: "3児の父。子連れNGの宿で悲しい思いをして以来、「家族に優しい温泉旅館」を探し続けています。貸切風呂と部屋食がある宿は即チェックしがち。",
    specialty: "ファミリー・シニア向けコンテンツ",
  },
  {
    id: 3,
    name: "あおい",
    image: "https://pub-b953f613e39f4e5ea2f7b7a0e48c659b.r2.dev/authors/aoi.webp",
    bio: "「週末どこ行こう？」が口癖。一人でふらっと日帰り温泉に行くのがストレス解消法。ご飯が美味しい宿には何度もリピートしてしまいます。",
    specialty: "一人旅・日帰り温泉コンテンツ",
  },
];

// コンテンツ作成プロセス
const processSteps = [
  {
    step: 1,
    title: "データ収集",
    description:
      "楽天トラベルに投稿された実際の宿泊者の口コミ・評価データを収集します。総合評価、お風呂評価、食事評価、サービス評価、清潔感など、多角的なデータを分析対象とします。",
    icon: "📊",
  },
  {
    step: 2,
    title: "分析・ポイント抽出",
    description:
      "数百〜数千件の口コミから、繰り返し言及されるポイントを抽出。「何が評価されているのか」「どんな人に向いているのか」を分析します。",
    icon: "🔍",
  },
  {
    step: 3,
    title: "編集部の視点を追加",
    description:
      "データだけではわからない「こんな方におすすめ」「予約時のポイント」「知っておきたい注意点」など、編集部独自の視点からコメントを追加します。",
    icon: "✍️",
  },
  {
    step: 4,
    title: "記事として公開",
    description:
      "読みやすく整理された情報と、編集部のおすすめポイントを合わせて記事として公開します。",
    icon: "📝",
  },
];

export default function AboutPage() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-indigo-50 via-white to-white">
      {/* ヒーローセクション */}
      <section className="relative h-[400px] md:h-[500px] flex items-center justify-center text-center text-white overflow-hidden">
        {/* 背景画像 */}
        <Image
          src="https://pub-b953f613e39f4e5ea2f7b7a0e48c659b.r2.dev/onsen_heroes/premium-travel-japan_Editorial-Dept01.webp"
          alt="Premium Travel Japan 編集部"
          fill
          className="object-cover"
          priority
        />
        {/* オーバーレイ */}
        <div className="absolute inset-0 bg-gradient-to-b from-black/50 via-black/40 to-black/60" />
        {/* コンテンツ */}
        <div className="relative z-10 max-w-4xl mx-auto px-4">
          <h1 className="text-3xl md:text-4xl font-bold mb-6 drop-shadow-lg">
            Premium Travel Japan について
          </h1>
          <p className="text-lg md:text-xl opacity-95 leading-relaxed drop-shadow-md">
            日本が誇る温泉文化の魅力を、
            <br className="hidden md:inline" />
            もっと多くの方に届けたい。
          </p>
        </div>
      </section>

      {/* 私たちの目的 */}
      <section className="py-16 px-4">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-2xl font-bold text-gray-800 mb-8 text-center">
            私たちの目的
          </h2>

          <div className="space-y-6 text-gray-700 leading-relaxed">
            <p className="text-lg font-medium text-indigo-800">
              日本の温泉文化は、世界に誇れる宝です。
            </p>

            <p>
              火山大国ならではの多様な泉質、四季折々の自然と調和した露天風呂、「おもてなし」の心が息づく温泉旅館。
              これほど豊かな温泉文化を持つ国は、世界を見渡しても日本だけです。
            </p>

            <p>
              しかし今、温泉旅館の情報はネット上に溢れ、どれを信じていいのかわからない状況が生まれています。
            </p>

            <ul className="space-y-2 pl-4">
              <li className="flex items-start gap-2">
                <span className="text-indigo-500 mt-1">•</span>
                <span>情報が多すぎて、比較しきれない</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-indigo-500 mt-1">•</span>
                <span>広告やPR記事が混在し、公平な評価が見えにくい</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-indigo-500 mt-1">•</span>
                <span>口コミも玉石混交で、本当の声がわからない</span>
              </li>
            </ul>

            <p>
              それでも私たちは、大切な人との記念日、家族との思い出、自分へのご褒美——
              そんな特別な時間を過ごす場所だからこそ、目的にぴったり合った、素敵な宿を選びたい。
            </p>

            <p className="text-lg font-medium text-indigo-800">
              Premium Travel Japan は、そんな想いに応えるために生まれたメディアです。
            </p>

            <p>
              実際の宿泊者の声を丁寧に分析し、本当におすすめできる温泉旅館だけを厳選。
              あなたの大切な旅が、「行ってよかった」と思える旅になるように。
              それが、私たちの願いです。
            </p>
          </div>
        </div>
      </section>

      {/* コンテンツ作成プロセス */}
      <section className="py-16 px-4 bg-gray-50">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-2xl font-bold text-gray-800 mb-4 text-center">
            編集部のコンテンツ作成プロセス
          </h2>
          <p className="text-gray-600 text-center mb-12">
            私たちがどのように情報を集め、記事を作成しているかをご紹介します。
          </p>

          <div className="space-y-6">
            {processSteps.map((item, index) => (
              <div
                key={item.step}
                className="flex gap-4 md:gap-6 items-start bg-white p-6 rounded-xl shadow-sm"
              >
                <div className="flex-shrink-0 w-12 h-12 md:w-14 md:h-14 bg-indigo-100 rounded-full flex items-center justify-center text-2xl">
                  {item.icon}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-xs font-bold text-indigo-600 bg-indigo-100 px-2 py-1 rounded">
                      STEP {item.step}
                    </span>
                    <h3 className="font-bold text-gray-800">{item.title}</h3>
                  </div>
                  <p className="text-gray-600 text-sm leading-relaxed">
                    {item.description}
                  </p>
                </div>
                {index < processSteps.length - 1 && (
                  <div className="hidden md:block absolute left-[2.25rem] mt-14 w-0.5 h-6 bg-indigo-200" />
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 私たちの約束 */}
      <section className="py-16 px-4">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-2xl font-bold text-gray-800 mb-8 text-center">
            私たちの約束
          </h2>

          <div className="grid md:grid-cols-2 gap-4">
            {[
              {
                icon: "✓",
                text: "実際の宿泊者の声をベースにした情報提供",
              },
              {
                icon: "✓",
                text: "良い点だけでなく、注意点も正直に伝える",
              },
              {
                icon: "✓",
                text: "「誰に向いているか」を明確にする",
              },
              {
                icon: "✓",
                text: "定期的な情報更新",
              },
            ].map((item, index) => (
              <div
                key={index}
                className="flex items-center gap-3 bg-green-50 p-4 rounded-lg"
              >
                <span className="text-green-600 font-bold text-lg">
                  {item.icon}
                </span>
                <span className="text-gray-700">{item.text}</span>
              </div>
            ))}
          </div>

          <p className="mt-8 text-sm text-gray-500 text-center">
            ※当サイトはアフィリエイトプログラムに参加しています。
            ただし、掲載内容は編集部の判断で作成しており、広告主による影響は受けていません。
          </p>
        </div>
      </section>

      {/* 編集部メンバー */}
      <section className="py-16 px-4 bg-gray-50">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-2xl font-bold text-gray-800 mb-4 text-center">
            編集部メンバー
          </h2>
          <p className="text-gray-600 text-center mb-12">
            Premium Travel Japan 編集部のライターをご紹介します。
          </p>

          <div className="grid md:grid-cols-3 gap-6">
            {editors.map((editor) => (
              <div
                key={editor.id}
                className="bg-white rounded-xl p-6 shadow-sm text-center"
              >
                <div className="relative w-24 h-24 mx-auto mb-4">
                  <Image
                    src={editor.image}
                    alt={editor.name}
                    fill
                    className="rounded-full object-cover border-4 border-indigo-100"
                  />
                </div>
                <h3 className="font-bold text-gray-800 mb-1">
                  ライター: {editor.name}
                </h3>
                <p className="text-xs text-indigo-600 mb-3">
                  {editor.specialty}
                </p>
                <p className="text-sm text-gray-600 leading-relaxed">
                  {editor.bio}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 運営者情報 */}
      <section className="py-16 px-4">
        <div className="max-w-2xl mx-auto">
          <h2 className="text-2xl font-bold text-gray-800 mb-8 text-center">
            運営者情報
          </h2>

          <div className="bg-white rounded-xl p-6 md:p-8 shadow-sm border border-gray-100">
            <dl className="space-y-4">
              <div className="flex flex-col md:flex-row md:gap-4">
                <dt className="font-medium text-gray-500 md:w-32">運営</dt>
                <dd className="text-gray-800">
                  Premium Travel Japan 編集部
                  <br />
                  <span className="text-sm text-gray-600">
                    KIZUNA合同会社内
                  </span>
                </dd>
              </div>
              <div className="flex flex-col md:flex-row md:gap-4">
                <dt className="font-medium text-gray-500 md:w-32">所在地</dt>
                <dd className="text-gray-800">
                  〒104-0061
                  <br />
                  東京都中央区銀座7丁目13番6号
                </dd>
              </div>
              <div className="flex flex-col md:flex-row md:gap-4">
                <dt className="font-medium text-gray-500 md:w-32">
                  お問い合わせ
                </dt>
                <dd className="text-gray-800">
                  <Link
                    href="/contact"
                    className="inline-flex items-center gap-2 text-indigo-600 hover:underline"
                  >
                    <span>お問い合わせフォーム</span>
                    <span className="text-xs">→</span>
                  </Link>
                </dd>
              </div>
            </dl>
          </div>
        </div>
      </section>

      {/* フッターリンク */}
      <section className="py-12 px-4 bg-gray-800 text-white">
        <div className="max-w-4xl mx-auto text-center">
          <p className="text-gray-400 mb-4">
            温泉旅館選びでお困りの方は、ぜひ当サイトをご活用ください。
          </p>
          <Link
            href="/"
            className="inline-block bg-indigo-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-indigo-700 transition"
          >
            トップページへ
          </Link>
        </div>
      </section>
    </main>
  );
}
