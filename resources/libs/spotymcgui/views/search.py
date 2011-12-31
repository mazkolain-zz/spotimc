'''
Created on 22/08/2011

@author: mikel
'''
import xbmcgui
from spotymcgui.views import BaseListContainerView



class SearchTracksView(BaseListContainerView):
    container_id = 1500
    list_id = 1520
    
    
    def click(self, view_manager, control_id):
        pass
    
    
    def get_container(self, view_manager):
        return view_manager.get_window().getControl(SearchTracksView.container_id)
    
    
    def get_list(self, view_manager):
        return view_manager.get_window().getControl(SearchTracksView.list_id)
    
    
    def _add_track(self, list, title, artist, album, path, duration):
        item = xbmcgui.ListItem(path=path)
        item.setInfo(
            "music",
            {
             "title": title, "artist": artist, "album": album,
             "duration": duration
            }
        )
        list.addItem(item)
    
    
    def render(self, view_manager):
        window = view_manager.get_window()
        l = self.get_list(view_manager)
        l.reset()
        
        self._add_track(l, "Track 1", "Artist1", "Album1", "", 186)
        self._add_track(l, "Track 1", "Artist1", "Album1", "", 256)
        self._add_track(l, "Track 1", "Artist1", "Album1", "", 256)
        self._add_track(l, "Track 1", "Artist1", "Album1", "", 256)
        self._add_track(l, "Track 1", "Artist1", "Album1", "", 256)
        self._add_track(l, "Track 1", "Artist1", "Album1", "", 256)
        self._add_track(l, "Track 1", "Artist1", "Album1", "", 256)
        self._add_track(l, "Track 1", "Artist1", "Album1", "", 256)
        self._add_track(l, "Track 1", "Artist1", "Album1", "", 256)
        self._add_track(l, "Track 1", "Artist1", "Album1", "", 7560)
        self._add_track(l, "A very long track name that overflows the column", "Huey Lewis and the News", "A long album name that overflows the column", "", 256)
        self._add_track(l, "Track 1", "Artist1", "Album1", "", 256)
        self._add_track(l, "Track 1", "Artist1", "Album1", "", 256)
        self._add_track(l, "Track 1", "Artist1", "Album1", "", 256)
        self._add_track(l, "Track 1", "Artist1", "Album1", "", 256)
        self._add_track(l, "Track 1", "Artist1", "Album1", "", 256)
        
        window.setProperty("SearchQuery", "Rick Astley")
        window.setProperty("SearchDidYouMeanStatus", "true")
        window.setProperty("SearchDidYouMeanString", "Rickrolled")
        
        return True
        #window.setProperty("AlbumCover", "http://www.me-pr.co.uk/axxis%20doom%20cover%20small.jpg")
        #window.setProperty("AlbumName", "Album Name")
        #window.setProperty("ArtistName", "Artist Name")
        #img.setImage("http://www.necramonium.com/photos/KISS-Album-Covers/cover_destroyer.jpg")
