'''
Created on 17/07/2011

@author: mikel
'''
from spotymcgui.views import BaseView


class HomeMenuView(BaseView):
    __group_id = 1100
    
    def click(self, window, control_id):
        print "control id %d clicked" % control_id
    
    def show(self, window):
        c = window.getControl(HomeMenuView.__group_id)
        c.setVisibleCondition("true")
        print "show!"
    
    def hide(self, window):
        c = window.getControl(HomeMenuView.__group_id)
        c.setVisibleCondition("false")
        print "hide!"
