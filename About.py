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
                thumbnails varchar(255),
                title varchar(255),
                description text,
                viewCount int,
                subscriberCount int,
                videoCount int,
                primary key (id))''')

        self.cur.execute('''create table if not exists playlists(
                id varchar(255) not null,
                channelId varchar(255),
                thumbnails varchar(255),
                title varchar(255),
                description text,
                itemCount int,
                constraint playlists_channelId_fk foreign key (channelId)
                references channels(id) on delete cascade,
                primary key (id))''')

        self.cur.execute('''create table if not exists videos(
                id varchar(255) not null,
                channelId varchar(255),
                playlistId varchar(255),
                thumbnails varchar(255),
                title varchar(255),
                description text,
                duration varchar(50),
                viewCount int,
                likeCount int,
                commentCount int,
                constraint videos_channelId_fk foreign key (channelId)
                references channels(id) on delete cascade,
                constraint videos_playlistId_fk foreign key (playlistId)
                references playlists(id) on delete cascade,
                primary key (id))''')

    def insert_data(self, _table_name: str, **kwargs):
        _data = tuple(x for x in kwargs.values())
        _cols = tuple(kwargs.keys())
        self.cur.execute(f'insert into {_table_name} {_cols} values {_data}')
        self.db.commit()

    def update_data(self, _table_name: str, **kwargs):
        _data = [f'{a}={b!r}' for a, b in zip(kwargs.keys(), kwargs.values())]
        self.cur.execute(f'update {_table_name} set {",".join(_data[1:])} where {_data[0]}')

    @with_cursor
    def fetch_data(self, query: str):
        self.cur.execute(query)
        return self.cur.fetchall()

    @with_cursor
    def add_channels_data(self, _df: pd.DataFrame):
        _df = _df[['id', 'thumbnails', 'title', 'description', 'viewCount', 'subscriberCount', 'videoCount']]
        _df.apply(lambda x: self.insert_data('channels', **x), axis=1)

    @with_cursor
    def add_playlists_data(self, _df: pd.DataFrame):
        _df = _df[['id', 'channelId', 'thumbnails', 'title', 'description', 'itemCount']]
        _df.apply(lambda x: self.insert_data('playlists', **x), axis=1)

    @with_cursor
    def add_videos_data(self, _df: pd.DataFrame):
        _df = _df[['id', 'channelId', 'playlistId', 'thumbnails', 'title', 'description',
                   'duration', 'viewCount', 'likeCount', 'commentCount']]
        _df.apply(lambda x: self.insert_data('videos', **x), axis=1)
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
        es = '''{'id': x.id, 'thumbnails': x.snippet['thumbnails']['default']['url'],
        'title': x.snippet['title'], 'description': x.snippet['description'],
        'viewCount': int(x.statistics['viewCount']), 'subscriberCount': int(x.statistics['subscriberCount']),
        'videoCount': int(x.statistics['videoCount']), 'uploads': x.contentDetails['relatedPlaylists']['uploads']}'''

        res = self.channel_list(_channel_id)
        _df = pd.DataFrame(res['items'])
        df = _df.apply(lambda x: eval(es), axis=1, result_type='expand')
        return df.set_index('channelId')

    def get_playlists_df(self, _channel_id: str):
        es = '''{'id': x.id, 'channelId': x.snippet['channelId'],
        'thumbnails': x.snippet['thumbnails']['default']['url'], 'title': x.snippet['title'],
        'description': x.snippet['description'], 'itemCount': int(x.contentDetails['itemCount'])}'''

        res = self.playlists_list(_channel_id)
        _df = pd.DataFrame(res['items'])
        df = _df.apply(lambda x: eval(es), axis=1, result_type='expand')

        while res.get('nextPageToken'):
            res = self.playlists_list(_channel_id, res.get('nextPageToken'))
            _df = pd.DataFrame(res['items'])
            df = pd.concat([df, _df.apply(lambda x: eval(es), axis=1, result_type='expand')])

        return df.set_index('playlistId')

    def get_videos_df(self, _playlist_id: str):
        es = '''{'id': x.id, 'channelId': x.snippet["channelId"], 'playlistId': _playlist_id,
        'thumbnails': x.snippet['thumbnails']['default']['url'], 'title': x.snippet['title'],
        'description': x.snippet['description'], 'duration': x.contentDetails['duration'],
        'viewCount': int(x.statistics['viewCount']), 'likeCount': int(x.statistics['likeCount']),
        'commentCount': int(x.statistics.get('commentCount', 0))}'''
        data = []

        res = self.playlist_items_list(_playlist_id)
        vid = [x['snippet']['resourceId']['videoId'] for x in res['items']]
        data.extend(self.videos_list(','.join(vid))['items'])

        while res.get('nextPageToken'):
            res = self.playlist_items_list(_playlist_id, res.get('nextPageToken'))
            vid = [x['snippet']['resourceId']['videoId'] for x in res['items']]
            data.extend(self.videos_list(','.join(vid))['items'])

        df = pd.DataFrame(data).apply(lambda x: eval(es), axis=1, result_type='expand')

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
        for l in f.readlines():
            st.markdown(l)
