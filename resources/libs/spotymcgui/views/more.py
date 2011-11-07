'''
Created on 20/08/2011

@author: mikel
'''
import xbmcgui
from spotymcgui.views import BaseView


class MoreView(BaseView):
    __group_id = 1900
    __list_id = 1901
    
    
    def click(self, view_manager, control_id):
        pass
    
    
    def _add_item(self, list, label, icon):
        list.addItem(xbmcgui.ListItem(label=label,iconImage=icon))
    
    
    def _draw_list(self, window):
        list = window.getControl(MoreView.__list_id)
        list.reset()
        
        #Add the items
        self._add_item(list, "Settings", "common/more-settings-icon.png")
        self._add_item(list, "Logout", "common/more-logout-icon.png")
        
    
    def show(self, view_manager):
        window = view_manager.get_window()
        self._draw_list(window)
        c = window.getControl(MoreView.__group_id)
        c.setVisibleCondition("true")
    
    
    def hide(self, view_manager):
        window = view_manager.get_window()
        c = window.getControl(MoreView.__group_id)
        c.setVisibleCondition("false")
