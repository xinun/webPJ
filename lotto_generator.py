# lotto_generator.py (사용자 정의 최종 알고리즘 v2 적용 버전)

import pandas as pd
import sqlite3
import random
import time
from collections import Counter

# --- 필터 함수들은 그대로 사용 ---
def is_all_even_or_all_odd(combination):
    """모든 숫자가 짝수이거나 홀수인지 확인"""
    return all(num % 2 == 0 for num in combination) or all(num % 2 != 0 for num in combination)

def has_consecutive_numbers(combination):
    """연속된 숫자가 있는지 확인"""
    return any(combination[i] + 1 == combination[i + 1] for i in range(len(combination) - 1))

# lotto_generator.py 파일의 이 함수만 교체해주세요.

def get_lotto_stats_and_numbers(count: int = 5) -> dict:
    print("\n--- [사용자 정의 알고리즘 v2 생성 로그] ---")
    start_time = time.time()
    
    # --- 1단계: 시뮬레이션을 통해 '엘리트 풀' 만들기 ---
    SIMULATION_COUNT = 100000  # 시뮬레이션 횟수
    TOP_N_POOL_SIZE = 15      # 시뮬레이션 결과 중 상위 몇 개의 번호를 엘리트 풀로 만들 것인가

    print(f"1. {SIMULATION_COUNT}회 시뮬레이션으로 '엘리트 풀' 생성 중...")
    
    all_numbers_from_simulation = []
    for _ in range(SIMULATION_COUNT):
        random_combination = random.sample(range(1, 46), 6)
        all_numbers_from_simulation.extend(random_combination)
        
    # 1b. 시뮬레이션 결과로 빈도수 계산
    number_frequencies = Counter(all_numbers_from_simulation)

    print("   - [시뮬레이션 빈도수 상세 결과 (높은 순)]")
    # .most_common()을 사용하면 가장 많이 나온 순서대로 정렬됩니다.
    for num, freq in number_frequencies.most_common():
        print(f"     ㄴ 숫자 {str(num).zfill(2)}: {freq}회")

    # 1c. 엘리트 풀 생성
    elite_pool = [num for num, freq in number_frequencies.most_common(TOP_N_POOL_SIZE)]
    print(f"   - 시뮬레이션 완료. 상위 {TOP_N_POOL_SIZE}개 번호로 엘리트 풀 생성: {elite_pool}")

    # --- 2단계: 엘리트 풀과 DB를 이용해 최종 조합 생성 ---
    print("2. DB 데이터 로드 및 최종 조합 생성 시작...")
    try:
        conn = sqlite3.connect("lotto_data.db")
        query = "SELECT `1st`, `2nd`, `3rd`, `4th`, `5th`, `6th` FROM tb_lotto_list"
        past_numbers_df = pd.read_sql_query(query, conn)
        conn.close()
        existing_combinations = set(past_numbers_df.apply(lambda row: tuple(sorted(row)), axis=1))
        print(f"   - DB에서 {len(existing_combinations)}개 조합 불러와 최종 필터로 사용")
    except Exception as e:
        raise ValueError(f"데이터베이스 로딩 중 오류 발생: {e}")

    generated_sets = set()
    final_attempts = 0
    while len(generated_sets) < count and final_attempts < 5000:
        final_attempts += 1
        
        if len(elite_pool) < 6:
             raise ValueError("엘리트 풀의 크기가 6보다 작아 조합을 만들 수 없습니다.")
        
        new_combination = tuple(sorted(random.sample(elite_pool, 6)))

        if new_combination in existing_combinations: continue
        if new_combination in generated_sets: continue
        if has_consecutive_numbers(new_combination): continue
        if is_all_even_or_all_odd(new_combination): continue
        
        generated_sets.add(new_combination)

    final_generated_list = [list(comb) for comb in generated_sets]

    # --- 3단계: 웹페이지 표시용 통계 생성 ---
    number_frequency_stats = pd.Series(past_numbers_df.values.flatten()).value_counts()
    stats = {
        "most_frequent": [{"number": int(num), "frequency": int(freq)} for num, freq in number_frequency_stats.head(5).items()],
        "least_frequent": [{"number": int(num), "frequency": int(freq)} for num, freq in number_frequency_stats.tail(5).items()]
    }
    
    print(f"총 생성 시간: {time.time() - start_time:.2f}초")
    return {"sets": final_generated_list, "stats": stats, "simulation_count": SIMULATION_COUNT}