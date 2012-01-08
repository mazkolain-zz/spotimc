'''
Created on 22/08/2011

@author: mikel
'''
import xbmc, xbmcgui
from spotymcgui.views import BaseListContainerView
from spotify import search, link, track
from spotymcgui.views.artists import open_artistbrowse_albums
from spotymcgui.views.album import AlbumTracksView



def ask_search_term():
    kb = xbmc.Keyboard('', 'Enter a search term')
    kb.doModal()
    
    if kb.isConfirmed():
        return kb.getText()



class SearchTracksCallbacks(search.SearchCallbacks):
    def search_complete(self, result):
        xbmc.executebuiltin("Action(Noop)")



class SearchTracksView(BaseListContainerView):
    container_id = 1500
    list_id = 1520
    
    
    button_did_you_mean = 1504
    button_new_search = 1510
    
    context_browse_artist_button = 5302
    context_browse_album_button = 5303
    context_toggle_star = 5304
    context_add_to_playlist = 5305
    
    
    __session = None
    __query = None
    __search = None
    
    
    def _do_search(self, query):
        self.__query = query
        cb = SearchTracksCallbacks()
        self.__search = search.Search(
            self.__session, query,
            track_offset=0, track_count=200,
            callbacks=cb
        )
    
    
    def __init__(self, session, query):
        self.__session = session
        self._do_search(query)
    
    
    def _get_current_track(self, view_manager):
        item = self.get_list(view_manager).getSelectedItem()
        pos = int(item.getProperty('TrackIndex'))
        
        if pos is not None:
            return self.__search.track(pos)
    
    
    def click(self, view_manager, control_id):
        if control_id == SearchTracksView.button_did_you_mean:
            if self.__search.did_you_mean():
                self._do_search(self.__search.did_you_mean())
                view_manager.show()
        
        elif control_id == SearchTracksView.button_new_search:
            term = ask_search_term()
            if term:
                self._do_search(term)
                view_manager.show()
        
        elif control_id == SearchTracksView.list_id:
            item = self.get_list(view_manager).getSelectedItem()
            pos = int(item.getProperty('TrackIndex'))
            playlist_manager = view_manager.get_var('playlist_manager')
            playlist_manager.play(self.__search.tracks(), pos)
        
        elif control_id == SearchTracksView.context_browse_artist_button:
            current_track = self._get_current_track(view_manager)
            artist_list = [artist for artist in current_track.artists()]
            open_artistbrowse_albums(view_manager, artist_list)
        
        elif control_id == SearchTracksView.context_browse_album_button:
            album = self._get_current_track(view_manager).album()
            v = AlbumTracksView(view_manager.get_var('session'), album)
            view_manager.add_view(v)
        
        elif control_id == SearchTracksView.context_toggle_star:
            item = self.get_list(view_manager).getSelectedItem()
            current_track = self._get_current_track(view_manager)
            
            if current_track is not None:
                if item.getProperty('IsStarred') == 'true':
                    item.setProperty('IsStarred', 'false')
                    track.set_starred(self.__session, [current_track], False)
                else:
                    item.setProperty('IsStarred', 'true')
                    track.set_starred(self.__session, [current_track], True)
    
    
    def get_container(self, view_manager):
        return view_manager.get_window().getControl(SearchTracksView.container_id)
    
    
    def get_list(self, view_manager):
        return view_manager.get_window().getControl(SearchTracksView.list_id)
    
    
    def _add_track(self, list, idx, title, artist, album, path, duration, is_starred):
        item = xbmcgui.ListItem(path=path)
        item.setProperty('TrackIndex', str(idx))
        
        if is_starred:
            item.setProperty('IsStarred', 'true')
        else:
            item.setProperty('IsStarred', 'false')
        
        item.setInfo(
            "music",
            {
             "title": title, "artist": artist, "album": album,
             "duration": duration
            }
        )
        list.addItem(item)
    
    
    def render(self, view_manager):
        if self.__search.is_loaded():
            window = view_manager.get_window()
            
            #Some view vars
            window.setProperty("SearchQuery", self.__query)
            
            did_you_mean = self.__search.did_you_mean()
            if did_you_mean:
                window.setProperty("SearchDidYouMeanStatus", "true")
                window.setProperty("SearchDidYouMeanString", did_you_mean)
            else:
                window.setProperty("SearchDidYouMeanStatus", "false")
            
            
            #Populate list
            l = self.get_list(view_manager)
            l.reset()
            
            for idx, track in enumerate(self.__search.tracks()):
                track_link = link.create_from_track(track)
                track_id = track_link.as_string()[14:]
                track_url = "http://localhost:8080/track/%s.wav" % track_id
            
                self._add_track(
                    l, idx,
                    track.name(), 
                    ', '.join([artist.name() for artist in track.artists()]),
                    track.album().name(),
                    track_url,
                    track.duration() / 1000,
                    track.is_starred(self.__session)
                )
                
                if track.is_starred(self.__session):
                    print "track starred: %s" % track.name()
            
            
            #Tell that the list is ready to render
            return True
