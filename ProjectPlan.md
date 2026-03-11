# Chicago Traffic Crash Severity Analysis

---

## Overview

This project analyzes what factors contribute most to severe traffic crashes in Chicago. We plan to build a multiple regression model to identify which variables (weather conditions, lighting, road defects, driver demographics) most strongly correlate with severe injuries or fatalities.

Our approach:
1. Acquire data from the City of Chicago's Open Data API (Socrata)
2. Clean and integrate the datasets by joining on unique crash identifiers
3. Assess data quality and handle missing or inconsistent values
4. Run a multiple regression model to measure the effect of each variable on crash outcomes
5. Visualize results to highlight patterns relevant to urban safety

---

## Team

| Member | Role | Responsibilities |
|---|---|---|
| **Luke Manthuruthil** | Data Acquisition and Workflow Lead | Data acquisition, API integration, Snakemake pipeline, "Crashes" dataset processing, GitHub repository management |
| **Ganga** | Data Cleaning and Modeling Lead | Data cleaning, quality assessment, statistical modeling, "People" dataset processing, integration logic, regression visualizations |
| **Both Members** | Shared | Markdown documentation, ethical data review, final report writing |

---

## Research Question(s)

> **What combination of environmental factors (lighting, weather) and human factors (age, safety equipment use) is the strongest predictor of "Incapacitating Injury" or "Fatal" outcomes in Chicago traffic accidents?**

---

## Datasets

### 1. Traffic Crashes - Crashes
- **Source:** [City of Chicago Data Portal](https://data.cityofchicago.org/Transportation/Traffic-Crashes-Crashes/85ca-t3if)
- **Format:** CSV via Socrata API
- **Description:** One record per crash incident. Includes date, location, posted speed limit, weather conditions, lighting conditions, and road surface conditions.
- **Key Variables:** `CRASH_DATE`, `WEATHER_CONDITION`, `LIGHTING_CONDITION`, `ROADWAY_SURFACE_COND`, `POSTED_SPEED_LIMIT`, `TRAFFIC_CONTROL_DEVICE`, `FIRST_CRASH_TYPE`, latitude/longitude
- **Integration Key:** `CRASH_RECORD_ID`

### 2. Traffic Crashes - People
- **Source:** [City of Chicago Data Portal](https://data.cityofchicago.org/Transportation/Traffic-Crashes-People/u6pd-qa9d)
- **Format:** CSV via Socrata API
- **Description:** One record per person involved in a crash. Includes demographics (age, sex), role (driver, passenger, pedestrian), safety equipment usage, and injury severity.
- **Key Variables:** `PERSON_TYPE`, `SEX`, `AGE`, `SAFETY_EQUIPMENT`, `INJURY_CLASSIFICATION`
- **Integration Key:** `CRASH_RECORD_ID`

### Dataset Integration
Both datasets share the `CRASH_RECORD_ID` field, which allows us to join crash-level environmental data with person-level demographic and injury data. Neither dataset on its own is sufficient to answer the research question, so the join is central to the analysis.
