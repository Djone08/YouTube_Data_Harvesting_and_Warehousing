import streamlit as st
import pandas as pd
from streamlit.delta_generator import DeltaGenerator
from About import YTAPI, YTDataBase


def upd_db(_channel_id: str, _empty: DeltaGenerator | None = st.empty()):
    with _empty.status('Adding Channel...') as s:
        s.update(label='Fetching Channel Data...')
        ch_df = yt_api.get_channels_df(_channel_id)
        yt_db.add_channels_data(ch_df)
        s.write('Channel Data Updated ✔️')
        s.update(label='Fetching All Videos Playlist...')
        pl_df = yt_api.get_playlists_df(id=ch_df.uploads.iloc[0])
        if not pl_df.empty:
            yt_db.add_playlists_data(pl_df)
            s.update(label='Fetching Videos Data...')
            vi_df = pd.concat([yt_api.get_videos_df(x) for x in ch_df['uploads']])
            yt_db.add_videos_data(vi_df)
            s.write('Videos Data Updated ✔️')
            s.update(label='Fetching Playlists Data...')
            pl_df = yt_api.get_playlists_df(channelId=_channel_id)
            if not pl_df.empty:
                yt_db.add_playlists_data(pl_df)
                s.write('Playlists Data Updated ✔️')
                s.update(label='Adding Playlist Id in Videos Data...')
                vi_df = pd.concat([yt_api.get_videos_df(x) for x in pl_df['id']])
                yt_db.add_videos_data(vi_df)
                s.write('Playlist Id Updated ✔️')
            else:
                s.write('The Channel Has No Playlists ❌')
            s.update(label='Fetching comments Data...')
            c_df = yt_api.get_comments_df(_channel_id)
            yt_db.add_comments_data(c_df)
            s.write('comments Data Updated ✔️')
        else:
            s.write('The Channel Has No Video Uploads ❌')
        s.write('Channel Loaded to Library ✔️')


def set_row_lib(_data: pd.Series):
    r1c1, r1c2, r1c3 = st.columns([.2, .6, .2])
    r2c1, r2c2, r2c3, r2c4 = st.columns([.1, .25, .2, .45])
    em = st.empty()

    with r1c1:
        st.write(f'''<a
        href="https://www.youtube.com/channel/{_data.id}"
        traget="_blank">
        <img src="{_data.thumbnails}"
        alt="thumbnails" title="{_data.id}" style="border-radius:50%" />
        </a>''', unsafe_allow_html=True)

    with r1c2:
        st.write(f'### {_data.title}')
        st.caption(f'Subscribers: {_data.subscriberCount} \\\n Videos: {_data.videoCount}')

    with r1c3:
        ''
        del_btn_state = [True, yt_db.execute(f'delete from channels where id = "{_data.id}"')
                         ][0]if st.session_state.get(f'del_{_data.id}') else False
        if not st.session_state.get(f'upd_st_{_data.id}'):
            ch_df = yt_api.get_channels_df(_data.id)
            st.session_state[f'upd_st_{_data.id}'] = ch_df.iloc[0].isin(_data).all()

        upd_btn_state = [True, st.session_state.update({f'upd_st_{_data.id}': True}), upd_db(_data.id, em)
                         ][0] if st.session_state.get(f'upd_{_data.id}') else any([
                            del_btn_state, st.session_state[f'upd_st_{_data.id}']])

        st.button('🗑️ Deleted' if del_btn_state else '🗑️ Delete', key=f'del_{_data.id}', disabled=del_btn_state)
        st.button('🛠️ Updated' if upd_btn_state else '🛠️ Update', key=f'upd_{_data.id}', disabled=upd_btn_state)

    with r2c2.popover('💬 Description'):
        st.caption(_data.description)

    with r2c3.popover(f'🧾 Playlists'):
        n = st.session_state.get(f'n_pl_{_data.id}') or 5
        pl_df = yt_db.fetch_data(f'''select id, thumbnails, title from playlists
        where channelId={_data.id!r}
        order by publishedAt desc''')
        for _i, pl in pl_df.head(n).iterrows():
            pc1, pc2 = st.columns([.3, .5])
            pc1.write(f'''<a
            href="https://www.youtube.com/playlist?list={pl.id}"
            traget="_blank">
            <img src="{pl.thumbnails}"
            alt="thumbnails" title="{pl.id}" style="border-radius:5%" />
            </a>''', unsafe_allow_html=True)
            pc2.write(pl.title)
            st.divider()
        n += 5 if st.button('more', key=f'pl_{_data.id}', disabled=len(pl_df) <= n) else 0
        st.session_state[f'n_pl_{_data.id}'] = n

    with r2c4.popover('▶ Videos'):
        vi_df = yt_db.fetch_data(f'''select id, thumbnails, title from videos
        where channelId={_data.id!r}
        order by publishedAt desc''')
        _n = st.session_state.get(f'n_vl_{_data.id}') or 5
        for _i, vi in vi_df.head(_n).iterrows():
            pc1, pc2 = st.columns([.3, .5])
            pc1.write(f'''<a
            href="https://www.youtube.com/video/{vi.id}"
            traget="_blank">
            <img src="{vi.thumbnails}"
            alt="thumbnails" title="{vi.id}" style="border-radius:5%" />
            </a>''', unsafe_allow_html=True)
            pc2.write(vi.title)
            st.divider()
        _n += 5 if st.button('more', key=f'vl_{_data.id}', disabled=len(vi_df) <= _n) else 0
        st.session_state[f'n_vl_{_data.id}'] = int(_n)

    st.divider()


if __name__ == '__main__':
    try:
        yt_api = st.session_state.get('yt_api')
        yt_api = yt_api or YTAPI(st.session_state.yt_api_creds)
        st.session_state.update({'yt_api': yt_api})

        yt_db = st.session_state.get('yt_db')
        yt_db = yt_db or YTDataBase(**st.session_state.yt_db_creds)
        st.session_state.update({'yt_db': yt_db})
    except AttributeError:
        st.switch_page('About.py')

    '# Channels Library'
    ''

    df = yt_db.fetch_data('select * from channels order by title')
    if not df.empty:
        df.apply(lambda x: set_row_lib(x), axis=1)
    else:
        st.info(':blue[Add Channels to the list Using Channel Search]', icon='ℹ️')
