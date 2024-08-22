import streamlit as st
import openai

def suggest_game(purpose):
    prompt = f"提案してほしい宴会の目的は「{purpose}」です。適切なゲームを提案してください。"
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content.strip()