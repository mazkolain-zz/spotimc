'''
Created on 12/07/2011

@author: mikel
'''
import xbmc
import xbmcgui



class ViewManager:
    __window = None
    __view_list = None
    __position = None
    
    
    def __init__(self, window):
        self.__window = window
        self.__view_list = []
        self.__position = -1
    
    
    def num_views(self):
        return len(self.__view_list)
    
    
    def position(self):
        return self.__position
    
    
    def has_next(self):
        return(
            self.num_views() > 0
            and self.position() < self.num_views() - 1
        )
    
    
    def _show_view(self, view):
        view.show(self.__window)
        container_id = view.get_container_id()
        if container_id is not None:
            xbmc.executebuiltin("Control.SetFocus(%d)" % container_id)
    
    
    def next(self):
        #Fail if no next window
        if not self.has_next():
            raise IndexError("No more views available")
        
        #If there's one active
        if self.__position != -1:
            self.__view_list[self.__position].hide(self.__window)
        
        #Show the next one
        self.__position += 1
        self._show_view(self.__view_list[self.__position])
    
    
    def has_previous(self):
        return self.__position > 0
    
    
    def previous(self):
        #Fail if no previous window
        if not self.has_previous():
            raise IndexError("No previous views available")
        
        #Hide current
        self.__view_list[self.__position].hide(self.__window)
        
        #Show previous
        self.__position -= 1
        self._show_view(self.__view_list[self.__position])
    
    
    def add_view(self, view):
        #Remove all views that come next (if any)
        del self.__view_list[self.__position:]
        
        #Add the new one
        self.__view_list.append(view)
        
        #Go to the next view
        self.next()
    
    
    def click(self, control_id):
        self.__view_list[self.__position].click(self, self.__window, control_id)



class BaseView:
    def click(self, view_manager, window, control_id):
        pass
    
    def show(self, window):
        pass
    
    def hide(self, window):
        pass
    
    #def get_control(self, window, control_id):
    #    pass
    
    def back(self, window):
        pass
    
    def get_container_id(self):
        pass
