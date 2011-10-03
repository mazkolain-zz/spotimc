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
        c = self.__window.getControl(AlbumTracksView.group_id)
        c.setVisibleCondition("true")
        self.__window.setFocusId(AlbumTracksView.group_id)



class AlbumTracksView(BaseView):
    group_id = 1300
    list_id = 1303
    
    __session = None
    __albumbrowse = None
    
    
    def __init__(self, session, album):
        self.__session = session
        self.__album = album
    
    
    def _play_selected_track(self, view_manager, window):
        #print 'inside play_selected track'
        #pos = self._get_list(window).getSelectedPosition()
        item = self._get_list(window).getSelectedItem()
        pos = item.getProperty("real_index")
        
        #If we have a valid index
        if pos is not None:
            track_item = self.__albumbrowse.track(int(pos))
            playlist_manager = view_manager.get_var('playlist_manager')
            playlist_manager.play(track_item)
    
    
    def click(self, view_manager, window, control_id):
        if control_id == AlbumTracksView.list_id:
            self._play_selected_track(view_manager, window)
    
    
    def _get_list(self, window):
        return window.getControl(AlbumTracksView.list_id)
    
    
    def _have_multiple_discs(self, track_list):
        for item in track_list:
            if item.disc() > 1:
                return True
        
        return False
    
    
    def _set_album_info(self, window, album, artist):
        window.setProperty("AlbumCover", "http://localhost:8080/image/%s.jpg" % album.cover())
        window.setProperty("AlbumName", album.name())
        window.setProperty("ArtistName", artist.name())
    
    
    def _add_disc_separator(self, list, disc_number):
        item = xbmcgui.ListItem()
        item.setProperty("IsDiscSeparator", "true")
        item.setProperty("DiscNumber", str(disc_number))
        list.addItem(item)
    
    def _add_track(self, list, track, real_index):
        track_link = link.create_from_track(track)
        track_id = track_link.as_string()[14:]
        track_url = "http://localhost:8080/track/%s.wav" % track_id
        
        item = xbmcgui.ListItem(path=track_url)
        info = {
            "title": track.name(),
            "duration": track.duration() / 1000,
            "tracknumber": track.index(),
        }
        
        item.setProperty("real_index", str(real_index))
        item.setInfo('music', info)
        list.addItem(item)
    
    
    def populate_list(self, window, albumbrowse):
        list = self._get_list(window)
        list.reset()
        
        #Set album info
        self._set_album_info(window, albumbrowse.album(), albumbrowse.artist())
        
        #For disc grouping
        multiple_discs = self._have_multiple_discs(albumbrowse.tracks())
        last_disc = None
        
        for idx, item in enumerate(albumbrowse.tracks()):
            #If disc was changed add a separator
            if multiple_discs and last_disc != item.disc():
                last_disc = item.disc()
                self._add_disc_separator(list, last_disc)
            
            self._add_track(list, item, idx)
        
    
    def show(self, window):
        if self.__albumbrowse is None:
            cb = AlbumCallbacks(window, self)
            self.__albumbrowse = albumbrowse.Albumbrowse(self.__session, self.__album, cb)
    
    
    def hide(self, window):
        c = window.getControl(AlbumTracksView.group_id)
        c.setVisibleCondition("false")
