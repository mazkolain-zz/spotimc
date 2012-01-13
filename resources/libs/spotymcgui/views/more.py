'''
Created on 20/08/2011

@author: mikel
'''
import xbmcgui
from spotymcgui.views import BaseListContainerView
from spotymcgui.settings import SettingsManager


class MoreView(BaseListContainerView):
    container_id = 1900
    list_id = 1901
    
    
    def _do_logout(self, view_manager):
        #Ask the user first
        dlg = xbmcgui.Dialog()
        response = dlg.yesno(
            'Logout',
            'This will forget the remembered user and exit.',
            'Are you sure?'
        )
        
        if response:
            session = view_manager.get_var('session')
            session.forget_me()
            view_manager.get_window().close()
    
    
    def _handle_list_click(self, view_manager):
        item = self.get_list(view_manager).getSelectedItem()
        
        if item is not None:
            key = item.getLabel2()
            
            if key == 'settings':
                session = view_manager.get_var('session')
                settings_obj = SettingsManager()
                settings_obj.show_dialog(session)
            
            elif key == 'logout':
                self._do_logout(view_manager)
    
    
    def click(self, view_manager, control_id):
        if control_id == MoreView.list_id:
            self._handle_list_click(view_manager)
    
    
    def get_container(self, view_manager):
        return view_manager.get_window().getControl(MoreView.container_id)
    
    
    def get_list(self, view_manager):
        return view_manager.get_window().getControl(MoreView.list_id)
    
    
    def _add_item(self, list_obj, key, label, icon):
        list_obj.addItem(
            xbmcgui.ListItem(label=label, label2=key, iconImage=icon)
        )
    
    
    def render(self, view_manager):
        list_obj = self.get_list(view_manager)
        list_obj.reset()
        
        #Add the items
        self._add_item(list_obj, 'settings', "Settings", "common/more-settings-icon.png")
        self._add_item(list_obj, 'logout', "Logout", "common/more-logout-icon.png")
        
        return True
