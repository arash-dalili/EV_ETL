# Washington Electric Vehicle ETL Pipeline

This project implements an ETL (Extract, Transform, Load) pipeline for analyzing electric and alternative fuel vehicles registered in Washington State. The goal is to prepare the dataset for loading into a data warehouse using a dimensional model (star schema).

## Dataset

Source: [Washington State - Electric Vehicle Population Data](https://data.wa.gov/Transportation/Electric-Vehicle-Population-Data/f6w7-q2d2)

The dataset includes information such as:
- Vehicle make, model, and year
- Electric range and MSRP
- Eligibility for clean alternative fuel incentives
- Geographic and utility-related data

## Project Structure

```plaintext
.
├── etl_script.py          # Main ETL logic
├── explore_data.py        # Exploratory Data Analysis (EDA)
├── requirements.txt       # Required Python packages
├── README.md              # Project documentation
└── output/
    ├── dim_vehicle.csv
    ├── dim_location.csv
    ├── dim_ev_type.csv
    ├── dim_cafv_eligibility.csv
    └── fact_vehicle.csv
```

## ETL Workflow

### 1. Extract
- Reads the dataset directly from the data.wa.gov open data portal.

### 2. Transform
- Handles missing values using a combination of:
  - Group-based mode imputation (by `City`, `County`)
  - Fallback to overall mode
  - Replaces zero values in key numeric fields with group-level means
- Encodes categorical fields:
  - `Electric Vehicle Type`
  - `Clean Alternative Fuel Vehicle (CAFV) Eligibility`

### 3. Load
- Creates **dimension tables**:
  - `dim_vehicle`
  - `dim_location`
  - `dim_ev_type`
  - `dim_cafv_eligibility`
- Creates a **fact table**:
  - `fact_vehicle` with foreign keys referencing the dimension tables

These tables are suitable for loading into a **star schema** data warehouse design.

## Exploratory Data Analysis (EDA)

A preliminary analysis was conducted to understand key characteristics of the dataset and guide the ETL design. The focus was on three main variables: `Electric Range`, `Base MSRP`, and `Model Year`.

### Electric Range
- **Mean**: ~44 miles  
- **Standard Deviation**: ~82.4 miles  
- **Range**: 0 to 337 miles  
- **IQR**: 37 miles  
- More than **60%** of entries had a value of 0, suggesting a need for imputation using grouped statistics.

### Base MSRP
- **Mean**: $727  
- **Standard Deviation**: ~$6,917  
- **Range**: $0 to $845,000  
- **IQR**: 0  
- Nearly all rows (247,437 out of 250,659) reported MSRP as 0, indicating a systemic data collection issue.

### Model Year
- **Mean**: 2021.6  
- **Standard Deviation**: ~3 years  
- **Range**: 2000 to 2026  
- **IQR**: 4  
- The majority of vehicles are recent (2020+), with some pre-registrations for future years (2025–2026).

### Missing Value Summary

| Column                  | Missing Count |
|-------------------------|----------------|
| Legislative District    | 583            |
| Electric Range          | 21             |
| Base MSRP               | 21             |
| Vehicle Location        | 14             |
| County                  | 6              |
| City                    | 6              |
| Postal Code             | 6              |
| Electric Utility        | 6              |
| 2020 Census Tract       | 6              |

These were addressed using a layered approach:
- Group-wise imputation by `City` or `County`
- Fallback to global mode (most common value)
- Replacement of invalid 0s with group-level means for numeric fields

## Output Tables

All final tables are exported as `.csv` files in the `output/` folder for inspection or downstream warehousing.

## How to Run

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/wa-ev-etl.git
   cd wa-ev-etl
   ```

2. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the ETL script:
   ```bash
   python etl_script.py
   ```

4. Run EDA:
   ```bash
   python explore_data.py
   ```

## Schema Diagram

A simplified star schema:

```
                  dim_ev_type
                       ▲
                       |
                 dim_vehicle        dim_cafv_eligibility
                       ▲                 ▲
                       |                 |
                    fact_vehicle  ◄──────┘
                       ▲
                       |
                dim_location
