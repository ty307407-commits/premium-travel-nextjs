import google.generativeai as genai
import os

api_key = "AIzaSyDJjjt-m-89aj6z4khO4YbDNtP21M92YAM"
genai.configure(api_key=api_key)

print("Geminiモデル一覧:")
try:
    models = genai.list_models()
    for m in models:
        print(f"- {m.name}")
except Exception as e:
    print(f"エラー: {e}")

print("\n--- テスト実行 ---")
try:
    # 確実に動く1.5-flashでテスト
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("こんにちは")
    print(f"応答: {response.text}")
except Exception as e:
    print(f"生成エラー: {e}")
