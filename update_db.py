import requests
import os

DB_URL = 'https://raw.githubusercontent.com/happylie/lotto_data/main/lotto_data.db'
DB_PATH = 'lotto_data.db'

def update_lotto_db_from_github():
    print(f"1. GitHub에서 최신 '{DB_PATH}' 다운로드 중...")
    try:
        response = requests.get(DB_URL)
        response.raise_for_status()
        with open(DB_PATH, 'wb') as f:
            f.write(response.content)
        file_size = os.path.getsize(DB_PATH) / 1024 / 1024
        print(f"✅ '{DB_PATH}' 다운로드 및 업데이트 성공! (크기: {file_size:.2f} MB)")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR: 데이터베이스 파일 다운로드 중 오류가 발생했습니다: {e}")
        return False