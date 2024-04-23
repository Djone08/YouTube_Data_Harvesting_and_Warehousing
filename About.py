from googleapiclient.discovery import build
import pandas as pd
import numpy as np
from typing import Literal
import streamlit as st


class YTAPI(object):
    # def __new__(cls, *args, **kwargs):
    #     cls.__init__(*args, **kwargs)
    #     pass
    #
    def __init__(self, _api_keys: list[str]):
        self.yt_apis = [build('youtube',
                              'v3', developerKey=x) for x in _api_keys]

    def search_list(self, text: str,
                    typ: Literal['channel', 'playlist', 'video'] = 'channel'):
        _res = self.yt_apis[0].search().list(
            part='snippet',
            # fields='nextPageToken,prevPageToken,items(snippet(channelId,thumbnails(default),channelTitle))',
            type=typ,
            maxResults=50,
            q=text).execute()
        return _res

    def channel_list(self, _channel_id: str):
        _res = self.yt_apis[0].channels().list(
            part='snippet,contentDetails,statistics',
            # fields='nextPageToken,prevPageToken,items(snippet(channelId,thumbnails(default),channelTitle))',
            id=_channel_id).execute()
        return _res


if __name__ == '__main__':
    api_key = 'AIzaSyAhcBInG7i36z7TYEygtIkMLCnm73YBf14'
    channel_id = 'UCiEmtpFVJjpvdhsQ2QAhxVA'
    yt = YTAPI([api_key])

    # st.write(yt.search_list(channel_id))

    '# Hi, Welcome to my Page 🎉'
    with open('README.md', 'r') as f:
        for x in f.readlines():
            st.markdown(x)
    # st.text_input(label='Channel Search', placeholder='Search', key='channel_search')
    # if st.button(label='Search', disabled=not bool(st.session_state.channel_search)):
    #     _df = pd.DataFrame(yt.search_list(st.session_state.channel_search, 'channel')['items'])
    #     _df = _df.apply(lambda x: x.snippet, axis=1, result_type='expand')
    #     _df.loc[:, 'logo'] = _df.thumbnails.apply(lambda x: x['default']['url'])
    #     _df.loc[:, 'check'] = False
    #     st.data_editor(_df,
    #                    column_config={
    #                        'check': st.column_config.CheckboxColumn('Check', default=False),
    #                        'logo': st.column_config.ImageColumn("Logo")
    #                    }
    #                    )
    #
    # st.write("Here's our first attempt at using data to create a table:")
    # df = pd.DataFrame({
    #     'first column': [1, 2, 3, 4],
    #     'second column': [10, 20, 30, 40]
    # })
    # st.dataframe(df.style.highlight_min())
    #
    # if st.checkbox('Show dataframe'):
    #     chart_data = pd.DataFrame(
    #         np.random.randn(20, 3),
    #         columns=['a', 'b', 'c'])
    #
    #     chart_data
    #
    # df = pd.DataFrame({
    #     'first column': [1, 2, 3, 4],
    #     'second column': [10, 20, 30, 40]
    # })
    #
    # option = st.selectbox(
    #     'Which number do you like best?',
    #     df['first column'])
    #
    # st.write('You selected: ', option)
    #
    # add_selectbox = st.sidebar.selectbox(
    #     'How would you like to be contacted?',
    #     ('Email', 'Home phone', 'Mobile phone')
    # )
    #
    # add_slider = st.sidebar.slider(
    #     'Select a range of values',
    #     0.0, 100.0, (25.0, 75.0)
    # )
    #
    # left_column, right_column = st.columns(2)
    # # You can use a column just like st.sidebar:
    # left_column.button('Press me!')
    #
    # # Or even better, call Streamlit functions inside a "with" block:
    # with right_column:
    #     chosen = st.radio(
    #         'Sorting hat',
    #         ("Gryffindor", "Ravenclaw", "Hufflepuff", "Slytherin"), key='hat')
    #     f"You are in {st.session_state.hat} house!"
    #
    # 'hi there'
