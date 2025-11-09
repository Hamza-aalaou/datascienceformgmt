import pandas as pd
import numpy as np
import re
import ast
from pathlib import Path

def clean_duration(duration_str):
    if pd.isna(duration_str):
        return np.nan
    hours = 0
    minutes = 0
    if 'h' in duration_str:
        hours = int(re.search(r'(\d+)h', duration_str).group(1))
    if 'm' in duration_str:
        minutes = int(re.search(r'(\d+)m', duration_str).group(1))
    return hours * 60 + minutes

def clean_currency(currency_str):
    if pd.isna(currency_str) or currency_str == '':
        return np.nan
    # Remove dollar sign, commas, and "(estimated)"
    cleaned_str = re.sub(r'[$,()]', '', str(currency_str)).replace('estimated', '').strip()
    try:
        return float(cleaned_str)
    except (ValueError, TypeError):
        return np.nan

def get_first_genre(genres_str):
    if pd.isna(genres_str):
        return None
    try:
        # The genres are in a string that looks like a list
        genres_list = ast.literal_eval(genres_str)
        if genres_list:
            return genres_list[0]
    except (ValueError, SyntaxError):
        # If it's not a list-like string, just return the string itself or None
        return genres_str.split(',')[0].strip() if genres_str else None
    return None

def clean_votes(votes_str):
    if pd.isna(votes_str):
        return np.nan
    votes_str = str(votes_str).strip()
    if votes_str.endswith('K'):
        return float(votes_str[:-1]) * 1000
    if votes_str.endswith('M'):
        return float(votes_str[:-1]) * 1000000
    try:
        return float(votes_str)
    except ValueError:
        return np.nan

from pathlib import Path

def main():
    # Establish the project root directory, which is two levels up from this script
    PROJECT_ROOT = Path(__file__).resolve().parent.parent
    
    # Load data using robust paths
    raw_data_path = PROJECT_ROOT / 'dsas_template' / 'data' / 'raw' / 'Movie_Data_1920_to_2025.csv'
    processed_data_path = PROJECT_ROOT / 'dsas_template' / 'data' / 'processed' / 'Movie_Data_1920_to_2025_cleaned.csv'
    
    df = pd.read_csv(raw_data_path)

    # Apply cleaning functions
    df['duration_minutes'] = df['duration'].apply(clean_duration)
    
    currency_cols = ['budget', 'opening_weekend_gross', 'gross_worldwide', 'gross_us_canada']
    for col in currency_cols:
        df[col] = df[col].apply(clean_currency)
        
    df['primary_genre'] = df['genres'].apply(get_first_genre)
    
    df['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
    
    df['votes_numeric'] = df['votes'].apply(clean_votes)

    # Filter data by release year
    df = df[df['release_date'].dt.year.between(1990, 2025)]

    # Drop original columns that have been replaced
    df = df.drop(columns=['duration', 'genres', 'votes'])

    # Save cleaned data
    df.to_csv(processed_data_path, index=False)
    print(f"Cleaned data saved to {processed_data_path}")

if __name__ == '__main__':
    main()
