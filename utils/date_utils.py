import datetime

def get_japanese_weekday(date):
    weekdays = ["月", "火", "水", "木", "金", "土", "日"]
    return weekdays[date.weekday()]
