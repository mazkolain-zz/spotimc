'''
Created on 22/08/2011

@author: mikel
'''
import xbmc

from spotify import playlist, playlistcontainer, BulkConditionChecker

from spotify.utils.iterators import CallbackIterator

from spotify.utils.decorators import run_in_thread

import weakref

import threading



class PlaylistCallbacks(playlist.PlaylistCallbacks):
    __playlist_loader = None
    
    
    def __init__(self, playlist_loader):
        self.__playlist_loader = weakref.proxy(playlist_loader)
    
    
    def playlist_state_changed(self, playlist):
        self.__playlist_loader.load_playlist()
    
    
    def playlist_metadata_updated(self, playlist):
        self.__playlist_loader.check()



class PlaylistLoader:
    __session = None
    __container_loader = None
    __playlist = None
    __checker = None
    
    #Playlist attributes
    __name = None
    __num_tracks = None
    __thumbnails = None
    __is_collaborative = None
    __is_loaded = None
    
    
    def __init__(self, session, container_loader, playlist):
        #Initialize all instance vars
        self.__session = session
        self.__container_loader = weakref.proxy(container_loader)
        self.__playlist = playlist
        self.__checker = BulkConditionChecker()
        self.__is_loaded = False
        
        #Add the callbacks we are interested in
        playlist.add_callbacks(PlaylistCallbacks(self))
        
        #Fire playlist loading if neccesary
        if not playlist.is_in_ram(self.__session):
            playlist.set_in_ram(self.__session, True)
        
        #And finish the rest in the background
        self.load_playlist()
    
    
    def _wait_for_metadata(self, track):
        def album_is_loaded():
            album = track.album()
            return album is not None and album.is_loaded()
        
        if not track.is_loaded():
            self.__checker.add_condition(track.is_loaded)
            self.__checker.complete_wait(10)
        
        if not album_is_loaded():
            self.__checker.add_condition(album_is_loaded)
            self.__checker.complete_wait(10)
    
    
    def _load_thumbnails(self):
        thumbnails = []
        
        for item in self.__playlist.tracks():
            #Wait until this track is fully loaded
            self._wait_for_metadata(item)
            
            #And append the cover if it's new
            cover = 'http://localhost:8080/image/%s.jpg' % item.album().cover()
            if cover not in thumbnails:
                thumbnails.append(cover)
            
            #If we reached to the desired thumbnail count...
            if len(thumbnails) == 4:
                return thumbnails
        
        #Track list exhausted, return the thumbnails anyway
        return thumbnails
    
    
    @run_in_thread(threads_per_class=10, single_instance=True)
    def load_playlist(self):
        if self.__playlist.is_loaded():
            thumbnails = self._load_thumbnails()
            
            #Now check for changes
            has_changes = False
            
            if self.__thumbnails != thumbnails:
                self.__thumbnails = thumbnails
                has_changes = True
            
            if self.__name != self.__playlist.name():
                self.__name = self.__playlist.name()
                has_changes = True
            
            if self.__num_tracks != self.__playlist.num_tracks():
                self.__num_tracks = self.__playlist.num_tracks()
                has_changes = True
            
            if self.__is_collaborative != self.__playlist.is_collaborative():
                self.__is_collaborative = self.__playlist.is_collaborative()
                has_changes = True
            
            #Finally set it as loaded
            self.__is_loaded = True
            
            #If we detected something different
            if has_changes:
                self.__container_loader.update()
    
    
    def check(self):
        self.__checker.check_conditions()
    
    
    def is_loaded(self):
        return self.__is_loaded
    
    
    def get_thumbnails(self):
        return self.__thumbnails
    
    
    def get_name(self):
        return self.__name
    
    
    def get_num_tracks(self):
        return self.__num_tracks
    
    
    def get_is_collaborative(self):
        return self.__is_collaborative
    
    
    def __del__(self):
        print "PlaylistLoader __del__"



class ContainerCallbacks(playlistcontainer.PlaylistContainerCallbacks):
    __loader = None
    
    
    def __init__(self, loader):
        self.__loader = weakref.proxy(loader)
    
    
    def playlist_added(self, container, playlist, position):
        self.__loader.add_playlist(playlist, position)
    
    
    def container_loaded(self, container):
        self.__loader.update()
    
    
    def playlist_removed(self, container, playlist, position):
        self.__loader.remove_playlist(position)



class ContainerLoader:
    __session = None
    __container = None
    __playlists = None
    __checker = None
    __loading_lock = None
    __is_loaded = None
    
    
    def __init__(self, session, container):
        self.__session = session
        self.__container = container
        self.__playlists = {}
        self.__checker = BulkConditionChecker()
        self.__loading_lock = threading.RLock()
        self.__is_loaded = False
        
        #Load the rest in the background
        self._start_load()
    
    
    def add_playlist(self, playlist, position):
        playlist_loader = PlaylistLoader(self.__session, self, playlist)
        self.__playlists[position] = playlist_loader
    
    
    def _load_container(self):
        
        #Wait for the container to be fully loaded
        self.__checker.add_condition(self.__container.is_loaded)
        self.__checker.complete_wait()
        
        """
        Ensure that we have seen all the playlists.
        Just if the container callbacks are registered too late
        and we missed some of them.
        """
        for idx, item in enumerate(self.__container.playlists()):
            if idx not in self.__playlists:
                self.add_playlist(item, idx)
        
        #Check that all playlists have been loaded
        for item in self.__playlists.itervalues():
            self.__checker.add_condition(item.is_loaded)
        
        #Wait until all conditions became true
        self.__checker.complete_wait(self.__container.num_playlists() * 5)
        
        #Set the status of the loader
        self.__is_loaded = True
        
        #Finally tell the gui we are done
        xbmc.executebuiltin("Action(Noop)")
    
    
    @run_in_thread
    def _start_update(self):
        """
        Try gaining a lock.
        If we can't get one, another update is running, so do nothing.
        """
        if self.__loading_lock.acquire(False):
            try:
                self._load_container()
            
            finally:
                self.__loading_lock.release()
    
    
    @run_in_thread
    def _start_load(self):
        self.__loading_lock.acquire()
        
        try:
            """
            Register container callbacks so they start loading after
            this point. Too bad if they reach before.
            """
            self.__container.add_callbacks(ContainerCallbacks(self))
            
            #And take care of the rest
            self._load_container()
        
        finally:
            self.__loading_lock.release()
    
    
    def update(self):
        self.__checker.check_conditions()
        self._start_update()
    
    
    def is_loaded(self):
        return self.__is_loaded
    
    
    def playlist(self, index):
        return self.__playlists[index]
    
    
    def num_playlists(self):
        return len(self.__playlists)
    
    
    def playlists(self):
        return CallbackIterator(self.num_playlists, self.playlist)
    
    
    def __del__(self):
        print "ContainerLoader __del__"