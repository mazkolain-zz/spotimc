'''
Created on 20/08/2011

@author: mikel
'''
import xbmcgui
from spotymcgui.views import BaseView


class MoreView(BaseView):
    __group_id = 1800
    __list_id = 1801
    
    
    def click(self, view_manager, window, control_id):
        pass
    
    
    def _populate_list(self, window):
        #window.setProperty("AlbumCover", "http://www.me-pr.co.uk/axxis%20doom%20cover%20small.jpg")
        pass
    
    
    def _add_item(self, list, label, icon):
        list.addItem(xbmcgui.ListItem(label=label,iconImage=icon))
    
    
    def _draw_list(self, window):
        l = window.getControl(MoreView.__list_id)
        l.reset()
        
        #Add the items
        self._add_item(l, "Settings", "common/more-settings-icon.png")
        self._add_item(l, "Logout", "common/more-logout-icon.png")
        
        
    
    def show(self, window):
        #Populate the list
        self._draw_list(window)
        
        c = window.getControl(MoreView.__group_id)
        c.setVisibleCondition("true")
        print "show!"
    
    
    def hide(self, window):
        c = window.getControl(MoreView.__group_id)
        c.setVisibleCondition("false")
        print "hide!"
