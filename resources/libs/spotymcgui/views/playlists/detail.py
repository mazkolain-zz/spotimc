'''
Created on 27/10/2011

@author: mikel
'''
import xbmcgui
from spotymcgui.views import BaseView

import loaders

from spotify import link


class PlaylistDetailView(BaseView):
    __group_id = 1800
    __list_id = 1801
    
    
    __loader = None
    __playlist = None
    
    
    def __init__(self, session, playlist):
        self.__playlist = playlist
        self.__loader = loaders.FullPlaylistLoader(session, playlist)
    
    
    def click(self, view_manager, control_id):
        if control_id == PlaylistDetailView.__list_id:
            item = self._get_list(view_manager).getSelectedItem()
            pos = int(item.getProperty('TrackIndex'))
            playlist_manager = view_manager.get_var('playlist_manager')
            playlist_manager.play(self.__playlist.tracks(), pos)
    
    
    def _get_list(self, view_manager):
        return view_manager.get_window().getControl(PlaylistDetailView.__list_id)
    
    
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
    
    
    def _set_playlist_properties(self, window, is_collaborative):
        if is_collaborative:
            window.setProperty("PlaylistDetailCollaborative", "True")
        else:
            window.setProperty("PlaylistDetailCollaborative", "False")
    
    
    def _set_playlist_image(self, window, thumbnails):
        if len(thumbnails) > 0:
            #Set cover info
            if len(thumbnails) < 4:
                window.setProperty("PlaylistDetailCoverLayout", "one")
            else:
                window.setProperty("PlaylistDetailCoverLayout", "four")
            
            #Now loop to set all the images
            for idx, thumb_item in enumerate(thumbnails):
                window.setProperty("PlaylistDetailCoverItem%d" % (idx + 1), thumb_item)
    
    
    def _populate_list(self, view_manager, track_list):
        list = self._get_list(view_manager)
        list.reset()
        
        for idx, item in enumerate(track_list):
            track_link = link.create_from_track(item)
            track_id = track_link.as_string()[14:]
            track_url = "http://localhost:8080/track/%s.wav" % track_id
            
            self._add_track(
                list,
                idx,
                item.name(),
                ', '.join([artist.name() for artist in item.artists()]),
                item.album().name(),
                track_url,
                item.duration() / 1000
            )
    
    
    def _draw_list(self, view_manager):
        window = view_manager.get_window()
        
        #Show loading animation
        window.show_loading()
        
        if self.__loader.is_loaded():
            group = window.getControl(PlaylistDetailView.__group_id)
            group.setVisibleCondition("false")
            
            #Draw the items on the list
            self._populate_list(view_manager, self.__loader.get_tracks())
            
            #Set the thumbnails
            self._set_playlist_image(window, self.__loader.get_thumbnails())
            
            #And the properties
            self._set_playlist_properties(window, self.__loader.get_is_collaborative())
            
            #Hide loading anim
            window.hide_loading()
            
            #Show container
            group.setVisibleCondition("true")
            window.setFocusId(PlaylistDetailView.__group_id)
    
    
    def show(self, view_manager):
        self._draw_list(view_manager)
    
    
    def update(self, view_manager):
        self._draw_list(view_manager)
    
    
    def hide(self, view_manager):
        window = view_manager.get_window()
        c = window.getControl(PlaylistDetailView.__group_id)
        c.setVisibleCondition("false")
