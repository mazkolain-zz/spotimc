'''
Created on 27/10/2011

@author: mikel
'''
import xbmcgui

from spotymcgui.views import BaseView

import loaders

import detail



class PlaylistView(BaseView):
    __group_id = 1700
    __list_id = 1701
    
    __loader = None
    
    __list_position = None
    
    
    def __init__(self, session, container):
        self.__loader = loaders.ContainerLoader(session, container)
    
    
    def click(self, view_manager, control_id):
        if control_id == PlaylistView.__list_id:
            item = self._get_list(view_manager).getSelectedItem()
            session = view_manager.get_var('session')
            playlist = self.__loader.playlist(int(item.getProperty('PlaylistId')))
            v = detail.PlaylistDetailView(session, playlist.get_playlist())
            view_manager.add_view(v)
    
    
    def _get_list(self, view_manager):
        return view_manager.get_window().getControl(PlaylistView.__list_id)
    
    
    def _add_playlist(self, list, key, loader, show_owner):
        item = xbmcgui.ListItem()
        item.setProperty("PlaylistId", str(key))
        item.setProperty("PlaylistName", loader.get_name())
        item.setProperty("PlaylistNumTracks", str(loader.get_num_tracks()))
        
        if show_owner:
            owner_name = loader.get_playlist().owner().canonical_name()
            item.setProperty("PlaylistShowOwner", "True")
            item.setProperty("PlaylistOwner", str(owner_name))
        else:
            item.setProperty("PlaylistShowOwner", "False")
        
        
        #Collaborative status
        if loader.get_is_collaborative():
            item.setProperty("PlaylistCollaborative", "True")
        else:
            item.setProperty("PlaylistCollaborative", "False")
        
        thumbnails = loader.get_thumbnails()
        
        if len(thumbnails) > 0:
            #Set cover info
            if len(thumbnails) < 4:
                item.setProperty("CoverLayout", "one")
            else:
                item.setProperty("CoverLayout", "four")
            
            #Now loop to set all the images
            for idx, thumb_item in enumerate(thumbnails):
                item.setProperty("CoverItem%d" % (idx + 1), thumb_item)
        
        list.addItem(item)
    
    
    def _draw_list(self, view_manager):
        window = view_manager.get_window()
        
        #Show loading animation
        window.show_loading()
        
        if self.__loader.is_loaded():
            self._save_list_position(view_manager)
            
            #Hide the whole group first
            group = window.getControl(PlaylistView.__group_id)
            group.setVisibleCondition("false")
            
            #Clear the list
            list = self._get_list(view_manager)
            list.reset()
            
            #Get the logged in user
            container_user = self.__loader.get_container().owner()
            container_username = None
            if container_user is not None:
                container_username = container_user.canonical_name()
            
            for key, item in enumerate(self.__loader.playlists()):
                playlist_username = item.get_playlist().owner().canonical_name()
                show_owner = playlist_username != container_username
                self._add_playlist(list, key, item, show_owner)
            
            #If we have the list index at hand...
            self._restore_list_position(view_manager)
            
            #Hide loading anim
            window.hide_loading()
            
            #Show the group again
            group.setVisibleCondition("true")
            
            #Focus the group
            window.setFocusId(PlaylistView.__group_id)
    
    
    def show(self, view_manager):
        self._draw_list(view_manager)
    
    
    def update(self, view_manager):
        self._draw_list(view_manager)
    
    
    def _save_list_position(self, view_manager):
        list = self._get_list(view_manager)
        self.__list_position = list.getSelectedPosition()
    
    
    def _restore_list_position(self, view_manager):
        #If we have the list index at hand...
        if self.__list_position is not None:
            list = self._get_list(view_manager)
            list.selectItem(self.__list_position)
    
    
    def hide(self, view_manager):
        window = view_manager.get_window()
        
        #Keep the list position
        self._save_list_position(view_manager)
        
        c = window.getControl(PlaylistView.__group_id)
        c.setVisibleCondition("false")
