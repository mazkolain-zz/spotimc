'''
Created on 17/07/2011

@author: mikel
'''
import spotymcgui.views as views
import xbmcgui


class HomeMenuView(views.BaseView):
    __group_id = 1100
    __selected_item = 0
    
    
    def _get_list(self, window):
        return window.getControl(HomeMenuView.__group_id)
    
    
    def _populate_list(self, window):
        l = self._get_list(window)
        l.reset()
        l.addItem(xbmcgui.ListItem('New Stuff', '', 'home-menu/new-stuff-active.png'))
        l.addItem(xbmcgui.ListItem('Playlists', '', 'home-menu/playlists-active.png'))
        l.addItem(xbmcgui.ListItem('Search', '', 'home-menu/search-active.png'))
        l.addItem(xbmcgui.ListItem('Toplists', '', 'home-menu/toplists-active.png'))
        l.addItem(xbmcgui.ListItem('Radio', '', 'home-menu/radio-active.png'))
        l.addItem(xbmcgui.ListItem('Settings', '', 'home-menu/settings-active.png'))
        l.addItem(xbmcgui.ListItem('Logout', '', 'home-menu/logout-active.png'))
        l.addItem(xbmcgui.ListItem('Exit', '', 'home-menu/exit-active.png'))
        l.selectItem(self.__selected_item)
    
    
    def click(self, window, control_id):
        print "control id: %d" % control_id
        print "list pos: %d" % self._get_list(window).getSelectedPosition()
        
    
    def show(self, window):
        l = self._get_list(window)
        l.setVisibleCondition("true")
        print "show!"
        
        #Populate the main menu
        self._populate_list(window)
    
    def hide(self, window):
        l = self._get_list(window)
        l.setVisibleCondition("false")
        print "hide!"
        
        #Store selected item
        self.__selected_item = l.getSelectedPosition()
