"""
BDAI 13기 데이터 핸들링과 자동화 — 5~16주 실습 데이터 생성 스크립트.
가상 회사 '카라멜팝콘'(온라인 스토어) 데이터를 만든다. 실제 인물·거래 없음.
재실행하면 항상 같은 결과가 나오도록 시드를 고정한다.
"""
import sqlite3
import random
import os
import csv
from datetime import date, timedelta

random.seed(42)

ROOT = os.path.dirname(os.path.abspath(__file__))

# ── 공통 마스터 데이터 ──────────────────────────────────────────
CATEGORIES = ["팝콘", "음료", "스낵", "굿즈"]
PRODUCTS = [
    (1, "카라멜팝콘 오리지널", "팝콘", 4900),
    (2, "카라멜팝콘 청양마요", "팝콘", 5400),
    (3, "카라멜팝콘 갈릭버터", "팝콘", 5400),
    (4, "콜드브루 캔", "음료", 3200),
    (5, "스파클링 레몬에이드", "음료", 3500),
    (6, "옥수수칩 오리지널", "스낵", 2900),
    (7, "옥수수칩 매운맛", "스낵", 2900),
    (8, "카라멜팝콘 에코백", "굿즈", 12000),
    (9, "카라멜팝콘 텀블러", "굿즈", 18000),
    (10, "카라멜팝콘 스티커팩", "굿즈", 3000),
]
REGIONS = ["서울", "경기", "인천", "부산", "대구", "광주", "대전", "기타"]

N_CUSTOMERS = 400

def make_customers():
    rows = []
    start = date(2025, 1, 1)
    for cid in range(1, N_CUSTOMERS + 1):
        joined = start + timedelta(days=random.randint(0, 600))
        rows.append((cid, f"고객{cid:04d}", random.choice(REGIONS), joined.isoformat()))
    return rows

def make_orders_and_items(customers):
    orders, items = [], []
    order_id = 1
    item_id = 1
    for cid, _, _, joined in customers:
        joined_date = date.fromisoformat(joined)
        n_orders = random.choices([0, 1, 2, 3, 4, 5, 8], weights=[10, 25, 25, 15, 10, 10, 5])[0]
        last_date = joined_date
        for _ in range(n_orders):
            gap = random.randint(3, 90)
            last_date = last_date + timedelta(days=gap)
            if last_date > date(2026, 6, 30):
                break
            n_items = random.randint(1, 4)
            chosen = random.sample(PRODUCTS, n_items)
            order_total = 0
            for pid, _, _, price in chosen:
                qty = random.randint(1, 3)
                order_total += price * qty
                items.append((item_id, order_id, pid, qty, price))
                item_id += 1
            orders.append((order_id, cid, last_date.isoformat(), order_total))
            order_id += 1
    return orders, items

def make_logins(customers):
    """세션 로그 — 6주차 리텐션 분석용. 로그인할수록 최근에 몰리게(가입 후 서서히 이탈)."""
    rows = []
    login_id = 1
    for cid, _, _, joined in customers:
        joined_date = date.fromisoformat(joined)
        active_weeks = random.choices([1, 2, 4, 8, 12, 20, 30], weights=[15, 20, 20, 15, 12, 10, 8])[0]
        d = joined_date
        for w in range(active_weeks):
            if random.random() < 0.75:  # 매주 접속하진 않음
                login_date = d + timedelta(days=random.randint(0, 6))
                if login_date <= date(2026, 6, 30):
                    rows.append((login_id, cid, login_date.isoformat()))
                    login_id += 1
            d += timedelta(days=7)
    return rows

def build_sqlite():
    path = os.path.join(ROOT, "_shared", "caramelpopcorn.db")
    if os.path.exists(path):
        os.remove(path)
    con = sqlite3.connect(path)
    cur = con.cursor()
    cur.execute("CREATE TABLE customers (customer_id INTEGER PRIMARY KEY, name TEXT, region TEXT, joined_date TEXT)")
    cur.execute("CREATE TABLE products (product_id INTEGER PRIMARY KEY, name TEXT, category TEXT, price INTEGER)")
    cur.execute("CREATE TABLE orders (order_id INTEGER PRIMARY KEY, customer_id INTEGER, order_date TEXT, order_total INTEGER)")
    cur.execute("CREATE TABLE order_items (item_id INTEGER PRIMARY KEY, order_id INTEGER, product_id INTEGER, qty INTEGER, unit_price INTEGER)")
    cur.execute("CREATE TABLE logins (login_id INTEGER PRIMARY KEY, customer_id INTEGER, login_date TEXT)")

    customers = make_customers()
    cur.executemany("INSERT INTO customers VALUES (?,?,?,?)", customers)
    cur.executemany("INSERT INTO products VALUES (?,?,?,?)", PRODUCTS)

    orders, items = make_orders_and_items(customers)
    cur.executemany("INSERT INTO orders VALUES (?,?,?,?)", orders)
    cur.executemany("INSERT INTO order_items VALUES (?,?,?,?,?)", items)

    logins = make_logins(customers)
    cur.executemany("INSERT INTO logins VALUES (?,?,?)", logins)

    con.commit()
    con.close()
    print(f"[_shared] caramelpopcorn.db 생성 — 고객 {len(customers)}, 주문 {len(orders)}, 주문항목 {len(items)}, 로그인 {len(logins)}")

# ── 7주차: 벡터화 vs 반복문 (대용량 CSV) ────────────────────────
def build_week07():
    path = os.path.join(ROOT, "week07_vectorization", "transactions_large.csv")
    n = 300_000
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["txn_id", "customer_id", "product_id", "qty", "unit_price", "region"])
        start = date(2025, 1, 1)
        for i in range(1, n + 1):
            cid = random.randint(1, N_CUSTOMERS)
            pid = random.choice(PRODUCTS)
            qty = random.randint(1, 5)
            region = random.choice(REGIONS)
            w.writerow([i, cid, pid[0], qty, pid[3], region])
    print(f"[week07] transactions_large.csv 생성 — {n:,}행")

# ── 11주차: 월별 반복 리포트 원본 (schema가 살짝 흔들림 — 자동화가 이걸 버텨야 함) ─
def build_week11():
    months = ["2026-01", "2026-02", "2026-03", "2026-04", "2026-05", "2026-06"]
    for mi, month in enumerate(months):
        path = os.path.join(ROOT, "week11_report_automation", "monthly", f"{month}.csv")
        rows = []
        for pid, name, cat, price in PRODUCTS:
            base = random.randint(30, 150)
            trend = int(base * (1 + mi * 0.06))
            units = max(0, trend + random.randint(-15, 15))
            revenue = units * price
            row = {"product_id": pid, "product_name": name, "category": cat, "units_sold": units, "revenue": revenue}
            rows.append(row)
        fieldnames = ["product_id", "product_name", "category", "units_sold", "revenue"]
        # 4월(2026-04)부터 채널 컬럼 추가 — "매달 같은 모양일 거라 믿지 마라"는 함정
        if month >= "2026-04":
            fieldnames.append("channel")
            for r in rows:
                r["channel"] = random.choice(["온라인", "오프라인", "제휴"])
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(rows)
    print(f"[week11] monthly/ 6개월치 생성 (2026-04부터 channel 컬럼 추가됨 — 의도된 함정)")

# ── 13주차: Claude Code 정제 실습용 지저분한 원본 ────────────────
def build_week13():
    path = os.path.join(ROOT, "week13_claude_code", "messy_sales_raw.csv")
    rows = []
    for i in range(1, 251):
        pid, name, cat, price = random.choice(PRODUCTS)
        qty = random.randint(1, 5)
        region = random.choice(REGIONS + ["", "SEOUL", "seoul"])  # 표기 안 맞는 지역 함정
        d = date(2026, 1, 1) + timedelta(days=random.randint(0, 180))
        date_str = d.isoformat() if i % 7 != 0 else d.strftime("%Y/%m/%d")  # 날짜 형식 섞임
        row = {
            "주문id": i,
            "상품명": name if i % 23 != 0 else None,  # 결측
            "카테고리": cat,
            "수량": qty,
            "단가": price,
            "지역": region,
            "주문일": date_str,
        }
        rows.append(row)
    # 중복 행 몇 개 끼워넣기
    rows += rows[5:8]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["주문id", "상품명", "카테고리", "수량", "단가", "지역", "주문일"])
        w.writeheader()
        w.writerows(rows)
    print(f"[week13] messy_sales_raw.csv 생성 — {len(rows)}행 (결측·중복·표기 불일치·날짜형식 섞임 포함)")

if __name__ == "__main__":
    build_sqlite()
    build_week07()
    build_week11()
    build_week13()
    print("완료.")
