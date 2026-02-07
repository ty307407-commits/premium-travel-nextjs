import type { Metadata } from "next";
import Image from "next/image";
import Link from "next/link";

export const metadata: Metadata = {
  title: "編集部について | Premium Travel Japan",
  description:
    "Premium Travel Japan編集部について。口コミの「文脈」を読み取る独自の分析力で、12,000軒以上の温泉旅館データから、あなたにぴったりの宿をご提案します。",
};

// 編集方針（ペルソナ）
const editorialApproaches = [
  {
    id: 1,
    name: "ゆり",
    targetReader: "カップル・夫婦向け",
    focusPoints: [
      "口コミから「二人の時間を大切にできた」という声を抽出",
      "お風呂評価、食事評価、サービス評価を重点的に分析",
      "「部屋で過ごす時間が充実」というレビューの有無",
    ],
    icon: "💑",
  },
  {
    id: 2,
    name: "けんた",
    targetReader: "ファミリー向け",
    focusPoints: [
      "口コミから「子供への配慮」に関する言及を抽出",
      "貸切風呂、部屋食、キッズスペースの評価を重点分析",
      "「家族で楽しめた」というレビューの文脈を深掘り",
    ],
    icon: "👨‍👩‍👧‍👦",
  },
  {
    id: 3,
    name: "あおい",
    targetReader: "一人旅・日帰り温泉向け",
    focusPoints: [
      "口コミから「一人でも居心地が良かった」という声を抽出",
      "料理のクオリティ、一人利用のしやすさを重点分析",
      "「接客の距離感が心地よい」というレビューの有無",
    ],
    icon: "🧳",
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
    title: "口コミの深掘り分析",
    description:
      "数百〜数千件の口コミから、単に繰り返し言及されるポイントを抽出するだけでなく、その「文脈」を丁寧に読み取ります。「料理が美味しい」の裏にある味付けの傾向、「お風呂が良い」の具体的な理由など、表面的な評価の奥にある本質を見抜きます。",
    icon: "🔍",
  },
  {
    step: 3,
    title: "趣味嗜好別の解釈",
    description:
      "同じ口コミでも、読む人の「求めるもの」によって解釈が変わります。例えば「料理のボリュームが多い」という口コミは、大食いの方にはポジティブ、量より質を求める方にはややネガティブ。ターゲット読者ごとに、口コミを最適に「翻訳」します。",
    icon: "🎯",
  },
  {
    step: 4,
    title: "記事として公開",
    description:
      "読みやすく整理された情報と、趣味嗜好に合わせた独自の解釈を合わせて記事として公開します。",
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
                <span className="font-medium">口コミも玉石混交で、本当の声がわからない</span>
              </li>
            </ul>

            <p>
              それでも私たちは、大切な人との記念日、家族との思い出、自分へのご褒美——
              そんな特別な時間を過ごす場所だからこそ、目的にぴったり合った、素敵な宿を選びたい。
            </p>

            <p className="text-lg font-medium text-indigo-800">
              Premium Travel Japan は、そんな想いに応えるために生まれたメディアです。
            </p>
          </div>
        </div>
      </section>

      {/* 運営会社 */}
      <section className="py-16 px-4 bg-gray-50">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-2xl font-bold text-gray-800 mb-8 text-center">
            運営会社
          </h2>

          <div className="bg-white rounded-xl p-6 md:p-8 shadow-sm">
            <p className="text-gray-700 leading-relaxed mb-6">
              当サイトは、<strong className="text-indigo-600">KIZUNA合同会社が運営する、温泉旅行データの分析をベースにし、口コミを個々人の趣味嗜好に合わせる形で独自に分析し、お伝えする温泉情報メディア</strong>です。
            </p>

            <dl className="space-y-4 text-sm">
              <div className="flex flex-col md:flex-row md:gap-4">
                <dt className="font-medium text-gray-500 md:w-32">社名</dt>
                <dd className="text-gray-800">KIZUNA合同会社</dd>
              </div>
              <div className="flex flex-col md:flex-row md:gap-4">
                <dt className="font-medium text-gray-500 md:w-32">代表社員</dt>
                <dd className="text-gray-800">山内匠</dd>
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
                <dt className="font-medium text-gray-500 md:w-32">事業内容</dt>
                <dd className="text-gray-800">
                  旅行情報メディアの運営、口コミデータ分析
                </dd>
              </div>
            </dl>

            <p className="mt-6 text-xs text-gray-500">
              特定商取引法に基づく表記は
              <Link href="/company" className="text-indigo-600 hover:underline mx-1">
                こちら
              </Link>
            </p>
          </div>
        </div>
      </section>

      {/* 編集長メッセージ */}
      <section className="py-16 px-4">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-2xl font-bold text-gray-800 mb-8 text-center">
            編集長メッセージ
          </h2>

          <div className="bg-white rounded-xl p-6 md:p-8 shadow-sm">
            {/* 編集長プロフィール */}
            <div className="flex flex-col md:flex-row gap-6 items-center md:items-start mb-8">
              <div className="relative w-32 h-32 md:w-40 md:h-40 flex-shrink-0">
                <Image
                  src="https://pub-b953f613e39f4e5ea2f7b7a0e48c659b.r2.dev/authors/takumi.webp"
                  alt="編集長 takumi"
                  fill
                  className="rounded-lg object-cover shadow-md"
                />
              </div>
              <div>
                <h3 className="text-xl font-bold text-gray-800 mb-1">
                  takumi（タクミ）
                </h3>
                <p className="text-sm text-indigo-600 mb-3">
                  代表社員 / 編集長
                </p>
                <p className="text-sm text-gray-600 leading-relaxed">
                  温泉旅行が好きすぎて、「どうやって本当に良い宿を見つけるか」をデータ分析で解明するためにこのサイトを立ち上げました。
                </p>
              </div>
            </div>

            {/* メッセージ本文 */}
            <div className="space-y-6 text-gray-700 leading-relaxed">
              <p>
                こんにちは。Premium Travel Japan 編集長のtakumiです。
              </p>

              <p>
                私は温泉旅行が大好きで、これまで全国50以上の温泉地を訪れてきました。
                しかし、いつも悩むのが「どの宿を選ぶか」。
              </p>

              <p>
                口コミサイトの情報は多すぎて、どれを信じていいかわからない。
                星の数だけ見ても、本当に自分に合った宿かどうかはわからない。
              </p>

              <h4 className="text-lg font-bold text-indigo-800 mt-8 mb-4">
                なぜ、多くの人は口コミを活かせないのか
              </h4>

              <p>
                実は、<strong>口コミを「正しく読む」のは、想像以上に難しい</strong>のです。
              </p>

              <p>
                例えば、食べログで高評価のお店でも、
                「自分には合わなかった」という経験はありませんか？
              </p>

              <p>
                逆に、星3.5のお店が「すごく良かった」ということも。
              </p>

              <p>
                その理由は、<strong className="text-indigo-600">口コミの「文脈」を読み取れていないから</strong>です。
              </p>

              <div className="bg-indigo-50 p-4 rounded-lg my-6">
                <ul className="space-y-2 text-sm">
                  <li className="flex items-start gap-2">
                    <span className="text-indigo-500 mt-0.5">•</span>
                    <span>「料理が美味しかった」→ どんな味付け？ 量は？ 食材は？</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-indigo-500 mt-0.5">•</span>
                    <span>「サービスが良かった」→ どんな場面で？ 何をしてくれた？</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-indigo-500 mt-0.5">•</span>
                    <span>「お風呂が最高」→ 泉質？ 雰囲気？ 広さ？</span>
                  </li>
                </ul>
              </div>

              <p className="font-medium text-indigo-800">
                私は、この「文脈」を読み取ることが得意です。
              </p>

              <p>
                食べログで店を選ぶ時、口コミを丁寧に読み込んで分析すれば、
                <strong>ほぼハズレがありません</strong>。
              </p>

              <h4 className="text-lg font-bold text-indigo-800 mt-8 mb-4">
                温泉宿選びでも、同じことができる
              </h4>

              <p>
                この「口コミ分析力」を、温泉宿選びにも活かせないか。
              </p>

              <p>
                そう考えて、楽天トラベルの12,000軒以上の温泉旅館データを分析し、
                <strong className="text-indigo-600">実際の宿泊者500万人以上の声を、個々人の趣味嗜好に合わせて解釈する</strong>
                仕組みを作りました。
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* 私たちの強み */}
      <section className="py-16 px-4 bg-gray-50">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-2xl font-bold text-gray-800 mb-8 text-center">
            私たちの強み
          </h2>

          <div className="grid md:grid-cols-3 gap-6">
            <div className="bg-white rounded-xl p-6 shadow-sm">
              <div className="text-4xl mb-4">📊</div>
              <h3 className="font-bold text-gray-800 mb-3">
                圧倒的なデータ量
              </h3>
              <ul className="text-sm text-gray-600 space-y-2">
                <li>• 対象施設: 12,000軒以上</li>
                <li>• レビュー総数: 500万件以上</li>
                <li>• 評価項目: 6項目で分析</li>
              </ul>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-sm">
              <div className="text-4xl mb-4">🔍</div>
              <h3 className="font-bold text-gray-800 mb-3">
                口コミ分析の専門性
              </h3>
              <p className="text-sm text-gray-600 leading-relaxed">
                「料理が美味しい」の裏にある味付けの傾向、
                「お風呂が良い」の具体的な理由など、
                表面的な評価の奥にある本質を見抜きます。
              </p>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-sm">
              <div className="text-4xl mb-4">🎯</div>
              <h3 className="font-bold text-gray-800 mb-3">
                趣味嗜好に合わせた提案
              </h3>
              <p className="text-sm text-gray-600 leading-relaxed">
                同じ宿でも、求めるものが違えば評価は変わります。
                あなたの「求めるもの」に合わせて、
                口コミを最適に「翻訳」します。
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* コンテンツ作成プロセス */}
      <section className="py-16 px-4">
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
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 編集部のアプローチ */}
      <section className="py-16 px-4 bg-gray-50">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-2xl font-bold text-gray-800 mb-4 text-center">
            編集部のアプローチ
          </h2>
          <p className="text-gray-600 text-center mb-12">
            Premium Travel Japan は、異なるニーズを持つ読者層に最適な情報を届けるため、
            <br className="hidden md:inline" />
            <strong>3つの視点（編集方針）</strong>で記事を作成しています。
          </p>

          <div className="grid md:grid-cols-3 gap-6 mb-8">
            {editorialApproaches.map((approach) => (
              <div
                key={approach.id}
                className="bg-white rounded-xl p-6 shadow-sm"
              >
                <div className="text-4xl mb-3">{approach.icon}</div>
                <h3 className="font-bold text-gray-800 mb-1">
                  視点{approach.id}: {approach.targetReader}
                </h3>
                <p className="text-xs text-indigo-600 mb-4">
                  編集方針: {approach.name}
                </p>
                <div className="space-y-2">
                  <p className="text-xs font-medium text-gray-700">
                    重視する分析ポイント:
                  </p>
                  <ul className="text-xs text-gray-600 space-y-1">
                    {approach.focusPoints.map((point, index) => (
                      <li key={index} className="flex items-start gap-1">
                        <span className="text-indigo-400 mt-0.5">•</span>
                        <span>{point}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>

          <div className="bg-amber-50 border-l-4 border-amber-400 p-4 rounded">
            <p className="text-sm text-gray-700 leading-relaxed">
              <strong className="text-amber-800">重要な注記:</strong>{" "}
              これらは記事作成時の<strong>編集方針を明確にするための視点（ペルソナ）</strong>です。
              すべての記事の根拠となるのは、楽天トラベルに投稿された
              <strong>実際の宿泊者レビュー（総数500万件以上）の統計分析と文脈理解</strong>です。
            </p>
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
              "実際の宿泊者の声をベースにした情報提供",
              "口コミの「文脈」を丁寧に読み取る",
              "趣味嗜好に合わせた最適な解釈を提供",
              "定期的な情報更新",
            ].map((item, index) => (
              <div
                key={index}
                className="flex items-center gap-3 bg-green-50 p-4 rounded-lg"
              >
                <span className="text-green-600 font-bold text-lg">✓</span>
                <span className="text-gray-700 text-sm">{item}</span>
              </div>
            ))}
          </div>

          <p className="mt-8 text-sm text-gray-500 text-center">
            ※ 当サイトはアフィリエイトプログラムに参加しています。
            ただし、掲載内容は編集部が実際の口コミデータを分析して独自に判断しており、
            広告主による影響は一切受けていません。
          </p>
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
