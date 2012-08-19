'''
Copyright 2011 Mikel Azkolain

This file is part of Spotimc.

Spotimc is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Spotimc is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Spotimc.  If not, see <http://www.gnu.org/licenses/>.
'''


import xbmc, xbmcgui
from spotify import link, track
import time
from __main__ import __addon_version__
import spotifyproxy
import math
import random
import settings
from spotify.utils.decorators import run_in_thread


#TODO: urllib 3.x compatibility
import urllib
        



class PlaylistManager:
    __server_port = None
    __user_agent = None
    __play_token = None
    __url_headers = None
    __track_list = None
    __playlist = None
    __cancel_set_tracks = None
    
    
    def __init__(self, server):
        self.__track_list = []
        self.__server_port = server.get_port()
        self.__play_token = server.get_user_token(self._get_user_agent())
        self.__playlist = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
    
    
    def _get_user_agent(self):
        if self.__user_agent is None:
            xbmc_build = xbmc.getInfoLabel("System.BuildVersion")
            self.__user_agent = 'Spotimc/%s (XBMC/%s)' % (__addon_version__, xbmc_build)
        
        return self.__user_agent
    
    
    def _get_play_token(self):
        return self.__play_token
    
    
    def _play_item(self, offset):
        player = xbmc.Player()
        player.playselected(offset)
    
    
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
    
    
    def get_track_url(self, track, list_index = None):
        track_id = self._get_track_id(track)
        headers = self._get_url_headers()
        
        if list_index is not None:
            args = (self.__server_port, track_id, list_index, headers)
            return 'http://127.0.0.1:%s/track/%s.wav?idx=%d|%s' % args
        else:
            args = (self.__server_port, track_id, headers)
            return 'http://127.0.0.1:%s/track/%s.wav|%s' % args
    
    
    def get_image_url(self, image_id):
        return 'http://127.0.0.1:%s/image/%s.jpg' % (self.__server_port, image_id)
    
    
    def _calculate_track_rating(self, track):
        popularity = track.popularity()
        if popularity == 0:
            return 0
        else:
            return int(math.ceil(popularity * 6 / 100.0)) - 1
        
    
    def create_track_info(self, track_obj, session, list_index = None):
        #Track is ok
        if track_obj.is_loaded() and track_obj.error() == 0:
            album = track_obj.album().name()
            artist = ', '.join([artist.name() for artist in track_obj.artists()])
            image_id = track_obj.album().cover()
            image_url = self.get_image_url(image_id)
            track_url = self.get_track_url(track_obj, list_index)
            rating_points = str(self._calculate_track_rating(track_obj))
            
            item = xbmcgui.ListItem(path=track_url, iconImage=image_url, thumbnailImage=image_url)
            info = {
                "title": track_obj.name(),
                "album": album,
                "artist": artist,
                "duration": track_obj.duration() / 1000,
                "tracknumber": track_obj.index(),
                "rating": rating_points,
            }
            item.setInfo("music", info)
            
            if list_index is not None:
                item.setProperty('ListIndex', str(list_index))
            
            if track_obj.is_starred(session):
                item.setProperty('IsStarred', 'true')
            else:
                item.setProperty('IsStarred', 'false')
            
            if track_obj.get_availability(session) == track.TrackAvailability.Available:
                item.setProperty('IsAvailable', 'true')
            else:
                item.setProperty('IsAvailable', 'false')
            
            #Rating points, again as a property for the custom stars
            item.setProperty('RatingPoints', rating_points)
            
            return track_url, item
        
        #Track has errors
        else:
            return '', xbmcgui.ListItem()
    
    
    def _stop_playback(self):
        player = xbmc.Player()
        player.stop()
    
    
    def _add_item(self, index, track, session):
        self.__track_list.insert(index, track)
        path, info = self.create_track_info(track, session, index)
        self.__playlist.add(path, info, index)
    
    
    def is_playing(self, consider_pause=True):
        if consider_pause:
            return xbmc.getCondVisibility('Player.Playing | Player.Paused')
        else:
            return xbmc.getCondVisibility('Player.Playing')
    
    
    def get_shuffle_status(self):
        #Get it directly from a boolean tag (if possible)
        if self.is_playing() and len(self.__playlist) > 0:
            return xbmc.getCondVisibility('Playlist.IsRandom')
    
        #Otherwise read it from guisettings.xml
        else:
            try:
                reader = settings.GuiSettingsReader()
                value = reader.get_setting('settings.mymusic.playlist.shuffle')
                return value == 'true'
            
            except:
                xbmc.log(
                    'Failed reading shuffle setting.',
                    xbmc.LOGERROR
                )
                return false
    
    
    @run_in_thread(single_instance=True)
    def _set_tracks(self, track_list, session, omit_offset):
        #Reset the cancel flag
        self.__cancel_set_tracks = False
        
        #Clear playlist if no offset is given to omit
        if omit_offset is None:
            self.__playlist.clear()
            self.__track_list = []
        
        #Iterate over the rest of the playlist
        for list_index, track in enumerate(track_list):
            #If a cancel was requested
            if self.__cancel_set_tracks:
                return
            
            #Ignore the item at offset, which is already added
            if list_index != omit_offset:
                self._add_item(list_index, track, session)
            
            #Deal with any potential dummy items
            if omit_offset is not None and list_index < omit_offset:
                self.__playlist.remove('dummy-%d' % list_index)
            
        #Set paylist's shuffle status
        if self.get_shuffle_status():
            self.__playlist.shuffle()
    
    
    def set_tracks(self, track_list, session, omit_offset=None):
        self.__cancel_set_tracks = True
        self._set_tracks(track_list, session, omit_offset)
    
    
    def play(self, track_list, session, offset=None):
        if len(track_list) > 0:
            #Cancel any possible set_tracks() loop
            self.__cancel_set_tracks = True
            
            #Get shuffle status
            is_shuffle = self.get_shuffle_status()
            
            #Clear the old contents
            self.__playlist.clear()
            self.__track_list = []
            
            #If we don't have an offset, get one
            if offset is None:
                if is_shuffle:
                    offset = random.randint(0, len(track_list) - 1)
                else:
                    offset = 0
            
            #Add some padding dummy items (to preserve playlist position)
            if offset > 0:
                for index in range(offset):
                    self.__playlist.add('dummy-%d' % index, xbmcgui.ListItem(''))
            
            #Add the desired item and play it
            self._add_item(offset, track_list[offset], session)
            self._play_item(offset)
            
            #If there are items left...
            if len(track_list) > 1:
                self.set_tracks(track_list, session, offset)
    
    
    def get_item(self, index):
        return self.__track_list[index]
    
    
    def get_current_item(self):
        playlist = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
        return self.get_item(playlist.getposition())
    
    
    def get_next_item(self):
        playlist = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
        next_index = playlist.getposition() + 1
        if next_index < len(playlist):
            return self.get_item(next_index)
    
    
    def __del__(self):
        #Cancel the set_tracks() loop at exit
        self.__cancel_set_tracks = True
