import streamlit as st
import pandas as pd
from Test import YTAPI


def on_search(_txt: str):
    st.session_state.update({'chn_srh_hst': {}}) if not st.session_state.get('chn_srh_hst') else None
    _data = yt.search_list(_txt, 'channel')
    st.session_state.update(NextPageToken=data.get('nextPageToken', False))
    _df = pd.DataFrame(_data['items'])
    _df = _df.apply(lambda x: x.snippet, axis=1, result_type='expand')
    _df.loc[:, 'logo'] = _df.thumbnails.apply(lambda x: x['default']['url'])
    _df.loc[:, 'check'] = False
    _df.to_csv('temp.csv', index=False)


def set_row(_data: pd.Series, _cont: st.delta_generator.DeltaGenerator):
    with _cont:
        c1, c2, c3 = st.columns([.1, .2, .7])
        with c1:
            ''
            ''
        with c2:
            st.write(f'''<p>
            <img src="{_data.logo}"
            alt="logo" title="{_data.channelTitle}" style="border-radius:50%" />
            </p>
            ''', unsafe_allow_html=True)
        with c3:
            st.write(f'### {_data.channelTitle}')
            st.caption(f'{_data.description}')
        st.divider()
        return c1.checkbox(f'cb_{_data.channelTitle}', label_visibility='collapsed')



api_key = 'AIzaSyBii7IbnVXI3CD1GIQ5tutU4bWmCxnVBHc'
channel_id = 'UCiEmtpFVJjpvdhsQ2QAhxVA'
yt = YTAPI([api_key])

# st.write(yt.channel_list(channel_id))
t1, t2 = st.tabs(['Add Channel by Name', 'Add Channel by ID'])
with t1:
    '# Channel Search'

    srh_txt = st.text_input(label='Search Bar', placeholder='Search', label_visibility='collapsed')

    if st.button(label='Search', disabled=not srh_txt):
        df = pd.DataFrame(yt.search_list(srh_txt, 'channel')['items'])
        df = df.apply(lambda x: x.snippet, axis=1, result_type='expand')
        df.loc[:, 'logo'] = df.thumbnails.apply(lambda x: x['default']['url'])
        df.loc[:, 'check'] = False
        df.to_csv('temp.csv', index=False)
    elif srh_txt:
        df = pd.read_csv('temp.csv', index_col='channelId')
    else:
        df = pd.read_csv('temp.csv')
        df = pd.DataFrame(columns=df.columns)
        df.to_csv('temp.csv', index=False)

    if not df.empty:
        st.button('Get Channel Details')
        # st.markdown('''<style><\style>''')
        cont = st.container()
        cb_df = df.apply(lambda x: set_row(x, cont), axis=1)
        df['check'] = cb_df
        cols = st.columns([.7, .2])
        cols[0].write('[Go Up :arrow_up:](#channel-search)')
        cols[1].button('See More...')
        # print(df[_df])

with t2:
    '# Add Channel by ID'

    ch_id = st.text_input(label='Channel ID', placeholder='Channel ID', label_visibility='collapsed').strip()
    id_chk = ch_id.replace('_', '0').replace('-', '0')

    btn_col = st.columns([.1, .4, .5])

    add_btn = btn_col[0].button(label='Add', disabled=not (id_chk.isalnum() and len(ch_id) == 24))

    with btn_col[1]:
        if ch_id and len(ch_id) != 24:
            st.caption(':red[The Channel ID must be of 24 Characters]')
        elif ch_id and not id_chk.isalnum():
            st.caption(':red[The Channel ID con not Contain Spaces or '
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
    import time
    em = st.empty()
    with em.status("Downloading data...", expanded=False) as status:
        st.write("Searching for data...")
        time.sleep(2)
        st.write("Found URL.")
        time.sleep(1)
        st.success("Downloading data...")
        time.sleep(1)
        status.update(label="Download complete!", state="complete", expanded=False)
    time.sleep(1)
    # em.empty()
