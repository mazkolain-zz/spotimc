'''
Created on 25/06/2011

@author: mikel
'''
import xbmc, xbmcgui



class LoginWindow(xbmcgui.WindowXMLDialog):
    #Controld id's
    username_input = 10
    password_input = 11
    
    __file = None
    __script_path = None
    __skin_dir = None
    
    
    __username = None
    __password = None
    
    
    def __init__(self, file, script_path, skin_dir):
        self.__file = file
        self.__script_path = script_path
        self.__skin_dir = skin_dir


    def onInit(self):
        pass
    #def onAction(self, action):
    #    pass
    
    
    def _get_input_value(self, controlID):
        c = self.getControl(controlID)
        return c.getLabel()
    
    
    def _set_input_value(self, controlID, value):
        c = self.getControl(controlID)
        c.setLabel(value)
    
    
    def onClick(self, controlID):
        if controlID == self.username_input:
            default = self._get_input_value(controlID)
            kb = xbmc.Keyboard(default, "Enter username")
            kb.setHiddenInput(False)
            kb.doModal()
            if kb.isConfirmed():
                value = kb.getText()
                self.__username = value
                self._set_input_value(controlID, value)
        
        elif controlID == self.password_input:
            kb = xbmc.Keyboard("", "Enter password")
            kb.setHiddenInput(True)
            kb.doModal()
            if kb.isConfirmed():
                value = kb.getText()
                self.__password = value
                self._set_input_value(controlID, "*" * len(value))
    
    
    def onFocus(self, controlID):
        pass



class PlaylistDialog(xbmcgui.WindowXMLDialog):
    #Controld id's
    
    
    __file = None
    __script_path = None
    __skin_dir = None
    
    
    def __init__(self, file, script_path, skin_dir):
        self.__file = file
        self.__script_path = script_path
        self.__skin_dir = skin_dir


    def onInit(self):
        c = self.getControl(3)
        c.addItem(xbmcgui.ListItem('Item #1'))
        c.addItem(xbmcgui.ListItem('Item #2'))
        c.addItem(xbmcgui.ListItem('Item #3'))
        c.addItem(xbmcgui.ListItem('Item #4'))
        c.addItem(xbmcgui.ListItem('Item #5'))
        c.addItem(xbmcgui.ListItem('Item #6'))
        """"c.addItem(xbmcgui.ListItem('Item #7'))
        c.addItem(xbmcgui.ListItem('Item #8'))
        c.addItem(xbmcgui.ListItem('Item #9'))
        c.addItem(xbmcgui.ListItem('Item #10'))
        c.addItem(xbmcgui.ListItem('Item #11'))
        c.addItem(xbmcgui.ListItem('Item #12'))
        c.addItem(xbmcgui.ListItem('Item #13'))
        c.addItem(xbmcgui.ListItem('Item #14'))"""
    
    
    def onClick(self, controlID):
        if controlID == 12:
            self.getControl(1).setVisibleCondition("False")
            import time
            time.sleep(0.2)
            self.close()
    
    
    def onFocus(self, controlID):
        pass
