'''
Created on 05/08/2011

@author: mikel
'''
import xbmc
import xbmcgui
from spotymcgui.views import BaseView
from spotymcgui.views import album

from spotify import search

import weakref



class NewStuffCallbacks(search.SearchCallbacks):
    def search_complete(self, result):
        xbmc.executebuiltin("Action(Noop)")



class NewStuffView(BaseView):
    __group_id = 1200
    __list_id = 1201
    
    __session = None
    __search = None
    
    
    def __init__(self, session):
        self.__session = session
        cb = NewStuffCallbacks()
        self.__search = search.Search(
            self.__session, 'tag:new', album_count=60, callbacks=cb
        )
        
    
    def _show_album(self, view_manager, window):
        pos = self._get_list(window).getSelectedPosition()
        v = album.AlbumTracksView(self.__session, self.__search.album(pos))
        view_manager.add_view(v)
    
    
    def click(self, view_manager, window, control_id):
        #If the list was clicked...
        if control_id == NewStuffView.__list_id:
            self._show_album(view_manager, window)
    
    
    def _get_list(self, window):
        return window.getControl(NewStuffView.__list_id)
    
    
    def _draw_list(self, window):
        l = self._get_list(window)
        l.reset()
        
        for album in self.__search.albums():
            print album.cover()
            l.addItem(xbmcgui.ListItem(album.name(), album.artist().name(), 'http://localhost:8080/image/%s.jpg' % album.cover()))
        
        c = window.getControl(NewStuffView.__group_id)
        c.setVisibleCondition("true")
        window.setFocusId(NewStuffView.__group_id)
        
    
    def update(self, window):
        self._draw_list(window)
    
    
    def show(self, window):
        self._draw_list(window)
    
    
    def hide(self, window):
        c = window.getControl(NewStuffView.__group_id)
        c.setVisibleCondition("false")
