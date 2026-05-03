import pandas as pd
import os

CRASHES_IN = "data/raw/crashes.csv"
PEOPLE_IN = "data/raw/people.csv"
OUT_PATH = "data/interim/merged.csv"


def main():
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)

    dfCrashes = pd.read_csv(CRASHES_IN, low_memory=False)
    dfPeople = pd.read_csv(PEOPLE_IN, low_memory=False)

    print(f"Crashes: {dfCrashes.shape[1]} columns and {dfCrashes.shape[0]} rows.")
    print(f"People: {dfPeople.shape[1]} columns and {dfPeople.shape[0]} rows.")

    dfPeople['age'] = pd.to_numeric(dfPeople['age'], errors='coerce')

    dfPeopleAgg = dfPeople.groupby('crash_record_id').agg(
        age_mean=('age', 'mean'),
        num_people=('person_id', 'count')
    ).reset_index()

    dfPeopleAgg['any_alcohol'] = (
        dfPeople[dfPeople['bac_result'] == 'POSITIVE']
        .groupby('crash_record_id')
        .size()
        .reindex(dfPeopleAgg['crash_record_id'], fill_value=0)
        .gt(0)
        .astype(int)
        .values
    )

    dfMain = dfCrashes.merge(dfPeopleAgg, on='crash_record_id', how='left')
    dfMain.to_csv(OUT_PATH, index=False)
    print(f"Merged dataset saved to {OUT_PATH}")
    print(f"Final shape: {dfMain.shape}")


if __name__ == "__main__":
    main()
