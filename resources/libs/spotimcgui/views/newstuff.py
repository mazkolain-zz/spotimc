'''
Created on 05/08/2011

@author: mikel
'''
import xbmc, xbmcgui
from spotimcgui.views import BaseListContainerView
from spotimcgui.views import album

from spotify import search


class NewStuffCallbacks(search.SearchCallbacks):
    def search_complete(self, result):
        xbmc.executebuiltin("Action(Noop)")



class NewStuffView(BaseListContainerView):
    container_id = 1200
    list_id = 1201
    
    __session = None
    __search = None
    
    
    def __init__(self, session):
        self.__session = session
        cb = NewStuffCallbacks()
        self.__search = search.Search(
            self.__session, 'tag:new', album_count=60, callbacks=cb
        )
        
    
    def _show_album(self, view_manager):
        pos = self.get_list(view_manager).getSelectedPosition()
        v = album.AlbumTracksView(self.__session, self.__search.album(pos))
        view_manager.add_view(v)
    
    
    def click(self, view_manager, control_id):
        #If the list was clicked...
        if control_id == NewStuffView.list_id:
            self._show_album(view_manager)
    
    
    def get_container(self, view_manager):
        return view_manager.get_window().getControl(NewStuffView.container_id)
    
    
    def get_list(self, view_manager):
        return view_manager.get_window().getControl(NewStuffView.list_id)
    
    
    def render(self, view_manager):
        if self.__search.is_loaded():
            list_obj = self.get_list(view_manager)
            list_obj.reset()
            playlist_manager = view_manager.get_var('playlist_manager')
            
            for album in self.__search.albums():
                item = xbmcgui.ListItem(
                    album.name(),
                    album.artist().name(),
                    playlist_manager.get_image_url(album.cover())
                )
                list_obj.addItem(item)
            
            return True
