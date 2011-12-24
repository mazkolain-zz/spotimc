'''
Created on 20/08/2011

@author: mikel
'''
import xbmc
from spotymcgui.views import BaseContainerView


class NowPlayingView(BaseContainerView):
    container_id = 1600
    
    
    def get_container(self, view_manager):
        return view_manager.get_window().getControl(NowPlayingView.container_id)
    
    
    def render(self, view_manager):
        return True
