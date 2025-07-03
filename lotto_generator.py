import pandas as pd
import sqlite3
import random
import time

def is_all_even_or_all_odd(combination):
    return all(num % 2 == 0 for num in combination) or all(num % 2 != 0 for num in combination)

def has_consecutive_numbers(combination):
    return any(combination[i] + 1 == combination[i + 1] for i in range(len(combination) - 1))

def get_lotto_stats_and_numbers(count: int = 5) -> dict:
    print("\n--- [로또 생성 로그] ---")
    start_time = time.time()
    print("1. SQLite DB에서 로또 당첨 번호 불러오는 중...")

    try:
        conn = sqlite3.connect("lotto_data.db")
        query = "SELECT `1st`, `2nd`, `3rd`, `4th`, `5th`, `6th` FROM tb_lotto_list"
        past_numbers_df = pd.read_sql_query(query, conn)
        conn.close()
        existing_combinations = set(past_numbers_df.apply(lambda row: tuple(sorted(row)), axis=1))
        print(f"   - DB에서 {len(existing_combinations)}개 조합 불러옴")
    except Exception as e:
        raise ValueError(f"데이터베이스 로딩 중 오류 발생: {e}. 'app.py'를 실행하여 DB를 먼저 생성해주세요.")

    numbers_flattened = past_numbers_df.values.flatten()
    number_frequency = pd.Series(numbers_flattened).value_counts()
    stats = {
        "most_frequent": [{"number": int(num), "frequency": int(freq)} for num, freq in number_frequency.head(5).items()],
        "least_frequent": [{"number": int(num), "frequency": int(freq)} for num, freq in number_frequency.tail(5).items()]
    }

    generated_sets = []
    attempts = 0
    max_attempts = 1000000

    while len(generated_sets) < count and attempts < max_attempts:
        attempts += 1
        random_combination = tuple(sorted(random.sample(range(1, 46), 6)))

        if random_combination in existing_combinations: continue
        if random_combination in [tuple(s) for s in generated_sets]: continue
        if is_all_even_or_all_odd(random_combination): continue
        if has_consecutive_numbers(random_combination): continue

        generated_sets.append(list(random_combination))

    if len(generated_sets) < count:
        print(f"경고: 요청된 {count}개 중 {len(generated_sets)}개만 생성했습니다. (시도: {attempts}회)")

    print(f"총 생성 시간: {time.time() - start_time:.2f}초 / 시도: {attempts}회")
    return {"sets": generated_sets, "stats": stats}