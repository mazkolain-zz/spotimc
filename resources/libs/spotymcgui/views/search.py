'''
Created on 22/08/2011

@author: mikel
'''
import xbmc, xbmcgui
from spotymcgui.views import BaseListContainerView
from spotify import search, link



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
        
    
    def get_container(self, view_manager):
        return view_manager.get_window().getControl(SearchTracksView.container_id)
    
    
    def get_list(self, view_manager):
        return view_manager.get_window().getControl(SearchTracksView.list_id)
    
    
    def _add_track(self, list, idx, title, artist, album, path, duration):
        item = xbmcgui.ListItem(path=path)
        item.setProperty('TrackIndex', str(idx))
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
                    track.duration() / 1000
                )
            
            
            #Tell that the list is ready to render
            return True
