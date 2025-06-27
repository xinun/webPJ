# 필요한 라이브러리를 불러옵니다.
from flask import Flask, render_template, request
import random

# Flask 앱을 생성합니다.
app = Flask(__name__)

# 기본 URL 경로("/")에 대한 라우트를 정의합니다.
# GET 방식(처음 페이지 접속)과 POST 방식(버튼 클릭)을 모두 처리합니다.
@app.route("/", methods=["GET", "POST"])
def index():
    numbers = []  # 번호를 담을 리스트를 미리 만듭니다.
    
    # 만약 사용자가 '번호 뽑기' 버튼을 눌러서(POST 요청) 접속했다면
    if request.method == "POST":
        # 1부터 45까지의 숫자 중에서 6개를 중복 없이 뽑아 리스트로 만듭니다.
        # sorted() 함수를 이용해 오름차순으로 정렬합니다.
        numbers = sorted(random.sample(range(1, 46), 6))
        
    # index.html 파일을 화면에 보여줍니다.
    # numbers 리스트를 HTML 파일로 전달하여 화면에 표시할 수 있도록 합니다.
    return render_template("index.html", numbers=numbers)

# 이 파일을 직접 실행했을 때 Flask 개발 서버를 시작합니다.
if __name__ == "__main__":
    app.run(debug=True)