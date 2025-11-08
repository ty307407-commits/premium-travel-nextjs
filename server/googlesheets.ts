import { google } from 'googleapis';
import fs from 'fs';

// Google Sheets API設定
const SPREADSHEET_ID = '1IuNe90BEjsFGLpCxF8sGbmuHDizlUhkoh803ukXdjYs';
const CREDENTIALS_PATH = '/home/ubuntu/upload/gen-lang-client-0978608719-8ac8ccf348c6.json';

// 認証クライアントの作成
function getAuthClient() {
  const credentials = JSON.parse(fs.readFileSync(CREDENTIALS_PATH, 'utf8'));
  
  const auth = new google.auth.GoogleAuth({
    credentials,
    scopes: ['https://www.googleapis.com/auth/spreadsheets.readonly'],
  });
  
  return auth;
}

// Google Sheets APIクライアントの取得
async function getSheetsClient() {
  const auth = getAuthClient();
  const authClient = await auth.getClient();
  
  return google.sheets({ version: 'v4', auth: authClient });
}

/**
 * Content_Templatesシートからデータを取得
 */
export async function getContentTemplates() {
  try {
    const sheets = await getSheetsClient();
    
    const response = await sheets.spreadsheets.values.get({
      spreadsheetId: SPREADSHEET_ID,
      range: '⭐️Content_Templates!A:K', // A列からK列まで
    });
    
    const rows = response.data.values;
    
    if (!rows || rows.length === 0) {
      return [];
    }
    
    // ヘッダー行を取得
    const headers = rows[0];
    
    // データ行を変換
    const templates = rows.slice(1).map((row) => {
      const template: any = {};
      headers.forEach((header, index) => {
        template[header] = row[index] || '';
      });
      return template;
    });
    
    return templates;
  } catch (error) {
    console.error('Error fetching Content_Templates:', error);
    throw new Error('Failed to fetch Content_Templates from Google Sheets');
  }
}

/**
 * OnsenAreasシートからデータを取得
 */
export async function getOnsenAreas() {
  try {
    const sheets = await getSheetsClient();
    
    const response = await sheets.spreadsheets.values.get({
      spreadsheetId: SPREADSHEET_ID,
      range: '⭐️OnsenAreas!A:J', // A列からJ列まで
    });
    
    const rows = response.data.values;
    
    if (!rows || rows.length === 0) {
      return [];
    }
    
    // ヘッダー行を取得
    const headers = rows[0];
    
    // データ行を変換
    const areas = rows.slice(1).map((row) => {
      const area: any = {};
      headers.forEach((header, index) => {
        area[header] = row[index] || '';
      });
      return area;
    });
    
    return areas;
  } catch (error) {
    console.error('Error fetching OnsenAreas:', error);
    throw new Error('Failed to fetch OnsenAreas from Google Sheets');
  }
}

/**
 * 特定の温泉地データを取得
 */
export async function getOnsenArea(regionName: string) {
  const areas = await getOnsenAreas();
  return areas.find((area) => area.region_name === regionName);
}

/**
 * Themesシートからデータを取得
 */
export async function getThemes() {
  try {
    const sheets = await getSheetsClient();
    
    const response = await sheets.spreadsheets.values.get({
      spreadsheetId: SPREADSHEET_ID,
      range: '⭐️Themes!A:Z', // A列からZ列まで（必要に応じて調整）
    });
    
    const rows = response.data.values;
    
    if (!rows || rows.length === 0) {
      return [];
    }
    
    // ヘッダー行を取得
    const headers = rows[0];
    
    // データ行を変換
    const themes = rows.slice(1).map((row) => {
      const theme: any = {};
      headers.forEach((header, index) => {
        theme[header] = row[index] || '';
      });
      return theme;
    });
    
    return themes;
  } catch (error) {
    console.error('Error fetching Themes:', error);
    throw new Error('Failed to fetch Themes from Google Sheets');
  }
}

/**
 * 特定のテーマデータを取得
 */
export async function getTheme(themeName: string) {
  const themes = await getThemes();
  return themes.find((theme) => theme.theme_name === themeName);
}
