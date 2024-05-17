import pandas as pd
import ast


def load_data(filename):
    # Load data from CSV
    df = pd.read_csv(filename)

    # Function to extract RSSI value
    def extract_rssi(value):
        if pd.isna(value):
            return value
        try:
            return ast.literal_eval(value)[0]  # Extract the RSSI value
        except (ValueError, IndexError, SyntaxError):
            return value

    # Apply the extraction function to each cell in the DataFrame
    for column in df.columns:
        if column != 'location':  # Apply only to RSSI columns
            df[column] = df[column].apply(extract_rssi)

    # Display the DataFrame
    print(df)
    return df


if __name__ == "__main__":
    data_file = 'wifi_rssi_data.csv'  # Specify your CSV file name here
    df = load_data(data_file)
