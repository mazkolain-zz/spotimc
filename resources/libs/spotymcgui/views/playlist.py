'''
Created on 22/08/2011

@author: mikel
'''
import xbmc, xbmcgui
from spotymcgui.views import BaseView

from spotify import playlist, playlistcontainer, link, BulkConditionChecker

from spotify.utils.iterators import CallbackIterator

import weakref



class PlaylistCallbacks(playlist.PlaylistCallbacks):
    __loader = None
    
    
    def __init__(self, loader):
        self.__loader = weakref.proxy(loader)
    
    
    def playlist_state_changed(self, playlist):
        print "playlist state changed"
        self.__loader.check()



class ContainerCallbacks(playlistcontainer.PlaylistContainerCallbacks):
    __loader = None
    
    
    def __init__(self, loader):
        self.__loader = weakref.proxy(loader)
    
    
    def playlist_added(self, container, playlist, position):
        print "playlist added (%d)" % position
        self.__loader.add_playlist(playlist, position)
    
    
    def container_loaded(self, container):
        print "container loaded"
        self.__loader.check()
    
    
    def playlist_removed(self, container, playlist, position):
        self.__loader.remove_playlist(position)



class ContainerLoader:
    __container = None
    __playlists = None
    __checker = None
    __initial_load = None
    __session = None
    
    
    def __init__(self, session, container):
        self.__session = session
        self.__container = container
        self.__playlists = {}
        self.__checker = BulkConditionChecker()
        self.__initial_load= True
        container.add_callbacks(ContainerCallbacks(self))
        self.__checker.add_condition(container.is_loaded)
    
    
    def add_playlist(self, playlist, position):
        if not playlist.is_loaded():
            self.__checker.add_condition(playlist.is_loaded)
        
        if not playlist.is_in_ram(self.__session):
            playlist.set_in_ram(self.__session, True)
        
        cb = PlaylistCallbacks(self)
        playlist.add_callbacks(cb)
        self.__playlists[position] = playlist
    
    
    def remove_playlist(self, position):
        del self.__playlists[position]
    
    
    def _check_playlists(self):
        """
        Ensure that all playlists have been loaded.
        Just if the container callbacks are registered too late
        and we missed some of them.
        """
        out = True
        
        for idx, item in enumerate(self.__container.playlists()):
            if idx not in self.__playlists:
                self.add_playlist(item, idx)
                out = False
        
        return out
    
    
    def is_loaded(self):
        return self.__checker.check_conditions() and self._check_playlists()
    
    
    def check(self):
        if self.is_loaded():
            xbmc.executebuiltin("Action(Noop)")
    
    
    def playlist(self, index):
        return self.__playlists[index]
    
    
    def num_playlists(self):
        return len(self.__playlists)
    
    
    def playlists(self):
        return CallbackIterator(self.num_playlists, self.playlist)



class PlaylistView(BaseView):
    __group_id = 1700
    __list_id = 1701
    
    __loader = None
    
    
    def __init__(self, session, container):
        self.__loader = ContainerLoader(session, container)
    
    
    def click(self, view_manager, window, control_id):
        pass
    
    
    def _get_list(self, window):
        return window.getControl(PlaylistView.__list_id)
    
    
    def _get_playlist_duration(self, playlist):
        sum = 0
        
        for item in playlist.tracks():
            sum += item.duration()
        
        return sum
    
    
    def _get_thumbnails(self, playlist):
        thumbnails = []
        
        for item in playlist.tracks():
            if len(thumbnails) == 4:
                return thumbnails
            
            else:
                album = item.album()
                cover = 'http://localhost:8080/image/%s.jpg' % album.cover()
                if cover not in thumbnails:
                    thumbnails.append(cover)
        
        return thumbnails
    
    
    def _add_playlist(self, playlist, window):
        item = xbmcgui.ListItem()
        item.setProperty("PlaylistName", playlist.name())
        item.setProperty("PlaylistNumTracks", str(playlist.num_tracks()))
        item.setProperty("PlaylistDuration", str(self._get_playlist_duration(playlist)))
        thumbnails = self._get_thumbnails(playlist)
        
        if len(thumbnails) > 0:
            #Set cover info
            if len(thumbnails) < 4:
                item.setProperty("CoverLayout", "one")
            else:
                item.setProperty("CoverLayout", "four")
            
            #Now loop to set all the images
            for idx, thumb_item in enumerate(thumbnails):
                print "adding thumb item: %s" % thumb_item
                item.setProperty("CoverItem%d" % (idx + 1), thumb_item)
        
        list = self._get_list(window)
        list.addItem(item)
    
    
    def _draw_list(self, window):
        if self.__loader.is_loaded():
            #Hide the whole group first
            group = window.getControl(PlaylistView.__group_id)
            group.setVisibleCondition("false")
            
            #Clear the list
            l = self._get_list(window)
            l.reset()
            
            for item in self.__loader.playlists():
                self._add_playlist(item, window)
            
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
