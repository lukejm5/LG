# Chicago Traffic Safety Analysis - Project Proposal
 
## 1. Overview
 
The central objective of this project is to conduct an in-depth, end-to-end analysis of traffic safety within the City of Chicago. Our specific goal is to identify and quantify the various factors that contribute to the severity of traffic crashes, specifically focusing on what leads to **"Incapacitating" or "Fatal" injuries**. By leveraging open-source municipal data, we aim to uncover hidden patterns that distinguish a minor "fender bender" from a life-altering collision. To achieve this, we will build a multiple regression model designed to isolate the predictive power of environmental variables versus human behaviors.
 
Our approach follows the professional data science lifecycle, beginning with programmatic data acquisition. We will utilize the **Socrata Open Data API (SODA)** to pull live data from the Chicago Data Portal, ensuring our analysis is based on the most current records available. Once the data is acquired, we will implement a rigorous cleaning and integration phase where we join disparate datasets on unique crash identifiers. This will be followed by a comprehensive data quality assessment to ensure our statistical results are valid. Finally, the entire project will be codified into a **Snakemake workflow**, ensuring that our findings are not just a one-time report but a fully reproducible scientific artifact.
 
---
 
## 2. Team: Roles and Responsibilities
 
To ensure accountability and a clear division of labor, we have split the project into two main workstreams: Data Engineering and Data Science.
 
### Luke Manthuruthil - Data Engineer
My primary responsibility is the technical foundation of the project. I will write the Python scripts required for automated data acquisition via API requests. I am also in charge of the repository architecture and the implementation of the Snakemake workflow. This involves managing the file organization, ensuring that all dependencies are listed in a requirements file, and creating the "Run All" functionality that allows the instructors to replicate our entire pipeline with a single command. I will also oversee the data integration phase, ensuring the relational join between the two datasets is handled without losing critical information.
 
### Ganga Sajith - Data Scientist
Ganga is responsible for the analytical integrity of the project. This role focuses on the data cleaning, profiling, and modeling phases. Ganga will perform a detailed data quality assessment to identify outliers, missing values, and potential biases in the raw datasets. Once the data is prepared, Ganga will lead the statistical modeling efforts, specifically the development and testing of our multiple regression models. This includes interpreting the coefficients to determine which factors are statistically significant. Finally, Ganga will create the visualizations and charts that translate our numerical results into clear, actionable insights for our final report.
 
---
 
## 3. Research Questions
 
Our project is driven by two main questions that seek to balance environmental context with human behavior.
 
### Primary Research Question
> When evaluating traffic accidents in Chicago, which set of variables has a higher predictive weight on injury severity: **environmental conditions** (such as weather, lighting, and road surface) or **human-centric factors** (such as driver age, sex, and the use of safety equipment like seatbelts and airbags)?
 
**Why this matters:** Understanding whether a crash is "caused" by the road or "worsened" by the person helps city planners decide if they should invest in better infrastructure or better public safety education.
 
### Secondary Research Question
> Is there a statistically significant interaction between specific driver demographics and hazardous road conditions? For example, are younger drivers more likely to be involved in severe accidents during icy or wet conditions compared to older, more experienced drivers?
 
**Why this matters:** This allows for more targeted safety interventions and helps identify "high-risk" scenarios that are a combination of both person and place.
 
---
 
## 4. Datasets
 
We will integrate two distinct datasets from the City of Chicago Open Data Portal. Both datasets are authoritative, regularly updated, and provide a high level of granularity.
 
### Dataset 1: Traffic Crashes - Crashes
- **Source:** City of Chicago Data Portal
> This dataset serves as our "event" table. It contains one record for every traffic crash that occurred within the city limits. It includes metadata about the crash itself, such as the date and time, the posted speed limit, the presence of traffic control devices, and environmental data like weather and lighting.
- **Access Method:** We will use the Socrata Open Data API (SODA) to pull this data in JSON format using the Python `requests` library.
 
### Dataset 2: Traffic Crashes - People
- **Source:** City of Chicago Data Portal
> This dataset serves as our "individual" table. Since multiple people can be involved in a single crash, this table has multiple rows for every one row in the Crashes table. It includes critical demographic data, the role of the person (driver, passenger, or pedestrian), safety equipment usage, and a standardized injury classification (Fatal, Incapacitating, Non-Incapacitating, etc.).
- **Access Method:** We will acquire this data in CSV format, either via a direct download script or the API.
 
### Integration Strategy
Both datasets include a common attribute: `CRASH_RECORD_ID`. This 128-bit unique identifier allows us to perform a relational **Left Join** in Pandas. We will join the People data onto the Crashes data to create a unified view where every person involved in a crash is linked to the specific environmental conditions present at the time of their accident.

### Dataset Descriptions

The **Traffic Crashes - Crashes** dataset shows information about each traffic crash on city streets within the City of Chicago limits and under the jurisdiction of Chicago Police Department (CPD). Data is taken directly from the electronic crash reporting system (E-Crash) from CPD without including personally identifiable information for privacy. As of November 21st, 2023, the RD_NO column representing Chicago Police Department report number has been removed for privacy reasons as well. 

This database is updated any time a crash report is finalized or when existing data within E-Crash is amended. This E-Crash data exists for limited police districts dating back to 2015, however, a majority of the data is available from September 2017 and onwards. Around 50% of all crash reports are self-reported to the police district by the driver or drivers involved in the crash. These mainly consist of minor crashes. However, the other half of all crash reports are recorded by the responding police officer at the scene. Several crash parameters such as street condition data, weather condition, and posted speed limits, are recorded by the reporting officer based on best available information at the time. Due to this subjective assessment of parameters, some may disagree on the recorded information and analysis of road conditions. 

If new or updated information on a crash becomes available, reporting officers have the ability to change details in the crash report after the fact. Most crashes that occur on interstate highways, freeway ramps, and local roads along the city boundaries that are still within city limits tend to occur where CPD is not the responding police agency. These data points are excluded from the dataset, since they may not be standardized according to the CPD. 

The specific format of crash recordings are outlined in the Traffic Crash Report, SR1050, of the Illinois Department of Transportation. Chicago data portal’s crash data follows the SR1050 structure for the most part. The Illinois Department of Transportation hosts the latest version of the SR1050 instructions manual with detailed descriptions of each data element.

Out of all crashes that occur, crashes are only reportable if they involve property damage value of $1,500 or more, bodily injury to one or more experiencing the crash, or occur on a public roadway involving at least one moving vehicle except bike dooring. This requirement is enforced by Illinois statute. However, all crashes are still recorded within CPD records, therefore not all crashes that have occurred will be documented and found in the crash dataset released by Illinois Department of Transportation.

The **Traffic Crashes - People** dataset contains information about people involved in a crash and details on injuries sustained if any occurred. This dataset is designed to be used in combination with the related Crashes and Vehicle (not used in this project) datasets from the same source. 

The records in this dataset correspond to occupants in a vehicle involved in a crash. It includes people not inside the motor vehicle such as pedestrians, bicyclists, and users of other non-motor vehicle modes of transportation. Initial reports that must be updated due to fatalities occurring after the crash are generally amended within 30 days of the date of the crash.

---

## 5. Timeline

**Data Aquisition:** Scripting API calls to pull raw JSON/CSV data from Socrata. 
 - Deadline: March 15
 - Responsibility: Luke

**Cleaning & Profiling:** Handling missing values (nulls in age/sex) and assessing data quality.
- Deadline: March 20
- Responsibility: Ganga

**Data Integration:** Merging datasets via CRASH_RECORD_ID and verifying join integrity.
- Deadline: March 25
- Responsibility: Luke & Ganga

**Interim Report:** Documenting progress and challenges in StatusReport.md.
- Deadline: March 31
- Responsibility: Luke & Ganga

**Analysis & Modeling:** Running multiple regression and generating visualizations.
- Deadline: April 15
- Responsibility: Ganga

**Workflow Automation:** Finalizing Snakemake pipeline and reproducibility documentation.
- Deadline: April 25
- Responsiblity: Luke

**Final Submission:** Completing README.md and creating the GitHub release.
- Deadline: May 03
- Responsiblity: Luke & Ganga

---

## 6. Constraints

**Ethical/Privacy:** While the data is public, the "People" dataset contains sensitive information. We must ensure no individual can be re-identified through a combination of attributes.

**Data Quality:** Records often contain "Unknown" entries for weather or safety equipment usage, which may bias the regression model.

**Volume:** These datasets are large (hundreds of thousands of rows), which may present memory management challenges in Python/Pandas.

---

## 7. Gaps

We need to further investigate how to handle high-cardinality categorical variables (like "Primary Contributory Cause") in our regression model.
