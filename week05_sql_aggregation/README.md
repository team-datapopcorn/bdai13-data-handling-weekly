# 5주차 · SQL ① 집계 — AI 쿼리를 읽고 검증한다

## 오늘 얻어가는 것

분석 질문을 SQL 집계 쿼리로 바꾸는 걸 AI에게 시키고, 그 결과가 맞는지 직접 확인한다.

## 준비된 데이터

같은 데이터를 두 가지 방식으로 준비해 뒀다. 실습은 **Postgres 실습 서버** 기준으로 진행한다 — 여러 사람이 같은 서버에 접속해 쿼리하는, 실제 현업에 가장 가까운 형태다.

### 방법 A — Postgres 실습 서버 (추천)

가상 온라인 스토어 데이터가 공용 Postgres에 올라가 있다. 설치 없이 Colab에서 바로 접속한다. 계정은 **읽기 전용**(SELECT만 가능)이라 실수로 데이터를 바꿀 걱정이 없다.

```python
!pip install psycopg2-binary -q
import psycopg2, pandas as pd

conn = psycopg2.connect(
    host="aws-1-us-east-1.pooler.supabase.com",
    port=6543,
    dbname="postgres",
    user="bdai13_student.ihenzvyxmlqmfrwjeknd",
    password="<수업 공지 확인>",
    sslmode="require",
)
pd.read_sql("SELECT * FROM bdai13.orders LIMIT 5", conn)
```

> 테이블 이름 앞에 항상 `bdai13.`을 붙인다(스키마 이름). 다섯 개 테이블: `bdai13.customers`, `bdai13.products`, `bdai13.orders`, `bdai13.order_items`, `bdai13.logins`.

### 방법 B — 로컬 SQLite (오프라인/보조용)

`../_shared/caramelpopcorn.db`. 같은 스키마, 데이터 구성만 다르다(연습용 재현성 때문에 별도 생성).

```python
import sqlite3, pandas as pd
con = sqlite3.connect("../_shared/caramelpopcorn.db")
pd.read_sql("SELECT * FROM orders LIMIT 5", con)
```

## 해야 할 일

1. **테이블 구조 파악** — 다섯 테이블의 컬럼과 관계(고객 1명이 여러 주문, 주문 1건이 여러 주문항목)를 그려본다.
2. **AI에게 집계 쿼리 3개를 시킨다.**
   - 지역(`region`)별 총 매출과 주문 건수
   - 카테고리(`category`)별 판매 수량 상위 3개
   - 월별(`order_date`의 연-월) 매출 추이
3. **검증한다** — AI가 준 쿼리 결과를 pandas의 `groupby`로 같은 걸 계산해서 숫자가 일치하는지 대조한다. 하나라도 다르면 어느 쪽(SQL vs pandas)이 틀렸는지 원인을 찾는다.
4. **흔한 함정 확인** — `order_items`와 `orders`를 조인할 때 `JOIN` 조건을 빼먹으면 행이 부풀려진다(카티션 곱). AI 쿼리에 이 함정이 있는지 행 수로 확인한다.

## 산출물

- 위 3개 집계 쿼리(.sql 또는 노트북 셀)
- SQL 결과 vs pandas 결과 대조표
- "AI 쿼리가 처음에 뭘 놓쳤는지" 한 줄 메모

## 검증 체크

- [ ] SQL 집계 합계 = pandas 집계 합계
- [ ] 조인 후 행 수가 기대한 범위인가(부풀려지지 않았는가)
- [ ] `NULL`이 있는 컬럼을 집계에서 빠뜨리지 않았는가
