'''
Created on 25/06/2011

@author: mikel
'''
import xbmc, xbmcgui
import time
from spotify.session import SessionCallbacks
from spotify import ErrorType



class LoginCallbacks(SessionCallbacks):
    __dialog = None
    
    def __init__(self, dialog):
        self.__dialog = dialog
    
    def logged_in(self, session, err):
        if err == 0:
            self.__dialog.do_close()
        
        else:
            self.__dialog.set_error(err)




class LoginWindow(xbmcgui.WindowXMLDialog):
    #Controld id's
    username_input = 1101
    password_input = 1102
    login_button = 1104
    cancel_button = 1105
    
    __file = None
    __script_path = None
    __skin_dir = None
    __session = None
    __callbacks = None
    
    
    __username = None
    __password = None
    
    
    __cancelled = None 
    
    
    def __init__(self, file, script_path, skin_dir, session):
        self.__file = file
        self.__script_path = script_path
        self.__skin_dir = skin_dir
        self.__session = session
        self.__callbacks = LoginCallbacks(self)
        self.__session.add_callbacks(self.__callbacks)
        self.__cancelled = False


    def onInit(self):
        pass
    
    
    #def onAction(self, action):
    #    pass
    
    def set_error(self, code):
        messages = {
            ErrorType.ClientTooOld: 'Client is too old',
            ErrorType.UnableToContactServer: 'Unable to contact server',
            ErrorType.BadUsernameOrPassword: 'Bad username or password',
            ErrorType.UserBanned: 'User is banned',
            ErrorType.UserNeedsPremium: 'A premium account is required!',
            ErrorType.OtherTransient: 'A transient error occurred. Try again after a few minutes.',
            ErrorType.OtherPermanent: 'A permanent error occurred.',
        }
        
        if code in messages:
            escaped =  messages[code].replace('"', '\"')
            xbmc.executebuiltin('SetProperty(LoginErrorMessage, "%s")' %  escaped)
        else:
            self.setProperty('LoginErrorMessage', 'Unknown error.')
        
        xbmc.executebuiltin('SetProperty(IsLoginError,true)')
    
    
    def _get_input_value(self, controlID):
        c = self.getControl(controlID)
        return c.getLabel()
    
    
    def _set_input_value(self, controlID, value):
        c = self.getControl(controlID)
        c.setLabel(value)
    
    
    def do_login(self):
        remember_set = xbmc.getCondVisibility(
            'Skin.HasSetting(spotymc_session_remember)'
        )
        self.__session.login(self.__username, self.__password, remember_set)
        xbmc.executebuiltin('SetProperty(IsLoginError,false)')
    
    
    def do_close(self):
        self.__session.remove_callbacks(self.__callbacks)
        c = self.getControl(1000)
        c.setVisibleCondition("False")
        time.sleep(0.2)
        self.close()
    
    
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
        
        
        elif controlID == self.login_button:
            self.do_login()
        
        elif controlID == self.cancel_button:
            self.__cancelled = True
            self.do_close()
        
    
    def is_cancelled(self):
        return self.__cancelled
            
    
    def onFocus(self, controlID):
        pass



class PlaylistDialog(xbmcgui.WindowXMLDialog):
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
    
    
    def onClick(self, controlID):
        if controlID == 12:
            self.getControl(1).setVisibleCondition("False")
            import time
            time.sleep(0.2)
            self.close()
    
    
    def onFocus(self, controlID):
        pass
