'''
Created on 20/08/2011

@author: mikel
'''
import xbmcgui
from spotymcgui.views import BaseListContainerView


class MoreView(BaseListContainerView):
    container_id = 1900
    list_id = 1901
    
    
    def click(self, view_manager, control_id):
        pass
    
    
    def get_container(self, view_manager):
        return view_manager.get_window().getControl(MoreView.container_id)
    
    
    def get_list(self, view_manager):
        return view_manager.get_window().getControl(MoreView.list_id)
    
    
    def _add_item(self, list, label, icon):
        list.addItem(xbmcgui.ListItem(label=label,iconImage=icon))
    
    
    def render(self, view_manager):
        list = self.get_list(view_manager)
        list.reset()
        
        #Add the items
        self._add_item(list, "Settings", "common/more-settings-icon.png")
        self._add_item(list, "Logout", "common/more-logout-icon.png")
        
        return True
