'''
Created on 20/08/2011

@author: mikel
'''
import xbmc
from spotymcgui.views import BaseContainerView
from spotymcgui.views.artists import open_artistbrowse_albums
from spotymcgui.views.album import AlbumTracksView


class NowPlayingView(BaseContainerView):
    container_id = 1600
    
    browse_artist_button = 1611
    browse_album_button = 1612
    
    
    def _get_current_track(self, view_manager):
        playlist_manager = view_manager.get_var('playlist_manager')
        index = int(xbmc.getInfoLabel('MusicPlayer.Property(ListIndex)'))
        return playlist_manager.get_item(index)
    
    
    def _do_browse_artist(self, view_manager):
        track = self._get_current_track(view_manager)
        artist_list = [artist for artist in track.artists()]
        open_artistbrowse_albums(view_manager, artist_list)
    
    
    def _do_browse_album(self, view_manager):
        track = self._get_current_track(view_manager)
        session = view_manager.get_var('session')
        v = AlbumTracksView(session, track.album())
        view_manager.add_view(v)
    
    
    def click(self, view_manager, control_id):
        if control_id == NowPlayingView.browse_artist_button:
            self._do_browse_artist(view_manager)
        
        elif control_id == NowPlayingView.browse_album_button:
            self._do_browse_album(view_manager)        
    
    
    def get_container(self, view_manager):
        return view_manager.get_window().getControl(NowPlayingView.container_id)
    
    
    def render(self, view_manager):
        return True
