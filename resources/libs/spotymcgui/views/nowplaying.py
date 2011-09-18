'''
Created on 20/08/2011

@author: mikel
'''
import xbmc
from spotymcgui.views import BaseView


class NowPlayingView(BaseView):
    __group_id = 1600
    
    
    def click(self, view_manager, window, control_id):
        pass
    
    
    def _populate_list(self, window):
        window.setProperty("AlbumCover", "http://www.me-pr.co.uk/axxis%20doom%20cover%20small.jpg")
        
    
    def show(self, window):
        p = xbmc.Player(xbmc.PLAYER_CORE_MPLAYER)
        p.play("http://localhost:8080/track/5zliLGuOl3fwoAu4G6sujx.wav")
        self._populate_list(window)
        c = window.getControl(NowPlayingView.__group_id)
        c.setVisibleCondition("true")
        print "show!"
    
    
    def hide(self, window):
        c = window.getControl(NowPlayingView.__group_id)
        c.setVisibleCondition("false")
        print "hide!"
