import streamlit as st
import openai

def get_recommendation_reason(selected_place_name, event_type):
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",  # モデル名を指定
        messages=[
            {"role": "system", "content": "あなたは有能なアシスタントです。"},
            {"role": "user", "content": f"{selected_place_name} の推薦理由を教えてください。イベントの種類は {event_type} です。"}
        ]
    )
    # 正しくレスポンスから内容を取得
    return response.choices[0].message.content
