
#samler klienternes individuelle CSV-filer til én samlet fil
#gør det nemmere at analysere resultaterne

import csv
from pathlib import Path

LOG_DIR = Path("logs")
OUTPUT_FILE = Path("baseline_results.csv")

def merge_csv():
    rows = []

    fieldnames = [
        "timestamp",
        "client_id",
        "request_id",
        "latency_ms",
        "status"
    ]

    # Find alle klienternes CSV-filer
    files = sorted(LOG_DIR.glob("client_*_log.csv"))

    if not files:
        print("Ingen klientlogfiler fundet.")
        return

    # Gennemgå alle CSV-filer
    for file in files:

        # Find klientens ID ud fra filnavnet
        client_id = file.name.removeprefix("client_").removesuffix("_log.csv")

        with open(file, "r", newline="") as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                rows.append({
                    "timestamp": row["timestamp"],
                    "client_id": client_id,
                    "request_id": row["request_id"],
                    "latency_ms": row["latency_ms"],
                    "status": row["status"]
                })

    # Sortér alle målinger efter tidspunkt
    rows.sort(key=lambda row: row["timestamp"])

    # Gem den samlede CSV-fil
    with open(OUTPUT_FILE, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Samlet {len(files)} klientfiler.")
    print(f"Samlet {len(rows)} requests.")
    print(f"Resultater gemt i {OUTPUT_FILE}")


if __name__ == "__main__":
    merge_csv()
