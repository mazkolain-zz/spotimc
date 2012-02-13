'''
Created on 03/12/2011

@author: mikel
'''
import xbmc



class SkinSettings:
    def has_bool_true(self, name):
        return xbmc.getCondVisibility('Skin.HasSetting(%s)' % name)
    
    
    def set_bool_true(self, name):
        xbmc.executebuiltin('Skin.SetBool(%s)' % name)
    
    
    def toggle_bool(self, name):
        xbmc.executebuiltin('Skin.ToggleSetting(%s)' % name)
    
    
    def get_value(self, name):
        return xbmc.getInfoLabel('Skin.String(%s)' % name)
    
    
    def set_value(self, name, value):
        xbmc.executebuiltin('Skin.SetString(%s,%s)' % (name, value))
