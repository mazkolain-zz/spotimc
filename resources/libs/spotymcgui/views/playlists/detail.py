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
    __list_position = None
    
    
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
    
    
    def _get_playlist_length_str(self):
        total_duration = 0
        
        for track in self.__playlist.tracks():
            total_duration += track.duration() / 1000
        
        #Now the string ranges
        one_minute = 60
        one_hour = 3600
        one_day = 3600 * 24
        
        if total_duration > one_day:
            num_days = int(round(total_duration / one_day))
            if num_days == 1:
                return 'one day'
            else:
                return '%d days' % num_days
        
        elif total_duration > one_hour:
            num_hours = int(round(total_duration / one_hour))
            if num_hours == 1:
                return 'one hour'
            else:
                return '%d hours' % num_hours
        
        else:
            num_minutes = int(round(total_duration / one_minute))
            if num_minutes == 1:
                return 'one minute'
            else:
                return '%d minutes' % num_minutes
    
    
    def _set_playlist_properties(self, view_manager):
        window = view_manager.get_window()
        
        #Playlist name
        window.setProperty("PlaylistDetailName", self.__playlist.name())
        
        #Owner info
        session = view_manager.get_var('session')
        current_username = session.user().canonical_name()
        playlist_username = self.__playlist.owner().canonical_name()
        
        if current_username != playlist_username:
            window.setProperty("PlaylistDetailShowOwner", "True")
            window.setProperty("PlaylistDetailOwner", str(playlist_username))
        else:
            window.setProperty("PlaylistDetailShowOwner", "False")
    
        #Collaboratie status
        if self.__playlist.is_collaborative():
            window.setProperty("PlaylistDetailCollaborative", "True")
        else:
            window.setProperty("PlaylistDetailCollaborative", "False")
        
        #Length data
        window.setProperty("PlaylistDetailNumTracks", str(self.__playlist.num_tracks()))
        window.setProperty("PlaylistDetailDuration", self._get_playlist_length_str())
        
        #Subscribers
        window.setProperty("PlaylistDetailNumSubscribers", str(self.__playlist.num_subscribers()))
    
    
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
            self._save_list_position(view_manager)
            
            group = window.getControl(PlaylistDetailView.__group_id)
            group.setVisibleCondition("false")
            
            #Draw the items on the list
            self._populate_list(view_manager, self.__loader.get_tracks())
            
            #Set the thumbnails
            self._set_playlist_image(window, self.__loader.get_thumbnails())
            
            #And the properties
            self._set_playlist_properties(view_manager)
            
            #If we have the list index at hand...
            self._restore_list_position(view_manager)
            
            #Hide loading anim
            window.hide_loading()
            
            #Show container
            group.setVisibleCondition("true")
            window.setFocusId(PlaylistDetailView.__group_id)
    
    
    def show(self, view_manager):
        self._draw_list(view_manager)
    
    
    def update(self, view_manager):
        self._draw_list(view_manager)
    
    
    def _save_list_position(self, view_manager):
        list = self._get_list(view_manager)
        self.__list_position = list.getSelectedPosition()
    
    
    def _restore_list_position(self, view_manager):
        #If we have the list index at hand...
        if self.__list_position is not None:
            list = self._get_list(view_manager)
            list.selectItem(self.__list_position)
    
    
    def hide(self, view_manager):
        window = view_manager.get_window()
        
        #Keep the list position
        self._save_list_position(view_manager)
        
        c = window.getControl(PlaylistDetailView.__group_id)
        c.setVisibleCondition("false")
