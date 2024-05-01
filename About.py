from googleapiclient.discovery import build
import mysql.connector as db
from functools import wraps
# import numpy as np
import pandas as pd
from typing import Literal
import streamlit as st


class YTDataBase(object):
    def __init__(self, _host: str, _user: str,
                 _password: str, _port: int, _data_base: str | None = None):
        _data_base = _data_base if _data_base and _data_base.isidentifier() else 'yt_db'
        self.db = db.connect(host=_host, user=_user, password=_password, port=_port)
        self.cur = self.db.cursor()
        self.cur.close()
        self.set_database(_data_base)

    @staticmethod
    def with_cursor(func):
        @wraps(func)
        def wrapper_func(self, *args, **kwargs):
            self.cur = self.db.cursor()
            value = func(self, *args, **kwargs)
            self.cur.close()
            return value
        return wrapper_func

    @with_cursor
    def set_database(self, db_name: str):
        self.cur.execute(f'create database if not exists {db_name}')
        self.cur.execute(f'use {db_name}')

        self.cur.execute('''create table if not exists channels(
                id varchar(255) not null,
                thumbnail varchar(255),
                title varchar(255),
                views int,
                description text,
                primary key (id))''')

        self.cur.execute('''create table if not exists playlists(
                id varchar(255) not null,
                channel_id varchar(255),
                description text,
                thumbnail varchar(255),
                title varchar(255),
                constraint playlists_channel_id_fk foreign key (channel_id)
                references channels(id) on delete cascade,
                primary key (id))''')

        self.cur.execute('''create table if not exists videos(
                id varchar(255) not null,
                channel_id varchar(255),
                playlist_id varchar(255),
                thumbnail varchar(255),
                name varchar(255),
                description text,
                constraint videos_channel_id_fk foreign key (channel_id)
                references channels(id) on delete cascade,
                constraint videos_playlist_id_fk foreign key (playlist_id)
                references playlists(id) on delete cascade,
                primary key (id))''')

    def insert_data(self, _table_name: str, **kwargs):
        _data = tuple(_x for _x in kwargs.values())
        _cols = tuple(kwargs.keys())
        self.cur.execute(f'insert into {_table_name} {_cols} values {_data}')
        self.db.commit()

    def update_data(self, _table_name: str, **kwargs):
        _data = [f'{a}={b!r}' for a, b in zip(kwargs.keys(), kwargs.values())]
        self.cur.execute(f'update {_table_name} set {",".join(_data[1:])} where {_data[0]}')

    @with_cursor
    def add_channels_data(self, _df: pd.DataFrame):
        _df = _df[['id', 'thumbnail', 'title', 'description', 'viewCount', 'subscriberCount', 'videoCount']]
        _df.apply(lambda _x: self.insert_data('channels', **_x), axis=1)

    @with_cursor
    def add_playlists_data(self, _df: pd.DataFrame):
        _df = _df[['id', 'channelId', 'thumbnail', 'title', 'description', 'itemCount']]
        _df.apply(lambda _x: self.insert_data('playlists', **_x), axis=1)

    @with_cursor
    def add_videos_data(self, _df: pd.DataFrame):
        _df = _df[['id', 'channelId', 'playlistId', 'thumbnail', 'title', 'description',
                   'duration', 'viewCount', 'likeCount', 'commentCount']]
        _df.apply(lambda _x: self.insert_data('videos', **_x), axis=1)
        # for i, r in _df.iterrows():
        #     try:
        #         self.insert_data('videos', **r)
        #     except Exception as e:
        #         print(e)
        #         self.update_data('videos', **r)

    @with_cursor
    def add_comments_data(self, df: pd.DataFrame):
        pass


class YTAPI(object):

    def __init__(self, _api_keys: list[str]):
        self.yt_apis = [build('youtube',
                              'v3', developerKey=_api) for _api in _api_keys]

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
                    part='snippet,contentDetails',
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

    def get_channels_df(self, _channel_id):
        res = self.channel_list(_channel_id)

        _df = pd.DataFrame(res['items'])
        es = '''{'channelId': _x.id, 'thumbnails': _x.snippet['thumbnails']['default']['url'],
        'title': _x.snippet['title'], 'description': _x.snippet['description'],
        'subscriberCount': _x.statistics['subscriberCount'], 'viewCount': _x.statistics['viewCount'],
        videoCount: _x.statistics['videoCount']}'''
        df = _df.apply(lambda _x: eval(es), axis=1, result_type='expand')
        return df.set_index('channelId')

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
        df = pd.DataFrame(data).apply(lambda _x: eval(es), axis=1, result_type='expand')
        df.playlistId = v_df.loc[df.videoId].playlistId.values

        return df.set_index('videoId')


if __name__ == '__main__':
    yt_api = st.session_state.get('yt_api')
    yt_api = yt_api or YTAPI(['AIzaSyBii7IbnVXI3CD1GIQ5tutU4bWmCxnVBHc'])
    st.session_state.update({'yt_api': yt_api})

    yt_db = st.session_state.get('yt_db')
    yt_db = yt_db or YTDataBase('localhost', 'root', 'root', 3306)
    st.session_state.update({'yt_db': yt_db})

    st.button('create table', on_click=lambda: yt_db.set_database())
    '# Hi, Welcome to my Page 🎉'
    with open('README.md', 'r') as f:
        for x in f.readlines():
            st.markdown(x)
