import streamlit as st
import pandas as pd
from About import YTAPI, YTDataBase


def set_row_del(_data: pd.Series):
    c1, c2, c3 = st.columns([.2, .6, .2])

    with c1:
        st.write(f'''<p>
        <img src="{_data.thumbnails}"
        alt="thumbnails" title="{_data.id}" style="border-radius:50%" />
        </p>
        ''', unsafe_allow_html=True)

    with c2:
        st.write(f'### {_data.title}')
        st.caption(_data.description)

    with c3:
        ''
        ''
        if st.session_state.get(f'del_{_data.id}'):
            yt_db.execute(f'delete from channels where id = "{_data.id}"')
            btn_state = True
        else:
            btn_state = False

        st.button('🗑️Deleted' if btn_state else '🗑️Delete', key=f'del_{_data.id}', disabled=btn_state)

    st.divider()


yt_api = st.session_state.get('yt_api')
# yt_api = yt_api or YTAPI(['AIzaSyBii7IbnVXI3CD1GIQ5tutU4bWmCxnVBHc'])
# st.session_state.update({'yt_api': yt_api})

yt_db = st.session_state.get('yt_db')
# yt_db = yt_db or YTDataBase('localhost', 'root', 'root', 3306)
# st.session_state.update({'yt_db': yt_db})

'# Channels Library'
''

df = yt_db.fetch_data('select * from channels')
if not df.empty:
    df.apply(lambda x: set_row_del(x), axis=1)
else:
    st.info(':blue[Add Channels to the list Using Channel Search]', icon='ℹ️')

