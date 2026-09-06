# ⚡ 종합 실습 프로젝트: PokeAPI 데이터 파이프라인 & 도감 분석 대시보드

[PokeAPI](https://pokeapi.co/)에서 추출한 1~9세대 포켓몬(총 1,025마리)의 원천 데이터와 정제 데이터셋입니다.  
데이터 엔지니어링의 기본 뼈대인 **수집(Extract) → 전처리·핸들링(Transform) → 저장(Load)** 과정을 실습하고, 최종적으로 **포켓몬 도감 인터랙티브 분석 대시보드**를 구축하는 종합 프로젝트용 데이터입니다.

---

## 📌 초반에 왜 PokeAPI를 다루는가?

1. **실무 REST API의 축소판 (중첩 JSON 구조)**:
   - 캐글(Kaggle)의 단정한 2차원 CSV와 달리, 현업 API는 딕셔너리와 리스트가 3~4겹 중첩된 비정형/반정형 구조입니다.
   - `json_normalize`, 딕셔너리 언팩, 리스트 컴프리헨션 등 **실무 데이터 평탄화(Flattening) 역량**을 제대로 훈련할 수 있습니다.
2. **인증 키·비용 없는 무제한 무료 (No-Auth, Zero-Setup)**:
   - 가입, 신용카드 등록, 토큰 만료 걱정 없이 `requests.get()` 한 줄로 누구나 즉시 호출 가능합니다.
3. **관계형 DB(RDB) 모델링 & 정규화 훈련**:
   - 포켓몬 기본 정보(1) - 6대 스탯(1:N) - 속성 타입(N:M) - 특성(N:M) - 종족/진화(1:1) 등 테이블 간의 엔터티 관계가 명확하여 **테이블 정규화와 SQL JOIN 실습**에 최적입니다.
4. **직관적이고 풍부한 분석 도메인**:
   - 1,000종 이상의 개체, 1~9세대, 18개 속성, 체력·공격·방어·특공·특방·스피드 6대 전투 지표, 신장/체중 등 친숙한 데이터로 EDA부터 가설 검증, 머신러닝 군집화까지 단번에 확장할 수 있습니다.

---

## 📁 제공 파일 목록

| 파일명 | 포맷 | 행 수 | 설명 |
| :--- | :--- | :--- | :--- |
| [`pokemon_all.parquet`](pokemon_all.parquet) | Parquet | 1,025 | 1~9세대 전체 포켓몬 (컬럼형 압축 포맷, 권장) |
| [`pokemon_all.csv`](pokemon_all.csv) | CSV (UTF-8-sig) | 1,025 | 1~9세대 전체 포켓몬 텍스트 데이터 |
| [`pokemon_gen1.parquet`](pokemon_gen1.parquet) | Parquet | 151 | 1세대(1~151번) 입문 실습용 압축 포맷 |
| [`pokemon_gen1.csv`](pokemon_gen1.csv) | CSV (UTF-8-sig) | 151 | 1세대 입문 실습용 CSV |
| [`pokemon.db`](pokemon.db) | SQLite DB | 4개 테이블 | 관계형 정규화 DB (`pokemon`, `pokemon_types`, `pokemon_stats`, `pokemon_abilities`) |
| [`pokemon.duckdb`](pokemon.duckdb) | DuckDB | 1,025 | 고속 분석용 OLAP 임베디드 데이터베이스 |
| [`extract_pokeapi.py`](extract_pokeapi.py) | Python 스크립트 | - | PokeAPI에서 실시간 병렬 추출 및 정제/적재를 수행하는 재현 코드 |

---

## 📊 데이터 명세 (Data Dictionary)

### 1. `pokemon` 메인 테이블 (1,025행 × 22열)

| 컬럼명 | 데이터 타입 | 설명 | 예시 |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | 전국도감 번호 (기본키) | `1`, `25` |
| `name_ko` | TEXT | 포켓몬 한국어 공식 명칭 | `이상해씨`, `피카츄` |
| `name_en` | TEXT | 포켓몬 영문 명칭 | `bulbasaur`, `pikachu` |
| `generation` | INTEGER | 세대 (1~9) | `1` |
| `height_m` | REAL | 키 (미터 단위) | `0.7` |
| `weight_kg` | REAL | 몸무게 (kg 단위) | `6.9` |
| `type_primary` | TEXT | 주 속성 (18개 타입 중 하나) | `grass`, `electric` |
| `type_secondary` | TEXT | 부 속성 (단일 속성은 NULL) | `poison`, `NULL` |
| `hp` | INTEGER | 기초 체력 (HP) | `45` |
| `attack` | INTEGER | 기초 물리 공격력 | `49` |
| `defense` | INTEGER | 기초 물리 방어력 | `49` |
| `special_attack` | INTEGER | 기초 특수 공격력 | `65` |
| `special_defense` | INTEGER | 기초 특수 방어력 | `65` |
| `speed` | INTEGER | 기초 스피드 | `45` |
| `total_stats` | INTEGER | 6대 스탯 총합 (종족값 Total) | `318` |
| `capture_rate` | INTEGER | 포획률 (0~255, 높을수록 잡기 쉬움) | `45` |
| `base_happiness` | INTEGER | 기본 친밀도 (0~255) | `70` |
| `is_legendary` | BOOLEAN | 전설의 포켓몬 여부 (0 또는 1) | `0` |
| `is_mythical` | BOOLEAN | 환상의 포켓몬 여부 (0 또는 1) | `0` |
| `growth_rate` | TEXT | 경험치 성장 곡선 유형 | `medium-slow` |
| `abilities` | TEXT | 보유 특성 목록 (콤마 구분) | `overgrow, chlorophyll` |
| `sprite_url` | TEXT | 공식 일러스트 (Official Artwork) 이미지 URL | `https://...` |

### 2. 관계형 정규화 테이블 (`pokemon.db` 내 포함)
- **`pokemon_types`**: `(pokemon_id, slot, type_name)` — 포켓몬과 18개 속성 간의 N:M 매핑 테이블
- **`pokemon_stats`**: `(pokemon_id, stat_name, base_stat)` — 6대 스탯의 세로형 정규화 테이블
- **`pokemon_abilities`**: `(pokemon_id, slot, ability_name, is_hidden)` — 일반 특성 및 숨겨진 특성 매핑

---

## 🎯 발굴해볼 수 있는 5대 분석 & EDA 주제

### 1. 세대별 파워 인플레이션(Power Creep) 검증 (통계 가설 검증)
- **가설**: "새로운 세대가 출시될수록(Gen 1 → Gen 9) 신규 포켓몬들의 평균 종족값(Total Stats)이 지속적으로 상승하는가?"
- **분석 기법**: 세대별 Boxplot, 평균/중앙값 추이 선그래프, **일원분산분석(One-way ANOVA)** 및 Tukey HSD 사후검정.

### 2. 18개 속성(Type) 조합의 시너지와 밸런스 분석 (EDA)
- **가설**: "단일 속성 포켓몬보다 듀얼 속성 포켓몬이 통계적으로 유의미하게 종족값이 높은가? 가장 강력한 공방 밸런스를 가진 속성 조합은?"
- **분석 기법**: 단일 vs 듀얼 독립표본 **t-test**, 18×18 속성 조합별 평균 스탯 **히트맵(Heatmap)**, 공격력 vs 방어력 사분면 산점도.

### 3. 체격(신장·체중)과 전투 스탯의 상관관계 및 반전 이상치(Outlier) 발굴
- **가설**: "무겁고 큰 포켓몬일수록 방어력과 체력이 높고 스피드가 느릴까? 겉보기와 완전히 다른 '반전 스피더' 이상치 포켓몬은 누구인가?"
- **분석 기법**: **Spearman 순위 상관분석**, Log 체중 vs 스피드 산점도 + 회귀 추세선, 회귀 잔차(Residual) 기반 이상치 발굴.

### 4. 포획 난이도(Capture Rate) 결정 요인 분석 (회귀 & 머신러닝)
- **가설**: "포획 난이도는 단순히 종족값 때문인가, 아니면 기본 친밀도·전설 여부·성장 곡선과 어떤 상관이 있는가?"
- **분석 기법**: 다중 선형 회귀분석, 결정 트리(Decision Tree) 기반 **Feature Importance(특성 중요도)** 산출.

### 5. 머신러닝(PCA & K-Means) 배틀 역할군(Role) 클러스터링
- **목표**: 공식 속성이 아닌 순수 6대 전투 수치 데이터만으로 4대 배틀 포지션('초고속 스위퍼', '물리 탱커', '특수 딜탱', '균형형 올라운더')을 비지도학습으로 자동 분류.
- **분석 기법**: StandardScaler 정규화 → **PCA(주성분 분석) 2차원 축소** → **K-Means 군집화** 및 레이더 차트 매핑.

---

## 💻 빠른 실습 쿼리 예시

### Python (Pandas & Parquet)
```python
import pandas as pd

# Parquet 로드
df = pd.read_parquet("pokemon_all.parquet")

# 1. 종족값 Top 5 포켓몬
print(df.sort_values(by="total_stats", ascending=False)[["name_ko", "type_primary", "total_stats"]].head(5))

# 2. 세대별 평균 종족값 비교
print(df.groupby("generation")["total_stats"].agg(["count", "mean", "median"]).round(1))
```

### SQL (SQLite / DuckDB)
```sql
-- 속성별 평균 공격력과 스피드 상위 5개 속성 조회
SELECT 
    type_primary,
    COUNT(*) as count,
    ROUND(AVG(attack), 1) as avg_attack,
    ROUND(AVG(speed), 1) as avg_speed,
    ROUND(AVG(total_stats), 1) as avg_total
FROM pokemon
GROUP BY type_primary
ORDER BY avg_attack DESC
LIMIT 5;
```

---

## 🔄 데이터 재생성 방법

데이터를 다시 추출하거나 확장하고 싶다면 아래 명령어로 파이프라인을 재실행합니다:

```bash
pip install requests pandas pyarrow duckdb
python extract_pokeapi.py
```
