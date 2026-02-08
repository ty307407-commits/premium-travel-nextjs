from google import genai
import os

api_key = "AIzaSyDJjjt-m-89aj6z4khO4YbDNtP21M92YAM"
client = genai.Client(api_key=api_key)

print("Gemini 2.0 Flash 接続テスト:")
try:
    # 2.0 Flashを指定
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents="Hello, Gemini 2.0!"
    )
    print(f"成功: {response.text}")
    
except Exception as e:
    print(f"2.0 Flash エラー: {e}")
    
    # 失敗したら1.5 Flashで試す
    print("\nGemini 1.5 Flash 接続テスト:")
    try:
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents="Hello, Gemini 1.5!"
        )
        print(f"成功: {response.text}")
    except Exception as e2:
        print(f"1.5 Flash エラー: {e2}")

# モデル一覧（参考）
print("\n--- 利用可能なモデル ---")
try:
    for m in client.models.list(config={"page_size": 100}):
        print(m.name)
except Exception as e:
    print(f"一覧取得エラー: {e}")
