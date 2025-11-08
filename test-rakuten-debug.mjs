const RAKUTEN_APPLICATION_ID = '1029472204308393704';
const RAKUTEN_AFFILIATE_ID = '12426598.beaffa49.12426599.e0b47e86';

const params = new URLSearchParams({
  applicationId: RAKUTEN_APPLICATION_ID,
  affiliateId: RAKUTEN_AFFILIATE_ID,
  largeClassCode: 'japan',
  middleClassCode: 'kanagawa',
  smallClassCode: 'hakone',
  hits: '5',
  responseType: 'small',
  datumType: '1',
  formatVersion: '2',
});

const url = `https://app.rakuten.co.jp/services/api/Travel/SimpleHotelSearch/20170426?${params}`;

const response = await fetch(url);
const data = await response.json();

console.log('レスポンス構造:');
console.log(JSON.stringify(data, null, 2));
