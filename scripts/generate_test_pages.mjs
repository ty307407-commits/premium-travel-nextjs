/**
 * ページコンテンツ生成スクリプト
 * 3ページのテスト生成
 */

import fs from 'fs';

const TIDB_API_BASE = 'https://ap-northeast-1.data.tidbcloud.com/api/v1beta/app/dataapp-pgnDYdcU/endpoint';
const TIDB_AUTH = Buffer.from('S2R9M3V0:8cc2d2cd-7567-422a-a9d1-8a96b5643286').toString('base64');

const RAKUTEN_APP_ID = '1029472204308393704';
const RAKUTEN_AFFILIATE_ID = '12426598.beaffa49.12426599.e0b47e86';

// 楽天エリアコードマッピング
const AREA_MAPPING = {
  'izukogen': { middle: 'shizuoka', small: 'izukogen' },
  'nikko': { middle: 'tochigi', small: 'nikko' },
  'ikaho': { middle: 'gunma', small: 'ikaho' },
  'hakone': { middle: 'kanagawa', small: 'hakone' },
  'atami': { middle: 'shizuoka', small: 'atami' },
  'kusatsu': { middle: 'gunma', small: 'kusatsu' },
  'gero': { middle: 'gifu', small: 'gero' },
  'beppu': { middle: 'oita', small: 'beppu' },
  'yufuin': { middle: 'oita', small: 'yufuin' },
  'jozankei': { middle: 'hokkaido', small: 'jozankei' },
  'noboribetsu': { middle: 'hokkaido', small: 'noboribetsu' },
  'kawaguchiko': { middle: 'yamanashi', small: 'kawaguchiko' },
  'manza': { middle: 'gunma', small: 'manza' },
};

// TiDBからページデータを取得
async function getPageData() {
  const response = await fetch(`${TIDB_API_BASE}/page_data_summary`, {
    headers: { 'Authorization': `Basic ${TIDB_AUTH}` }
  });
  const data = await response.json();
  return data.data.rows;
}

// 楽天APIでホテル検索
async function searchHotels(areaCode, limit = 3) {
  const mapping = AREA_MAPPING[areaCode];
  if (!mapping) {
    console.log(`  ⚠️ エリアコード ${areaCode} のマッピングがありません`);
    return [];
  }

  const params = new URLSearchParams({
    applicationId: RAKUTEN_APP_ID,
    affiliateId: RAKUTEN_AFFILIATE_ID,
    largeClassCode: 'japan',
    middleClassCode: mapping.middle,
    smallClassCode: mapping.small,
    hits: limit.toString(),
    responseType: 'small',
    datumType: '1',
    formatVersion: '2',
  });

  const url = `https://app.rakuten.co.jp/services/api/Travel/SimpleHotelSearch/20170426?${params}`;

  try {
    const response = await fetch(url);
    const data = await response.json();

    if (!data.hotels || data.hotels.length === 0) {
      return [];
    }

    return data.hotels.map((item) => {
      const h = item[0].hotelBasicInfo;
      return {
        hotelName: h.hotelName,
        hotelSpecial: h.hotelSpecial || '',
        hotelMinCharge: h.hotelMinCharge,
        reviewAverage: h.reviewAverage,
        access: h.access,
        hotelInformationUrl: h.hotelInformationUrl,
        hotelImageUrl: h.hotelImageUrl,
      };
    });
  } catch (error) {
    console.error('楽天API error:', error);
    return [];
  }
}

// コンテンツ生成
function generateContent(page, hotels) {
  const themeParts = page.theme_title.split(' - ');
  const themeMain = themeParts[0];
  const themeSub = themeParts[1] || '';

  const hotelList = hotels.map((h, i) => `
### ${i + 1}. ${h.hotelName}

${h.hotelImageUrl ? `![${h.hotelName}](${h.hotelImageUrl})` : ''}

${h.hotelSpecial ? h.hotelSpecial.slice(0, 300) + (h.hotelSpecial.length > 300 ? '...' : '') : '温泉と心のこもったおもてなしで、特別な時間をお過ごしいただけます。'}

| 項目 | 詳細 |
|------|------|
| 💰 料金 | ${h.hotelMinCharge?.toLocaleString() || '要確認'}円〜 |
| ⭐ 評価 | ${h.reviewAverage || '-'}/5.0 |
| 🚃 アクセス | ${h.access || '詳細は公式サイトをご確認ください'} |

👉 [詳細・予約はこちら](${h.hotelInformationUrl})
`).join('\n---\n');

  return `# ${page.region_name}で${themeMain}

> ${themeSub}

---

## はじめに

**${page.region_name}**は、${themeMain}にぴったりの温泉地です。

${themeSub ? `${themeSub}を実現するために、厳選した宿をご紹介します。` : '日常の疲れを癒し、心身ともにリフレッシュできる特別な時間をお過ごしください。'}

大切な人との時間を、${page.region_name}の温泉で過ごしてみませんか？

---

## 🏨 おすすめの宿泊施設

${hotelList || '> 現在、おすすめの宿泊施設を準備中です。近日公開予定！'}

---

## 🌸 ${page.region_name}の魅力

${page.region_name}は、四季折々の自然の美しさと歴史ある温泉文化が融合した、魅力的な温泉地です。

### この温泉地の特徴

- 🌊 **泉質**: 肌に優しい温泉で、美肌効果も期待できます
- 🍽️ **グルメ**: 地元の食材を活かした絶品料理
- 🚶 **散策**: 温泉街の風情ある街並みを楽しめます

---

## 📍 アクセス情報

${page.region_name}へのアクセスは、各宿泊施設のページで詳細をご確認ください。

---

## まとめ

${themeMain}をお考えなら、${page.region_name}がおすすめです。

上質な温泉と心のこもったおもてなしで、忘れられない思い出を作りましょう。

---

*最終更新: ${new Date().toLocaleDateString('ja-JP')}*

*当サイトはアフィリエイトプログラムに参加しています。*
`;
}

// メイン処理
async function main() {
  console.log('=== 3ページテスト生成 ===\n');

  // テスト用の固定ページID
  const testPageIds = ['3105', '1955', '4612'];

  // ページデータ取得
  console.log('1. ページデータを取得中...');
  const allPages = await getPageData();
  console.log(`   総ページ数: ${allPages.length}`);

  // 指定されたページを選択
  let testPages = testPageIds
    .map(id => allPages.find(p => p.page_id === id))
    .filter(Boolean);

  // 見つからない場合はランダムに選択
  if (testPages.length < 3) {
    console.log('   指定ページが見つからないため、ランダム選択します');
    const shuffled = [...allPages].sort(() => Math.random() - 0.5);
    testPages = shuffled.slice(0, 3);
  }

  console.log(`   選択したページ: ${testPages.map(p => p.page_id).join(', ')}\n`);

  // 各ページを生成
  const results = [];
  for (const page of testPages) {
    console.log(`2. ページ生成: ${page.page_id}`);
    console.log(`   テーマ: ${page.theme_title.slice(0, 50)}...`);
    console.log(`   地域: ${page.region_name}`);
    console.log(`   エリアコード: ${page.rakuten_area_code}`);

    // ホテル検索
    console.log('   ホテル検索中...');
    const hotels = await searchHotels(page.rakuten_area_code, 3);
    console.log(`   取得ホテル数: ${hotels.length}`);

    // コンテンツ生成
    const content = generateContent(page, hotels);
    console.log(`   生成コンテンツ: ${content.length}文字`);

    // 結果をファイルに保存
    const filename = `./generated/page_${page.page_id}.md`;
    fs.writeFileSync(filename, content);
    console.log(`   ✅ 保存: ${filename}\n`);

    results.push({ page_id: page.page_id, filename, length: content.length });

    // API制限対策で少し待機
    await new Promise(r => setTimeout(r, 500));
  }

  console.log('=== 生成完了 ===');
  console.log('生成されたファイル:');
  results.forEach(r => console.log(`  - ${r.filename} (${r.length}文字)`));
}

main().catch(console.error);
