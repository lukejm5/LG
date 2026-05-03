import pandas as pd
import os

IN_PATH = "data/interim/merged.csv"
OUT_PATH = "data/processed/clean.csv"


def collapse_rare(series, n_keep=10, other_label='OTHER'):
    top = series.value_counts().head(n_keep).index
    return series.where(series.isin(top), other_label)


def main():
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    dfMain = pd.read_csv(IN_PATH, low_memory=False)

    cols_to_drop = [
        'driver_action', 'driver_vision', 'physical_condition',
        'ejection', 'airbag_deployed', 'safety_equipment', 'bac_result'
    ]
    dfMain = dfMain.drop(columns=[c for c in cols_to_drop if c in dfMain.columns])

    dfMain = dfMain.dropna(subset=['injuries_total', 'injuries_fatal', 'injuries_incapacitating'])
    dfMain['severe'] = (dfMain['injuries_total'] > 0).astype(int)
    print(f"Severe crash rate: {dfMain['severe'].mean():.1%}")
    print(f"Shape after dropping nulls: {dfMain.shape}")

    invalid_speeds = list(range(0, 10)) + [99]
    dfMain['posted_speed_limit'] = dfMain['posted_speed_limit'].replace(invalid_speeds, pd.NA)
    dfMain['posted_speed_limit'] = dfMain['posted_speed_limit'].fillna(dfMain['posted_speed_limit'].median())

    dfMain['prim_contributory_cause'] = collapse_rare(dfMain['prim_contributory_cause'], n_keep=14)
    dfMain['traffic_control_device'] = collapse_rare(dfMain['traffic_control_device'], n_keep=4)
    dfMain['weather_condition'] = collapse_rare(dfMain['weather_condition'], n_keep=5)
    dfMain['road_defect'] = collapse_rare(dfMain['road_defect'], n_keep=2)

    str_cols = [
        'traffic_control_device', 'weather_condition', 'lighting_condition',
        'roadway_surface_cond', 'road_defect', 'crash_type', 'damage',
        'prim_contributory_cause'
    ]
    for col in str_cols:
        dfMain[col] = dfMain[col].astype('category')

    cat_cols = dfMain.select_dtypes('category').columns
    for col in cat_cols:
        if dfMain[col].isna().any():
            if 'UNKNOWN' not in dfMain[col].cat.categories:
                dfMain[col] = dfMain[col].cat.add_categories('UNKNOWN')
            dfMain[col] = dfMain[col].fillna('UNKNOWN')

    dfMain['latitude'] = dfMain['latitude'].fillna(dfMain['latitude'].median())
    dfMain['longitude'] = dfMain['longitude'].fillna(dfMain['longitude'].median())
    dfMain['age_mean'] = dfMain['age_mean'].fillna(dfMain['age_mean'].median())
    dfMain['any_alcohol'] = dfMain['any_alcohol'].fillna(0)

    dfMain['crash_date'] = pd.to_datetime(dfMain['crash_date'])
    dfMain['posted_speed_limit'] = pd.to_numeric(dfMain['posted_speed_limit'], errors='coerce').astype(int)

    print(f"Final shape: {dfMain.shape}")
    print(f"Duplicate crash IDs: {dfMain['crash_record_id'].duplicated().sum()}")
    print(f"Nulls remaining: {dfMain.isnull().sum().sum()}")

    dfMain.to_csv(OUT_PATH, index=False)
    print(f"Cleaned dataset saved to {OUT_PATH}")


if __name__ == "__main__":
    main()
