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
