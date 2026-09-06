"""
PokeAPI Data Pipeline & Extraction Script
BDAI 13th Data Handling and Automation Lecture Series
Extracts Pokemon data from https://pokeapi.co/ (Gen 1 to 9, IDs 1 to 1025)
Outputs:
- pokemon_all.csv & pokemon_all.parquet
- pokemon_gen1.csv & pokemon_gen1.parquet
- pokemon.db (SQLite relational DB with normalized tables)
- pokemon.duckdb (DuckDB database for high-performance SQL analytics)
"""

import time
import os
import sqlite3
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import pandas as pd
import duckdb

BASE_URL = "https://pokeapi.co/api/v2"
HEADERS = {"User-Agent": "bdai13-lecture-datapopcorn/1.0"}

GEN_MAP = {
    "generation-i": 1,
    "generation-ii": 2,
    "generation-iii": 3,
    "generation-iv": 4,
    "generation-v": 5,
    "generation-vi": 6,
    "generation-vii": 7,
    "generation-viii": 8,
    "generation-ix": 9,
}

def fetch_single_pokemon(pid, max_retries=3):
    """Fetch and parse a single pokemon and its species metadata with retries."""
    for attempt in range(max_retries):
        try:
            # 1. Main Pokemon endpoint
            p_res = requests.get(f"{BASE_URL}/pokemon/{pid}", headers=HEADERS, timeout=12)
            if p_res.status_code != 200:
                time.sleep(0.5)
                continue
            p_data = p_res.json()

            # 2. Species endpoint (for Korean name, generation, capture rate, etc.)
            s_res = requests.get(f"{BASE_URL}/pokemon-species/{pid}", headers=HEADERS, timeout=12)
            s_data = s_res.json() if s_res.status_code == 200 else {}

            # Korean Name extraction
            ko_name = p_data["name"]
            for name_entry in s_data.get("names", []):
                if name_entry.get("language", {}).get("name") == "ko":
                    ko_name = name_entry["name"]
                    break

            # Generation mapping
            gen_str = s_data.get("generation", {}).get("name", "generation-i")
            gen_num = GEN_MAP.get(gen_str, 1)

            # 6 Base Stats
            stat_map = {item["stat"]["name"]: item["base_stat"] for item in p_data["stats"]}

            # Primary and Secondary Types
            sorted_types = sorted(p_data["types"], key=lambda x: x["slot"])
            type_names = [t["type"]["name"] for t in sorted_types]
            type1 = type_names[0] if len(type_names) > 0 else None
            type2 = type_names[1] if len(type_names) > 1 else None

            # Abilities
            sorted_abilities = sorted(p_data["abilities"], key=lambda x: x["slot"])
            ability_names = [a["ability"]["name"] for a in sorted_abilities]

            # Official Artwork Sprite
            sprite_url = (
                p_data.get("sprites", {})
                .get("other", {})
                .get("official-artwork", {})
                .get("front_default")
            )
            if not sprite_url:
                sprite_url = p_data.get("sprites", {}).get("front_default")

            # Main Record
            record = {
                "id": p_data["id"],
                "name_ko": ko_name,
                "name_en": p_data["name"],
                "generation": gen_num,
                "height_m": round(p_data["height"] / 10.0, 2),
                "weight_kg": round(p_data["weight"] / 10.0, 2),
                "type_primary": type1,
                "type_secondary": type2,
                "hp": stat_map.get("hp", 0),
                "attack": stat_map.get("attack", 0),
                "defense": stat_map.get("defense", 0),
                "special_attack": stat_map.get("special-attack", 0),
                "special_defense": stat_map.get("special-defense", 0),
                "speed": stat_map.get("speed", 0),
                "total_stats": sum(stat_map.values()),
                "capture_rate": s_data.get("capture_rate"),
                "base_happiness": s_data.get("base_happiness"),
                "is_legendary": bool(s_data.get("is_legendary", False)),
                "is_mythical": bool(s_data.get("is_mythical", False)),
                "growth_rate": s_data.get("growth_rate", {}).get("name"),
                "abilities": ", ".join(ability_names),
                "sprite_url": sprite_url,
            }

            # Relational child rows
            types_rel = [
                {"pokemon_id": p_data["id"], "slot": t["slot"], "type_name": t["type"]["name"]}
                for t in sorted_types
            ]
            stats_rel = [
                {"pokemon_id": p_data["id"], "stat_name": s["stat"]["name"], "base_stat": s["base_stat"]}
                for s in p_data["stats"]
            ]
            abilities_rel = [
                {"pokemon_id": p_data["id"], "slot": a["slot"], "ability_name": a["ability"]["name"], "is_hidden": a["is_hidden"]}
                for a in sorted_abilities
            ]

            return record, types_rel, stats_rel, abilities_rel

        except Exception as e:
            if attempt == max_retries - 1:
                print(f"❌ Error fetching Pokemon #{pid}: {e}")
                return None
            time.sleep(1.0)
    return None

def run_pipeline(total_count=1025, max_workers=14):
    print(f"🚀 Starting PokeAPI Extraction Pipeline (Total {total_count} Pokemon)...")
    t0 = time.time()

    all_records = []
    all_types_rel = []
    all_stats_rel = []
    all_abilities_rel = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(fetch_single_pokemon, pid): pid for pid in range(1, total_count + 1)}
        done_count = 0
        for future in as_completed(futures):
            res = future.result()
            if res:
                rec, t_rel, s_rel, a_rel = res
                all_records.append(rec)
                all_types_rel.extend(t_rel)
                all_stats_rel.extend(s_rel)
                all_abilities_rel.extend(a_rel)
            done_count += 1
            if done_count % 100 == 0 or done_count == total_count:
                print(f"  [{done_count}/{total_count}] Fetched (elapsed {round(time.time() - t0, 1)}s)...")

    # Sort records by ID
    all_records.sort(key=lambda x: x["id"])
    all_types_rel.sort(key=lambda x: (x["pokemon_id"], x["slot"]))
    all_stats_rel.sort(key=lambda x: (x["pokemon_id"], x["stat_name"]))
    all_abilities_rel.sort(key=lambda x: (x["pokemon_id"], x["slot"]))

    df_all = pd.DataFrame(all_records)
    df_gen1 = df_all[df_all["generation"] == 1].copy()

    df_types = pd.DataFrame(all_types_rel)
    df_stats = pd.DataFrame(all_stats_rel)
    df_abilities = pd.DataFrame(all_abilities_rel)

    out_dir = os.path.dirname(os.path.abspath(__file__))

    # 1. Export CSV
    csv_all = os.path.join(out_dir, "pokemon_all.csv")
    csv_gen1 = os.path.join(out_dir, "pokemon_gen1.csv")
    df_all.to_csv(csv_all, index=False, encoding="utf-8-sig")
    df_gen1.to_csv(csv_gen1, index=False, encoding="utf-8-sig")
    print(f"💾 Saved: {csv_all} ({len(df_all)} rows)")
    print(f"💾 Saved: {csv_gen1} ({len(df_gen1)} rows)")

    # 2. Export Parquet
    pq_all = os.path.join(out_dir, "pokemon_all.parquet")
    pq_gen1 = os.path.join(out_dir, "pokemon_gen1.parquet")
    df_all.to_parquet(pq_all, index=False)
    df_gen1.to_parquet(pq_gen1, index=False)
    print(f"💾 Saved: {pq_all}")
    print(f"💾 Saved: {pq_gen1}")

    # 3. Export SQLite Relational DB
    db_path = os.path.join(out_dir, "pokemon.db")
    if os.path.exists(db_path):
        os.remove(db_path)
    conn = sqlite3.connect(db_path)
    df_all.to_sql("pokemon", conn, if_exists="replace", index=False)
    df_types.to_sql("pokemon_types", conn, if_exists="replace", index=False)
    df_stats.to_sql("pokemon_stats", conn, if_exists="replace", index=False)
    df_abilities.to_sql("pokemon_abilities", conn, if_exists="replace", index=False)
    
    # Create indexes for SQL performance
    with conn:
        conn.execute("CREATE INDEX idx_pokemon_id ON pokemon(id);")
        conn.execute("CREATE INDEX idx_pokemon_gen ON pokemon(generation);")
        conn.execute("CREATE INDEX idx_pokemon_type1 ON pokemon(type_primary);")
        conn.execute("CREATE INDEX idx_types_pid ON pokemon_types(pokemon_id);")
        conn.execute("CREATE INDEX idx_stats_pid ON pokemon_stats(pokemon_id);")
    conn.close()
    print(f"💾 Saved SQLite DB: {db_path} (tables: pokemon, pokemon_types, pokemon_stats, pokemon_abilities)")

    # 4. Export DuckDB
    duck_path = os.path.join(out_dir, "pokemon.duckdb")
    if os.path.exists(duck_path):
        os.remove(duck_path)
    dconn = duckdb.connect(duck_path)
    dconn.register("df_all_view", df_all)
    dconn.execute("CREATE TABLE pokemon AS SELECT * FROM df_all_view")
    dconn.close()
    print(f"💾 Saved DuckDB: {duck_path}")

    print(f"🎉 All completed successfully in {round(time.time() - t0, 1)} seconds!")

if __name__ == "__main__":
    run_pipeline(total_count=1025, max_workers=14)
