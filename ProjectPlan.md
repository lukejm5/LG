# Chicago Traffic Safety Analysis — Project Proposal
 
## 1. Overview
 
The central objective of this project is to conduct an in-depth, end-to-end analysis of traffic safety within the City of Chicago. Our specific goal is to identify and quantify the various factors that contribute to the severity of traffic crashes, specifically focusing on what leads to **"Incapacitating" or "Fatal" injuries**. By leveraging open-source municipal data, we aim to uncover hidden patterns that distinguish a minor "fender bender" from a life-altering collision. To achieve this, we will build a multiple regression model designed to isolate the predictive power of environmental variables versus human behaviors.
 
Our approach follows the professional data science lifecycle, beginning with programmatic data acquisition. We will utilize the **Socrata Open Data API (SODA)** to pull live data from the Chicago Data Portal, ensuring our analysis is based on the most current records available. Once the data is acquired, we will implement a rigorous cleaning and integration phase where we join disparate datasets on unique crash identifiers. This will be followed by a comprehensive data quality assessment to ensure our statistical results are valid. Finally, the entire project will be codified into a **Snakemake workflow**, ensuring that our findings are not just a one-time report but a fully reproducible scientific artifact.
 
---
 
## 2. Team: Roles and Responsibilities
 
To ensure accountability and a clear division of labor, we have split the project into two main workstreams: Data Engineering and Data Science.
 
### Luke Manthuruthil — Lead Data Engineer
My primary responsibility is the technical foundation of the project. I will write the Python scripts required for automated data acquisition via API requests. I am also in charge of the repository architecture and the implementation of the Snakemake workflow. This involves managing the file organization, ensuring that all dependencies are listed in a requirements file, and creating the "Run All" functionality that allows the instructors to replicate our entire pipeline with a single command. I will also oversee the data integration phase, ensuring the relational join between the two datasets is handled without losing critical information.
 
### Ganga — Lead Data Scientist
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
 
### Dataset 1: Traffic Crashes — Crashes
- **Source:** City of Chicago Data Portal
- **Description:** This dataset serves as our "event" table. It contains one record for every traffic crash that occurred within the city limits. It includes metadata about the crash itself, such as the date and time, the posted speed limit, the presence of traffic control devices, and environmental data like weather and lighting.
- **Access Method:** We will use the Socrata Open Data API (SODA) to pull this data in JSON format using the Python `requests` library.
 
### Dataset 2: Traffic Crashes — People
- **Source:** City of Chicago Data Portal
- **Description:** This dataset serves as our "individual" table. Since multiple people can be involved in a single crash, this table has multiple rows for every one row in the Crashes table. It includes critical demographic data, the role of the person (driver, passenger, or pedestrian), safety equipment usage, and a standardized injury classification (Fatal, Incapacitating, Non-Incapacitating, etc.).
- **Access Method:** We will acquire this data in CSV format, either via a direct download script or the API.
 
### Integration Strategy
Both datasets include a common attribute: `CRASH_RECORD_ID`. This 128-bit unique identifier allows us to perform a relational **Left Join** in Pandas. We will join the People data onto the Crashes data to create a unified view where every person involved in a crash is linked to the specific environmental conditions present at the time of their accident.
