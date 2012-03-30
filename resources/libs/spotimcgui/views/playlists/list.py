'''
Copyright 2011 Mikel Azkolain

This file is part of Spotimc.

Spotimc is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Spotimc is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Spotimc.  If not, see <http://www.gnu.org/licenses/>.
'''


import xbmcgui

from spotimcgui.views import BaseListContainerView, iif

import loaders

import detail



class PlaylistView(BaseListContainerView):
    container_id = 1700
    list_id = 1701
    
    __starred_loader = None
    __inbox_loader = None
    __container_loader = None
    
    
    def __init__(self, session, container, playlist_manager):
        #Add the starred playlist
        self.__starred_loader = loaders.SpecialPlaylistLoader(
            session, session.starred_create(), playlist_manager,
            'Starred', ["common/pl-starred.png"]
        )
        
        #And the inbox one
        self.__inbox_loader = loaders.SpecialPlaylistLoader(
            session, session.inbox_create(), playlist_manager,
            'Inbox', ['common/pl-inbox.png']
        )
        
        #And the rest of the playlists
        self.__container_loader = loaders.ContainerLoader(
            session, container, playlist_manager
        )
    
    
    def click(self, view_manager, control_id):
        if control_id == PlaylistView.list_id:
            item = self.get_list(view_manager).getSelectedItem()
            playlist_id = item.getProperty('PlaylistId')
            session = view_manager.get_var('session')
            pm = view_manager.get_var('playlist_manager')
            
            if playlist_id == 'starred':
                loader_obj = self.__starred_loader
                view_obj = detail.SpecialPlaylistDetailView(
                    session, loader_obj.get_playlist(), pm,
                    loader_obj.get_name(), loader_obj.get_thumbnails()
                )
            
            elif playlist_id == 'inbox':
                loader_obj = self.__inbox_loader
                view_obj = detail.SpecialPlaylistDetailView(
                    session, loader_obj.get_playlist(), pm,
                    loader_obj.get_name(), loader_obj.get_thumbnails()
                )
            
            else:
                loader_obj = self.__container_loader.playlist(int(playlist_id))
                view_obj = detail.PlaylistDetailView(
                    session, loader_obj.get_playlist(), pm
                )
            
            view_manager.add_view(view_obj)
    
    
    def get_container(self, view_manager):
        return view_manager.get_window().getControl(PlaylistView.container_id)
    
    
    def get_list(self, view_manager):
        return view_manager.get_window().getControl(PlaylistView.list_id)
    
    
    def _add_playlist(self, list, key, loader, show_owner):
        item = xbmcgui.ListItem()
        item.setProperty("PlaylistId", str(key))
        item.setProperty("PlaylistName", loader.get_name())
        item.setProperty("PlaylistNumTracks", str(loader.get_num_tracks()))
        
        item.setProperty("PlaylistShowOwner", iif(show_owner, "true", "false"))
        if show_owner:
            owner_name = loader.get_playlist().owner().canonical_name()
            item.setProperty("PlaylistOwner", str(owner_name))
        
        #Collaborative status
        is_collaborative = loader.get_is_collaborative()
        item.setProperty("PlaylistCollaborative", iif(is_collaborative, "true", "false"))
        
        #Thumbnails
        thumbnails = loader.get_thumbnails()
        if len(thumbnails) > 0:
            #Set cover info
            item.setProperty("CoverLayout", iif(len(thumbnails) < 4, "one", "four"))
            
            #Now loop to set all the images
            for idx, thumb_item in enumerate(thumbnails):
                item_num = idx + 1
                is_remote = thumb_item.startswith("http://")
                item.setProperty("CoverItem%d" % item_num, thumb_item)
                item.setProperty("CoverItem%dIsRemote" % item_num, iif(is_remote, "true", "false"))
        
        list.addItem(item)
    
    
    def all_loaded(self):
        return (
            (self.__starred_loader.is_loaded() or self.__starred_loader.has_errors()) and
            (self.__inbox_loader.is_loaded() or self.__inbox_loader.has_errors()) and
            self.__container_loader.is_loaded()
        )
    
    
    def render(self, view_manager):
        if self.all_loaded():
            #Clear the list
            list = self.get_list(view_manager)
            list.reset()
            
            #Get the logged in user
            container_user = self.__container_loader.get_container().owner()
            container_username = None
            if container_user is not None:
                container_username = container_user.canonical_name()
            
            #Add the starred and inbox playlists
            self._add_playlist(list, 'starred', self.__starred_loader, False)
            self._add_playlist(list, 'inbox', self.__inbox_loader, False)
            
            #And iterate over the rest of the playlists
            for key, item in enumerate(self.__container_loader.playlists()):
                show_playlist = (
                    item is not None and
                    not item.has_errors() and
                    item.is_loaded()
                )
                
                if show_playlist:
                    playlist_username = item.get_playlist().owner().canonical_name()
                    show_owner = playlist_username != container_username
                    self._add_playlist(list, key, item, show_owner)
            
            return True
