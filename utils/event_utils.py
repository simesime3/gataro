import streamlit as st
from pathlib import Path
import time

# データキャッシュをクリア
st.cache_data.clear()

# リソースキャッシュをクリア
st.cache_resource.clear()

options = {
    "会社の固い宴会": {"description": "正式な会社の宴会", "image": "./img/item01.png"},
    "会社の同僚と宴会": {"description": "同僚と楽しく飲む", "image": "./img/item02.png"},
    "合コン": {"description": "新しい出会いの場", "image": "./img/item03.png"},
    "友人との遊び": {"description": "友人と気軽に楽しむ", "image": "./img/item04.png"},
}

def custom_select(label, options):
    # セッションステートに選択されたイベントがない場合、デフォルト値を設定
    if 'selected_event' not in st.session_state:
        st.session_state.selected_event = next(iter(options.keys()))

    selected_value = st.session_state.selected_event
    cols = st.columns(len(options))

    for i, (key, value) in enumerate(options.items()):
        with cols[i]:
            if st.button(f"{key}", key=f"{key}_btn"):
                selected_value = key
                st.session_state.selected_event = key
            
            # 選択されているかどうかを判定してCSSクラスを適用
            selected_class = "selected" if key == selected_value else ""

            # 画像のパスを取得し、存在する場合に表示
            image_path = Path(value["image"])
            if image_path.exists():
                # ローカルパスの直接指定
                st.image(str(image_path), caption=key, use_column_width=True, output_format="PNG")
            else:
                st.error(f"画像ファイルが見つかりません: {image_path}")

            # st.write(f"**{key}**")
            # st.write(value['description'])

    return selected_value

