/**
 * ページコンテンツ生成スクリプト
 * 3ページのテスト生成
 */

const TIDB_API_BASE = 'https://ap-northeast-1.data.tidbcloud.com/api/v1beta/app/dataapp-pgnDYdcU/endpoint';
const TIDB_AUTH = Buffer.from('S2R9M3V0:8cc2d2cd-7567-422a-a9d1-8a96b5643286').toString('base64');

const RAKUTEN_APP_ID = '1029472204308393704';
const RAKUTEN_AFFILIATE_ID = '12426598.beaffa49.12426599.e0b47e86';

// 楽天エリアコードからMiddle/Small Classを取得するためのマスタ（TiDBのrakuten_area_masterを使用）
const AREA_MAPPING: Record<string, { middle: string; small: string }> = {
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
};

interface PageData {
  page_id: string;
  theme_id: string;
  theme_title: string;
  region_name: string;
  url_slug: string;
  rakuten_area_code: string;
}

interface Hotel {
  hotelName: string;
  hotelSpecial: string;
  hotelMinCharge: number;
  reviewAverage: number;
  access: string;
  hotelInformationUrl: string;
}

// TiDBからページデータを取得
async function getPageData(): Promise<PageData[]> {
  const response = await fetch(`${TIDB_API_BASE}/page_data_summary`, {
    headers: { 'Authorization': `Basic ${TIDB_AUTH}` }
  });
  const data = await response.json();
  return data.data.rows;
}

// 楽天APIでホテル検索
async function searchHotels(areaCode: string, limit: number = 3): Promise<Hotel[]> {
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

    return data.hotels.map((item: any) => {
      const h = item[0].hotelBasicInfo;
      return {
        hotelName: h.hotelName,
        hotelSpecial: h.hotelSpecial || '',
        hotelMinCharge: h.hotelMinCharge,
        reviewAverage: h.reviewAverage,
        access: h.access,
        hotelInformationUrl: h.hotelInformationUrl,
      };
    });
  } catch (error) {
    console.error('楽天API error:', error);
    return [];
  }
}

// コンテンツ生成（簡易版 - Gemini APIを使用する場合はここを拡張）
function generateContent(page: PageData, hotels: Hotel[]): string {
  const hotelList = hotels.map((h, i) => `
### ${i + 1}. ${h.hotelName}

${h.hotelSpecial ? h.hotelSpecial.slice(0, 200) + '...' : ''}

- **最低料金**: ${h.hotelMinCharge?.toLocaleString() || '要確認'}円〜
- **評価**: ${h.reviewAverage || '-'}/5.0
- **アクセス**: ${h.access || '-'}

[詳細・予約はこちら](${h.hotelInformationUrl})
`).join('\n');

  return `# ${page.region_name}で${page.theme_title.split(' - ')[0]}

## ${page.theme_title.split(' - ')[1] || ''}

${page.region_name}は、${page.theme_title}にぴったりの温泉地です。
日常の疲れを癒し、心身ともにリフレッシュできる特別な時間をお過ごしください。

---

## おすすめの宿泊施設

${hotelList || '現在、おすすめの宿泊施設を準備中です。'}

---

## ${page.region_name}の魅力

${page.region_name}は、四季折々の自然の美しさと、
歴史ある温泉文化が融合した魅力的な温泉地です。

### アクセス情報

詳細なアクセス方法は各宿泊施設のページをご確認ください。

---

*この記事は${new Date().toLocaleDateString('ja-JP')}に更新されました。*
`;
}

// メイン処理
async function main() {
  console.log('=== 3ページテスト生成 ===\n');

  // ページデータ取得
  console.log('1. ページデータを取得中...');
  const allPages = await getPageData();
  console.log(`   総ページ数: ${allPages.length}`);

  // ランダムに3件選択
  const testPages = [
    allPages.find(p => p.page_id === '3105'),
    allPages.find(p => p.page_id === '1955'),
    allPages.find(p => p.page_id === '4612'),
  ].filter(Boolean) as PageData[];

  // 見つからない場合はランダムに選択
  if (testPages.length < 3) {
    const shuffled = allPages.sort(() => Math.random() - 0.5);
    while (testPages.length < 3 && shuffled.length > 0) {
      testPages.push(shuffled.pop()!);
    }
  }

  console.log(`   選択したページ: ${testPages.map(p => p.page_id).join(', ')}\n`);

  // 各ページを生成
  for (const page of testPages) {
    console.log(`2. ページ生成: ${page.page_id}`);
    console.log(`   テーマ: ${page.theme_title.slice(0, 40)}...`);
    console.log(`   地域: ${page.region_name}`);
    console.log(`   エリアコード: ${page.rakuten_area_code}`);

    // ホテル検索
    console.log('   ホテル検索中...');
    const hotels = await searchHotels(page.rakuten_area_code, 3);
    console.log(`   取得ホテル数: ${hotels.length}`);

    // コンテンツ生成
    const content = generateContent(page, hotels);
    console.log(`   生成コンテンツ: ${content.length}文字`);

    // 結果をファイルに保存（確認用）
    const filename = `/home/user/premium-travel-nextjs/generated/page_${page.page_id}.md`;
    await Bun.write(filename, content);
    console.log(`   保存: ${filename}\n`);
  }

  console.log('=== 完了 ===');
  console.log('生成されたファイルは generated/ ディレクトリにあります。');
}

main().catch(console.error);
