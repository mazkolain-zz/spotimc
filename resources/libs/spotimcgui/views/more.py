'''
Copyright 2011 Mikel Azkolain

This file is part of Spotimc.

Spotimc is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Spotimc is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Spotimc.  If not, see <http://www.gnu.org/licenses/>.
'''


import xbmcgui
from spotimcgui.views import BaseListContainerView
from spotimcgui.settings import SettingsManager


class MoreView(BaseListContainerView):
    container_id = 1900
    list_id = 1901
    
    
    def _do_logout(self, view_manager):
        #Ask the user first
        dlg = xbmcgui.Dialog()
        response = dlg.yesno(
            'Sign Off',
            'This will forget the remembered user.',
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
            
            elif key == 'sign-off':
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
        self._add_item(list_obj, 'sign-off', "Sign Off", "common/more-logout-icon.png")
        
        return True
