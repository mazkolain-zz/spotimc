'''
Created on 23/09/2011

@author: mikel
'''
import xbmc, xbmcgui
from spotify import link
import time
from __main__ import __addon_version__
import spotifyproxy
import math


#TODO: urllib 3.x compatibility
import urllib


class PlaylistManager:
    __server_port = None
    __user_agent = None
    __play_token = None
    __url_headers = None
    __track_list = None
    
    
    def __init__(self, server_port):
        self.__track_list = []
        self.__server_port = server_port
    
    
    def _get_user_agent(self):
        if self.__user_agent is None:
            xbmc_build = xbmc.getInfoLabel("System.BuildVersion")
            self.__user_agent = 'Spotymc/%s (XBMC/%s)' % (__addon_version__, xbmc_build)
        
        return self.__user_agent
    
    
    def _get_play_token(self):
        if self.__play_token is None:
            address = 'localhost:%s' % self.__server_port
            user_agent = self._get_user_agent()
            self.__play_token = spotifyproxy.httpproxy.get_my_token(address, user_agent)
        
        return self.__play_token
    
    
    def _play_item(self, offset):
        xbmc.executebuiltin('playlist.playoffset(music,%d)' % offset)
    
    
    def clear(self):
        pass
    
    
    def _get_track_id(self, track):
        track_link = link.create_from_track(track)
        return track_link.as_string()[14:]
    
    
    def _get_url_headers(self):
        if self.__url_headers is None:
            str_agent = self._get_user_agent()
            str_token = self._get_play_token()
            header_dict = {'User-Agent': str_agent, 'X-Spotify-Token': str_token}
            self.__url_headers = urllib.urlencode(header_dict)
        
        return self.__url_headers
    
    
    def get_track_url(self, track):
        track_id = self._get_track_id(track)
        headers = self._get_url_headers()
        args = (self.__server_port, track_id, headers)
        return 'http://localhost:%s/track/%s.wav|%s' % args
    
    
    def get_image_url(self, image_id):
        return 'http://localhost:%s/image/%s.jpg' % (self.__server_port, image_id)
    
    
    def _calculate_track_rating(self, track):
        popularity = track.popularity()
        if popularity == 0:
            return 0
        else:
            return int(math.ceil(popularity * 6 / 100.0)) - 1
        
    
    def create_track_info(self, track, session, list_index = None):
        album = track.album().name()
        artist = ','.join([artist.name() for artist in track.artists()])
        image_id = track.album().cover()
        image_url = self.get_image_url(image_id)
        track_url = self.get_track_url(track)
        rating_points = str(self._calculate_track_rating(track))
        
        item = xbmcgui.ListItem(path=track_url, iconImage=image_url, thumbnailImage=image_url)
        info = {
            "title": track.name(),
            "album": album,
            "artist": artist,
            "duration": track.duration() / 1000,
            "tracknumber": track.index(),
            "rating": rating_points,
        }
        item.setInfo("music", info)
        
        if list_index is not None:
            item.setProperty('ListIndex', str(list_index))
        
        if track.is_starred(session):
            item.setProperty('IsStarred', 'true')
        else:
            item.setProperty('IsStarred', 'false')
        
        #Rating points, again as a property for the custom stars
        item.setProperty('RatingPoints', rating_points)
        
        return track_url, item
    
    
    def _stop_playback(self):
        if xbmc.getCondVisibility('Player.Playing'):
            #Don't ask me why, but these ones help a lot
            xbmc.executebuiltin('playercontrol(stop)')
            time.sleep(0.7)
    
    
    def play(self, track_list, session, offset=0):
        self._stop_playback()
        
        playlist = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
        playlist.clear()
        self.__track_list = []
        
        #And iterate over the give track list
        for list_index, track in enumerate(track_list):
            self.__track_list.append(track)
            path, info = self.create_track_info(track, session, list_index)
            playlist.add(path, info)
        
        print 'before _play_item'
        self._play_item(offset)
    
    
    def get_item(self, index):
        return self.__track_list.append[index]
