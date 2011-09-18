'''
Created on 22/08/2011

@author: mikel
'''
import xbmcgui
from spotymcgui.views import BaseView


class PlaylistView(BaseView):
    __group_id = 1700
    __list_id = 1701
    
    
    def click(self, view_manager, window, control_id):
        pass
    
    
    def _get_list(self, window):
        return window.getControl(PlaylistView.__list_id)
    
    
    def _add_playlist(self, list, name, thumb_list=[], collaborative=False, num_tracks="", duration=""):
        item = xbmcgui.ListItem()
        item.setProperty("PlaylistName", name)
        item.setProperty("PlaylistNumTracks", str(num_tracks))
        item.setProperty("PlaylistDuration", str(duration))
        thumb_list = thumb_list[:4]
        
        if len(thumb_list) > 0:
            #Set cover info
            if len(thumb_list) == 1:
                item.setProperty("CoverLayout", "one")
            else:
                item.setProperty("CoverLayout", "four")
            
            #Now loop to set all the images
            for idx, thumb_item in enumerate(thumb_list[:4]):
                print "adding thumb item: %s" % thumb_item
                item.setProperty("CoverItem%d" % (idx + 1), thumb_item)
        
        list.addItem(item)
    
    
    def _populate_list(self, window):
        l = self._get_list(window)
        l.reset()
        
        multi_cover = [
            "http://www.halogendesigns.com/blog/wp-content/uploads/cover1.jpg",
            "http://2.bp.blogspot.com/-ALJZJztSDLA/TkR6ggCVQmI/AAAAAAAAGJk/BZT3Rf2vkuU/s1600/abbey_road_album_cover.jpg",
            "http://images.mirror.co.uk/upl/dailyrecord3/oct2009/4/8/susan-boyle-album-cover-image-1-733838072.jpg",
            "http://www.cddesign.com/covertalk/images/dark-side-of-the-moon-cd-cover-design.jpg",
        ]
        
        one_cover = [
            "http://www.eljinetepalido.es/wp-content/uploads/weezer-raditude-album-cover1.jpg",
        ]
        
        one_cover2 = [
            "http://media.smashingmagazine.com/images/music-cd-covers/43.jpg",
        ]
        
        portrait_cover = [
            "http://youlook.files.wordpress.com/2011/07/img_7446web.jpg",
        ]
        
        mixed_pl = [
            "http://www.halogendesigns.com/blog/wp-content/uploads/cover1.jpg",
            "http://2.bp.blogspot.com/-ALJZJztSDLA/TkR6ggCVQmI/AAAAAAAAGJk/BZT3Rf2vkuU/s1600/abbey_road_album_cover.jpg",
            "http://images.mirror.co.uk/upl/dailyrecord3/oct2009/4/8/susan-boyle-album-cover-image-1-733838072.jpg",
            "http://youlook.files.wordpress.com/2011/07/img_7446web.jpg",
        ]
        
        self._add_playlist(l, "Playlist 1", multi_cover, False, 140, "16 hours")
        self._add_playlist(l, "Playlist 2", one_cover2, False, 356, "1 day")
        self._add_playlist(l, "Playlist 3", one_cover, False, 16, "35 minutes")
        self._add_playlist(l, "Playlist 4", multi_cover, False, 17)
        self._add_playlist(l, "Playlist 5", portrait_cover)
        self._add_playlist(l, "Playlist 6", portrait_cover)
        self._add_playlist(l, "Playlist 7", mixed_pl)
        self._add_playlist(l, "Playlist 8")
    
    
    def show(self, window):
        self._populate_list(window)
        c = window.getControl(PlaylistView.__group_id)
        
        c.setVisibleCondition("true")
        print "show!"
    
    
    def hide(self, window):
        c = window.getControl(PlaylistView.__group_id)
        c.setVisibleCondition("false")
        print "hide!"
