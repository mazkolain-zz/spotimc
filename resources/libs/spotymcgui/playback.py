'''
Created on 23/09/2011

@author: mikel
'''
import xbmc, xbmcgui
from spotify import link



class PlaylistManager:
    __primary_queue = None
    __secondary_queue = None
    __server_info = None
    
    
    def __init__(self, server_info):
        self.__primary_queue = []
        self.__secondary_queue = []
        self.__server_info = server_info
    
    
    def _play_first_item(self):
        xbmc.executebuiltin('Playlist.PlayOffset(music,0)')
    
    
    def _rebuild_playlist(self):
        pl = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
        pl.clear()
        
        for item in self.__secondary_queue:
            path, info = self._prepare_track(item)
            pl.add(path, info)
    
    
    def clear(self):
        pass
    
    
    def _get_track_id(self, track):
        track_link = link.create_from_track(track)
        return track_link.as_string()[14:]
    
    
    def _prepare_track(self, track):
        #Get the track url first
        track_id = self._get_track_id(track)
        track_url = "http://localhost:8080/track/%s.wav" % track_id
        
        #And generate a listitem with track metadata
        item = xbmcgui.ListItem(path=track_url)
        info = {
            "title": track.name(),
            "duration": track.duration() / 1000,
            "tracknumber": track.index()
        }
        item.setInfo("music", info)
        
        return track_url, item
    
    
    def play(self, track, additional_tracks=None):
        self.__secondary_queue = [track]
        track_id = self._get_track_id(track)
        
        #Add the additional tracks except the one matching track param
        if additional_tracks is not None:
            for item in additional_tracks:
                if self._get_track_id(item) != track_id:
                    self.__secondary_queue.append(item)
        
        self._rebuild_playlist()
        self._play_first_item()
