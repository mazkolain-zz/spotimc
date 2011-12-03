'''
Created on 29/11/2011

@author: mikel
'''
import xbmc
from spotify import artistbrowse, albumbrowse, BulkConditionChecker
from spotify.album import AlbumType as SpotifyAlbumType
from spotify.utils.decorators import run_in_thread
import weakref




class AlbumType:
    Album = 0
    Single = 1
    Compilation = 2
    AppearsIn = 3



class AlbumCallbacks(albumbrowse.AlbumbrowseCallbacks):
    __checker = None
    
    
    def __init__(self, checker):
        self.__checker = checker
    
    
    def albumbrowse_complete(self, albumbrowse):
        self.__checker.check_conditions()



class ArtistCallbacks(artistbrowse.ArtistbrowseCallbacks):
    __artistalbumloader = None
    
    
    def __init__(self, artistalbumloader):
        self.__artistalbumloader = weakref.proxy(artistalbumloader)
    
    
    def artistbrowse_complete(self, artistbrowse):
        self.__artistalbumloader.check()



class ArtistAlbumLoader:
    __checker = None
    __artist = None
    __album_data = None
    __artistbrowse = None
    __is_loaded = None
    
    
    def __init__(self, session, artist):
        self.__checker = BulkConditionChecker()
        self.__session = session
        self.__artist = artist
        self.__album_data = {}
        cb = ArtistCallbacks(self)
        self.__artistbrowse = artistbrowse.Artistbrowse(session, artist, cb)
        self.__is_loaded = False
        
        #Avoid locking this thread and continue in another one
        self.continue_in_background()
    
    
    def check(self):
        self.__checker.check_conditions()
    
    
    def _wait_for_album_info(self, album_info, checker):
        def info_is_loaded():
            return album_info.is_loaded()
        
        if not info_is_loaded():
            checker.add_condition(info_is_loaded)
            checker.complete_wait(10) #Should be enough for an album
    
    
    def _num_available_tracks(self, album_info):
        count = 0
        
        #Return true if it has at least one playable track
        for track in album_info.tracks():
            if track.is_available(self.__session):
                count += 1
        
        return count
    
    
    def _get_album_type(self, album):
        if album.type() == SpotifyAlbumType.Single:
            return AlbumType.Single
        
        elif album.type() == SpotifyAlbumType.Compilation:
            return AlbumType.Compilation
        
        #Sure? That will work?
        elif album.artist().name() == 'Various Artists':
            return AlbumType.AppearsIn
        
        else:
            return AlbumType.Album
    
    
    @run_in_thread(threads_per_class=5)
    def load_album_info(self, index, album):
        #A checker for a single condition? Overkill!
        checker = BulkConditionChecker()
        cb = AlbumCallbacks(checker)
        album_info = albumbrowse.Albumbrowse(self.__session, album, cb)
        
        #Now wait until it's loaded
        self._wait_for_album_info(album_info, checker)
        
        #Populate it's data
        self.__album_data[index] = {
            'available_tracks': self._num_available_tracks(album_info),
            'type': self._get_album_type(album),
        }
        
        #Tell that we've done
        self.__checker.check_conditions()
        
        
    def _wait_for_album_list(self):
        if not self.__artistbrowse.is_loaded():
            self.__checker.add_condition(self.__artistbrowse.is_loaded)
            self.__checker.complete_wait(60) #Should be enough?
    
    
    def _add_album_processed_check(self, index):
        def album_is_processed():
            return index in self.__album_data
        
        if not album_is_processed():
            self.__checker.add_condition(album_is_processed)
    
    
    @run_in_thread(threads_per_class=1)
    def continue_in_background(self):
        #Wait until the album list got loaded
        self._wait_for_album_list()
        
        #Now load albumbrowse data from each one
        for index, album in enumerate(self.__artistbrowse.albums()):
            #Add a condition for the next wait
            self._add_album_processed_check(index)
            
            #Start loading the info in the background
            self.load_album_info(index, album)
        
        #Now wait until all info gets loaded
        self.__checker.complete_wait(60)
        
        #Final steps...
        self.__is_loaded = True
        xbmc.executebuiltin("Action(Noop)")
    
    
    def is_loaded(self):
        return self.__is_loaded
    
    
    def get_album_available_tracks(self, index):
        return self.__album_data[index]['available_tracks']
    
    
    def get_album_type(self, index):
        return self.__album_data[index]['type']
    
    
    def get_album(self, index):
        return self.__artistbrowse.album(index)
    
    
    def get_albums(self):
        return self.__artistbrowse.albums()
