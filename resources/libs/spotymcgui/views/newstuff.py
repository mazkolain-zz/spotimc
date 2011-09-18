'''
Created on 05/08/2011

@author: mikel
'''
import xbmc
import xbmcgui
from spotymcgui.views import BaseView

from spotify import search



class NewStuffCallbacks(search.SearchCallbacks):
    __window = None
    __view = None
    
    
    def __init__(self, window, view):
        self.__window = window
        self.__view = view
    
    
    def search_complete(self, result):
        self.__view.populate_list(self.__window, result)



class NewStuffView(BaseView):
    __group_id = 1200
    __list_id = 1201
    
    __view_manager = None
    __session = None
    
    
    def __init__(self, view_manager, session):
        self.__view_manager = view_manager
        self.__session = session
    
    
    def click(self, view_manager, window, control_id):
        pass
    
    
    def _get_list(self, window):
        return window.getControl(NewStuffView.__list_id)
    
    
    def populate_list(self, window, result):
        l = self._get_list(window)
        l.reset()
        
        #xbmc.log('result loadad: %d' % result.is_loaded())
        xbmc.log("num results: %d, %d" % (result.num_albums(), result.total_albums()))
        
        
        for album in result.albums():
            l.addItem(xbmcgui.ListItem(album.name(), album.artist().name(), 'http://localhost:8080/image/%s.jpg' % album.cover()))
        
    
    def show(self, window):
        #Start a new search
        cb = NewStuffCallbacks(window, self)
        search.Search(self.__session, 'tag:new', album_count=60, callbacks=cb)
        
        c = window.getControl(NewStuffView.__group_id)
        c.setVisibleCondition("true")
        print "show!"
    
    
    def hide(self, window):
        c = window.getControl(NewStuffView.__group_id)
        c.setVisibleCondition("false")
        print "hide!"
