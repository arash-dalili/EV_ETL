import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def explore_features(df):
    print("Summary Statistics:")
    print("\nElectric Range:")
    print(df['Electric Range'].describe())
    print("\nBase MSRP:")
    print(df['Base MSRP'].describe())
    print("\nModel Year:")
    print(df['Model Year'].describe())

    print("\nDispersion Metrics:")
    dispersion_metrics = {
        'Metric': ['Standard Deviation', 'IQR', 'Range'],
        'Electric Range': [
            df['Electric Range'].std(),
            df['Electric Range'].quantile(0.75) - df['Electric Range'].quantile(0.25),
            df['Electric Range'].max() - df['Electric Range'].min()
        ],
        'Base MSRP': [
            df['Base MSRP'].std(),
            df['Base MSRP'].quantile(0.75) - df['Base MSRP'].quantile(0.25),
            df['Base MSRP'].max() - df['Base MSRP'].min()
        ],
        'Model Year': [
            df['Model Year'].std(),
            df['Model Year'].quantile(0.75) - df['Model Year'].quantile(0.25),
            df['Model Year'].max() - df['Model Year'].min()
        ]
    }
    dispersion_df = pd.DataFrame(dispersion_metrics)
    print(dispersion_df)

def plot_distributions(df):
    sns.histplot(df['Electric Range'], bins=40, kde=True)
    plt.title('Distribution of Electric Range')
    plt.xlabel('Electric Range (miles)')
    plt.show()

    sns.histplot(df['Base MSRP'], bins=40, kde=True)
    plt.title('Distribution of Base MSRP')
    plt.xlabel('MSRP ($)')
    plt.xlim(0, 100000)
    plt.show()

    sns.histplot(df['Model Year'], bins=25)
    plt.title('Distribution of Model Year')
    plt.xlabel('Model Year')
    plt.show()

def missing_values_report(df):
    print("\nMissing values per column:")
    missing_counts = df.isnull().sum()
    missing_counts = missing_counts[missing_counts > 0].sort_values(ascending=False)
    print(missing_counts)

    print(f"\nNumber of 0 values in 'Electric Range': {df['Electric Range'].eq(0).sum()}")
    print(f"Number of 0 values in 'Base MSRP': {df['Base MSRP'].eq(0).sum()}")
    print(f"Total size of DataFrame: {len(df)}")

def main():
    url = "https://data.wa.gov/api/views/f6w7-q2d2/rows.csv?accessType=DOWNLOAD"
    df = pd.read_csv(url)

    explore_features(df)
    plot_distributions(df)
    missing_values_report(df)

if __name__ == "__main__":
    main()
