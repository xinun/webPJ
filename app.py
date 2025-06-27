from flask import Flask, render_template, request, jsonify
# lotto_generator에서 올바른 함수를 가져옵니다.
from lotto_generator import get_lotto_stats_and_numbers

# Flask 앱을 생성합니다.
app = Flask(__name__)

@app.route("/")
def index():
    """메인 페이지를 렌더링합니다."""
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate_numbers():
    """
    '/generate' 주소로 들어오는 POST 요청을 처리하는 함수입니다.
    이 부분이 없으면 404 오류가 발생합니다.
    """
    count = 1
    try:
        # 프론트엔드에서 보낸 요청에서 생성할 개수(count)를 가져옵니다.
        data = request.get_json()
        count = int(data.get('count', 1))
    except Exception:
        # 요청에 문제가 있으면 기본값 1을 사용합니다.
        count = 1
        
    try:
        # lotto_generator의 함수를 호출하여 번호와 통계를 받아옵니다.
        result_data = get_lotto_stats_and_numbers(count)
        
        # 생성된 번호가 없는 경우, 클라이언트에 에러 메시지를 보냅니다.
        if not result_data.get("sets"):
            return jsonify({"error": "조건에 맞는 번호를 생성하지 못했습니다. 잠시 후 다시 시도해주세요."}), 500
        
        # 생성된 데이터를 JSON 형태로 클라이언트에 성공적으로 응답합니다.
        return jsonify(result_data)
    
    except (ConnectionError, ValueError) as e:
        # 데이터 다운로드나 처리 중 발생한 오류를 처리합니다.
        print(f"ERROR: {e}")
        return jsonify({"error": str(e)}), 500
    except Exception as e:
        # 그 외 예상치 못한 모든 서버 오류를 처리합니다.
        print(f"An unexpected error occurred: {e}")
        return jsonify({"error": "알 수 없는 서버 오류가 발생했습니다. 서버 로그를 확인해주세요."}), 500

# 이 파일을 직접 실행했을 때 Flask 개발 서버를 시작합니다.
if __name__ == "__main__":
    app.run(debug=True)
