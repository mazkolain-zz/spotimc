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


#TODO: urllib 3.x compatibility
import urllib



class PlaylistManager:
    __server_port = None
    __user_agent = None
    __play_token = None
    __url_headers = None
    __track_list = None
    __track_queue = None
    
    
    def __init__(self, server):
        self.__track_list = []
        self.__track_queue = {}
        self.__server_port = server.get_port()
        self.__play_token = server.get_user_token(self._get_user_agent())
    
    
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
        self.__track_list = []
        self.__track_queue.clear()
        xbmc.PlayList(xbmc.PLAYLIST_MUSIC).clear()
    
    
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
            return 'http://127.0.0.1:%s/track/%s.wav?idx=%s|%s' % args
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
    
    
    def _remove_queued_item(self, path_to_remove, session):
        for index, item in self.__track_queue.items():
            queue_index = 'q' + str(index)
            path, info = self.create_track_info(item, session, queue_index)
            if path == path_to_remove:
                del self.__track_queue[index]
                return True
        
        return False
    
    
    def _get_next_queue_position(self):
        if len(self.__track_queue):
            return sorted(self.__track_queue.keys())[-1] + 1
        else:
            return 0
    
    
    def _purge_queued_items(self, session):
        playlist = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
        
        for idx in range(0, playlist.getposition() + 1):
            self._remove_queued_item(playlist[idx].getfilename(), session)
    
    
    def _add_playlist_item(self, track, session, list_index, offset=None):
        path, info = self.create_track_info(track, session, list_index)
        
        if offset is None:
            xbmc.PlayList(xbmc.PLAYLIST_MUSIC).add(path, info)
        else:
            xbmc.PlayList(xbmc.PLAYLIST_MUSIC).add(path, info, offset)
    
    
    def get_queued_tracks(self):
        tracks = self.__track_queue
        return [tracks[index] for index in sorted(tracks.keys())]
    
    
    def _enqueue(self, track_list, session):
        #Purge past items first
        self._purge_queued_items(session)
        
        playlist = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
        
        #And add the requested items to the queue
        for track in track_list:
            queue_index = self._get_next_queue_position()
            str_index = 'q' + str(queue_index)
            offset = playlist.getposition() + len(self.__track_queue) + 1
            self._add_playlist_item(track, session, str_index, offset)
            self.__track_queue[queue_index] = track
    
    
    def play(self, track_list, session, offset=0):
        #Purge past queued items first
        self._purge_queued_items(session)
        
        #Keep a copy of the queued tracks
        track_queue = self.get_queued_tracks()
        
        #Stop playback and clear the list
        self._stop_playback()
        self.clear()
        
        #Add every track to the XBMC playlist
        for list_index, track in enumerate(track_list):
            self._add_playlist_item(track, session, list_index)
            self.__track_list.append(track)
        
        #Start playback of current item
        self._play_item(offset)
        
        #Re-add pending queued items
        self._enqueue(track_queue, session)
    
    
    def enqueue(self, track_list, session):
        #Do the real queuing
        self._enqueue(track_list, session)
        
        #Now show the notifications
        if len(track_list) > 1:
            msg = "%d tracks added to queue." % len(track_list)
            xbmc.executebuiltin("Notification(Queue updated, %s)" % msg)
        
        else:
            msg = "Track added into position #%d" % len(self.__track_queue)
            xbmc.executebuiltin("Notification(Queue updated, %s)" % msg)
    
    
    def get_item(self, index):
        str_index = str(index)
        
        #Check if belongs to the queue
        if str_index.startswith('q'):
            return self.__track_queue[int(str_index[1:])]
        
        #Otherwise it's on the regular list
        else:
            return self.__track_list[int(index)]
