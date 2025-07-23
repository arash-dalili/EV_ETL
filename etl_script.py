import pandas as pd
import numpy as np

def safe_mean(series):
    non_zero_series = series[(series != 0) & series.notna()]
    return 0 if non_zero_series.empty else non_zero_series.mean()

def extract_data(url):
    return pd.read_csv(url)

def transform_data(df):
    df.rename(columns={"VIN (1-10)": "VIN"}, inplace=True)

    # Fill missing Electric Range and MSRP with overall mean first
    df['Base MSRP'] = df['Base MSRP'].fillna(df['Base MSRP'][(df['Base MSRP'] != 0)].mean())
    df['Electric Range'] = df['Electric Range'].fillna(df['Electric Range'][(df['Electric Range'] != 0)].mean())

    # Replace 0s with group-level mean
    group_means = (
        df.groupby(['Make', 'Model', 'Model Year'])
          .agg({'Base MSRP': safe_mean, 'Electric Range': safe_mean})
          .rename(columns={'Base MSRP': 'group_mean_msrp', 'Electric Range': 'group_mean_range'})
          .reset_index()
    )
    df = df.merge(group_means, on=['Make', 'Model', 'Model Year'], how='left')

    df['Base MSRP'] = df.apply(
        lambda row: row['group_mean_msrp'] if row['Base MSRP'] == 0 and row['group_mean_msrp'] != 0 else row['Base MSRP'],
        axis=1
    )
    df['Electric Range'] = df.apply(
        lambda row: row['group_mean_range'] if row['Electric Range'] == 0 and row['group_mean_range'] != 0 else row['Electric Range'],
        axis=1
    )

    df.drop(columns=['group_mean_msrp', 'group_mean_range'], inplace=True)

    # Imputation
    for col in ['Legislative District', '2020 Census Tract']:
        df[col] = df.groupby('City')[col].transform(lambda x: x.fillna(x.mode()[0] if not x.mode().empty else np.nan))
        if df[col].isna().sum() > 0:
            df[col] = df[col].fillna(df[col].mode()[0])

    df['City'] = df.groupby('County')['City'].transform(lambda x: x.fillna(x.mode()[0] if not x.mode().empty else np.nan))
    if df['City'].isna().sum() > 0:
        df['City'] = df['City'].fillna(df['City'].mode()[0])

    df['Postal Code'] = df.groupby(['County', 'City'])['Postal Code'].transform(
        lambda x: x.fillna(x.mode()[0] if not x.mode().empty else np.nan)
    )
    if df['Postal Code'].isna().sum() > 0:
        df['Postal Code'] = df['Postal Code'].fillna(df['Postal Code'].mode()[0])

    categorical_cols_other = ['County', 'Vehicle Location', 'Electric Utility']
    for col in categorical_cols_other:
        df[col] = df[col].fillna(df[col].mode()[0])

    return df

def encode_and_model(df):
    ev_type_dim = pd.DataFrame(df['Electric Vehicle Type'].dropna().unique(), columns=['Electric Vehicle Type'])
    ev_type_dim['ev_type_id'] = ev_type_dim.index + 1
    df = df.merge(ev_type_dim, on='Electric Vehicle Type', how='left')

    cafv_dim = pd.DataFrame(df['Clean Alternative Fuel Vehicle (CAFV) Eligibility'].dropna().unique(),
                            columns=['Clean Alternative Fuel Vehicle (CAFV) Eligibility'])
    cafv_dim['cafv_id'] = cafv_dim.index + 1
    df = df.merge(cafv_dim, on='Clean Alternative Fuel Vehicle (CAFV) Eligibility', how='left')

    dim_vehicle = df[['Make', 'Model', 'Model Year', 'ev_type_id', 'cafv_id']].drop_duplicates().reset_index(drop=True)
    dim_vehicle['vehicle_id'] = dim_vehicle.index + 1
    df = df.merge(dim_vehicle, on=['Make', 'Model', 'Model Year', 'ev_type_id', 'cafv_id'], how='left')

    dim_location = df[['City', 'County', 'State', 'Postal Code', 'Electric Utility', 'Legislative District',
                       'Vehicle Location', '2020 Census Tract']].drop_duplicates().reset_index(drop=True)
    dim_location['location_id'] = dim_location.index + 1
    df = df.merge(dim_location, on=['City', 'County', 'State', 'Postal Code', 'Electric Utility',
                                    'Legislative District', 'Vehicle Location', '2020 Census Tract'], how='left')

    fact_vehicle = df[['VIN', 'DOL Vehicle ID', 'Base MSRP', 'Electric Range', 'vehicle_id', 'location_id']].copy()
    fact_vehicle['fact_id'] = fact_vehicle.index + 1

    return dim_vehicle, dim_location, ev_type_dim, cafv_dim, fact_vehicle

def save_outputs(dim_vehicle, dim_location, dim_ev_type, dim_cafv, fact_vehicle):
    dim_vehicle.to_csv("output/dim_vehicle.csv", index=False)
    dim_location.to_csv("output/dim_location.csv", index=False)
    dim_ev_type.to_csv("output/dim_ev_type.csv", index=False)
    dim_cafv.to_csv("output/dim_cafv_eligibility.csv", index=False)
    fact_vehicle.to_csv("output/fact_vehicle.csv", index=False)

def main():
    url = "https://data.wa.gov/api/views/f6w7-q2d2/rows.csv?accessType=DOWNLOAD"
    df = extract_data(url)
    df = transform_data(df)
    dim_vehicle, dim_location, dim_ev_type, dim_cafv, fact_vehicle = encode_and_model(df)
    save_outputs(dim_vehicle, dim_location, dim_ev_type, dim_cafv, fact_vehicle)

if __name__ == "__main__":
    main()
