import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json

IN_PATH = "data/processed/clean.csv"
FIG_DIR = "results/figures"
SUMMARY_PATH = "results/eda_summary.json"
STATE = 42


def main():
    os.makedirs(FIG_DIR, exist_ok=True)
    dfMain = pd.read_csv(IN_PATH, low_memory=False)

    sample = dfMain.sample(frac=0.1, random_state=STATE)
    summary = {}

    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    sample['injuries_total'].value_counts().sort_index().head(15).plot(kind='bar', ax=axes[0])
    axes[0].set_title('injuries_total distribution')
    axes[0].set_xlabel('injury count')
    sample['injuries_fatal'].value_counts().sort_index().head(10).plot(kind='bar', ax=axes[1], color='salmon')
    axes[1].set_title('injuries_fatal distribution')
    plt.tight_layout()
    plt.savefig(f"{FIG_DIR}/injury_distributions.png", dpi=120)
    plt.close()

    summary['zero_injury_rate'] = float((sample['injuries_total'] == 0).mean())
    summary['fatal_crash_rate'] = float((sample['injuries_fatal'] > 0).mean())
    summary['injuries_total_describe'] = sample['injuries_total'].describe().to_dict()

    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    sample['posted_speed_limit'].plot(kind='hist', bins=30, ax=axes[0])
    axes[0].set_title('posted_speed_limit')
    sample['crash_hour'].value_counts().sort_index().plot(kind='bar', ax=axes[1])
    axes[1].set_title('crash hour')
    sample['crash_month'].value_counts().sort_index().plot(kind='bar', ax=axes[2])
    axes[2].set_title('crash month')
    plt.tight_layout()
    plt.savefig(f"{FIG_DIR}/temporal_distributions.png", dpi=120)
    plt.close()

    means_by_cat = {}
    for col in ['weather_condition', 'lighting_condition', 'road_defect', 'roadway_surface_cond']:
        means = sample.groupby(col, observed=True)['injuries_total'].mean().sort_values(ascending=False)
        means_by_cat[col] = means.to_dict()
    summary['mean_injuries_by_category'] = means_by_cat

    top_causes = sample['prim_contributory_cause'].value_counts().head(15).index
    cause_means = (
        sample[sample['prim_contributory_cause'].isin(top_causes)]
        .groupby('prim_contributory_cause', observed=True)['injuries_total']
        .mean()
        .sort_values(ascending=False)
    )
    cause_means.plot(kind='barh', figsize=(10, 6))
    plt.title('mean injuries_total by top contributory causes')
    plt.tight_layout()
    plt.savefig(f"{FIG_DIR}/contributory_causes.png", dpi=120)
    plt.close()
    summary['mean_injuries_by_cause'] = cause_means.to_dict()

    pivot = sample.pivot_table(
        values='injuries_total',
        index='crash_day_of_week',
        columns='crash_hour',
        aggfunc='mean'
    )
    plt.figure(figsize=(16, 4))
    sns.heatmap(pivot, cmap='YlOrRd', linewidths=0.3)
    plt.title('mean injuries by hour vs day of week')
    plt.tight_layout()
    plt.savefig(f"{FIG_DIR}/hour_dayofweek_heatmap.png", dpi=120)
    plt.close()

    mini = sample.sample(5000, random_state=STATE)
    plt.figure(figsize=(8, 4))
    plt.scatter(mini['posted_speed_limit'], mini['injuries_total'], alpha=0.2, s=10)
    plt.xlabel('posted_speed_limit')
    plt.ylabel('injuries_total')
    plt.title('speed limit vs injuries')
    plt.tight_layout()
    plt.savefig(f"{FIG_DIR}/speed_vs_injuries.png", dpi=120)
    plt.close()

    with open(SUMMARY_PATH, "w") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"EDA summary saved to {SUMMARY_PATH}")
    print(f"Figures saved to {FIG_DIR}")


if __name__ == "__main__":
    main()
