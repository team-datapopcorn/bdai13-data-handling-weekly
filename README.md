# BDAI 13기 · 데이터 핸들링과 자동화 — 5~16주 실습 데이터

BDAI 13기 정규반 "데이터분석 실전반 — 데이터 핸들링과 자동화" 5~16주차 실습에 쓰는 데이터와 과제 정의를 모은 저장소입니다. 1~4주차는 공공데이터를 매주 직접 API로 받아오므로 이 저장소가 필요 없고([`2_강의자료/exercises`](https://github.com/team-datapopcorn/b2b-lecture-note) 참고), 5주차부터는 실습마다 필요한 데이터를 여기서 미리 준비해 둡니다.

전부 가상 데이터입니다. 가상 온라인 스토어 **카라멜팝콘**(팝콘·음료·스낵·굿즈 판매)을 기준으로 고객·주문·로그인 기록을 만들었습니다. 실제 인물·거래·금액이 아닙니다.

## SQL 실습 서버 (5·6·14주)

로컬 SQLite 말고 실제로 여러 사람이 접속해 쿼리하는 **Postgres 실습 서버**를 운영합니다(Supabase, `bdai13` 스키마). 계정은 읽기 전용이라 데이터를 실수로 바꿀 걱정이 없습니다.

```python
!pip install psycopg2-binary -q
import psycopg2, pandas as pd
conn = psycopg2.connect(
    host="aws-1-us-east-1.pooler.supabase.com", port=6543,
    dbname="postgres", user="bdai13_student.ihenzvyxmlqmfrwjeknd",
    password="<수업 공지 확인>", sslmode="require",
)
pd.read_sql("SELECT * FROM bdai13.orders LIMIT 5", conn)
```

테이블 앞에 항상 `bdai13.`을 붙입니다. 자세한 사용법은 `week05_sql_aggregation/README.md`.

## 구조

한 주차 = 한 폴더. 폴더 안 `README.md`에 그 주에 **무엇이 준비되어 있고, 무엇을 해야 하는지**를 정의합니다.

| 폴더 | 주차 | 핵심 개념 | 데이터 |
|---|---|---|---|
| [`_shared/`](_shared/) | 5·6·14주 공용 | — | `caramelpopcorn.db` (SQLite, 고객·상품·주문·주문항목·로그인 5개 테이블) |
| [`week05_sql_aggregation/`](week05_sql_aggregation/) | 5주 | SQL ① 집계, AI 쿼리를 읽고 검증 | `_shared/caramelpopcorn.db` |
| [`week06_sql_window/`](week06_sql_window/) | 6주 | SQL ② 윈도우 함수·서브쿼리 | `_shared/caramelpopcorn.db` |
| [`week07_vectorization/`](week07_vectorization/) | 7주 | 벡터화 vs 반복문 | `transactions_large.csv` (30만행) |
| [`week08_reproducibility/`](week08_reproducibility/) | 8주 | 재현 가능한 코드 + 과제 1 | 새 데이터 없음 — 그동안 쓴 코드를 정리 |
| [`week09_pandas_limits/`](week09_pandas_limits/) | 9주 | Pandas의 한계, Polars·Dask | `generate_big_data.py` (실행해서 만드는 대용량 데이터) |
| [`week10_automation_thinking/`](week10_automation_thinking/) | 10주 | 자동화 사고: 반복을 분해한다 | 새 데이터 없음 — 자기 반복 업무를 재료로 |
| [`week11_report_automation/`](week11_report_automation/) | 11주 | 반복 리포트 자동화(Python) + 과제 2 | `monthly/2026-01.csv` ~ `2026-06.csv` |
| [`week12_n8n_demo/`](week12_n8n_demo/) | 12주 | 노코드 파이프라인 데모: n8n | `week11_report_automation/monthly/` 재사용(강사 데모) |
| [`week13_claude_code/`](week13_claude_code/) | 13주 | AI 에이전트: Claude Code | `messy_sales_raw.csv` (일부러 지저분하게 만듦) |
| [`week14_text2sql/`](week14_text2sql/) | 14주 | Text2SQL과 분석 자동화 | `_shared/caramelpopcorn.db` 재사용 |
| [`week15_metrics/`](week15_metrics/) | 15주 | 지표로 마무리: OMTM·KPI·데이터 품질 | `week11_report_automation/monthly/` 재사용 |
| [`week16_capstone/`](week16_capstone/) | 16주 | 과제 2 발표와 회고 | 새 데이터 없음 — 과제 2 결과물 |

## 데이터 재생성

전부 [`generate.py`](generate.py) 하나로 만듭니다. 시드를 고정해 언제 돌려도 같은 데이터가 나옵니다.

```bash
pip install pandas
python generate.py
```

`_shared/caramelpopcorn.db`, `week07_vectorization/transactions_large.csv`, `week11_report_automation/monthly/*.csv`, `week13_claude_code/messy_sales_raw.csv`를 다시 만듭니다. 데이터를 손대고 싶으면 이 파일을 고칩니다 — 각 주차 폴더에 직접 CSV를 새로 얹지 않습니다(원천이 둘로 갈라지면 어긋납니다).

## 카라멜팝콘 데이터 사전

- **customers** — `customer_id`, `name`, `region`(서울/경기/…/기타), `joined_date`
- **products** — `product_id`, `name`, `category`(팝콘/음료/스낵/굿즈), `price`
- **orders** — `order_id`, `customer_id`, `order_date`, `order_total`
- **order_items** — `item_id`, `order_id`, `product_id`, `qty`, `unit_price`
- **logins** — `login_id`, `customer_id`, `login_date` (6주차 리텐션 분석용 세션 로그)

## 라이선스

[MIT](./LICENSE). 교육 목적으로 자유롭게 가져다 씁니다.
