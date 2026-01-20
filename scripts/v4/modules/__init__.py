# V4 モジュール
from .hotel_fetcher import HotelFetcher, fetch_candidates_for_page
from .post_processor import PostProcessor, process_article

# Geminiクライアントは遅延インポート（依存関係の問題を回避）
def get_gemini_client():
    from .gemini_client import GeminiClient
    return GeminiClient

def generate_article_with_gemini(prompt):
    from .gemini_client import generate_article_with_gemini as _generate
    return _generate(prompt)
