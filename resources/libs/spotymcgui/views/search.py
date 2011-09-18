'''
Created on 22/08/2011

@author: mikel
'''
import xbmcgui
from spotymcgui.views import BaseView


class SearchTracksView(BaseView):
    __group_id = 1500
    __list_id = 1501
    
    
    def click(self, view_manager, window, control_id):
        pass
    
    
    def _get_list(self, window):
        return window.getControl(SearchTracksView.__list_id)
    
    
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
    
    def _populate_list(self, window):
        l = self._get_list(window)
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
        
        window.setProperty("SearchQuery", "Rick Astley")
        #window.setProperty("AlbumCover", "http://www.me-pr.co.uk/axxis%20doom%20cover%20small.jpg")
        #window.setProperty("AlbumName", "Album Name")
        #window.setProperty("ArtistName", "Artist Name")
        #img.setImage("http://www.necramonium.com/photos/KISS-Album-Covers/cover_destroyer.jpg")
        
    
    def show(self, window):
        self._populate_list(window)
        c = window.getControl(SearchTracksView.__group_id)
        c.setVisibleCondition("true")
        print "show!"
    
    
    def hide(self, window):
        c = window.getControl(SearchTracksView.__group_id)
        c.setVisibleCondition("false")
        print "hide!"
