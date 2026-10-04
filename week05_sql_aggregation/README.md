# 5주차 · SQL ① 집계 — AI 쿼리를 읽고 검증한다

## 오늘 얻어가는 것

분석 질문을 SQL 집계 쿼리로 바꾸는 걸 AI에게 시키고, 그 결과가 맞는지 직접 확인한다.
1~4주의 공공데이터 수집에 이어, **오늘부터 가상 온라인 스토어 ‘카라멜팝콘’ 데이터**를 사용한다. 실제 고객 정보가 아닌 수업용 가상데이터다.

## 실습 방법 선택

| 방법 | 준비 | 용도 |
|---|---|---|
| DBeaver Community | 프로그램 설치 | 테이블을 눈으로 확인하고 SQL 실행 |
| Google Colab | 구글 계정·브라우저 | SQL 실행 + pandas로 결과 검증 |

두 방법 모두 **같은 공용 Postgres 서버**에 접속한다. DBeaver에서 쿼리를 만들고 Colab에서 검증해도 된다. 계정은 읽기 전용이며, 비밀번호는 수업 중 강사가 안내한다.

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/team-datapopcorn/bdai13-data-handling-weekly/blob/master/week05_sql_aggregation/05_sql_aggregation_colab.ipynb)

## 방법 A — DBeaver 설치와 접속

### 1. 무료 Community 버전 설치

[공식 다운로드 페이지](https://dbeaver.io/download/)에서 운영체제에 맞는 **DBeaver Community**를 선택한다.

- **Windows:** CPU에 맞는 EXE 설치 파일을 실행하고 설치 마법사를 따른다. 일반적인 Intel·AMD PC는 x86 버전을 선택한다.
- **macOS:** Apple Silicon(M1 이후) 또는 Intel에 맞는 DMG를 받는다. DMG를 열고 DBeaver를 Applications(응용 프로그램) 폴더로 끌어 넣은 뒤 실행한다.

### 2. PostgreSQL 연결 만들기

1. DBeaver 실행 → **새 데이터베이스 연결(New Database Connection)** → **PostgreSQL** 선택.
2. 아래 접속 정보를 입력한다.

| 항목 | 값 |
|---|---|
| Host | `aws-1-us-east-1.pooler.supabase.com` |
| Port | `6543` |
| Database | `postgres` |
| Username | `bdai13_student.ihenzvyxmlqmfrwjeknd` |
| Password | 수업 중 안내하는 비밀번호 |
| SSL | 사용함, Mode `require` |

3. **SSL** 탭에서 SSL 사용을 켜고 Mode를 `require`로 설정한다. 버전에 따라 Driver properties의 `sslmode`에서 설정할 수 있다.
4. **Test Connection(연결 테스트)**을 누른다. PostgreSQL 드라이버 다운로드 창이 나오면 다운로드한다.
5. 연결 성공을 확인한 뒤 **Finish(완료)**를 누른다.

공식 참고: [연결 생성 안내](https://dbeaver.com/docs/dbeaver/Create-Connection/).

### 3. 첫 SQL 실행

만든 연결을 우클릭 → **SQL Editor → New SQL Script**를 연다. 아래 쿼리를 붙여 넣고 선택한 뒤 도구 모음의 SQL 실행 버튼을 누른다.

```sql
SELECT * FROM bdai13.orders LIMIT 5;
```

**주문 5행이 보이면 준비 완료.** 왼쪽 탐색기에서는 연결 → Schemas → `bdai13` → Tables를 펼친다. 다른 스키마 이름이 보이더라도 수업에서는 `bdai13`만 사용한다.

## 방법 B — 설치 없이 Google Colab

### 1. 실습 노트북 열기

[5주차 Colab 노트북 바로 열기](https://colab.research.google.com/github/team-datapopcorn/bdai13-data-handling-weekly/blob/master/week05_sql_aggregation/05_sql_aggregation_colab.ipynb) → 구글 계정 로그인 → **파일 → Drive에 사본 저장**으로 자신의 실습본을 만든다. 위에서 아래로 셀의 ▶ 버튼을 눌러 실행한다.

### 2. 라이브러리 설치

```python
!pip install psycopg2-binary -q
```

### 3. 접속하고 주문 5행 확인

```python
from getpass import getpass
import psycopg2
import pandas as pd

conn = psycopg2.connect(
    host="aws-1-us-east-1.pooler.supabase.com",
    port=6543,
    dbname="postgres",
    user="bdai13_student.ihenzvyxmlqmfrwjeknd",
    password=getpass("수업에서 안내한 비밀번호: "),
    sslmode="require",
    connect_timeout=15,
)
conn.autocommit = True

def query(sql):
    with conn.cursor() as cur:
        cur.execute(sql)
        return pd.DataFrame(cur.fetchall(), columns=[col[0] for col in cur.description])

query("SELECT * FROM bdai13.orders LIMIT 5")
```

비밀번호 입력창에 수업에서 안내한 값을 입력한다. 코드나 출력에 비밀번호를 적지 않는다. 주문 5행이 보이면 준비 완료다.

### 4. SQL 실행과 pandas 검증

```python
# AI가 만든 SELECT 쿼리를 따옴표 안에 넣는다.
sql = """
SELECT COUNT(*) AS order_count
FROM bdai13.orders
"""
query(sql)

# 같은 서버에서 읽은 원본을 pandas로 검증한다.
orders = query("SELECT * FROM bdai13.orders")
print("pandas 주문 건수:", len(orders))
```

노트북에 테이블 구조 확인, 집계 쿼리 3개를 넣을 자리, pandas 검증 예시와 제출 체크리스트가 들어 있다. 런타임이 초기화되면 설치·접속 셀부터 다시 실행한다. 수업을 마치면 `conn.close()`로 연결을 닫는다.

## 오늘 사용할 테이블

테이블 이름 앞에 항상 **`bdai13.`**을 붙인다.

| 테이블 | 내용 |
|---|---|
| `bdai13.customers` | 고객·지역 |
| `bdai13.products` | 상품·카테고리 |
| `bdai13.orders` | 주문·주문일·주문 금액 |
| `bdai13.order_items` | 주문별 상품·수량·단가 |
| `bdai13.logins` | 고객 로그인 이력 |

고객 1명 → 주문 여러 건, 주문 1건 → 주문항목 여러 행이다. 주문항목을 붙인 뒤 주문 금액을 단순 합산하면 같은 주문 금액이 반복되어 매출이 부풀려질 수 있다. 실제 컬럼은 접속 후 확인한다.

## 접속이 안 될 때

| 증상 | 먼저 확인 |
|---|---|
| 비밀번호 인증 실패 | 수업 비밀번호·Username을 다시 확인하고 앞뒤 공백 제거 |
| 연결 시간 초과 | Host·Port·인터넷 연결 확인. 학교·회사망이면 다른 네트워크에서 재시도 |
| SSL 관련 오류 | SSL 사용 및 `sslmode=require` 확인 |
| 테이블을 찾을 수 없음 | `orders` 대신 `bdai13.orders` 사용 |
| SQL 오류 후 Colab 실행 실패 | 접속 셀 재실행 후 수정한 SELECT 실행 |

## 보조용 SQLite

서버 접속이 어려울 때는 [카라멜팝콘 SQLite 다운로드](../_shared/caramelpopcorn.db)를 사용할 수 있다. DBeaver에서 SQLite 연결을 만들고 다운받은 파일을 선택하거나, Colab 왼쪽 파일 탭에 업로드한 뒤 아래 코드를 실행한다.

```python
import sqlite3
import pandas as pd
con = sqlite3.connect("/content/caramelpopcorn.db")  # Colab 업로드 파일
pd.read_sql_query("SELECT * FROM orders LIMIT 5", con)
```

로컬에서 주차 폴더를 기준으로 실행할 때 경로는 `../_shared/caramelpopcorn.db`다. SQLite에는 `bdai13.`을 붙이지 않는다. Postgres와 스키마는 같지만 **별도 생성한 데이터**이므로 두 환경의 합계를 서로 대조하지 않는다. SQL과 pandas는 반드시 같은 원본으로 검증한다. 날짜 함수 등 SQL 문법도 DB에 따라 다를 수 있다.

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

## 선택 실습 — 준비된 5개 테이블 직접 적재

공용 계정은 읽기 전용입니다. 개인 SQLite에 고객·상품·주문·주문항목·로그인을 모두 적재해 보세요.

[전체 테이블 적재 Colab 바로 열기](https://colab.research.google.com/github/team-datapopcorn/bdai13-data-handling-weekly/blob/master/week05_sql_aggregation/05_load_all_tables_colab.ipynb) · [DBeaver 단계별 안내 및 통합 SQL 다운로드](https://bdai13-data-handling.vercel.app/ch05#load-all-tables)

| 순서 | 파일 | 원본 행 수 |
|---|---|---|
| 1 | `insert_customers.sql` | 400 |
| 2 | `insert_products.sql` | 10 |
| 3 | `insert_orders.sql` | 713 |
| 4 | `insert_order_items.sql` | 1782 |
| 5 | `insert_logins.sql` | 1953 |
