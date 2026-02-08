import mysql.connector
import json

TIDB_CONFIG = {
    'host': 'gateway01.ap-northeast-1.prod.aws.tidbcloud.com',
    'port': 4000,
    'user': '4VWXcjUowH2PPCE.root',
    'password': '6KcooGBdpDcmeIGI',
    'database': 'test'
}

def check_onsen_data():
    conn = mysql.connector.connect(**TIDB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    
    print("Checking total count...")
    cursor.execute("SELECT COUNT(*) as count FROM hotel_review_analysis_v2")
    count = cursor.fetchone()['count']
    print(f"Total analyzed hotels: {count}")
    
    print("\nChecking onsen quality...")
    cursor.execute("SELECT analysis_json FROM hotel_review_analysis_v2 LIMIT 100")
    rows = cursor.fetchall()
    
    onsen_quality_gt_0 = 0
    total_checked = 0
    
    for row in rows:
        try:
            data = json.loads(row['analysis_json'])
            # Logic here handles both dict and list (first item) structures if encountered
            if isinstance(data, list):
                if len(data) > 0:
                    data = data[0]
                else:
                    continue
            
            radar = data.get('radar_chart_data', {})
            quality = radar.get('onsen_quality', 0)
            if float(quality) > 0:
                onsen_quality_gt_0 += 1
            total_checked += 1
        except Exception as e:
            print(f"Error parsing JSON: {e}")

    print(f"Sample Check (100 rows): Used a valid JSON format: {total_checked}")
    print(f"Onsen Quality > 0 in sample: {onsen_quality_gt_0}")
    
    conn.close()

if __name__ == "__main__":
    check_onsen_data()
