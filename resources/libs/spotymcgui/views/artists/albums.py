'''
Created on 29/11/2011

@author: mikel
'''
import xbmc, xbmcgui
from spotymcgui.views import BaseListContainerView, album
from loaders import ArtistAlbumLoader, AlbumType
from spotymcgui.utils.settings import SkinSettings



class ArtistAlbumsView(BaseListContainerView):
    container_id = 2000
    list_id = 2001
    
    
    #Filtering controls
    filter_albums_button = 6011
    filter_singles_button = 6012
    filter_compilations_button = 6013
    filter_appears_in_button = 6014
    filter_hide_similar = 6016
    
    
    
    __artist = None
    __loader = None
    __settings = SkinSettings()
    
    
    def __init__(self, session, artist):
        self._init_config()
        self.__artist = artist
        self.__loader = ArtistAlbumLoader(session, artist)
    
    
    def _init_config(self):
        if not self.__settings.has_bool_true('spotymc_albumbrowse_album_init'):
            print 'init config'
            self.__settings.set_bool_true('spotymc_albumbrowse_album_init')
            self.__settings.set_bool_true('spotymc_artistbrowse_albums_albums')
            self.__settings.set_bool_true('spotymc_artistbrowse_albums_singles')
            self.__settings.set_bool_true('spotymc_artistbrowse_albums_compilations')
            self.__settings.set_bool_true('spotymc_artistbrowse_albums_appears_in')
            self.__settings.set_bool_true('spotymc_artistbrowse_albums_hide_similar')
    
    
    def _get_album_filter(self):
        filter_types = []
        
        if self.__settings.has_bool_true('spotymc_artistbrowse_albums_albums'):
            filter_types.append(AlbumType.Album)
        
        if self.__settings.has_bool_true('spotymc_artistbrowse_albums_singles'):
            filter_types.append(AlbumType.Single)
        
        if self.__settings.has_bool_true('spotymc_artistbrowse_albums_compilations'):
            filter_types.append(AlbumType.Compilation)
        
        if self.__settings.has_bool_true('spotymc_artistbrowse_albums_appears_in'):
            filter_types.append(AlbumType.AppearsIn)
        
        return filter_types
    
    
    def _get_similar_filter(self):
        return self.__settings.has_bool_true('spotymc_artistbrowse_albums_hide_similar')
    
    
    def _show_album(self, view_manager):
        item = self.get_list(view_manager).getSelectedItem()
        real_index = int(item.getProperty('real_index'))
        album_obj = self.__loader.get_album(real_index)
        session = view_manager.get_var('session')
        v = album.AlbumTracksView(session, album_obj)
        view_manager.add_view(v)
    
    
    def click(self, view_manager, control_id):
        filter_controls = [
            ArtistAlbumsView.filter_albums_button,
            ArtistAlbumsView.filter_singles_button,
            ArtistAlbumsView.filter_compilations_button,
            ArtistAlbumsView.filter_appears_in_button,
            ArtistAlbumsView.filter_hide_similar
        ]
        
        #If the list was clicked...
        if control_id == ArtistAlbumsView.list_id:
            self._show_album(view_manager)
        
        elif control_id in filter_controls:
            view_manager.show(False)
    
    
    def get_container(self, view_manager):
        return view_manager.get_window().getControl(ArtistAlbumsView.container_id)
    
    
    def get_list(self, view_manager):
        return view_manager.get_window().getControl(ArtistAlbumsView.list_id)
    
    
    def render(self, view_manager):
        if self.__loader.is_loaded():
            l = self.get_list(view_manager)
            l.reset()
            
            #Get the non-similar list, if asked to do so
            if self._get_similar_filter():
                non_similar_list = self.__loader.get_non_similar_albums()
            
            #Set the artist name
            window = view_manager.get_window()
            window.setProperty('artistbrowse_artist_name', self.__artist.name())
            
            #Get the album types to be shown
            filter_types = self._get_album_filter()
            print 'album filter: %s' % filter_types
            
            #Now loop over all the loaded albums
            for index, album in self.__loader.get_albums():
                album_type = self.__loader.get_album_type(index)
                is_in_filter = album_type in filter_types
                is_available = self.__loader.get_album_available_tracks(index) > 0
                is_similar = self._get_similar_filter() and index not in non_similar_list
                
                #Discard unavailable/non-filtered/similar albums
                if is_available and is_in_filter and not is_similar:
                    item = xbmcgui.ListItem(
                        album.name(), str(album.year()),
                        'http://localhost:8080/image/%s.jpg' % album.cover()
                    )
                    item.setProperty('real_index', str(index))
                    l.addItem(item)
            
            return True
