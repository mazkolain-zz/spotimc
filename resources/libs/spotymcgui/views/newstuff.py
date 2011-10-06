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
    
    #To store the list's last position
    __list_position = None
    
    
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
        if self.__search.is_loaded():
            #Ensure that the group is hidden first
            group = window.getControl(NewStuffView.__group_id)
            group.setVisibleCondition("false")
            
            #Now start working on the list
            l = self._get_list(window)
            l.reset()
            
            for album in self.__search.albums():
                print album.cover()
                l.addItem(xbmcgui.ListItem(album.name(), album.artist().name(), 'http://localhost:8080/image/%s.jpg' % album.cover()))
            
            #If we have the list index at hand...
            if self.__list_position is not None:
                l.selectItem(self.__list_position)
            
            #Show the list again
            group = window.getControl(NewStuffView.__group_id)
            group.setVisibleCondition("true")
                
            #And give it focus
            window.setFocusId(NewStuffView.__group_id)
    
    
    def update(self, window):
        self._draw_list(window)
    
    
    def show(self, window):
        self._draw_list(window)
    
    
    def hide(self, window):
        #Keep the list position
        l = window.getControl(NewStuffView.__list_id)
        self.__list_position = l.getSelectedPosition()
        
        #And hide the group
        group = window.getControl(NewStuffView.__group_id)
        group.setVisibleCondition("false")
