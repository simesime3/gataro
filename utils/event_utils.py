import streamlit as st

options = {
    "会社の固い宴会": {"description": "正式な会社の宴会", "image": "./img/item01.png"},
    "会社の同僚との気さくな宴会": {"description": "同僚と楽しく過ごす宴会", "image": "./img/image2.png"},
    "合コン": {"description": "新しい出会いの場", "image": "./img/image3.png"},
    "友人との遊び": {"description": "友人と気軽に楽しむ", "image": "./img/image4.png"},
}

def custom_select(label, options):
    selected_value = st.session_state.selected_event
    cols = st.columns(len(options))

    for i, (key, value) in enumerate(options.items()):
        with cols[i]:
            if st.button(f"{key}", key=f"{key}_btn"):
                selected_value = key
                st.session_state.selected_event = key
            selected_class = "selected" if key == selected_value else ""
            st.markdown(f"""
                <div class="select-img {selected_class}">
                    <img src="{value['image']}" alt="{key}">
                    <div>{key}</div>
                    <div style="font-size:small;">{value['description']}</div>
                </div>
                """, unsafe_allow_html=True)

    return selected_value

