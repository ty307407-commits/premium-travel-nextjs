import { getContentTemplates, getOnsenArea, getThemes } from './server/googlesheets.ts';

console.log('🔍 Google Sheets API接続テスト開始...\n');

try {
  // 1. Content_Templatesシートのテスト
  console.log('1. Content_Templatesシートからデータ取得中...');
  const templates = await getContentTemplates();
  console.log(`✅ ${templates.length}件のテンプレートを取得しました`);
  
  if (templates.length > 0) {
    console.log('\n最初のテンプレート:');
    console.log(JSON.stringify(templates[0], null, 2));
  }
  
  // 2. OnsenAreasシートのテスト（箱根）
  console.log('\n2. OnsenAreasシートから箱根データ取得中...');
  const hakone = await getOnsenArea('箱根温泉');
  
  if (hakone) {
    console.log('✅ 箱根温泉データを取得しました:');
    console.log(JSON.stringify(hakone, null, 2));
  } else {
    console.log('❌ 箱根温泉データが見つかりませんでした');
  }
  
  // 3. Themesシートのテスト
  console.log('\n3. Themesシートからデータ取得中...');
  const themes = await getThemes();
  console.log(`✅ ${themes.length}件のテーマを取得しました`);
  
  if (themes.length > 0) {
    console.log('\n最初のテーマ:');
    console.log(JSON.stringify(themes[0], null, 2));
  }
  
  console.log('\n🎉 すべてのテストが成功しました！');
  
} catch (error) {
  console.error('\n❌ エラーが発生しました:', error);
  process.exit(1);
}
