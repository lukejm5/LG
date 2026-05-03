import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import os
import json

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_auc_score, RocCurveDisplay
)

IN_PATH = "data/processed/clean.csv"
FIG_DIR = "results/figures"
METRICS_PATH = "results/metrics.json"
COEF_PATH = "results/coefficients.csv"
STATE = 42


def main():
    os.makedirs(FIG_DIR, exist_ok=True)
    dfMain = pd.read_csv(IN_PATH, low_memory=False)

    cat_cols_to_convert = [
        'traffic_control_device', 'weather_condition', 'lighting_condition',
        'roadway_surface_cond', 'road_defect', 'crash_type', 'damage',
        'prim_contributory_cause'
    ]
    for col in cat_cols_to_convert:
        dfMain[col] = dfMain[col].astype('category')

    drop_cols = [
        'crash_record_id',
        'crash_date',
        'injuries_total',
        'injuries_fatal',
        'injuries_incapacitating',
        'crash_type',
        'damage',
    ]
    dfTemp = dfMain.drop(columns=drop_cols)

    dfModel = pd.get_dummies(
        dfTemp,
        columns=dfTemp.select_dtypes('category').columns.tolist(),
        drop_first=True
    )

    X = dfModel.drop(columns=["severe"])
    y = dfModel["severe"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=STATE, stratify=y
    )

    num_cols = [
        'posted_speed_limit', 'num_units', 'crash_hour', 'crash_day_of_week',
        'crash_month', 'latitude', 'longitude', 'age_mean', 'num_people', 'any_alcohol'
    ]
    scaler = StandardScaler()
    X_train[num_cols] = scaler.fit_transform(X_train[num_cols])
    X_test[num_cols] = scaler.transform(X_test[num_cols])

    model = LogisticRegression(max_iter=1000, random_state=STATE, class_weight="balanced")
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    results = {
        "roc_auc": float(roc_auc_score(y_test, y_prob)),
        "thresholds": {}
    }

    for thresh in [0.50, 0.30, 0.25]:
        preds_t = (y_prob >= thresh).astype(int)
        report = classification_report(y_test, preds_t, output_dict=True)
        results["thresholds"][f"{thresh:.2f}"] = {
            "accuracy": report["accuracy"],
            "precision_class_1": report["1"]["precision"],
            "recall_class_1": report["1"]["recall"],
            "f1_class_1": report["1"]["f1-score"],
            "precision_class_0": report["0"]["precision"],
            "recall_class_0": report["0"]["recall"],
            "f1_class_0": report["0"]["f1-score"],
        }
        print(f"\nThreshold {thresh}")
        print(classification_report(y_test, preds_t))

    print(f"ROC-AUC: {results['roc_auc']:.4f}")

    RocCurveDisplay.from_predictions(y_test, y_prob)
    plt.title("ROC Curve")
    plt.tight_layout()
    plt.savefig(f"{FIG_DIR}/roc_curve.png", dpi=120)
    plt.close()

    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(5, 4))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.title('Confusion Matrix (threshold 0.50)')
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    plt.tight_layout()
    plt.savefig(f"{FIG_DIR}/confusion_matrix.png", dpi=120)
    plt.close()

    coef_df = pd.DataFrame({
        'feature': X_train.columns,
        'coefficient': model.coef_[0]
    }).sort_values('coefficient', key=abs, ascending=False)
    coef_df.to_csv(COEF_PATH, index=False)
    print(f"\nTop 20 features by coefficient magnitude:")
    print(coef_df.head(20).to_string(index=False))

    top_20 = coef_df.head(20).iloc[::-1]
    plt.figure(figsize=(10, 8))
    colors = ['steelblue' if c > 0 else 'salmon' for c in top_20['coefficient']]
    plt.barh(top_20['feature'], top_20['coefficient'], color=colors)
    plt.xlabel('Coefficient')
    plt.title('Top 20 features by coefficient magnitude')
    plt.tight_layout()
    plt.savefig(f"{FIG_DIR}/top_coefficients.png", dpi=120)
    plt.close()

    env_features = [
        'weather_condition', 'lighting_condition', 'roadway_surface_cond', 'road_defect'
    ]
    human_features = [
        'age_mean', 'any_alcohol', 'prim_contributory_cause'
    ]

    def category_magnitude(prefix_list):
        mask = coef_df['feature'].apply(
            lambda f: any(f == p or f.startswith(p + '_') for p in prefix_list)
        )
        return float(coef_df.loc[mask, 'coefficient'].abs().sum())

    results["coefficient_magnitude_by_group"] = {
        "environmental": category_magnitude(env_features),
        "human_factors": category_magnitude(human_features)
    }

    with open(METRICS_PATH, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nMetrics saved to {METRICS_PATH}")


if __name__ == "__main__":
    main()
