import google.generativeai as genai
import os

# API Key設定
os.environ["GOOGLE_API_KEY"] = "AIzaSyDJjjt-m-89aj6z4khO4YbDNtP21M92YAM"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

print("利用可能なモデル一覧:")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")
except Exception as e:
    print(f"エラー: {e}")
