'''
Created on 20/08/2011

@author: mikel
'''
import xbmc, xbmcgui
from spotymcgui.views import BaseListContainerView
from spotify import albumbrowse, link, track



class AlbumCallbacks(albumbrowse.AlbumbrowseCallbacks):
    def albumbrowse_complete(self, albumbrowse):
        xbmc.executebuiltin("Action(Noop)")



class AlbumTracksView(BaseListContainerView):
    container_id = 1300
    list_id = 1303
    
    context_toggle_star = 5307
    
    __albumbrowse = None
    
    
    def __init__(self, session, album):
        cb = AlbumCallbacks()
        self.__albumbrowse = albumbrowse.Albumbrowse(session, album, cb)
    
    
    def _play_selected_track(self, view_manager):
        item = self.get_list(view_manager).getSelectedItem()
        pos = int(item.getProperty("real_index"))
        
        #If we have a valid index
        if pos is not None:
            #track_item = self.__albumbrowse.track(int(pos))
            playlist_manager = view_manager.get_var('playlist_manager')
            playlist_manager.play(self.__albumbrowse.tracks(), pos)
    
    
    def click(self, view_manager, control_id):
        if control_id == AlbumTracksView.list_id:
            self._play_selected_track(view_manager)
        
        elif control_id == AlbumTracksView.context_toggle_star:
            item = self.get_list(view_manager).getSelectedItem()
            pos = int(item.getProperty("real_index"))
            
            if pos is not None:
                session = view_manager.get_var('session')
                current_track = self.__albumbrowse.track(pos)
                
                if item.getProperty('IsStarred') == 'true':
                    item.setProperty('IsStarred', 'false')
                    track.set_starred(session, [current_track], False)
                else:
                    item.setProperty('IsStarred', 'true')
                    track.set_starred(session, [current_track], True)
    
    
    def get_container(self, view_manager):
        return view_manager.get_window().getControl(AlbumTracksView.container_id)
    
    
    def get_list(self, view_manager):
        return view_manager.get_window().getControl(AlbumTracksView.list_id)
    
    
    def _have_multiple_discs(self, track_list):
        for item in track_list:
            if item.disc() > 1:
                return True
        
        return False
    
    
    def _set_album_info(self, window, album, artist):
        window.setProperty("AlbumCover", "http://localhost:8080/image/%s.jpg" % album.cover())
        window.setProperty("AlbumName", album.name())
        window.setProperty("ArtistName", artist.name())
    
    
    def _add_disc_separator(self, list, disc_number):
        item = xbmcgui.ListItem()
        item.setProperty("IsDiscSeparator", "true")
        item.setProperty("DiscNumber", str(disc_number))
        list.addItem(item)
    
    
    def _add_track(self, list, track, real_index, is_starred):
        track_link = link.create_from_track(track)
        track_id = track_link.as_string()[14:]
        track_url = "http://localhost:8080/track/%s.wav" % track_id
        
        item = xbmcgui.ListItem(path=track_url)
        info = {
            "title": track.name(),
            "duration": track.duration() / 1000,
            "tracknumber": track.index(),
        }
        
        if is_starred:
            item.setProperty('IsStarred', 'true')
        else:
            item.setProperty('IsStarred', 'false')
        
        #Set rating points for this track
        rating_points = int(round(track.popularity() * 5 / 100.0))
        item.setProperty("rating_points", str(rating_points))
        
        item.setProperty("real_index", str(real_index))
        item.setInfo('music', info)
        list.addItem(item)
    
    
    def render(self, view_manager):
        if self.__albumbrowse.is_loaded():
            session = view_manager.get_var('session')
            list = self.get_list(view_manager)
            list.reset()
            
            #Set album info
            self._set_album_info(
                view_manager.get_window(),
                self.__albumbrowse.album(),
                self.__albumbrowse.artist()
            )
            
            #For disc grouping
            last_disc = None
            multiple_discs = self._have_multiple_discs(
                self.__albumbrowse.tracks()
            )
            
            for idx, item in enumerate(self.__albumbrowse.tracks()):
                #If disc was changed add a separator
                if multiple_discs and last_disc != item.disc():
                    last_disc = item.disc()
                    self._add_disc_separator(list, last_disc)
                
                is_starred = item.is_starred(session)
                self._add_track(list, item, idx, is_starred)
            
            return True
