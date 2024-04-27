import streamlit as st
import pandas as pd
import mysql.connector as db
# from streamlit import errors as st_er
from streamlit.delta_generator import DeltaGenerator
from About import YTAPI


def on_search(_txt: str):
    _data = yt.search_list(_txt, 'channel')
    st.session_state.update(NextPageToken=_data.get('nextPageToken', False))
    _df = pd.DataFrame(_data['items'])
    _df = _df.apply(lambda x: x.snippet, axis=1, result_type='expand')
    _df.loc[:, 'logo'] = _df.thumbnails.apply(lambda x: x['default']['url'])
    _df.loc[:, 'check'] = False
    st.session_state.chn_srh_hst.update({_txt: _df})


def set_row(_data: pd.Series):
    c1, c2, c3 = st.columns([.2, .2, .6])
    with c1:
        ''
        ''
        btn_em = st.empty()

    with c2:
        st.write(f'''<p>
        <img src="{_data.logo}"
        alt="logo" title="{_data.channelTitle}" style="border-radius:50%" />
        </p>
        ''', unsafe_allow_html=True)

    with c3:
        st.write(f'### {_data.channelTitle}')
        st.caption(_data.description)

    em = st.empty()

    if _data.check:
        btn_em.success('Added', icon='✅')
        btn = False
    else:
        btn_state = st.session_state.get(_data.channelId) or False

        # if btn_state:
        #     st.session_state.update({_data.channelId: btn_state})
        #     btn = True
        # else:
        #     btn = btn_em.button('Add', key=_data.channelId, disabled=btn_state,
        #                         on_click=lambda: add_channel(_data, em))

        btn = btn_em.button('Add', key=_data.channelId, disabled=btn_state,
                            # on_click=lambda: add_channel(_data, em)
                            )
        btn = btn_state or btn

    st.divider()
    return {'check': btn, 'state': em}


def add_channel(_data: pd.Series, _state: DeltaGenerator):
    with _state.status('Adding Channel...') as s:
        s.write('Downloading Data...')
        print(yt.channel_list(_data.channelId))


api_key = 'AIzaSyBii7IbnVXI3CD1GIQ5tutU4bWmCxnVBHc'
channel_id = 'UCiEmtpFVJjpvdhsQ2QAhxVA'
yt = YTAPI([api_key])

tab_1, tab_2 = st.tabs(['Add Channel by Name', 'Add Channel by ID'])
if not st.session_state.get('chn_srh_hst'):
    st.session_state.update({'chn_srh_hst': {}})

with tab_1:
    '# Channel Search'

    srh_txt = st.text_input(label='Search Bar', placeholder='Search', label_visibility='collapsed')

    st.button(label='Search', disabled=not srh_txt, on_click=lambda: on_search(srh_txt), type='primary')

    df = st.session_state.chn_srh_hst[srh_txt] if srh_txt in st.session_state.chn_srh_hst else pd.DataFrame()
    if not df.empty:
        filter_check = st.selectbox('Filter', ['All', 'In Library', 'Not In Library'])
        f_df = df[df.check == (filter_check == 'In Library')] if filter_check != 'All' else df

        cont = st.container()
        with cont:
            cb_df = f_df.apply(lambda x: set_row(x), axis=1, result_type='expand')

        st.write('[Go Up :arrow_up:](#channel-search)')
        # cols = st.columns([.7, .2])
        # cols[0].write('[Go Up :arrow_up:](#channel-search)')
        # cols[1].button('See More...', disabled=filter_check == 'In Library')
        df[cb_df.check].apply(lambda x: add_channel(x, cb_df.state.loc[x.name]), axis=1)
        # df.update(cb_df[cb_df.check])
        # st.session_state.chn_srh_hst.update({srh_txt: df})
        # print(df)

with tab_2:
    '# Add Channel by ID'

    ch_id = st.text_input(label='Channel ID', placeholder='Channel ID', label_visibility='collapsed').strip()
    id_chk = ch_id.replace('_', '0').replace('-', '0')

    btn_col = st.columns([.1, .95])

    add_btn = btn_col[0].button(label='Add', disabled=not (id_chk.isalnum() and len(ch_id) == 24))

    with btn_col[1]:
        if ch_id and len(ch_id) != 24:
            st.error(':red[The Channel ID must be of 24 Characters]')
        elif ch_id and not id_chk.isalnum():
            st.error(':red[The Channel ID con not Contain Spaces or '
                     'Any other Special Characters except ( "_" , "-" )]')

    if add_btn:
        data = yt.channel_list(ch_id)['items'][0]
        logo = data['snippet']['thumbnails']['default']['url']
        title = data['snippet']['title']
        description = data['snippet']['description']

        cols = st.columns(3)

        with cols[0]:
            st.image(logo)
        with cols[1]:
            f'# {title}'
            st.caption(description)
        st.success('yeay!')
        st.error('This is an error', icon='🚨')
        # print(bool(st.session_state.get('new_')))
    # import time
    # em = st.empty()
    # with em.status("Downloading data...", expanded=False) as status:
    #     st.write("Searching for data...")
    #     time.sleep(2)
    #     st.write("Found URL.")
    #     time.sleep(1)
    #     st.success("Downloading data...")
    #     time.sleep(1)
    #     status.update(label="Download complete!", state="complete", expanded=False)
    # time.sleep(1)
    # em.empty()
