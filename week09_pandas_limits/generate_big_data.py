"""
9주차용 대용량 데이터 생성기.
저장소에는 큰 파일을 커밋하지 않는다 — 이 스크립트를 각자 실행해서 로컬에 만든다.
행 수를 인자로 조절해 "얼마나 커지면 Pandas가 버거워지는지"를 직접 느껴본다.
"""
import sys
import random
import csv

random.seed(42)


def generate(n_rows: int, out_path: str) -> None:
    regions = ["서울", "경기", "인천", "부산", "대구", "광주", "대전", "기타"]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["txn_id", "customer_id", "product_id", "qty", "unit_price", "region", "note"])
        for i in range(1, n_rows + 1):
            w.writerow([
                i,
                random.randint(1, 50_000),
                random.randint(1, 10),
                random.randint(1, 5),
                random.choice([2900, 3200, 3500, 4900, 5400, 12000, 18000]),
                random.choice(regions),
                "카라멜팝콘 거래 시뮬레이션 데이터 " * random.randint(1, 3),
            ])


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 5_000_000
    out = sys.argv[2] if len(sys.argv) > 2 else "big_transactions.csv"
    generate(n, out)
    print(f"{out} 생성 완료 — {n:,}행")
