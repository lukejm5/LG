# Chicago Traffic Safety Analysis

## Contributors

- **Luke Manthuruthil** (lukejm5) - Data Engineer
- **Ganga Sajith** (gangasaj) - Data Scientist

---

## Summary

This project investigates what drives injury severity in traffic crashes within the City of Chicago. We wanted to understand whether the conditions of the road and environment matter more than the people involved when it comes to predicting whether a crash leaves someone hurt. The motivation here is practical. If environmental factors dominate, the city should invest in infrastructure. If human factors dominate, education and enforcement carry more weight.

We pulled two datasets from the Chicago Data Portal using the **Socrata Open Data API (SODA)**. The first is **Traffic Crashes - Crashes**, which contains one row per reported crash (~1.04 million rows, 20 columns). The second is **Traffic Crashes - People**, which contains one row per person involved in a crash (~2.28 million rows, 16 columns). Both share a `crash_record_id` field, which we used to join the two tables. Because there are multiple people per crash, we aggregated the people-level data up to the crash level before merging, computing the average age of people involved, the count of people, and a binary flag for whether anyone in the crash had a positive BAC test.

### Research Questions

**Primary:** When evaluating traffic accidents in Chicago, which set of variables has a higher predictive weight on injury severity: environmental conditions (weather, lighting, road surface) or human-centric factors (driver age, alcohol use, contributory cause)?

**Secondary:** Is there a statistically significant interaction between driver demographics and hazardous road conditions?

### Findings

We trained a **logistic regression model** to predict whether a crash resulted in at least one injury (`severe = 1`). The model achieved a ROC-AUC of **0.7298** on the held-out test set, which suggests it has real but not overwhelming predictive power. The clearest finding is that **human factors carry more weight than environmental ones**. The features with the largest coefficient magnitudes are all forms of `prim_contributory_cause`, which is a driver-behavior field filled in by the reporting officer. Causes like "improper backing", "improper overtaking", and "following too closely" are strong negative predictors of severe injury, meaning crashes with these causes tend to be lower-severity. Environmental conditions like weather, lighting, and road surface produced much smaller coefficients in absolute terms.

The mean-injury breakdowns reinforce this picture. Crashes during **rain** (mean 0.24 injuries) and on **wet** roads (0.25) average only slightly more injuries than crashes in clear weather (0.20) on dry roads (0.20). Lighting condition shows a similar narrow band. The differences between contributory causes are larger by comparison. Note that these means are computed per-crash within each weather category, not as raw injury totals, so they are not biased by the fact that clear weather is more common overall.

We were not able to formally test the secondary research question about demographic-environment interactions within the scope of this submission, since the merged dataset only contains aggregated people-level features rather than per-person records, and including interaction terms in a high-cardinality logistic regression would require a separate modeling pass. We discuss this in the Future Work section.

---

## Data profile

### Dataset 1: Traffic Crashes - Crashes
- **Source:** [City of Chicago Data Portal](https://data.cityofchicago.org/Transportation/Traffic-Crashes-Crashes/85ca-t3if)
- **Endpoint:** `https://data.cityofchicago.org/resource/85ca-t3if.json`
- **Access method:** Socrata Open Data API (SODA) via Python `requests`
- **Rows:** 1,040,997
- **Columns selected:** 20
- **Format:** JSON (response), stored locally as CSV
- **Coverage:** September 2017 onward, updated continuously as crash reports are finalized or amended
- **Location in repo:** `data/raw/crashes.csv` (gitignored, distributed via Box)

This dataset serves as our "event" table. It contains one record for every traffic crash that occurred within the City of Chicago limits and under the jurisdiction of Chicago Police Department (CPD). Data is taken directly from the electronic crash reporting system (E-Crash). It includes metadata about the crash itself such as the date and time, the posted speed limit, the presence of traffic control devices, and environmental data like weather and lighting. Several parameters such as street condition, weather condition, and posted speed limits are recorded by the reporting officer based on best available information at the time. Due to this subjective assessment, some recorded values may be inconsistent across reports.

Crashes are only reportable if they involve property damage of $1,500 or more, bodily injury, or occur on a public roadway involving at least one moving vehicle. This requirement is enforced by Illinois statute and means the dataset systematically excludes minor incidents.

### Dataset 2: Traffic Crashes - People
- **Source:** [City of Chicago Data Portal](https://data.cityofchicago.org/Transportation/Traffic-Crashes-People/u6pd-qa9d)
- **Endpoint:** `https://data.cityofchicago.org/resource/u6pd-qa9d.json`
- **Access method:** Socrata Open Data API (SODA) via Python `requests`
- **Rows:** 2,284,768
- **Columns selected:** 16
- **Format:** JSON (response), stored locally as CSV
- **Coverage:** Same as Crashes
- **Location in repo:** `data/raw/people.csv` (gitignored, distributed via Box)

This dataset serves as our "individual" table. Since multiple people can be involved in a single crash, this table has multiple rows for every one row in the Crashes table. It includes demographic data, the role of the person (driver, passenger, pedestrian), safety equipment usage, and a standardized injury classification (Fatal, Incapacitating, Non-Incapacitating, etc.).

### Integration strategy

Both datasets share `crash_record_id` as a common 128-bit identifier. Because the People table has many rows per crash, we aggregated People to one row per `crash_record_id` before joining. The aggregation produces three new features: `age_mean` (average age of people in the crash), `num_people` (count of people involved), and `any_alcohol` (1 if any person in the crash had `bac_result == 'POSITIVE'`, else 0). We then performed a left join from Crashes onto this aggregated People table on `crash_record_id`. The resulting merged dataset has 1,040,997 rows and 23 columns and is saved to `data/interim/merged.csv`.

### Ethical and legal constraints

The data is public and released under the City of Chicago Data Portal terms of use. The People dataset contains some sensitive information including age, sex, and BAC results, but no direct personal identifiers (names, addresses, license numbers) are included. The `RD_NO` field, which previously held the police report number, was removed from the source dataset in November 2023 for privacy reasons. We treat the data as public-but-sensitive and do not attempt re-identification, do not link to external person-level data, and do not republish the raw files. We use Box for distribution rather than GitHub because the file sizes exceed GitHub's 50MB limit.

---

## Data quality

We assessed data quality on the merged dataset of 1,040,997 rows and 23 columns. Several issues showed up during profiling.

**Missing values.** A handful of columns had non-trivial missingness in the raw People table. `bac_result_value` was 99.93% missing, which made it unusable as a feature, and `cell_phone_use` was 99.91% missing for the same reason. Both were dropped before aggregation. After aggregation, the merged dataset had missing values in `age_mean` (about 32% of crashes had no people-level age data, mostly hit-and-runs and pedestrian-only crashes), `latitude`/`longitude` (~0.8%), and `injuries_total`/`injuries_fatal`/`injuries_incapacitating` (~0.2%). Person-level columns we considered keeping (`driver_action`, `driver_vision`, `physical_condition`, `bac_result`) had 19-20% missingness in the raw People table and would have been difficult to aggregate cleanly, so we dropped them.

**Type errors and contaminated columns.** The `age` field in the People table arrived as object dtype because it contained string values like "USAGE UNKNOWN" and "SAFETY BELT USED" mixed in with numeric ages. We coerced the column to numeric with `errors='coerce'`, which turned the contaminating strings into NaN, and capped at 120 to remove obvious data-entry errors. The `bac_result` column similarly mixed categorical text (`TEST NOT OFFERED`, `TEST REFUSED`, `POSITIVE`, `NEGATIVE`) which is the intended schema, but we converted it to a binary `any_alcohol` flag during aggregation.

**Suspicious values in `posted_speed_limit`.** The raw column contained values of 0, 1, 2, 3, 5, and 99, which are not legal posted speed limits in Chicago. We treated values from 0 to 9 inclusive plus 99 as data-entry errors and replaced them with the median. **Known limitation:** our filter does not catch a small number of other clearly-invalid values that survived in the cleaned data (11, 12, 14, 22, 26, 31, 32, 33, 34, 36, 39, 44, 46, 49 mph), which are not standard posted limits in Chicago. The combined volume of these is under 0.05% of rows so the impact on modeling is small, but we note it here for transparency. A stricter filter that keeps only multiples of 5 between 10 and 70 would address this.

**High-cardinality categoricals.** `prim_contributory_cause` had over 40 distinct values, many appearing in fewer than 1% of crashes. Including all of them as one-hot features would inflate the feature space and harm model interpretability. We collapsed rare categories using a `collapse_rare()` helper that keeps the top-N most frequent values and bins everything else as `OTHER`. Top-N was set to 14 for `prim_contributory_cause`, 5 for `weather_condition`, 4 for `traffic_control_device`, and 2 for `road_defect`.

**Duplicate `crash_record_id`.** Earlier pulls of the Crashes dataset had a small number of duplicate `crash_record_id` rows (around 3,700). The pull used for this final analysis no longer contains any duplicates, but we kept this check in our quality assessment because the join logic in `merge.py` is designed to be robust against the issue regardless. The aggregation step ensures the People-side contribution to each crash is unique, so even if duplicates reappeared in a future pull they would not amplify during merging.

**Severe class imbalance.** The target variable `severe` (defined as `injuries_total > 0`) has a positive rate of about 14.4%. Standard logistic regression without weighting will tend to ignore the minority class. We addressed this with `class_weight='balanced'` during fitting.

**Zero-inflation in injury counts.** The raw `injuries_total` column is 85.8% zeros and the rest are heavily right-skewed. Standard regression with `injuries_total` as a continuous target would be inappropriate. This is one of the reasons we converted to a binary `severe` target instead of trying to predict a count.

---

## Data cleaning

The cleaning pipeline lives in `scripts/clean.py` and runs as a single Snakemake rule on the merged dataset. The operations are listed below in execution order, with the quality issue each one addresses.

1. **Drop person-level columns not aggregated**. Removes `driver_action`, `driver_vision`, `physical_condition`, `ejection`, `airbag_deployed`, `safety_equipment`, and `bac_result` from the merged frame. These were left over from earlier exploration but are not used as features. Addresses: redundant columns, residual missingness.

2. **Drop rows with missing target components**. `dropna(subset=['injuries_total', 'injuries_fatal', 'injuries_incapacitating'])`. Removes 2,250 rows where the injury count fields were null. Addresses: cannot construct target variable from null fields.

3. **Construct binary target**. `severe = (injuries_total > 0).astype(int)`. Addresses: zero-inflation and right-skew of the raw count makes regression inappropriate.

4. **Filter and impute `posted_speed_limit`**. Replace values in `[0, 1, 2, ..., 9, 99]` with NA, then fill with the column median. Addresses: data entry errors.

5. **Collapse rare categories**. Apply `collapse_rare()` to `prim_contributory_cause` (top 14), `traffic_control_device` (top 4), `weather_condition` (top 5), and `road_defect` (top 2). All other values are replaced with `OTHER`. Addresses: high cardinality and one-hot feature blowup.

6. **Convert string columns to category dtype**. Casts the eight categorical columns (`traffic_control_device`, `weather_condition`, `lighting_condition`, `roadway_surface_cond`, `road_defect`, `crash_type`, `damage`, `prim_contributory_cause`) to pandas `category` dtype. Reduces memory usage from ~610MB to ~143MB.

7. **Impute remaining nulls**. For categorical columns, fill nulls with `'UNKNOWN'` (added as a category if not already present). For `latitude`, `longitude`, `age_mean`, fill with the column median. For `any_alcohol`, fill with 0 (a missing positive-BAC count means no positive test, treat as no alcohol). Addresses: residual missingness.

8. **Convert datetime and numeric types**. `crash_date` to `datetime64`, `posted_speed_limit` to `int`. Addresses: stored-as-string fields that need typed handling for downstream features.

After cleaning, the dataset has 1,038,747 rows, 24 columns, zero remaining nulls, and a severe-crash rate of 14.4%.

---

## Findings

The logistic regression model trained on the cleaned dataset achieved the following metrics on the 20% held-out test set (207,750 rows).

**At default threshold (0.50):**
- ROC-AUC: 0.7298
- Accuracy: 0.68
- Class 1 (severe) precision: 0.26, recall: 0.64, F1: 0.37
- Class 0 (not severe) precision: 0.92, recall: 0.69, F1: 0.79

We tested two lower thresholds (0.30 and 0.25) to see if recall on the minority class could be improved without crushing precision. The lower thresholds did push recall higher (up to 0.97 at threshold 0.25), but precision and overall accuracy dropped sharply, and F1 on the positive class actually declined or held flat. We report the default threshold as the preferred operating point.

**Coefficient analysis.** The 20 features with the largest absolute coefficients are dominated by `prim_contributory_cause` dummies. The top five negative coefficients are all contributory causes:

| Feature | Coefficient |
|---|---|
| prim_contributory_cause_IMPROPER BACKING | -1.87 |
| prim_contributory_cause_IMPROPER OVERTAKING/PASSING | -1.40 |
| prim_contributory_cause_IMPROPER LANE USAGE | -1.24 |
| prim_contributory_cause_FOLLOWING TOO CLOSELY | -0.95 |
| prim_contributory_cause_DRIVING SKILLS/KNOWLEDGE | -0.83 |

Negative coefficients here mean the model assigns lower probability of severe injury when these causes are present, which makes intuitive sense. Improper backing crashes happen at parking-lot speeds. Following too closely produces fender benders. The strongest *positive* predictors of severe injury are `traffic_control_device_OTHER` (0.59), `num_people` (0.47), and `traffic_control_device_STOP SIGN/FLASHER` (0.44). Stop-sign-controlled intersections being more severe than signal-controlled ones is consistent with literature on uncontrolled or partially-controlled intersection crashes.

**Environmental versus human factors.** Summing absolute coefficients within each group gives a rough magnitude comparison. The four environmental categories (`weather_condition`, `lighting_condition`, `roadway_surface_cond`, `road_defect`) sum to a total magnitude that is substantially smaller than the sum from human-factor categories (`age_mean`, `any_alcohol`, `prim_contributory_cause`). The exact magnitudes are written to `results/metrics.json` when the pipeline runs. **The answer to our primary research question is that human factors, particularly the contributory cause assigned by the reporting officer, carry more predictive weight than environmental conditions in this model.**

Figures generated by the pipeline include the ROC curve (`results/figures/roc_curve.png`), confusion matrix (`confusion_matrix.png`), top coefficients bar chart (`top_coefficients.png`), injury distribution histograms, hour-by-day heatmap, and category breakdowns. All figures are produced from a 10% random sample of the cleaned data for plotting speed.

---

## Future work

Several extensions would strengthen the analysis. The most important is **modeling the secondary research question directly**. Right now we have an implicit answer (human factors dominate environmental ones), but we did not test interaction terms between driver demographics and road conditions. Adding terms like `age_mean * roadway_surface_cond_ICE` or `any_alcohol * lighting_condition_DARKNESS` to the logistic regression would let us measure whether young drivers are disproportionately affected by ice, or whether alcohol amplifies darkness risk. This would require either a more careful feature engineering pass or a switch to a model that handles interactions natively.

A second direction is **comparing models**. Logistic regression is interpretable and gave us coefficients we could read off directly, but it forces a linear decision boundary in feature space and can underperform on tabular data with non-linear relationships. Running gradient boosting (XGBoost or LightGBM) on the same feature matrix and comparing ROC-AUC would tell us whether the 0.73 ceiling is a ceiling on the data or a ceiling on the model. SHAP values from a tree model would also provide a more nuanced picture of feature importance than logistic coefficients alone.

A third direction is **moving away from the aggregated person table**. We currently roll People up to one row per crash before joining, which loses information. A per-person modeling approach where the unit of observation is "one person involved in one crash" would let us include individual-level features (the actual age of each person, their actual safety equipment usage, their position in the vehicle) rather than crash-level averages. The cost is that the analysis becomes about person-level injury rather than crash-level injury, and we would need to handle within-crash correlation.

A fourth direction is **temporal validation**. We did a random train/test split, but crashes are time-stamped and the data spans multiple years. A more honest evaluation would train on 2017-2022 and test on 2023-2024, which would tell us whether the model generalizes forward in time or whether it's picking up patterns specific to certain reporting periods.

Finally, we'd want to **investigate the `prim_contributory_cause` field more carefully**. This field is filled in by the reporting officer at the scene and is partially subjective. The fact that it dominates our coefficient table is partly a real signal about driver behavior and partly an artifact of how strongly the field correlates with the officer's assessment of crash severity. A more rigorous analysis would either drop this field and see how the model performs, or treat it as an outcome rather than a predictor.

### Lessons learned

The largest practical lesson was that **data quality work takes longer than modeling**. The actual logistic regression fit takes about a minute. The cleaning pipeline took several iterations to get right, and we kept finding new edge cases (string contamination in `age`, mixed numeric and categorical in `bac_result`, suspect speed limits) every time we re-profiled. The second lesson was that **aggregation choices have downstream consequences**. By aggregating People to crash level before joining, we made all per-person variation invisible to the model, which is the main reason the secondary research question is unanswered above. If we were starting again we would have kept the long-format merge available and built two parallel modeling pipelines.

---

## Challenges

The biggest single challenge was **dataset volume**. The Crashes table has over a million rows and the People table has over two million. Pulling them via API meant paginating at 50,000 rows per request, and a full pull of People takes around 45 minutes on a typical residential connection. We added checkpointing to the acquisition scripts so a network failure does not force a restart from offset zero. The CSVs are also too large for GitHub (>50MB), so we use Box for distribution and added SHA-256 checksums so the TAs can verify they got the same files we did.

A related challenge was **memory pressure during cleaning**. The merged dataset at object dtype was around 610MB in pandas. Operations like `value_counts` on the full frame were slow enough to interrupt the iteration loop. Converting categorical columns to `category` dtype dropped that to roughly 143MB and made interactive profiling tractable. We kept the EDA on a 10% random sample for plotting purposes, which speeds up rendering of the 16-hour-by-day heatmap and the scatter plot considerably without changing the patterns visible.

A more conceptual challenge was **deciding on the target variable**. The original plan was to predict `injuries_total` directly with multiple regression. The first profiling pass made it obvious that the count is 86% zeros and the non-zero tail is heavy, which makes ordinary least squares inappropriate without a transformation. We considered a Poisson model, a zero-inflated negative binomial, and a binary classification. Binary won because the question we cared about is "does this crash hurt someone or not", and because logistic regression is well-suited to that and gives interpretable coefficients out of the box. The cost is that we collapsed three distinct levels of severity (none, non-incapacitating, incapacitating, fatal) into two.

We also ran into a smaller but annoying issue around **handling unknowns versus missing**. The Chicago data uses literal `'UNKNOWN'` strings in many categorical fields, which is semantically different from a missing value but functionally similar. We chose to treat both the same (impute missing as `'UNKNOWN'`, leave existing `'UNKNOWN'` alone), but this means the model cannot distinguish between "the officer didn't fill it in" and "the officer marked it unknown explicitly." A cleaner approach would have been to keep two separate categories.

Finally, **collaboration coordination** was harder than expected with a team of two. We split work between data engineering (Luke) and data science (Ganga), but the boundary between cleaning and modeling is fuzzy. We spent some time duplicating effort early on. Pinning the column list, the target definition, and the rare-category collapse rules to a single `clean.py` script (rather than letting cleaning live in the notebook) was the move that fixed it.

---

## Reproducing

These steps will let someone else reproduce the entire pipeline from acquisition through final figures.

### 1. Clone the repository

```
git clone https://github.com/lukejm5/LG.git
cd LG
```

### 2. Set up the environment

We recommend Python 3.11. Create a virtual environment and install dependencies.

```
python -m venv .venv
source .venv/bin/activate     # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

The exact package versions used to produce the results in this report are listed in `requirements_freeze.txt`. Use that file instead of `requirements.txt` if you want bit-for-bit reproducibility.

### 3. Get the data

You have two options.

**Option A: pull fresh from the Chicago Data Portal.** This takes around an hour total because the People table is large. An app token speeds it up but is not required.

```
export SOCRATA_APP_TOKEN=your_token_here    # optional
snakemake fetch_crashes --cores 1
snakemake fetch_people --cores 1
```

**Option B: download the snapshot we used from Box.** If you want the exact dataset that produced the metrics in this report, download the two CSVs from our Box folder and place them in `data/raw/`.

Box link: *(to be added by Ganga before final submission)*

After download, verify the files match the snapshot we used by comparing SHA-256 checksums:

```
sha256sum data/raw/crashes.csv data/raw/people.csv
```

The expected checksums are stored in `data/raw/checksums.txt`, which is generated by the acquisition scripts.

### 4. Run the full pipeline

```
snakemake --cores 1
```

This will run merge, clean, EDA, and model rules in dependency order. Outputs will appear in `data/interim/`, `data/processed/`, and `results/`.

### 5. Verify outputs

After a successful run, you should see:

- `data/interim/merged.csv` (~1.04M rows, 23 columns)
- `data/processed/clean.csv` (~1.04M rows, 24 columns)
- `results/metrics.json` containing ROC-AUC and threshold metrics
- `results/coefficients.csv` ranking features by coefficient magnitude
- `results/eda_summary.json` with descriptive statistics
- `results/figures/*.png` containing all eight figures referenced in this report

You can also re-run the original notebook (`ProjectCode.ipynb`) end-to-end after the pipeline completes, since it reads from the same `data/raw/` files. The notebook is preserved as a human-readable narrative version of the same logic that lives in the scripts.

### File structure

```
LG/
├── Snakefile
├── README.md                       this file
├── ProjectPlan.md                  Milestone 2 deliverable
├── StatusReport.md                 Milestone 3 deliverable
├── ProjectCode.ipynb               human-readable notebook version
├── requirements.txt                top-level dependencies
├── requirements_freeze.txt         pinned versions for exact reproduction
├── LICENSE                         MIT for code
├── LICENSE-DATA                    CC BY 4.0 for derived data
├── scripts/
│   ├── fetch_crashes.py
│   ├── fetch_people.py
│   ├── merge.py
│   ├── clean.py
│   ├── eda.py
│   └── model.py
├── data/
│   ├── raw/                        gitignored, available via Box
│   │   ├── crashes.csv
│   │   ├── people.csv
│   │   └── checksums.txt
│   ├── interim/
│   │   └── merged.csv
│   └── processed/
│       └── clean.csv
├── results/
│   ├── metrics.json
│   ├── coefficients.csv
│   ├── eda_summary.json
│   └── figures/
│       └── *.png
└── docs/
    ├── data_dictionary.txt
    └── metadata.jsonld             Schema.org descriptive metadata
```

### Tie to data lifecycle

The project follows the data lifecycle covered in Module 1. Acquisition (Module 4) is handled by `fetch_crashes.py` and `fetch_people.py`. Storage and organization (Module 2) is the directory layout above with raw, interim, and processed separation. Ethical handling (Module 3) is documented in the Data Profile section. Integration (Modules 7-8) happens in `merge.py`. Quality assessment (Module 10) and cleaning (Modules 11-12) are in `clean.py` and the Data Quality and Data Cleaning sections of this report. Workflow automation (Module 13) is the Snakefile. Reproducibility and provenance (Module 14) is this README plus the SHA-256 checksums and pinned requirements. Metadata (Module 15) is the data dictionary in `docs/data_dictionary.txt` and the Schema.org metadata in `docs/metadata.jsonld`.

### Contributions

Both team members contributed throughout. Luke handled data acquisition (`fetch_crashes.py`, `fetch_people.py`), the script refactor that pulled cleaning and modeling out of the notebook into reusable modules, the Snakemake workflow, the final analysis writeup, requirements management, and most of this README. Ganga handled the original cleaning logic, the EDA in the notebook, and the modeling pass that produced the logistic regression results. The Git commit history reflects this split.

---

## References

City of Chicago. (2026). *Traffic Crashes - Crashes* [Dataset]. Chicago Data Portal. https://data.cityofchicago.org/Transportation/Traffic-Crashes-Crashes/85ca-t3if

City of Chicago. (2026). *Traffic Crashes - People* [Dataset]. Chicago Data Portal. https://data.cityofchicago.org/Transportation/Traffic-Crashes-People/u6pd-qa9d

Illinois Department of Transportation. *Illinois Traffic Crash Report SR1050 Instructions Manual*. https://idot.illinois.gov/

Mölder, F., Jablonski, K. P., Letcher, B., Hall, M. B., Tomkins-Tinch, C. H., Sochat, V., Forster, J., Lee, S., Twardziok, S. O., Kanitz, A., Wilm, A., Holtgrewe, M., Rahmann, S., Nahnsen, S., & Köster, J. (2021). Sustainable data analysis with Snakemake. *F1000Research*, 10, 33.

Pedregosa, F., Varoquaux, G., Gramfort, A., Michel, V., Thirion, B., Grisel, O., Blondel, M., Prettenhofer, P., Weiss, R., Dubourg, V., Vanderplas, J., Passos, A., Cournapeau, D., Brucher, M., Perrot, M., & Duchesnay, E. (2011). Scikit-learn: Machine Learning in Python. *Journal of Machine Learning Research*, 12, 2825-2830.

McKinney, W. (2010). Data structures for statistical computing in Python. *Proceedings of the 9th Python in Science Conference*, 56-61.

Hunter, J. D. (2007). Matplotlib: A 2D graphics environment. *Computing in Science & Engineering*, 9(3), 90-95.

Waskom, M. L. (2021). seaborn: statistical data visualization. *Journal of Open Source Software*, 6(60), 3021.

Socrata. *Socrata Open Data API (SODA) Documentation*. https://dev.socrata.com/

### Licensing

- **Code**: This project's code is released under the MIT License (`LICENSE`).
- **Derived data and figures**: The cleaned dataset and figures produced by this pipeline are released under Creative Commons Attribution 4.0 (`LICENSE-DATA`).
- **Source data**: The raw Chicago Data Portal datasets remain under the City of Chicago's terms of use. We do not redistribute the raw files; users obtain them either through the API or through our Box folder.