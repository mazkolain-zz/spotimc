'''
Created on 20/08/2011

@author: mikel
'''
import xbmcgui
from spotymcgui.views import BaseView


class AlbumTracksView(BaseView):
    __group_id = 1300
    __list_id = 1303
    
    
    def get_container_id(self):
        return self.__group_id
    
    
    def click(self, view_manager, window, control_id):
        pass
    
    
    def _get_list(self, window):
        return window.getControl(AlbumTracksView.__list_id)
    
    
    def _add_track(self, list, title, path, duration, number):
        item = xbmcgui.ListItem(path=path)
        item.setInfo(
            "music",
            {"title": title, "duration": duration, "tracknumber": number}
        )
        list.addItem(item)
    
    
    def _populate_list(self, window):
        l = self._get_list(window)
        l.reset()
        
        self._add_track(l, "Track 1", "", 186, 1)
        self._add_track(l, "Track 2", "", 120, 2)
        self._add_track(l, "Track 3", "", 5, 3)
        self._add_track(l, "Track 4", "", 389, 4)
        self._add_track(l, "Track 5", "", 7200, 5)
        self._add_track(l, "Track 1", "", 186, 6)
        self._add_track(l, "Track 2", "", 120, 7)
        self._add_track(l, "Track 3", "", 5, 8)
        self._add_track(l, "Track 4", "", 389, 9)
        self._add_track(l, "Track 5", "", 7200, 10)
        self._add_track(l, "Track 1", "", 186, 11)
        self._add_track(l, "Track 2", "", 120, 12)
        self._add_track(l, "Track 3", "", 5, 13)
        self._add_track(l, "Track 4", "", 389, 14)
        self._add_track(l, "Track 5", "", 7200, 15)
        self._add_track(l, "Track 1", "", 186, 16)
        self._add_track(l, "Track 2", "", 120, 17)
        self._add_track(l, "Track 3", "", 5, 18)
        self._add_track(l, "Track 4", "", 389, 19)
        self._add_track(l, "Track 5", "", 7200, 100)
        
        window.setProperty("AlbumCover", "http://www.me-pr.co.uk/axxis%20doom%20cover%20small.jpg")
        window.setProperty("AlbumName", "Album Name")
        window.setProperty("ArtistName", "Artist Name")
        #img.setImage("http://www.necramonium.com/photos/KISS-Album-Covers/cover_destroyer.jpg")
        
    
    def show(self, window):
        self._populate_list(window)
        c = window.getControl(AlbumTracksView.__group_id)
        c.setVisibleCondition("true")
        print "show!"
    
    
    def hide(self, window):
        c = window.getControl(AlbumTracksView.__group_id)
        c.setVisibleCondition("false")
        print "hide!"
