'''
Created on 20/08/2011

@author: mikel
'''
import xbmcgui
from spotymcgui.views import BaseView

from spotify import albumbrowse, link

import weakref

import xbmc



class AlbumCallbacks(albumbrowse.AlbumbrowseCallbacks):
    __window = None
    __view = None
    
    
    def __init__(self, window, view):
        self.__window = window
        self.__view = weakref.proxy(view)
    
    
    def albumbrowse_complete(self, albumbrowse):
        self.__view.populate_list(self.__window, albumbrowse)



class AlbumTracksView(BaseView):
    __group_id = 1300
    __list_id = 1303
    
    __session = None
    __albumbrowse = None
    
    
    def __init__(self, session, album):
        self.__session = session
        self.__album = album
    
    
    def _play_selected_track(self, view_manager, window):
        #print 'inside play_selected track'
        pos = self._get_list(window).getSelectedPosition()
        track_item = self.__albumbrowse.track(pos)
        playlist_manager = view_manager.get_var('playlist_manager')
        playlist_manager.play(track_item)
    
    
    def click(self, view_manager, window, control_id):
        print "list clicked: id: %d" % control_id
        if control_id == AlbumTracksView.__list_id:
            print 'control id test ok'
            self._play_selected_track(view_manager, window)
    
    
    def _get_list(self, window):
        return window.getControl(AlbumTracksView.__list_id)
    
    
    def _add_track(self, list, title, item_path, duration, number):
        item = xbmcgui.ListItem(path=item_path)
        item.setInfo(
            "music",
            {"title": title, "duration": duration, "tracknumber": number}
        )
        list.addItem(item)
    
    
    def populate_list(self, window, albumbrowse):
        l = self._get_list(window)
        l.reset()
        
        for item in albumbrowse.tracks():
            track_link = link.create_from_track(item)
            track_id = track_link.as_string()[14:]
            track_url = "http://localhost:8080/track/%s.wav" % track_id
            self._add_track(
                l, item.name(), track_url, item.duration() / 1000, item.index()
            )
        
        album = albumbrowse.album()
        artist = albumbrowse.artist()
        
        window.setProperty("AlbumCover", "http://localhost:8080/image/%s.jpg" % album.cover())
        window.setProperty("AlbumName", album.name())
        window.setProperty("ArtistName", artist.name())
        
    
    def show(self, window):
        cb = AlbumCallbacks(window, self)
        self.__albumbrowse = albumbrowse.Albumbrowse(self.__session, self.__album, cb)
        c = window.getControl(AlbumTracksView.__group_id)
        c.setVisibleCondition("true")
    
    
    def hide(self, window):
        c = window.getControl(AlbumTracksView.__group_id)
        c.setVisibleCondition("false")
