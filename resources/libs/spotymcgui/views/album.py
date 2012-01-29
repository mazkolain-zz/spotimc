'''
Created on 20/08/2011

@author: mikel
'''
import xbmc, xbmcgui
from spotymcgui.views import BaseListContainerView
from spotify import albumbrowse, track



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
        pos = int(item.getProperty("ListIndex"))
        
        print 'clicked pos: %s' % pos
        
        #If we have a valid index
        if pos is not None:
            session = view_manager.get_var('session')
            playlist_manager = view_manager.get_var('playlist_manager')
            playlist_manager.play(self.__albumbrowse.tracks(), session, pos)
    
    
    def click(self, view_manager, control_id):
        if control_id == AlbumTracksView.list_id:
            self._play_selected_track(view_manager)
        
        elif control_id == AlbumTracksView.context_toggle_star:
            item = self.get_list(view_manager).getSelectedItem()
            pos = int(item.getProperty("ListIndex"))
            
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
    
    
    def _have_multiple_discs(self):
        for item in self.__albumbrowse.tracks():
            if item.disc() > 1:
                return True
        
        return False
    
    
    def _set_album_info(self, view_manager):
        window = view_manager.get_window()
        pm = view_manager.get_var('playlist_manager')
        album = self.__albumbrowse.album()
        artist = self.__albumbrowse.artist()
        window.setProperty("AlbumCover", pm.get_image_url(album.cover()))
        window.setProperty("AlbumName", album.name())
        window.setProperty("ArtistName", artist.name())
    
    
    def _add_disc_separator(self, list_obj, disc_number):
        item = xbmcgui.ListItem()
        item.setProperty("IsDiscSeparator", "true")
        item.setProperty("DiscNumber", str(disc_number))
        list_obj.addItem(item)
    
    
    def render(self, view_manager):
        if self.__albumbrowse.is_loaded():
            session = view_manager.get_var('session')
            pm = view_manager.get_var('playlist_manager')
            
            #Reset list
            list_obj = self.get_list(view_manager)
            list_obj.reset()
            
            #Set album info
            self._set_album_info(view_manager)
            
            #For disc grouping
            last_disc = None
            multiple_discs = self._have_multiple_discs()
            
            #Iterate over the track list
            for list_index, track in enumerate(self.__albumbrowse.tracks()):
                #If disc was changed add a separator
                if multiple_discs and last_disc != track.disc():
                    last_disc = track.disc()
                    self._add_disc_separator(list_obj, last_disc)
                
                #Add the track item
                url, info = pm.create_track_info(track, session, list_index)
                list_obj.addItem(info)
            
            return True
