import google.generativeai as genai
import os

api_key = "AIzaSyDJjjt-m-89aj6z4khO4YbDNtP21M92YAM"
genai.configure(api_key=api_key)

print("Gemini Pro テスト:")
try:
    # 最も標準的なモデルを指定
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content("こんにちは")
    print(f"成功: {response.text}")
except Exception as e:
    print(f"エラー: {e}")
