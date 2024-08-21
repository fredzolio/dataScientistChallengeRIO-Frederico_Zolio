import requests
import pandas as pd
from scripts.wcm import weather_code_map

def get_holiday_data(year):
    url = f"https://date.nager.at/api/v3/PublicHolidays/{year}/BR"
    response = requests.get(url)
    return pd.DataFrame(response.json())

def get_holidays_by_month(holidays_df):
    holidays_df['date'] = pd.to_datetime(holidays_df['date'])
    holidays_df['month'] = holidays_df['date'].dt.month
    return holidays_df['month'].value_counts().sort_index()

def get_holidays_weekdays(holidays_df):
    holidays_df['date'] = pd.to_datetime(holidays_df['date'])
    holidays_df['weekday'] = holidays_df['date'].dt.weekday
    return holidays_df[holidays_df['weekday'] < 5]

def get_weather_data():
    url = ("https://archive-api.open-meteo.com/v1/archive?latitude=-22.9064&longitude=-43.1822&start_date=2024-01-01&end_date=2024-08-01&daily=weather_code,temperature_2m_max,temperature_2m_min&timezone=America%2FSao_Paulo")
    response = requests.get(url)
    weather_data = response.json()
    df_weather = pd.DataFrame({
        'date': weather_data['daily']['time'],
        'temperature_2m_max': weather_data['daily']['temperature_2m_max'],
        'temperature_2m_min': weather_data['daily']['temperature_2m_min'],
        'weather_code': weather_data['daily']['weather_code']
    })
    df_weather['date'] = pd.to_datetime(df_weather['date'])
    df_weather['average_temp'] = (df_weather['temperature_2m_max'] + df_weather['temperature_2m_min']) / 2
    return df_weather

def get_weather_by_month(df_weather):
    df_weather['month'] = df_weather['date'].dt.month
    avg_temp_by_month = df_weather.groupby('month')['average_temp'].mean().reset_index()
    
    return avg_temp_by_month

def get_weather_code_by_month(df_weather):
    df_weather['month'] = df_weather['date'].dt.month
    df_weather_cleaned = df_weather.dropna(subset=['weather_code'])
    weather_code_by_month = df_weather_cleaned.groupby('month')['weather_code'].agg(lambda x: x.value_counts().idxmax()).reset_index()
    weather_code_by_month['description'] = weather_code_by_month['weather_code'].map(lambda x: weather_code_map.get(x, {}).get('description', 'N/A'))
    weather_code_by_month['image'] = weather_code_by_month['weather_code'].map(lambda x: weather_code_map.get(x, {}).get('image', ''))
    
    return weather_code_by_month

def get_weather_and_holiday_data(df_holidays, df_weather):
    df_holidays['date'] = pd.to_datetime(df_holidays['date'])
    return pd.merge(df_holidays, df_weather, on='date', how='inner')

def add_weather_description(df):
    df['description'] = df['weather_code'].map(lambda x: weather_code_map.get(x, {}).get('description', 'N/A'))
    return df