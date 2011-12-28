'''
Created on 23/09/2011

@author: mikel
'''
import xbmc, xbmcgui
from spotify import link
import time


class PlaylistManager:
    __primary_queue = None
    __secondary_queue = None
    __server_info = None
    
    
    def __init__(self, server_info):
        self.__primary_queue = []
        self.__secondary_queue = []
        self.__server_info = server_info
    
    
    def _play_item(self, offset):
        xbmc.executebuiltin('playlist.playoffset(music,%d)' % offset)
    
    
    def _rebuild_playlist(self):
        pl = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
        pl.clear()
        
        for idx, item in enumerate(self.__secondary_queue):
            path, info = self._prepare_track(item, idx)
            pl.add(path, info)
    
    
    def clear(self):
        pass
    
    
    def _get_track_id(self, track):
        track_link = link.create_from_track(track)
        return track_link.as_string()[14:]
    
    
    def _prepare_track(self, track, index):
        #Get the track url first
        track_id = self._get_track_id(track)
        track_url = "http://localhost:8080/track/%s.wav" % track_id
        
        #And generate a listitem with track metadata
        album = track.album().name()
        cover = "http://localhost:8080/image/%s.jpg" % track.album().cover()
        artist = ','.join([artist.name() for artist in track.artists()])
        
        item = xbmcgui.ListItem(path=track_url, iconImage=cover, thumbnailImage=cover)
        info = {
            "title": track.name(),
            "album": album,
            "artist": artist,
            "duration": track.duration() / 1000,
            "tracknumber": track.index(),
        }
        item.setInfo("music", info)
        item.setProperty('real_index', str(index))
        
        return track_url, item
    
    
    def _stop_playback(self):
        if xbmc.getCondVisibility('Player.Playing'):
            #Don't ask me why, but these ones help a lot
            xbmc.executebuiltin('playercontrol(stop)')
            time.sleep(0.7)
    
    
    def play(self, track_list, offset=0):
        self._stop_playback()
        self.__secondary_queue = []
        
        for item in track_list:
            self.__secondary_queue.append(item)
        
        self._rebuild_playlist()
        self._play_item(offset)
    
    
    def get_item(self, index):
        return self.__secondary_queue[index]
