import { searchHotels } from './server/rakuten.ts';

console.log('🔍 Rakuten Travel API接続テスト開始...\n');

try {
  console.log('箱根の宿を検索中...');
  const hotels = await searchHotels('箱根', 5);
  
  console.log(`✅ ${hotels.length}件の宿を取得しました\n`);
  
  hotels.forEach((hotel, index) => {
    console.log(`${index + 1}. ${hotel.hotelName}`);
    console.log(`   料金: ¥${hotel.hotelMinCharge.toLocaleString()}〜`);
    console.log(`   評価: ${hotel.reviewAverage} (${hotel.reviewCount}件)`);
    console.log(`   画像: ${hotel.hotelImageUrl}`);
    console.log(`   URL: ${hotel.hotelInformationUrl}`);
    console.log('');
  });
  
  console.log('🎉 テスト成功！');
  
} catch (error) {
  console.error('\n❌ エラーが発生しました:', error);
  process.exit(1);
}
