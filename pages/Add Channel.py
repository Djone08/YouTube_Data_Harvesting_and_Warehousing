import streamlit as st
import pandas as pd
from streamlit.delta_generator import DeltaGenerator
from About import YTAPI, YTDataBase


def on_search(_txt: str):
    _data = yt_api.search_list(_txt, 'channel')
    st.session_state.update(NextPageToken=_data.get('nextPageToken', False))
    _df = pd.DataFrame(_data['items'])
    _df = _df.apply(lambda x: x.snippet, axis=1, result_type='expand')
    _df.loc[:, 'logo'] = _df.thumbnails.apply(lambda x: x['default']['url'])
    f_data = yt_db.fetch_data('select id from channels')
    _df.loc[:, 'check'] = _df.channelId.isin(f_data.id)
    st.session_state.chn_srh_hst.update({_txt: _df})


def set_row_srh(_data: pd.Series):
    c1, c2, c3 = st.columns([.2, .2, .6])
    with c1:
        ''
        ''
        if _data.check:
            st.success('Added', icon='✅')
        else:
            if st.session_state.get(f'srh_{_data.channelId}'):
                st.session_state.chn_add_lst.append(pd.Series(_data))
                btn_state = True
            else:
                ch_df = pd.DataFrame(st.session_state.chn_add_lst)
                btn_state = False if ch_df.empty else _data.channelId in ch_df.channelId.values

            st.button('➕ In List'if btn_state else '➕ Add', key=f'srh_{_data.channelId}', disabled=btn_state)

    with c2:
        st.write(f'''<p>
        <img src="{_data.logo}"
        alt="logo" title="{_data.channelTitle}" style="border-radius:50%" />
        </p>
        ''', unsafe_allow_html=True)

    with c3:
        st.write(f'### {_data.channelTitle}')
        st.caption(_data.description)

    st.divider()


def set_row_add(_data: pd.Series):
    c1, c2, c3 = st.columns([.2, .6, .2])

    with c1:
        st.write(f'''<p>
        <img src="{_data.logo}"
        alt="logo" title="{_data.channelTitle}" style="border-radius:50%" />
        </p>
        ''', unsafe_allow_html=True)

    with c2:
        st.write(f'### {_data.channelTitle}')
        st.caption(_data.description)

    with c3:
        ''
        ''
        if st.session_state.get(f'add_{_data.channelId}'):
            _chn_add_lst = st.session_state.chn_add_lst
            st.session_state.chn_add_lst = [x for x in _chn_add_lst if x.channelId != _data.channelId]

        ch_df = pd.DataFrame(st.session_state.chn_add_lst)
        btn_state = True if ch_df.empty else _data.channelId not in ch_df.channelId.values

        st.button('➖ Removed' if btn_state else '➖ Remove', key=f'add_{_data.channelId}', disabled=btn_state)

    em = st.empty()
    st.divider()
    return {'_channel_id': _data.channelId, '_empty': em}


def add_to_db(_channel_id: str, _empty: DeltaGenerator | None = st.empty()):
    with _empty.status('Adding Channel...') as s:
        s.update(label='Fetching Channel Data...')
        ch_df = yt_api.get_channels_df(_channel_id)
        yt_db.add_channels_data(ch_df)
        s.write('Channel Data DownLoaded ✅')
        s.update(label='Fetching All Videos Playlist...')
        pl_df = yt_api.get_playlists_df(id=ch_df['uploads'].iloc[0])
        yt_db.add_playlists_data(pl_df)
        s.update(label='Fetching Videos Data...')
        v_df = pd.concat([yt_api.get_videos_df(x) for x in ch_df['uploads']])
        yt_db.add_videos_data(v_df)
        s.write('Videos Data DownLoaded ✅')
        s.update(label='Fetching Playlists Data...')
        pl_df = yt_api.get_playlists_df(channelId=_channel_id)
        yt_db.add_playlists_data(pl_df)
        s.write('Playlists Data DownLoaded ✅')
        s.update(label='Adding Playlist Id in Videos Data...')
        v_df = pd.concat([yt_api.get_videos_df(x) for x in pl_df['id']])
        yt_db.add_videos_data(v_df)
        s.write('Playlist Id Added ✅')
        s.update(label='Fetching comments Data...')
        c_df = yt_api.get_comments_df(_channel_id)
        yt_db.add_comments_data(c_df)
        s.write('comments Data DownLoaded ✅')


if __name__ == '__main__':
    yt_api = st.session_state.get('yt_api')
    yt_api = yt_api or YTAPI(st.session_state.yt_api_creds)
    # yt_api = yt_api or YTAPI(['AIzaSyBii7IbnVXI3CD1GIQ5tutU4bWmCxnVBHc'])
    st.session_state.update({'yt_api': yt_api})

    yt_db = st.session_state.get('yt_db')
    yt_db = yt_db or YTDataBase(**st.session_state.yt_db_creds)
    # yt_db = yt_db or YTDataBase('localhost', 'root', 'root', '3306')
    st.session_state.update({'yt_db': yt_db})

    tab_1, tab_2 = st.tabs(['search Channels', 'Add Channels'])

    if not st.session_state.get('chn_srh_hst'):
        st.session_state.update({'chn_srh_hst': {}})

    if not st.session_state.get('chn_add_lst'):
        st.session_state.update({'chn_add_lst': []})

    with tab_1:
        '# Channel Search'

        srh_txt = st.text_input(label='Search Bar', placeholder='Search', label_visibility='collapsed')

        st.button(label='Search', disabled=not srh_txt, on_click=lambda: on_search(srh_txt), type='primary')

        df = st.session_state.chn_srh_hst[srh_txt] if srh_txt in st.session_state.chn_srh_hst else pd.DataFrame()
        if not df.empty:
            fetch_df = yt_db.fetch_data('select id from channels')
            df.loc[:, 'check'] = df.channelId.isin(fetch_df.id)
            st.session_state.chn_srh_hst.update({srh_txt: df})

            with st.container():
                filter_check = st.selectbox('Filter', ['All', 'In Library', 'Not In Library'])
                filter_df = df[df.check == (filter_check == 'In Library')] if filter_check != 'All' else df

                filter_df.apply(lambda x: set_row_srh(x), axis=1)

                cols = st.columns([.7, .2])
                cols[0].write('[Go Up :arrow_up:](#channel-search)')
                # cols[1].button('See More...', disabled=filter_check == 'In Library')

    with tab_2:
        '# Add Channels to Library'
        ''

        df = pd.DataFrame(st.session_state.chn_add_lst)
        if not df.empty:
            cols = st.columns([.7, .3])
            with cols[1]:
                add_btn = st.button(label='Add All to Library', type='primary')
            r_df = df.apply(lambda x: set_row_add(x), axis=1, result_type='expand')
            if add_btn:
                r_df.apply(lambda x: add_to_db(**x), axis=1)
                chn_add_lst = st.session_state.chn_add_lst
                fetch_df = yt_db.fetch_data('select id from channels')
                st.session_state.chn_add_lst = [x for x in chn_add_lst if x.channelId not in fetch_df.id.values]
                st.rerun()
        else:
            st.info(':blue[Add Channels to the list Using Channel Search]', icon='ℹ️')

    # with tab_3:
    #     '# Add by Channel ID'
    #
    #     ch_id = st.text_input(label='Channel ID', placeholder='Channel ID', label_visibility='collapsed').strip()
    #     id_chk = ch_id.replace('_', '0').replace('-', '0')
    #
    #     btn_col = st.columns([.1, .95])
    #
    #     add_btn = btn_col[0].button(label='Add', disabled=not (id_chk.isalnum() and len(ch_id) == 24))
    #     fetch_data = yt_db.fetch_data('select id from channels')
    #
    #     with btn_col[1]:
    #         if ch_id and len(ch_id) != 24:
    #             st.error(':red[The Channel ID must be of 24 Characters]')
    #         elif ch_id and not id_chk.isalnum():
    #             st.error(':red[The Channel ID con not Contain Spaces or '
    #                      'Any other Special Characters except ( "_" , "-" )]')
    #         elif ch_id in fetch_data['id'].values:
    #             st.info(':blue[Channel Id already in List]')
    #
    #     if add_btn:
    #         if ch_id not in fetch_data['id'].values:
    #             df.loc[:, 'logo'] = df.thumbnails.apply(lambda x: x['default']['url'])
    #             df = pd.DataFrame(yt_api.channel_list(ch_id)['items'])
    #             df = df.apply(lambda x: x.snippet, axis=1, result_type='expand')
    #             st.session_state.chn_add_lst.append(df.iloc[0])
    #             st.success(':green[Successfully Added to the List]')
