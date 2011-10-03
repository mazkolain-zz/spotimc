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
    __window = None
    __view = None
    
    
    def __init__(self, window, view):
        self.__window = window
        self.__view = weakref.proxy(view)
    
    
    def search_complete(self, result):
        self.__view.populate_list(self.__window, result)



class NewStuffView(BaseView):
    __group_id = 1200
    __list_id = 1201
    
    __session = None
    __search = None
    
    
    def __init__(self, session):
        self.__session = session
        
    
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
    
    
    def populate_list(self, window, result):
        l = self._get_list(window)
        l.reset()
        
        for album in result.albums():
            print album.cover()
            l.addItem(xbmcgui.ListItem(album.name(), album.artist().name(), 'http://localhost:8080/image/%s.jpg' % album.cover()))
        
        window.setFocusId(NewStuffView.__group_id)
        
    
    def show(self, window):
        #Start a new search
        cb = NewStuffCallbacks(window, self)
        self.__search = search.Search(self.__session, 'tag:new', album_count=60, callbacks=cb)
        c = window.getControl(NewStuffView.__group_id)
        c.setVisibleCondition("true")
    
    
    def hide(self, window):
        c = window.getControl(NewStuffView.__group_id)
        c.setVisibleCondition("false")
