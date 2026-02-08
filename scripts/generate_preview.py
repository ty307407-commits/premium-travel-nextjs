
import mysql.connector
import os
import sys

# HTMLプレビュー生成用スクリプト
def generate_preview_html():
    page_id = 897
    output_file = f"preview_{page_id}.html"

    print(f"Fetching article for page {page_id}...")
    
    # DB接続（一貫性のために前のスクリプトと同じ設定）
    conn = mysql.connector.connect(
        host='gateway01.ap-northeast-1.prod.aws.tidbcloud.com',
        port=4000,
        user='4VWXcjUowH2PPCE.root',
        password='6KcooGBdpDcmeIGI',
        database='test',
        ssl_verify_cert=False,
        use_pure=True
    )
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT title, content, meta_description FROM articles WHERE page_id = %s", (page_id,))
    article = cursor.fetchone()
    conn.close()

    if not article:
        print("Article not found!")
        return

    # コンテンツの整形（簡易的なマークダウンのHTML変換）
    # 通常はMarkdownパーサーを通すが、Geminiの出力はマークダウンが混じる場合がある
    # V4と同じロジックを使うのがベストだが、ここでは確認用に簡易整形
    import markdown
    
    # プレースホルダーの強調表示
    content = article['content']
    content = content.replace("[RADAR_CHART:", "<div style='background:#e0f7fa; padding:10px; border:2px dashed #006064; text-align:center;'>📊 RADAR CHART PLACEHOLDER: ")
    content = content.replace("[HOTEL_LINK:", "<div style='background:#fff3e0; padding:10px; border:2px dashed #e65100; text-align:center;'>🏨 HOTEL LINK PLACEHOLDER: ")
    content = content.replace("[HOTEL_IMAGE:", "<div style='background:#f3e5f5; padding:10px; border:2px dashed #4a148c; text-align:center;'>🖼️ IMAGE PLACEHOLDER: ")
    content = content.replace("[REVIEW_BLOCK:", "<div style='background:#e8f5e9; padding:10px; border:2px dashed #1b5e20; text-align:center;'>💬 REVIEW BLOCK PLACEHOLDER: ")
    content = content.replace("[CTA_BUTTON:", "<div style='background:#ffebee; padding:10px; border:2px dashed #b71c1c; text-align:center;'>🔘 CTA BUTTON PLACEHOLDER: ")
    
    # 閉じ括弧の処理（簡易）
    content = content.replace("]", "</div>") 
    
    # マークダウンをHTMLに変換
    html_content = markdown.markdown(content)

    html_template = f"""
    <!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Preview: {article['title']}</title>
        <style>
            body {{ font-family: "Helvetica Neue", Arial, "Hiragino Kaku Gothic ProN", "Hiragino Sans", Meiryo, sans-serif; line-height: 1.8; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; background-color: #f9f9f9; }}
            .container {{ background: white; padding: 40px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.05); }}
            h1 {{ font-size: 2em; border-bottom: 2px solid #008080; padding-bottom: 10px; margin-bottom: 30px; color: #008080; }}
            h2 {{ font-size: 1.6em; margin-top: 40px; margin-bottom: 20px; color: #333; border-left: 5px solid #008080; padding-left: 15px; }}
            h3 {{ font-size: 1.3em; margin-top: 30px; color: #444; }}
            p {{ margin-bottom: 1.5em; }}
            .meta-info {{ background: #eee; padding: 15px; margin-bottom: 30px; border-radius: 5px; font-size: 0.9em; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="meta-info">
                <strong>Meta Description:</strong><br>
                {article['meta_description']}
            </div>
            
            <h1>{article['title']}</h1>
            
            <div class="content">
                {html_content}
            </div>
        </div>
    </body>
    </html>
    """
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_template)
        
    print(f"✅ Preview HTML generated: {output_file}")
    
    # 自動的にブラウザで開く（Mac用）
    os.system(f"open {output_file}")

if __name__ == "__main__":
    generate_preview_html()
