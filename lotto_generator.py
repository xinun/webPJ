import pandas as pd
import random
from urllib.error import URLError

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
    # GitHub 저장소에 있는 원본 CSV 파일 주소
    url = 'https://raw.githubusercontent.com/happylie/lotto_data/main/lotto.csv'

    # 1. GitHub에서 데이터를 불러옵니다.
    try:
        # 이 CSV 파일은 헤더가 없으므로 header=None 옵션을 사용합니다.
        lotto_data_raw = pd.read_csv(url, header=None)
        
        # 첫번째 열은 회차 정보이므로, 1번부터 6번 열까지(실제 당첨번호)를 사용합니다.
        numbers_columns = [1, 2, 3, 4, 5, 6]
        past_numbers_df = lotto_data_raw[numbers_columns]
        
        # 빠른 조회를 위해 정렬된 튜플 형태의 세트(set)로 만들어 저장합니다.
        existing_combinations = set(past_numbers_df.apply(lambda row: tuple(sorted(row)), axis=1))
    except URLError:
        # 인터넷 연결 문제나 GitHub 접속 오류 시
        raise ConnectionError("GitHub에서 로또 데이터를 가져올 수 없습니다. 인터넷 연결을 확인해주세요.")
    except Exception as e:
        # 그 외 파일 형식 등의 문제 발생 시
        raise ValueError(f"데이터 처리 중 오류가 발생했습니다: {e}")

    # 2. 과거 당첨 번호 통계를 분석합니다.
    numbers_flattened = past_numbers_df.values.flatten()
    number_frequency = pd.Series(numbers_flattened).value_counts()
    
    # 웹에 보내기 좋은 형식으로 데이터를 가공합니다. (JSON 직렬화 가능하도록 int로 변환)
    stats = {
        "most_frequent": [
            {"number": int(num), "frequency": int(freq)}
            for num, freq in number_frequency.head(5).items()
        ],
        "least_frequent": [
            {"number": int(num), "frequency": int(freq)}
            for num, freq in number_frequency.tail(5).items()
        ]
    }

    # 3. 새로운 필터링 규칙에 맞는 번호 조합을 생성합니다.
    generated_sets = []
    attempts = 0
    max_attempts = 1000000

    while len(generated_sets) < count and attempts < max_attempts:
        random_combination = tuple(sorted(random.sample(range(1, 46), 6)))
        is_valid = (
            random_combination not in existing_combinations and
            random_combination not in [tuple(s) for s in generated_sets] and
            not is_all_even_or_all_odd(random_combination) and
            not has_consecutive_numbers(random_combination)
        )
        if is_valid:
            generated_sets.append(list(random_combination))
        attempts += 1
    
    if len(generated_sets) < count:
        print(f"Warning: Could not generate {count} sets due to strict rules.")

    # 4. 생성된 번호와 통계 데이터를 함께 딕셔너리 형태로 반환합니다.
    return {"sets": generated_sets, "stats": stats}
