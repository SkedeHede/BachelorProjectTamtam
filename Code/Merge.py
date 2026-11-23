
# Samler klienternes individuelle CSV-filer til én samlet fil
# Gør det nemmere at analysere resultaterne fra hvert eksperiment

import csv
import argparse
from pathlib import Path


def merge_csv(experiment_dir):
    # Angiver mappen for det specifikke eksperiment
    LOG_DIR = Path(experiment_dir)

    # Den samlede CSV-fil gemmes i samme eksperimentmappe
    OUTPUT_FILE = LOG_DIR / "merged_results.csv"

    # Liste til at gemme alle klienternes målinger
    rows = []

    # Definerer kolonnerne i den samlede CSV-fil
    fieldnames = [
        "timestamp",
        "client_id",
        "request_id",
        "latency_ms",
        "status"
    ]

    # Finder alle klienternes CSV-filer i eksperimentmappen
    files = sorted(LOG_DIR.glob("client_*_log.csv"))

    # Kontrollerer om der findes klientlogfiler
    if not files:
        print(f"Ingen klientlogfiler fundet i {LOG_DIR}")
        return

    # Gennemgår alle klienternes CSV-filer
    for file in files:

        # Finder klientens ID ud fra filnavnet
        client_id = file.name.removeprefix("client_").removesuffix("_log.csv")

        # Åbner klientens CSV-fil
        with open(file, "r", newline="") as csvfile:
            reader = csv.DictReader(csvfile)

            # Gennemgår hver måling fra klienten
            for row in reader:
                rows.append({
                    "timestamp": row["timestamp"],
                    "client_id": client_id,
                    "request_id": row["request_id"],
                    "latency_ms": row["latency_ms"],
                    "status": row["status"]
                })

    # Sorterer alle målinger efter tidspunkt
    rows.sort(key=lambda row: row["timestamp"])

    # Gemmer alle målinger i én samlet CSV-fil
    with open(OUTPUT_FILE, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Skriver kolonneoverskrifter
        writer.writeheader()

        # Skriver alle klienternes målinger
        writer.writerows(rows)

    # Udskriver information om de samlede resultater
    print(f"Samlet {len(files)} klientfiler.")
    print(f"Samlet {len(rows)} requests.")
    print(f"Resultater gemt i {OUTPUT_FILE}")


# Udføres kun, når Merge.py køres direkte
if __name__ == "__main__":

    # Opretter parser til kommandolinjeargumenter
    parser = argparse.ArgumentParser(
        description="Merge client CSV files from a specific experiment"
    )

    # Angiver hvilket eksperiment der skal samles
    parser.add_argument(
        "--experiment-id",
        type=int,
        required=True,
        help="ID of the experiment to merge"
    )

    # Indlæser argumenterne
    args = parser.parse_args()

    # Kontrollerer at eksperiment-ID ikke er negativt
    if args.experiment_id < 0:
        parser.error("--experiment-id must be non-negative")

    # Finder mappen for det valgte eksperiment
    experiment_dir = Path("logs/csv") / f"experiment_{args.experiment_id:03d}"

    # Samler klienternes CSV-filer
    merge_csv(experiment_dir)
