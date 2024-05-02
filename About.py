from googleapiclient.discovery import build
import mysql.connector as db
from functools import wraps
import pandas as pd
from typing import Literal
import streamlit as st
from configparser import ConfigParser


class YTDataBase(object):
    def __init__(self, host: str, user: str,
                 password: str, port: str, schema: str | None = None):
        schema = schema if schema and schema.isidentifier() else 'yt_db'
        self.db = db.connect(host=host, user=user, password=password, port=int(port))
        self.cur = self.db.cursor()
        self.cur.close()
        self.set_database(schema)

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
                viewCount bigint,
                subscriberCount bigint,
                videoCount int,
                primary key (id))''')

        self.cur.execute('''create table if not exists playlists(
                id varchar(255) not null,
                channelId varchar(255),
                thumbnails varchar(255),
                title varchar(255),
                description text,
                publishedAt datetime,
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
                publishedAt datetime,
                duration time,
                viewCount bigint,
                likeCount bigint,
                dislikeCount bigint,
                commentCount bigint,
                constraint videos_channelId_fk foreign key (channelId)
                references channels(id) on delete cascade,
                constraint videos_playlistId_fk foreign key (playlistId)
                references playlists(id) on delete cascade,
                primary key (id))''')

        self.cur.execute('''create table if not exists comments(
                id varchar(255) not null,
                channelId varchar(255),
                videoId varchar(255),
                authorProfileImage varchar(255),
                textDisplay text,
                textOriginal text,
                likeCount int,
                publishedAt datetime,
                updatedAt datetime,
                constraint comments_channelId_fk foreign key (channelId)
                references channels(id) on delete cascade,
                constraint comments_videoId_fk foreign key (videoId)
                references videos(id) on delete cascade,
                primary key (id))''')

    def insert_data(self, _table_name: str, **kwargs):
        _data = tuple(x for x in kwargs.values())
        _cols = ','.join(x for x in kwargs)
        self.cur.execute(f'insert into {_table_name} ({_cols}) values {_data}')
        self.db.commit()

    def update_data(self, _table_name: str, **kwargs):
        _data = [f'{a}={b!r}' for a, b in zip(kwargs.keys(), kwargs.values())]
        self.cur.execute(f'update {_table_name} set {",".join(_data[1:])} where {_data[0]}')
        self.db.commit()

    @with_cursor
    def fetch_data(self, query: str):
        self.cur.execute(query)
        data = self.cur.fetchall()
        # noinspection PyUnresolvedReferences
        cols = self.cur.column_names
        # cols = [x[0] for x in self.cur.description]
        return pd.DataFrame(data, columns=cols)

    @with_cursor
    def execute(self, query: str):
        self.cur.execute(query)
        self.db.commit()

    @with_cursor
    def add_channels_data(self, _df: pd.DataFrame):
        _df = _df[['id', 'thumbnails', 'title', 'description', 'viewCount', 'subscriberCount', 'videoCount']]
        # _df.apply(lambda x: self.insert_data('channels', **x), axis=1)
        for i, r in _df.iterrows():
            try:
                self.insert_data('channels', **r)
            except Exception as e:
                if str(e).startswith('1062 (23000): Duplicate entry'):
                    self.update_data('channels', **r)
                else:
                    raise e

    @with_cursor
    def add_playlists_data(self, _df: pd.DataFrame):
        _df = _df[['id', 'channelId', 'thumbnails', 'title', 'description', 'publishedAt', 'itemCount']]
        _df.publishedAt = _df.publishedAt.apply(lambda x: x.split('Z')[0].replace('T', ' '))
        # _df.apply(lambda x: self.insert_data('playlists', **x), axis=1)
        for i, r in _df.iterrows():
            try:
                self.insert_data('playlists', **r)
            except Exception as e:
                if str(e).startswith('1062 (23000): Duplicate entry'):
                    self.update_data('playlists', **r)
                elif str(e).startswith('1452 (23000): Cannot add or update a child row'):
                    st.toast(f':red[{e}]')
                else:
                    raise e

    @with_cursor
    def add_videos_data(self, _df: pd.DataFrame):
        _df = _df[['id', 'channelId', 'playlistId', 'thumbnails', 'title', 'description', 'publishedAt',
                   'duration', 'viewCount', 'likeCount', 'dislikeCount', 'commentCount']]
        _df.duration = _df.duration.apply(lambda x: str(x)[-8:])
        # _df.apply(lambda x: self.insert_data('videos', **x), axis=1)
        for i, r in _df.iterrows():
            try:
                self.insert_data('videos', **r)
            except Exception as e:
                if str(e).startswith('1062 (23000): Duplicate entry'):
                    self.update_data('videos', **r)
                elif str(e).startswith('1452 (23000): Cannot add or update a child row'):
                    st.toast(f':red[{e}]')
                else:
                    raise e

    @with_cursor
    def add_comments_data(self, _df: pd.DataFrame):
        _df = _df[['id', 'channelId', 'videoId', 'authorProfileImage', 'textDisplay',
                   'textOriginal', 'likeCount', 'publishedAt', 'updatedAt']]
        _df.publishedAt = _df.publishedAt.apply(lambda x: x.split('Z')[0].replace('T', ' '))
        _df.updatedAt = _df.updatedAt.apply(lambda x: x.split('Z')[0].replace('T', ' '))
        # _df.apply(lambda x: self.insert_data('comments', **x), axis=1)
        for i, r in _df.iterrows():
            try:
                self.insert_data('comments', **r)
            except Exception as e:
                if str(e).startswith('1062 (23000): Duplicate entry'):
                    self.update_data('comments', **r)
                elif str(e).startswith('1452 (23000): Cannot add or update a child row'):
                    st.toast(f':red[{e}]')
                else:
                    raise e


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

    def playlists_list(self, **kwargs):
        for _yt in self.yt_apis:
            try:
                _res = _yt.playlists().list(
                    part='snippet,contentDetails',
                    maxResults=50,
                    **kwargs).execute()
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

    def comment_threads_list(self, _channel_id: str, **kwargs):
        for _yt in self.yt_apis:
            try:
                _res = _yt.commentThreads().list(
                    part='id,replies,snippet',
                    allThreadsRelatedToChannelId=_channel_id,
                    maxResults=100,
                    **kwargs).execute()
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
        return df

    def get_playlists_df(self, **kwargs):
        es = '''{'id': x.id, 'channelId': x.snippet['channelId'],
        'thumbnails': x.snippet['thumbnails']['default']['url'], 'title': x.snippet['title'],
        'description': x.snippet['description'], 'publishedAt': x.snippet['publishedAt'],
        'itemCount': int(x.contentDetails['itemCount'])}'''

        res = self.playlists_list(**kwargs)
        _df = pd.DataFrame(res['items'])
        df = _df.apply(lambda x: eval(es), axis=1, result_type='expand')

        while res.get('nextPageToken'):
            res = self.playlists_list(pageToken=res.get('nextPageToken'), **kwargs)
            _df = pd.DataFrame(res['items'])
            df = pd.concat([df, _df.apply(lambda x: eval(es), axis=1, result_type='expand')])

        return df

    def get_videos_df(self, _playlist_id: str):
        es = '''{'id': x.id, 'channelId': x.snippet["channelId"], 'playlistId': '',
        'thumbnails': x.snippet['thumbnails']['default']['url'], 'title': x.snippet['title'],
        'description': x.snippet['description'], 'publishedAt': x.snippet['publishedAt'],
        'duration': x.contentDetails['duration'], 'viewCount': int(x.statistics.get('viewCount', 0)),
        'likeCount': int(x.statistics.get('likeCount', 0)), 'dislikeCount': int(x.statistics.get('dislikeCount', 0)),
        'commentCount': int(x.statistics.get('commentCount', 0))}'''
        data = []

        res = self.playlist_items_list(_playlist_id)
        vid = [x['snippet']['resourceId']['videoId'] for x in res['items']]
        data.extend(self.videos_list(','.join(vid))['items'])

        while res.get('nextPageToken'):
            res = self.playlist_items_list(_playlist_id, res.get('nextPageToken'))
            vid = [x['snippet']['resourceId']['videoId'] for x in res['items']]
            try:
                data.extend(self.videos_list(','.join(vid))['items'])
            except TypeError:
                print(vid)
                print('='*100)
                print(res['items'])
                print('=' * 100)
                # data.extend(self.videos_list(','.join(vid))['items'])

        df = pd.DataFrame(data).apply(lambda x: eval(es), axis=1, result_type='expand')
        if not df.empty:
            df.playlistId = _playlist_id
            df.publishedAt = df.publishedAt.apply(lambda x: x.split('Z')[0].replace('T', ' '))
            df.duration = pd.to_timedelta(df.duration.str[1:].str.replace('T', '').str.lower())

        return df

    def get_comments_df(self, _channel_id):
        es = '''{'id': x.id, 'channelId': x.snippet["channelId"], 'videoId': x.snippet['videoId'],
                'authorProfileImage': x.snippet['topLevelComment']['snippet']['authorProfileImageUrl'],
                'textDisplay': x.snippet['topLevelComment']['snippet']['textDisplay'],
                'textOriginal': x.snippet['topLevelComment']['snippet']['textOriginal'],
                'likeCount': x.snippet['topLevelComment']['snippet']['likeCount'],
                'publishedAt': x.snippet['topLevelComment']['snippet']['publishedAt'],
                'updatedAt': x.snippet['topLevelComment']['snippet']['updatedAt']}'''

        res = self.comment_threads_list(_channel_id)
        _df = pd.DataFrame(res['items'])
        df = _df.apply(lambda x: eval(es), axis=1, result_type='expand')

        return df


if __name__ == '__main__':

    if not st.session_state.get('yt_api_creds'):
        cfg = ConfigParser()
        cfg.read('Config.ini')
        apis = list(dict(cfg.items('YouTubeAPI')).values())
        st.session_state['yt_api_creds'] = [x for x in apis if x]

    if not st.session_state.get('yt_db_creds'):
        cfg = ConfigParser()
        cfg.read('Config.ini')
        db_cred = dict(cfg.items('YouTubeDataBase'))
        st.session_state['yt_db_creds'] = db_cred

    yt_api = st.session_state.get('yt_api')
    yt_api = yt_api or YTAPI(st.session_state.yt_api_creds)
    st.session_state.update({'yt_api': yt_api})

    yt_db = st.session_state.get('yt_db')
    yt_db = yt_db or YTDataBase(**st.session_state.yt_db_creds)
    st.session_state.update({'yt_db': yt_db})

    '# Hi, Welcome to my Page 🎉'
    ''
    with open('README.md', 'r') as f:
        for li in f.readlines():
            st.markdown(li)
