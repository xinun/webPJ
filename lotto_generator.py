import pandas as pd
import random
from urllib.error import URLError
import time

# --- 분석에 필요한 헬퍼 함수 ---

def is_all_even_or_all_odd(combination: tuple) -> bool:
    """조합이 모두 짝수이거나 모두 홀수인지 확인합니다."""
    return all(num % 2 == 0 for num in combination) or all(num % 2 != 0 for num in combination)

def has_consecutive_numbers(combination: tuple) -> bool:
    """조합에 연속된 숫자가 포함되어 있는지 확인합니다. (조합은 정렬된 상태로 들어옵니다)"""
    return any(combination[i] + 1 == combination[i + 1] for i in range(len(combination) - 1))

# --- app.py에서 호출할 메인 함수 ---

def get_lotto_stats_and_numbers(count: int) -> dict:
    """
    GitHub의 최신 당첨 데이터를 분석하여 통계 정보와 'count' 개수만큼의 로또 번호 세트를 생성합니다.
    """
    print("\n--- [로또 생성 로그] ---")
    start_time = time.time()
    
    # GitHub 저장소에 있는 원본 CSV 파일 주소
    url = 'https://raw.githubusercontent.com/happylie/lotto_data/main/lotto.csv'

    # 1. GitHub에서 데이터를 불러옵니다.
    print("1. GitHub에서 최신 데이터 다운로드 중...")
    try:
        lotto_data_raw = pd.read_csv(url, header=None)
        numbers_columns = [1, 2, 3, 4, 5, 6]
        past_numbers_df = lotto_data_raw[numbers_columns]
        existing_combinations = set(past_numbers_df.apply(lambda row: tuple(sorted(row)), axis=1))
    except URLError:
        raise ConnectionError("GitHub에서 로또 데이터를 가져올 수 없습니다. 인터넷 연결을 확인해주세요.")
    except Exception as e:
        raise ValueError(f"데이터 처리 중 오류가 발생했습니다: {e}")
    print(f"   - 데이터 로딩 완료. (소요 시간: {time.time() - start_time:.2f}초)")

    # 2. 과거 당첨 번호 통계를 분석합니다.
    numbers_flattened = past_numbers_df.values.flatten()
    number_frequency = pd.Series(numbers_flattened).value_counts()
    stats = {
        "most_frequent": [{"number": int(num), "frequency": int(freq)} for num, freq in number_frequency.head(5).items()],
        "least_frequent": [{"number": int(num), "frequency": int(freq)} for num, freq in number_frequency.tail(5).items()]
    }
    print("2. 과거 당첨 번호 통계 분석 완료.")

    # 3. 새로운 필터링 규칙에 맞는 번호 조합을 생성합니다.
    print(f"3. {count}개의 새로운 번호 조합 생성 시작...")
    generated_sets = []
    attempts = 0
    max_attempts = 1000000
    
    # 필터링 로그를 위한 카운터
    rejection_counts = {"existing": 0, "duplicate": 0, "even_odd": 0, "consecutive": 0}

    while len(generated_sets) < count and attempts < max_attempts:
        attempts += 1
        random_combination = tuple(sorted(random.sample(range(1, 46), 6)))
        
        # 각 필터링 규칙을 순서대로 확인하고 원인을 카운트합니다.
        if random_combination in existing_combinations:
            rejection_counts["existing"] += 1
            continue
        if random_combination in [tuple(s) for s in generated_sets]:
            rejection_counts["duplicate"] += 1
            continue
        if is_all_even_or_all_odd(random_combination):
            rejection_counts["even_odd"] += 1
            continue
        if has_consecutive_numbers(random_combination):
            rejection_counts["consecutive"] += 1
            continue
        
        # 모든 필터를 통과하면 유효한 조합으로 추가하고 로그를 남깁니다.
        generated_sets.append(list(random_combination))
        print(f"   => [{len(generated_sets)}/{count}] 유효한 조합 발견! (총 {attempts}회 시도)")
    
    # 4. 생성 결과 및 로그 요약 출력
    generation_time = time.time() - start_time
    print("\n--- [생성 결과 요약] ---")
    print(f"요청 개수: {count}개, 생성된 개수: {len(generated_sets)}개")
    print(f"총 시도 횟수: {attempts}회 (최대 {max_attempts}회)")
    print(f"총 소요 시간: {generation_time:.2f}초")
    print("\n[필터링 상세 로그]")
    print(f" - 과거 당첨과 중복: {rejection_counts['existing']}회")
    print(f" - 이번 생성과 중복: {rejection_counts['duplicate']}회")
    print(f" - 짝수/홀수 편중: {rejection_counts['even_odd']}회")
    print(f" - 연속 번호 포함: {rejection_counts['consecutive']}회")
    print("------------------------\n")
    
    if len(generated_sets) < count:
        print(f"Warning: 엄격한 규칙으로 인해 요청된 {count}개 중 {len(generated_sets)}개만 생성했습니다.")

    # 5. 생성된 번호와 통계 데이터를 함께 딕셔너리 형태로 반환합니다.
    return {"sets": generated_sets, "stats": stats}
