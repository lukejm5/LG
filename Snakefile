rule all:
    input:
        "results/metrics.json",
        "results/coefficients.csv",
        "results/eda_summary.json",
        "results/figures/roc_curve.png",
        "results/figures/confusion_matrix.png",
        "results/figures/top_coefficients.png",
        "results/figures/injury_distributions.png",
        "results/figures/temporal_distributions.png",
        "results/figures/contributory_causes.png",
        "results/figures/hour_dayofweek_heatmap.png",
        "results/figures/speed_vs_injuries.png"

rule fetch_crashes:
    output:
        "data/raw/crashes.csv"
    shell:
        "python scripts/fetch_crashes.py"

rule fetch_people:
    output:
        "data/raw/people.csv"
    shell:
        "python scripts/fetch_people.py"

rule merge:
    input:
        crashes = "data/raw/crashes.csv",
        people = "data/raw/people.csv"
    output:
        "data/interim/merged.csv"
    shell:
        "python scripts/merge.py"

rule clean:
    input:
        "data/interim/merged.csv"
    output:
        "data/processed/clean.csv"
    shell:
        "python scripts/clean.py"

rule eda:
    input:
        "data/processed/clean.csv"
    output:
        "results/eda_summary.json",
        "results/figures/injury_distributions.png",
        "results/figures/temporal_distributions.png",
        "results/figures/contributory_causes.png",
        "results/figures/hour_dayofweek_heatmap.png",
        "results/figures/speed_vs_injuries.png"
    shell:
        "python scripts/eda.py"

rule model:
    input:
        "data/processed/clean.csv"
    output:
        "results/metrics.json",
        "results/coefficients.csv",
        "results/figures/roc_curve.png",
        "results/figures/confusion_matrix.png",
        "results/figures/top_coefficients.png"
    shell:
        "python scripts/model.py"
