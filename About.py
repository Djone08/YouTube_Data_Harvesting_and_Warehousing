from googleapiclient.discovery import build
import mysql.connector as db
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
        for _yt in self.yt_apis:
            try:
                _res = self.yt_apis[0].search().list(
                    part='snippet',
                    type=typ,
                    maxResults=50,
                    q=text).execute()
                return _res
            except Exception as e:
                print(e)

    def channel_list(self, _channel_id: str):
        for _yt in self.yt_apis:
            try:
                _res = _yt.channels().list(
                    part='snippet,contentDetails,statistics',
                    # fields='nextPageToken,prevPageToken,items(snippet(channelId,thumbnails(default),channelTitle))',
                    id=_channel_id).execute()
                return _res
            except Exception as e:
                # self.yt_apis.remove(_yt)
                print(e)

    def playlists_list(self, _channel_id: str, _page_token: str | None = None):
        for _yt in self.yt_apis:
            try:
                _res = _yt.playlists().list(
                    part='snippet, contentDetails',
                    pageToken=_page_token,
                    maxResults=50,
                    channelId=_channel_id).execute()
                return _res
            except Exception as e:
                print(e)

    def playlist_items_list(self, _playlist_id: str, _page_token: str | None = None):
        for _yt in self.yt_apis:
            try:
                _res = _yt.playlistItems().list(
                    part='snippet,status',
                    # fields='nextPageToken,items(snippet(resourceId(videoId)))',
                    pageToken=_page_token,
                    maxResults=50,
                    playlistId=_playlist_id).execute()
                return _res
            except Exception as e:
                print(e)

    def videos_list(self, _video_id: str):
        for _yt in self.yt_apis:
            try:
                _res = _yt.videos().list(
                    part='snippet,contentDetails,statistics',
                    id=_video_id).execute()
                return _res
            except Exception as e:
                print(e)

    def comment_threads_list(self, _channel_id: str):
        for _yt in self.yt_apis:
            try:
                _res = _yt.commentThreads().list(
                    part='id,replies,snippet',
                    allThreadsRelatedToChannelId=_channel_id).execute()
                return _res
            except Exception as e:
                print(e)

    def get_playlists_df(self, _channel_id: str):
        res = self.playlists_list(_channel_id)

        _df = pd.DataFrame(res['items'])
        es = '''{'playlistId': _x.id, 'channelId': _x.snippet['channelId'],
        'thumbnails': _x.snippet['thumbnails']['default']['url'],'title': _x.snippet['title'],
        'description': _x.snippet['description'],'itemCount': _x.contentDetails['itemCount']}'''
        df = _df.apply(lambda _x: eval(es), axis=1, result_type='expand')

        while res.get('nextPageToken'):
            res = self.playlists_list(_channel_id, res.get('nextPageToken'))
            _df = pd.DataFrame(res['items'])
            df = pd.concat([df, _df.apply(lambda _x: eval(es), axis=1, result_type='expand')])

        return df.set_index('playlistId')

    def get_videos_df(self, _playlist_ids: iter):
        es = '''{'videoId': _x.id, 'playlistId': '', 'channelId': _x.snippet["channelId"],
        'thumbnails': _x.snippet['thumbnails']['default']['url'], 'title': _x.snippet['title'],
        'description': _x.snippet['description'], 'duration': _x.contentDetails['duration'],
        'viewCount': _x.statistics['viewCount'], 'likeCount': _x.statistics['likeCount'],
        'commentCount': _x.statistics.get('commentCount', 0)}'''
        data = []
        v_ids = []

        for _playlist_id in _playlist_ids:
            res = self.playlist_items_list(_playlist_id)
            _df = pd.DataFrame(res['items'])
            df = _df.apply(lambda _x: {'videoId': _x.snippet['resourceId']['videoId'],
                                       'playlistId': _x.snippet['playlistId']}, axis=1, result_type='expand')

            while res.get('nextPageToken'):
                res = self.playlist_items_list(_playlist_id, res.get('nextPageToken'))
                _df = pd.DataFrame(res['items'])
                df = _df.apply(lambda _x: {'videoId': _x.snippet['resourceId']['videoId'],
                                           'playlistId': _x.snippet['playlistId']}, axis=1, result_type='expand')

            v_ids.append(df)

        v_df = pd.concat(v_ids).set_index('videoId')
        v_df = v_df[~v_df.index.duplicated()]

        _ = [data.extend(self.videos_list(','.join(v_df.index[i:i+50]))['items']) for i in range(0, len(v_df), 50)]
        df = pd.DataFrame(data).apply(lambda _x: eval(es), axis=1, result_type='expand').set_index('videoId')
        df.playlistId = v_df.loc[df.index]

        return df


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
