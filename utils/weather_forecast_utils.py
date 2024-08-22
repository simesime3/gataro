import streamlit as st
import requests

# 天気APIの設定
city_code_list = {
    "東京都": "130010",
    "大阪": "270000",
    "福岡": "400010"
}

def get_weather_forecast(city_code):
    url = f"https://weather.tsukumijima.net/api/forecast/city/{city_code}"
    response = requests.get(url)
    return response.json()