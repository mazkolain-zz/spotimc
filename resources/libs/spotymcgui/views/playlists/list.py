'''
Created on 27/10/2011

@author: mikel
'''
import xbmcgui

from spotymcgui.views import BaseListContainerView

import loaders

import detail



class PlaylistView(BaseListContainerView):
    container_id = 1700
    list_id = 1701
    
    __loader = None
    
    
    def __init__(self, session, container):
        self.__loader = loaders.ContainerLoader(session, container)
    
    
    def click(self, view_manager, control_id):
        if control_id == PlaylistView.list_id:
            item = self.get_list(view_manager).getSelectedItem()
            session = view_manager.get_var('session')
            playlist = self.__loader.playlist(int(item.getProperty('PlaylistId')))
            v = detail.PlaylistDetailView(session, playlist.get_playlist())
            view_manager.add_view(v)
    
    
    def get_container(self, view_manager):
        return view_manager.get_window().getControl(PlaylistView.container_id)
    
    
    def get_list(self, view_manager):
        return view_manager.get_window().getControl(PlaylistView.list_id)
    
    
    def _add_playlist(self, list, key, loader, show_owner):
        item = xbmcgui.ListItem()
        item.setProperty("PlaylistId", str(key))
        item.setProperty("PlaylistName", loader.get_name())
        item.setProperty("PlaylistNumTracks", str(loader.get_num_tracks()))
        
        if show_owner:
            owner_name = loader.get_playlist().owner().canonical_name()
            item.setProperty("PlaylistShowOwner", "true")
            item.setProperty("PlaylistOwner", str(owner_name))
        else:
            item.setProperty("PlaylistShowOwner", "false")
        
        
        #Collaborative status
        if loader.get_is_collaborative():
            item.setProperty("PlaylistCollaborative", "true")
        else:
            item.setProperty("PlaylistCollaborative", "false")
        
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
    
    
    def render(self, view_manager):
        if self.__loader.is_loaded():
            #Clear the list
            list = self.get_list(view_manager)
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
            
            return True
