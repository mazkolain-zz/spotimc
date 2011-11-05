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
    
    
    def __init__(self, session, container):
        self.__loader = loaders.ContainerLoader(session, container)
    
    
    def click(self, view_manager, window, control_id):
        if control_id == PlaylistView.__list_id:
            item = self._get_list(window).getSelectedItem()
            session = view_manager.get_var('session')
            playlist = self.__loader.playlist(int(item.getProperty('PlaylistId')))
            v = detail.PlaylistDetailView(session, playlist.get_playlist())
            view_manager.add_view(v)
    
    
    def _get_list(self, window):
        return window.getControl(PlaylistView.__list_id)
    
    
    def _add_playlist(self, key, playlist, window):
        item = xbmcgui.ListItem()
        item.setProperty("PlaylistId", str(key))
        item.setProperty("PlaylistName", playlist.get_name())
        item.setProperty("PlaylistNumTracks", str(playlist.get_num_tracks()))
        
        #Collaborative status
        if playlist.get_is_collaborative():
            item.setProperty("PlaylistCollaborative", "True")
        else:
            item.setProperty("PlaylistCollaborative", "False")
        
        thumbnails = playlist.get_thumbnails()
        
        if len(thumbnails) > 0:
            #Set cover info
            if len(thumbnails) < 4:
                item.setProperty("CoverLayout", "one")
            else:
                item.setProperty("CoverLayout", "four")
            
            #Now loop to set all the images
            for idx, thumb_item in enumerate(thumbnails):
                item.setProperty("CoverItem%d" % (idx + 1), thumb_item)
        
        list = self._get_list(window)
        list.addItem(item)
    
    
    def _draw_list(self, window):
        #Show loading animation
        window.show_loading()
        
        if self.__loader.is_loaded():
            #Hide the whole group first
            group = window.getControl(PlaylistView.__group_id)
            group.setVisibleCondition("false")
            
            #Clear the list
            l = self._get_list(window)
            l.reset()
            
            for key, item in enumerate(self.__loader.playlists()):
                self._add_playlist(key, item, window)
            
            #Hide loading anim
            window.hide_loading()
            
            #Show the group again
            group.setVisibleCondition("true")
            
            #Focus the group
            window.setFocusId(PlaylistView.__group_id)
    
    
    def show(self, window):
        self._draw_list(window)
        print "show!"
    
    
    def update(self, window):
        self._draw_list(window)
    
    
    def hide(self, window):
        c = window.getControl(PlaylistView.__group_id)
        c.setVisibleCondition("false")
        print "hide!"
