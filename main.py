import streamlit as st
import googlemaps
import pandas as pd
import datetime
import openai
import openai
import folium
from streamlit_folium import folium_static
from collections import Counter

from dotenv import load_dotenv

from utils.date_utils import get_japanese_weekday
from utils.event_utils import custom_select, options
from utils.member_utils import add_member
from utils.gmaps_utils import find_restaurants, gmaps
from utils.game_utils import suggest_game
from utils.weather_forecast_utils import get_weather_forecast, city_code_list
from utils.reason_utils import get_recommendation_reason

# Initialize session state
if "selected_event" not in st.session_state:
    st.session_state.selected_event = None

if "dates" not in st.session_state:
    st.session_state.dates = []

if "members" not in st.session_state:
    st.session_state.members = []

# 選択肢を表示する関数
def custom_select(label, options):
    selected_value = st.session_state.selected_event
    cols = st.columns(len(options))

    for i, (key, value) in enumerate(options.items()):
        with cols[i]:
            if st.button(f"{key}", key=f"{key}_btn"):
                selected_value = key
                st.session_state.selected_event = key
            # 選択されているかどうかを判定してCSSクラスを適用
            selected_class = "selected" if key == selected_value else ""
            st.markdown(f"""
                <div class="select-img {selected_class}">
                    <img src="{value['image']}" alt="{key}">
                    <div>{key}</div>
                    <div style="font-size:small;">{value['description']}</div>
                </div>
                """, unsafe_allow_html=True)

    return selected_value

# サイドバーでナビゲーションメニューを作成
st.sidebar.title("メニュー")
section = st.sidebar.radio("セクションを選択してください", ["幹事の設定", "メンバーの入力", "結果の確認"])

# 幹事の設定セクション
if section == "幹事の設定":
    st.header("幹事の設定")

    # 会の趣旨セクション
    st.header("会の趣旨を選択してください")

    # カスタム選択肢の結果を取得
    event_type = custom_select("宴会の目的", options)

    # 選択された値を表示
    if event_type:
        st.write(f"選択された会の趣旨: {event_type}")

    # Save event_type to session state
    st.session_state.event_type = event_type

    st.subheader("日程候補の入力")

    # カレンダーから日付を選択して追加
    new_date = st.date_input("日程を選択してください", value=datetime.datetime.today())
    if st.button("日程を追加"):
        if new_date not in st.session_state.dates:
            st.session_state.dates.append(new_date)

    # 選択された日程候補を表示
    if st.session_state.dates:
        st.markdown("### 選択された日程候補")
        for date in st.session_state.dates:
            day_of_week = get_japanese_weekday(date)
            st.write(f"{date.strftime('%Y/%m/%d')} ({day_of_week}曜日)")

# メンバーの入力セクション
if section == "メンバーの入力":
    st.header("メンバーの入力")

    if "members" not in st.session_state:
        st.session_state.members = []

    def add_member():
        st.session_state.members.append({
            "name": "",
            "availability": {date: "" for date in st.session_state.dates},
            "location": "",
            "hobbies": [],
            "favorite_foods": [],
            "dates": []
        })

    if st.button("＋ メンバーを追加"):
        add_member()

    # 趣味と好きな食べ物の選択肢
    hobbies_options = ["スポーツ", "ゲーム", "読書", "映画", "音楽", "旅行"]
    food_options = ["和食", "イタリアン", "中華", "フレンチ", "焼肉", "寿司", "カレー", "ラーメン"]

    for i, member in enumerate(st.session_state.members):
        st.subheader(f"メンバー {i + 1} の入力")
        st.session_state.members[i]["name"] = st.text_input("メンバーの名前", key=f"name_{i}")

        for date in st.session_state.dates:
            st.session_state.members[i]["availability"][date] = st.radio(
                f"{date.strftime('%Y-%m-%d')} ({get_japanese_weekday(date)}) の出欠を選んでください ({member['name']})", 
                ["○", "×", "△"], 
                key=f"availability_{i}_{date}"
            )

        st.session_state.members[i]["location"] = st.text_input("自宅からの最寄り駅", key=f"location_{i}")

        st.session_state.members[i]["hobbies"] = st.multiselect(
            "趣味を選んでください", 
            hobbies_options, 
            key=f"hobbies_{i}"
        )

        st.session_state.members[i]["favorite_foods"] = st.multiselect(
            "好きな食べ物を選んでください", 
            food_options, 
            key=f"favorite_foods_{i}"
        )

if section == "結果の確認":
    st.header("入力内容の確認")

    # 出欠の集計
    attendance_summary = {date: {"○": 0, "×": 0, "△": 0} for date in st.session_state.dates}

    for member in st.session_state.members:
        for date, attendance in member["availability"].items():
            if attendance:
                attendance_summary[date][attendance] += 1

    # 集計結果をテーブルで表示し、ユーザーが日程を選択できるようにする
    st.subheader("出欠状況と日程の選択")

    # DataFrameで集計結果を表示
    attendance_df = pd.DataFrame([
        {
            "日程": date.strftime('%Y-%m-%d'),
            "曜日": get_japanese_weekday(date),
            "○": summary["○"],
            "×": summary["×"],
            "△": summary["△"]
        } for date, summary in attendance_summary.items()
    ])

    st.table(attendance_df)

    # ユーザーが日程を選択できるセクション
    selected_date = st.selectbox("最適な日程を選んでください", options=attendance_summary.keys(), format_func=lambda date: f"{date.strftime('%Y-%m-%d')} ({get_japanese_weekday(date)}曜日)")

    if selected_date:
        st.write(f"選択された日程: {selected_date.strftime('%Y-%m-%d')} ({get_japanese_weekday(selected_date)}曜日)")
        st.session_state.optimal_date = selected_date  # optimal_date をセッションステートに保存

    # メンバーごとの好みや制約を表示
    st.subheader("メンバーの好みや制約")
    for member in st.session_state.members:
        st.write(f"**{member['name']}**")
        st.write(f"自宅からの最寄り駅: {member['location']}")
        st.write(f"趣味: {', '.join(member['hobbies'])}")
        st.write(f"好きな食べ物: {', '.join(member['favorite_foods'])}")
        st.write("---")

if section == "結果の確認" and 'optimal_date' in st.session_state:
    st.header("最適な飲食店を探す")
    if st.button("飲食店を探す"):
        participants = st.session_state.members
        if participants:
            try:
                locations = [
                    gmaps.geocode(participant['location'])[0]['geometry']['location']
                    for participant in participants
                ]
                avg_lat = sum(location['lat'] for location in locations) / len(locations)
                avg_lng = sum(location['lng'] for location in locations) / len(locations)
                st.session_state.avg_location = (avg_lat, avg_lng)

                places_result = gmaps.places_nearby(
                    location=(avg_lat, avg_lng), radius=1000, type='restaurant', open_now=True
                )

                if places_result['results']:
                    sorted_places = sorted(
                        places_result['results'],
                        key=lambda x: x.get('rating', 0),
                        reverse=True
                    )
                    st.session_state.place_names = []
                    latitude_list = []
                    longitude_list = []

                    for place in sorted_places[:5]:
                        details = gmaps.place(place_id=place['place_id'])
                        website = details.get('result', {}).get('website')
                        location = details['result']['geometry']['location']
                        latitude_list.append(location['lat'])
                        longitude_list.append(location['lng'])
                        
                        # 評価と価格レベルを取得
                        rating = place.get('rating', '評価なし')
                        price_level = place.get('price_level', '価格情報なし')
                        price_text = "価格情報なし"
                        if isinstance(price_level, int):
                            price_text = "￥" * price_level
                        
                        st.session_state.place_names.append({
                            'name': place['name'],
                            'vicinity': place['vicinity'],
                            'place_id': place['place_id'],
                            'url': website if website else "公式サイトなし",
                            'rating': rating,
                            'price_level': price_text
                        })

                    # 地図の生成
                    map = folium.Map(location=[latitude_list[0], longitude_list[0]], zoom_start=15)
                    for i in range(len(st.session_state.place_names)):
                        folium.Marker(
                            location=[latitude_list[i], longitude_list[i]],
                            popup=st.session_state.place_names[i]['name']
                        ).add_to(map)

                    folium_static(map)

                    st.write("点数の高い飲食店の候補:")
                    for place in st.session_state.place_names:
                        url_text = f"[公式サイトで見る]({place['url']})" if place['url'] != "公式サイトなし" else "公式サイトなし"
                        st.write(f"{place['name']} - {place['vicinity']} - 評価: {place['rating']} - {url_text} - 参考価格: {place['price_level']}")

                    # 天気予報の取得
                    closest_city_code = min(city_code_list.items(), 
                    key=lambda x: (avg_lat - gmaps.geocode(x[0])[0]['geometry']['location']['lat'])**2 + (avg_lng - gmaps.geocode(x[0])[0]['geometry']['location']['lng'])**2)[1]
                    weather_json = get_weather_forecast(closest_city_code)

                    # 宴会の日の天気をチェック
                    weather_forecast_message = "天気予報情報が利用できません。"  # 初期化してデフォルトメッセージを設定
                    if 'forecasts' in weather_json:
                        for forecast in weather_json['forecasts']:
                            if forecast['date'] == st.session_state.optimal_date.strftime('%Y-%m-%d'):
                                rain_chance = forecast['chanceOfRain']['T18_24']
                                if int(rain_chance.replace('%', '')) > 50:
                                    weather_forecast_message = f"天気予報: {forecast['telop']}、降水確率: {rain_chance}。雨の可能性が高いです。傘をお持ちください。"
                                else:
                                    weather_forecast_message = f"天気予報: {forecast['telop']}、降水確率: {rain_chance}。"
                                break

                else:
                    st.write("適切な飲食店が見つかりませんでした。")
            except Exception as e:
                st.write("エラーが発生しました。詳細:", e)
        else:
            st.write("参加者情報を入力してください。")

    # 飲食店の決定とLINEメッセージの表示
    if 'place_names' in st.session_state:
        selected_place_name = st.selectbox("どの飲食店にしますか？", [p['name'] for p in st.session_state.place_names])
        if selected_place_name:
            selected_place = next(p for p in st.session_state.place_names if p['name'] == selected_place_name)
            place_details = gmaps.place(place_id=selected_place['place_id'])
            phone_number = place_details.get('result', {}).get('formatted_phone_number', '電話番号なし')
            address = place_details.get('result', {}).get('formatted_address', '住所なし')
            st.session_state.selected_place = selected_place
            st.session_state.phone_number = phone_number
            st.session_state.address = address

            # おすすめ理由を取得
            recommendation_reason = get_recommendation_reason(selected_place_name, st.session_state.event_type)

            st.write(f"選択した飲食店: {selected_place_name}")
            st.write(f"おすすめ理由: {recommendation_reason}")

            if st.button("LINEで送信するメッセージを見る"):
                line_message = (
                    f"次回の{st.session_state.event_type}は、{st.session_state.optimal_date.strftime('%Y-%m')}の19:00から「{selected_place_name}」のお店で行います。\n"
                    f"住所: {st.session_state.address}\n"
                    f"電話番号: {st.session_state.phone_number}\n"
                    f"公式サイト: {selected_place['url']}\n"
                    # f"当日の天気: {weather_forecast_message}\n"
                    f"おすすめ理由: {recommendation_reason}\n"
                    "当日楽しみにしております！"
                )
                st.write("LINEで送信するメッセージ:")
                st.code(line_message)

    # ゲーム提案のボタンをLINEメッセージの後に配置
    if st.button("ゲームを提案してもらう"):
        game_suggestion = suggest_game(st.session_state.event_type)
        st.write

