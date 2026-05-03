import requests
import pandas as pd
import os
import time
import hashlib

BASE_URL = "https://data.cityofchicago.org/resource/85ca-t3if.json"
OUT_PATH = "data/raw/crashes.csv"
CHECKSUM_PATH = "data/raw/checksums.txt"
PAGE_SIZE = 50000
SLEEP_SEC = 1

APP_TOKEN = os.getenv("SOCRATA_APP_TOKEN", None)
HEADERS = {"X-App-Token": APP_TOKEN} if APP_TOKEN else {}

SELECT_COLS = ",".join([
    "crash_record_id",
    "crash_date",
    "posted_speed_limit",
    "traffic_control_device",
    "weather_condition",
    "lighting_condition",
    "roadway_surface_cond",
    "road_defect",
    "crash_type",
    "damage",
    "prim_contributory_cause",
    "num_units",
    "injuries_total",
    "injuries_fatal",
    "injuries_incapacitating",
    "crash_hour",
    "crash_day_of_week",
    "crash_month",
    "latitude",
    "longitude",
])


def compute_sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def write_checksum(path, checksum_path):
    digest = compute_sha256(path)
    filename = os.path.basename(path)
    lines = []
    if os.path.exists(checksum_path):
        with open(checksum_path) as f:
            lines = [ln for ln in f.read().splitlines() if not ln.endswith(filename)]
    lines.append(f"{digest}  {filename}")
    with open(checksum_path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"SHA-256: {digest}  {filename}")


def main():
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)

    if os.path.exists(OUT_PATH):
        existing = pd.read_csv(OUT_PATH)
        rows_done = len(existing)
        offset = rows_done
        print(f"Resuming from row {rows_done:,}")
    else:
        rows_done = 0
        offset = 0

    page = (offset // PAGE_SIZE) + 1

    while True:
        params = {
            "$select": SELECT_COLS,
            "$limit": PAGE_SIZE,
            "$offset": offset,
            "$order": "crash_record_id ASC",
        }

        batch = None
        for attempt in range(5):
            try:
                resp = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=120)
                resp.raise_for_status()
                batch = resp.json()
                break
            except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError):
                print(f"  Connection error on attempt {attempt + 1}, retrying in 10s...")
                time.sleep(10)

        if batch is None:
            print("Failed after 5 attempts, run the script again to resume.")
            return

        if not batch:
            break

        df_batch = pd.DataFrame(batch)
        write_header = not os.path.exists(OUT_PATH) or (offset == 0)
        df_batch.to_csv(OUT_PATH, mode="a", header=write_header, index=False)

        rows_done += len(batch)
        print(f"Page {page}: {rows_done:,} total rows saved")

        if len(batch) < PAGE_SIZE:
            break

        offset += PAGE_SIZE
        page += 1
        time.sleep(SLEEP_SEC)

    print(f"Done. File saved to {OUT_PATH}")
    write_checksum(OUT_PATH, CHECKSUM_PATH)


if __name__ == "__main__":
    main()
