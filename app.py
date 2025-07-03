from flask import Flask, render_template, request, jsonify
from lotto_generator import get_lotto_stats_and_numbers
from update_db import update_lotto_db_from_github

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    try:
        count = request.json.get('count', 5) if request.is_json else 5
        data = get_lotto_stats_and_numbers(count=count)
        return jsonify(data)
    except Exception as e:
        print(f"ERROR: 로또 번호 생성 중 오류 발생: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("--- 서버 시작 준비 ---")

    # update_lotto_db_from_github() 함수의 성공 여부를 is_db_ready 변수에 저장
    is_db_ready = update_lotto_db_from_github()

    # 만약 DB가 준비되지 않았다면(False 라면), 메시지를 출력하고 서버 실행을 중단
    if not is_db_ready:
        print("❌ 데이터베이스 준비에 실패하여 서버를 시작할 수 없습니다.")
        print("   - 네트워크 연결 또는 방화벽 설정을 확인해주세요.")
        print("   - 이전 단계에서 안내한 `curl -v 'URL'` 테스트를 다시 진행하여 결과를 확인하는 것이 좋습니다.")
    else:
        # 성공한 경우에만 서버 실행
        print("--------------------")
        app.run(debug=True)
