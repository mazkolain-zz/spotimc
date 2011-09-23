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
    
    
    def _rebuild_playlist(self, track_list):
        pl = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
        pl.clear()
        
        for item in track_list:
            path, info = self._prepare_track(item)
            pl.add(path, info)
    
    
    def clear(self):
        pass
    
    
    def _prepare_track(self, track):
        #Get the track url first
        track_link = link.create_from_track(track)
        track_id = track_link.as_string()[14:]
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
        self._rebuild_playlist([track])
        self._play_first_item()
