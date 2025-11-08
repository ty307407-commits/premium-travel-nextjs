import { google } from 'googleapis';
import fs from 'fs';

const SPREADSHEET_ID = '1IuNe90BEjsFGLpCxF8sGbmuHDizlUhkoh803ukXdjYs';
const CREDENTIALS_PATH = '/home/ubuntu/upload/gen-lang-client-0978608719-8ac8ccf348c6.json';

const credentials = JSON.parse(fs.readFileSync(CREDENTIALS_PATH, 'utf8'));

const auth = new google.auth.GoogleAuth({
  credentials,
  scopes: ['https://www.googleapis.com/auth/spreadsheets.readonly'],
});

const authClient = await auth.getClient();
const sheets = google.sheets({ version: 'v4', auth: authClient });

const response = await sheets.spreadsheets.get({
  spreadsheetId: SPREADSHEET_ID,
});

console.log('シート一覧:');
response.data.sheets.forEach((sheet) => {
  console.log(`- ${sheet.properties.title}`);
});
