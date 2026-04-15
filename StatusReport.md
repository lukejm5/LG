# Status Report: Chicago Traffic Safety Analysis

## 1. Task Updates

### Data Acquisition
We have completed the data aquisition. We wrote 2 python scripts to pull live data from the City of Chicago Data Portal via the Socrata Open Data API: [`scripts/fetch_crashes.py`](scripts/fetch_crashes.py) and [`scripts/fetch_people.py`](scripts/fetch_people.py). Both scripts paginate through the full datasets in 50,000-row batches and write results to disk incrementally so that progress is not lost if the connection drops mid-pull. Only the columns relevant to our research questions were selected to reduce download time and memory overhead.

The raw datasets pulled are:

- Crashes: 1,041,273 rows and 20 columns
- People: 2,285,353 rows and 16 columns

All dependencies are listed in [`requirements.txt`](requirements.txt). The `data/raw/` directory is excluded from version control via [`.gitignore`](.gitignore) due to file size. The scripts themselves are the reproducible acquisition artifact.

### Cleaning and Profiling
See Ganga Sajith's contribution section below for a full description of the cleaning and profiling work completed in [`ProjectCode.ipynb`](ProjectCode.ipynb).

### Data Integration
The two datasets were merged on `crash_record_id` using a Pandas inner join inside [`ProjectCode.ipynb`](ProjectCode.ipynb). The resulting merged dataset contains 2,285,353 rows and 35 columns. The higher row count relative to the Crashes dataset reflects the one-to-many relationship between crashes and people. All People records were successfully matched to a Crashes record.

### Interim Report
This document.

### Analysis and Modeling
Not yet started. Pending completion of data cleaning. Will involve building a regression model with `injury_classification` as the target variable.

### Workflow Automation
Not yet started. A Snakemake pipeline will be built to chain acquisition, integration, cleaning, and modeling into a single reproducible workflow.

### Final Submission
Not yet started.

---

## 2. Updated Timeline

| Task | Original Deadline | Status | Updated Completion |
|---|---|---|---|
| Data Acquisition | March 15 | Complete | March 31 |
| Cleaning and Profiling | March 20 | In Progress | April 10 |
| Data Integration | March 25 | Complete | March 31 |
| Interim Report | March 31 | Complete | March 31 |
| Analysis and Modeling | April 15 | Not Started | April 20 |
| Workflow Automation | April 25 | Not Started | April 25 |
| Final Submission | May 3 | Not Started | May 3 |

Data acquisition ran behind the original March 15 deadline due to repeated API timeout errors encountered during large pulls. This pushed integration back as well. Both tasks are now complete.

---

## 3. Changes to Project Plan

The project-plan release tag was noted in feedback as needing correction. The tag should be named `project-plan` and the release should include a `ProjectPlan.md` file.

On the plan itself, the original proposal listed the People dataset access method as either a direct CSV download or the API. We standardized on the API for both datasets to keep the acquisition method consistent and fully scripted. Additionally, `cell_phone_use` and `bac_result_value` were originally considered as potential model features but will be dropped given that both are over 99.9% missing. The `age` column required more cleaning work than anticipated due to encoding errors in the raw data, where non-numeric strings appeared in a column expected to hold numeric age values.

---

## 4. Challenges

The main technical challenge during acquisition was repeated connection timeouts from the Socrata API. The initial scripts had no retry logic, meaning a crash mid-pull would lose all fetched data and require starting over from scratch. We rewrote both scripts to save each page to disk as it is fetched, so a restart picks up from the last saved page rather than the beginning. We also added automatic retry logic that catches both `ReadTimeout` and `ConnectionError` exceptions and retries up to five times with a delay before giving up. Adding a Socrata app token raised our rate limit and reduced the frequency of timeouts.

On the data quality side, several columns that were expected to be numeric turned out to contain mixed types. The `age` column included strings like "USAGE UNKNOWN" alongside numeric values, and `bac_result` mixed categorical text with raw numeric BAC readings. Neither issue was flagged in the original proposal and both required additional cleaning steps to resolve.

---

## 5. Individual Contributions

### Luke Manthuruthil

I handled the data engineering work this milestone. I wrote both acquisition scripts and set up the repository structure including `requirements.txt` and `.gitignore`. After the initial scripts failed repeatedly due to API timeouts, I rewrote them to include checkpoint saving and retry logic so the pull could resume from where it left off rather than restarting. I also resolved Git conflicts that came up when both contributors pushed at the same time. I wrote the merge script and confirmed the join produced the correct row count.

### Ganga Sajith

As discussed earlier, data in the Traffic Crashes - Crashes dataset is shown as is from the Chicago Police Department’s (CPD) electronic crash reporting system, called E-Crash. Since these crash reports are self-reported at the police district by drivers involved or police officers responding to the crash on the scene, the data has the potential to be very messy. Some crash parameters including street condition data, weather condition, and posted speed limits, are recorded subjectively by each police officer on the scene with information available at the time, so these are some columns we should take a closer look at.

We start the data cleaning process with a look at the dataframe using the `pandas.DataFrame.info()` function. This gives us a general overview of the dataframe’s columns and corresponding data types, memory usage, and index range. These are all relevant features since we can look at the data types and diagnose misrepresented values and consider ways to reduce memory usage when working with a relatively medium to large sized dataset like this one. 

Before merging the two datasets, we addressed a structural issue with the join. Since the People dataset contains one row per person involved in a crash, a direct merge on `crash_record_id` produces duplicate crash rows (one per person), inflating the dataset and distorting crash-level statistics. To resolve this, we aggregated the People dataset down to one row per crash before merging. This aggregation produced three crash-level features: `age_mean`, the mean age of all people involved in a crash; `num_people`, the total number of people involved; and `any_alcohol`, a binary flag indicating whether any person in the crash tested positive for alcohol. We then coerced age values from object to numeric before aggregating, as the column contained non-numeric strings alongside valid age values. The aggregated People dataset was then merged with the Crashes dataset on `crash_record_id` using a left join, producing a clean crash-level dataframe with no duplicate records.

We then addressed data quality issues in the `posted_speed_limit` column. Since speed limits are recorded subjectively by responding officers, the column contains a number of clearly erroneous values. We replaced all values below 10 and the known placeholder value of 99 with NaN and imputed these with the column median. This was a conservative approach that preserves the majority of valid records while removing obvious data entry errors.

We also dropped several person-level columns that did not aggregate cleanly to the crash level, including `driver_action`, `driver_vision`, `physical_condition`, `ejection`, `airbag_deployed`, `safety_equipment`, and `bac_result`. These columns either had missingness rates around 20% or higher, or represented individual-level attributes that lose meaning when summarized across multiple people in a crash. The `bac_result` column in particular was superseded by the `any_alcohol` binary flag created during aggregation.

We then collapsed rare categories across several categorical columns. `prim_contributory_cause` contained 40 unique values with 26 appearing in fewer than 1% of records, so we retained the top 14 categories and binned the remainder into an `OTHER` category. We applied the same logic to `traffic_control_device` (top 4 kept), weather_condition (top 5 kept), and road_defect (top 2 kept). This reduces noise in the feature matrix and prevents rare categories from producing unstable coefficients in the regression model.

Remaining null values in categorical columns were filled with `UNKNOWN`, consistent with values already present in those columns from the original data. Numeric null values in latitude, longitude, and age_mean were filled with their respective column medians. The `any_alcohol` column was filled with 0 for crashes with no matched People records.

We then dropped the 2,250 rows where `injuries_total` was null, as these records have an unknown outcome and cannot be used for modeling. Finally, we created our binary target variable severe, defined as `injuries_total` > 0, to address the severe zero-inflation identified during EDA where 82% of crashes recorded zero injuries. Using a binary target is more appropriate than raw injury counts for a standard regression framework given this distribution.

In our final check using pandas.DataFrame.info(), we confirmed zero duplicate `crash_record_id` values, no remaining null values, correct data types across all columns, and a final shape of 1,039,023 rows and 24 columns. Memory usage decreased from the pre-cleaning state, and the severe crash rate in the cleaned dataset is 14.4%.

Moving onto our EDA, we created several different visualizations to explore the relationship between our variables. To start, we defined a smaller random sample of records from our full dataset using the `pandas.DataFrame.sample()` function. We decided on a 10% subset of all records and included a `random_state` value of 42 for reproducibility. 

Our first visualization explores the distribution of `injuries_total` and `injuries_fatal` values. We see that the data is extremely skewed right with severe zero-inflation and likely requires transformation of variables. If we continue with regression models, we could risk underfitting with our current data and producing a model that predicts negative injuries. Since we see a large proportion of 0 values for both `injuries_total` and `injuries_fatal`, we may consider using a zero-inflated model for our analysis or creating a binary target variable, such as `injuries_total > 0`, for example. 

In our univariate analysis, we created frequency tables for the 18 categorical variables in our dataset to examine their distributions. We’re looking for rare categories here, which would reveal the interesting edge cases in the data. We notice that `prim_contributory_cause` is the most important univariate observation with many different unique values. We should consider condensing them to a list of the most frequently seen causes to be able to use this variable strategically. 

Transitioning to bivariate analysis, we want to primarily see how our `prim_contributory_cause` column interacts with other variables. We notice that the 2 highest contributory causes are disregarding traffic signals and disregarding stop signs. Other prevalent causes are displayed in the visualization. With our heatmap we can see that a majority of the crashes occur on day 1 of the week, which will require further analysis to determine if that refers to Sunday or Monday, according to E-Crash. We see significantly less crashes occur during the day, which is expected as daylight generally makes it easier to see traffic risks. We see a majority of injuries happen in 30-mph speed zones, which may simply be because most speed limits are around 30 mph. We might want to investigate proportions here instead of simple counts.

Regarding data quality, we look at metrics such as null rates, anomalies, outliers, duplicates, and coverage for `bac_result` and `physical_condition`. Our null rates display an empty series, which confirms that our data cleaning was successful. Our speed limit values are much more reasonable, and we’re able to address the specific anomalies directly. We notice that after aggregation, there are only 37 duplicate `crash_record_ids`. We do not see any missing values for `bac_result` or `physical_condition`. Our data is now ready for preprocessing and model fitting.

