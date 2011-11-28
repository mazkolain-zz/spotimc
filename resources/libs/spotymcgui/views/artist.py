'''
Created on 22/08/2011

@author: mikel
'''
import xbmc, xbmcgui
from spotymcgui.views import BaseView, BaseListContainerView
from spotify import artistbrowse


class ArtistTracksView(BaseView):
    __group_id = 1400
    __list_id = 1401
    
    
    def click(self, view_manager, window, control_id):
        pass
    
    
    def _get_list(self, window):
        return window.getControl(ArtistTracksView.__list_id)
    
    
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
        
        window.setProperty("ArtistName", "Artist Name")
        #img.setImage("http://www.necramonium.com/photos/KISS-Album-Covers/cover_destroyer.jpg")
        
    
    def show(self, window):
        self._populate_list(window)
        c = window.getControl(ArtistTracksView.__group_id)
        c.setVisibleCondition("true")
        print "show!"
    
    
    def hide(self, window):
        c = window.getControl(ArtistTracksView.__group_id)
        c.setVisibleCondition("false")
        print "hide!"



class ArtistAlbumCallbacks(artistbrowse.ArtistbrowseCallbacks):
    def artistbrowse_complete(self, artistbrowse):
        xbmc.executebuiltin("Action(Noop)")



class ArtistAlbumsView(BaseListContainerView):
    container_id = 2000
    list_id = 2001
    
    __artistbrowse = None
    
    
    def __init__(self, session, artist):
        cb = ArtistAlbumCallbacks()
        self.__artistbrowse = artistbrowse.Artistbrowse(session, artist, cb)
        
    
    #def _show_album(self, view_manager):
    #    pos = self.get_list(view_manager).getSelectedPosition()
    #    v = album.AlbumTracksView(self.__session, self.__search.album(pos))
    #    view_manager.add_view(v)
    
    
    def click(self, view_manager, control_id):
        #If the list was clicked...
        if control_id == ArtistAlbumsView.list_id:
            #self._show_album(view_manager)
            pass
    
    
    def get_container(self, view_manager):
        return view_manager.get_window().getControl(ArtistAlbumsView.container_id)
    
    
    def get_list(self, view_manager):
        return view_manager.get_window().getControl(ArtistAlbumsView.list_id)
    
    
    def render(self, view_manager):
        if self.__artistbrowse.is_loaded():
            l = self.get_list(view_manager)
            l.reset()
            
            for album in self.__artistbrowse.albums():
                item = xbmcgui.ListItem(
                    album.name(), str(album.year()),
                    'http://localhost:8080/image/%s.jpg' % album.cover()
                )
                l.addItem(item)
            
            return True
