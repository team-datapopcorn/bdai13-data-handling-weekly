# 5주차 · 본인 Supabase Postgres에서 SQL 집계와 검증

오늘부터 가상 온라인 스토어 카라멜팝콘 데이터를 사용합니다. 각자 자신의 Supabase 프로젝트에 원본 SQL 5개를 입력하고, 같은 DB에서 SQL과 pandas 결과를 대조합니다.

## 1. 프로젝트 생성과 데이터 적재

[교안의 단계별 안내](https://bdai13-data-handling.vercel.app/ch05#load-all-tables)를 따라 본인 Supabase 프로젝트를 생성합니다. SQL Editor에서 [전체 테이블 생성·적재 SQL](caramelpopcorn_postgres_setup.sql)의 내용을 한 번 실행합니다.

개별 실행을 원하면 [테이블 생성 SQL](00_create_tables_postgres.sql)을 먼저 실행한 뒤 아래 순서를 따릅니다. 원본의 `bdai13.`을 제거하지 않습니다.

| 순서 | 원본 SQL | 예상 행 수 |
|---|---|---|
| 1 | [insert_customers.sql](../insert_customers.sql) | 400 |
| 2 | [insert_products.sql](../insert_products.sql) | 10 |
| 3 | [insert_orders.sql](../insert_orders.sql) | 713 |
| 4 | [insert_order_items.sql](../insert_order_items.sql) | 1782 |
| 5 | [insert_logins.sql](../insert_logins.sql) | 1953 |

빈 연습 스키마에서 한 번 실행합니다. 기존 테이블이나 고객 ID가 있으면 먼저 COUNT로 상태를 확인하고 INSERT를 반복하지 않습니다. 외래 키가 고객·주문·상품 연결을 검증합니다. 통합 SQL은 오류 시 전체 rollback됩니다.

## 2. DBeaver 설치·접속

[무료 DBeaver Community](https://dbeaver.io/download/)를 설치합니다. Windows는 CPU에 맞는 EXE, Mac은 Apple Silicon·Intel에 맞는 DMG를 선택하고 Applications로 옮깁니다.

1. 본인 Supabase 프로젝트의 **Connect → Session pooler**를 엽니다.
2. DBeaver → New Database Connection → PostgreSQL. Connect 창의 Host·Port·Database·User를 그대로 입력합니다. Host는 프로젝트마다 다릅니다.
3. Password는 본인 Database password, SSL mode는 `require`입니다. Session pooler의 포트는 일반적으로 5432이며 Connect 창의 값을 사용합니다.
4. Test Connection → 드라이버 다운로드 → Finish.
5. SQL Editor에서 `SELECT current_database(), current_user;`로 접속 확인.
6. 아직 적재하지 않았다면 통합 SQL 파일을 열어 본인 연결에서 **Execute SQL Script**로 전체 실행합니다. 이미 적재했다면 SELECT부터 시작합니다.

공식 참고: [Supabase DB 연결](https://supabase.com/docs/guides/database/connecting-to-postgres), [DBeaver SQL 실행](https://dbeaver.com/docs/dbeaver/SQL-Execution/).

## 3. Colab에서 본인 DB에 적재·분석

- [전체 적재 Colab](https://colab.research.google.com/github/team-datapopcorn/bdai13-data-handling-weekly/blob/master/week05_sql_aggregation/05_load_all_tables_colab.ipynb): 프로젝트 접속 → 테이블 생성 → 원본 INSERT 5개 → 건수 검증.
- [SQL 집계·pandas 검증 Colab](https://colab.research.google.com/github/team-datapopcorn/bdai13-data-handling-weekly/blob/master/week05_sql_aggregation/05_sql_aggregation_colab.ipynb): 적재가 끝난 같은 본인 DB로 분석.

파일 → Drive에 사본 저장 후 실행합니다. Connect → Session pooler의 Host·Port·User를 입력하고 본인 DB 비밀번호는 getpass 입력창으로 받습니다. API key와 DB 비밀번호는 다릅니다. 생성·INSERT 셀은 한 번만 실행하며 이미 적재했다면 건너뜁니다.

```sql
SELECT 'customers' AS table_name, COUNT(*) AS row_count FROM bdai13.customers
UNION ALL
SELECT 'products' AS table_name, COUNT(*) AS row_count FROM bdai13.products
UNION ALL
SELECT 'orders' AS table_name, COUNT(*) AS row_count FROM bdai13.orders
UNION ALL
SELECT 'order_items' AS table_name, COUNT(*) AS row_count FROM bdai13.order_items
UNION ALL
SELECT 'logins' AS table_name, COUNT(*) AS row_count FROM bdai13.logins;
```

SQL에서는 `bdai13.customers`, `bdai13.products`, `bdai13.orders`, `bdai13.order_items`, `bdai13.logins`를 사용합니다. 생성문은 RLS를 활성화하며, 적재는 본인 프로젝트의 postgres 계정으로 실행합니다. 수업은 직접 DB 연결이므로 bdai13을 Data API 노출 스키마에 추가할 필요가 없습니다.

## 접속·적재 오류

- 인증 실패: 본인 DB 비밀번호와 Session pooler User 확인. 공용 수업 비밀번호·API key가 아닙니다.
- timeout: 프로젝트 실행 상태, Host·Port·SSL 확인. IPv4 환경은 Session pooler를 사용합니다.
- relation does not exist: 테이블 생성 후 `bdai13.` 접두어 사용.
- duplicate key / already exists: 기존 건수 확인. INSERT 반복 실행 금지.
- foreign key violation: 고객·상품 → 주문 → 주문항목·로그인 순서 확인.
- transaction is aborted: Rollback 후 상태 확인. Colab 적재 셀은 자동 rollback합니다.

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

