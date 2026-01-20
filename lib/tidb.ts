const TIDB_API_BASE = 'https://ap-northeast-1.data.tidbcloud.com/api/v1beta/app/dataapp-pgnDYdcU/endpoint'
const TIDB_PUBLIC_KEY = 'S2R9M3V0'
const TIDB_PRIVATE_KEY = '8cc2d2cd-7567-422a-a9d1-8a96b5643286'

function getAuthHeader(): string {
  const credentials = Buffer.from(`${TIDB_PUBLIC_KEY}:${TIDB_PRIVATE_KEY}`).toString('base64')
  return `Basic ${credentials}`
}

async function fetchTiDB<T>(endpoint: string, params?: Record<string, string | number>): Promise<T> {
  const url = new URL(`${TIDB_API_BASE}${endpoint}`)
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      url.searchParams.append(key, String(value))
    })
  }

  const response = await fetch(url.toString(), {
    headers: {
      'Authorization': getAuthHeader(),
    },
    next: { revalidate: 3600 }, // 1時間キャッシュ
  })

  if (!response.ok) {
    throw new Error(`TiDB API error: ${response.status}`)
  }

  const data = await response.json()
  return data.data.rows as T
}

export interface Theme {
  theme_id: string
  theme_title: string
  pages: string
}

export interface PageData {
  page_id: string
  theme_id: string
  theme_title: string
  region_name: string
  page_title: string
  url_slug: string
  meta_description: string
  hero_image_url: string
  prefecture_code: string
  area_code: string
  prefecture_name: string
  temp_full_markdown?: string
}

export async function getActiveThemes(): Promise<Theme[]> {
  return fetchTiDB<Theme[]>('/active_themes')
}

export async function getPageDetail(pageId: number): Promise<PageData | null> {
  const rows = await fetchTiDB<PageData[]>('/page_detail', { page_id: pageId })
  return rows[0] || null
}

export async function getRandomPages(limit: number = 5): Promise<PageData[]> {
  return fetchTiDB<PageData[]>('/random_pages', { limit_count: limit })
}

export async function getPagesByTheme(themeId: number): Promise<PageData[]> {
  // page_with_area エンドポイントを使用（将来的に専用エンドポイント追加可能）
  const allPages = await fetchTiDB<PageData[]>('/page_with_area')
  return allPages.filter(page => page.theme_id === String(themeId))
}
