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



from __main__ import __addon_path__
import sys, os.path



def set_lib_paths():
    #Set local library paths
    libs_dir = os.path.join(__addon_path__, "resources/libs")
    sys.path.insert(0, libs_dir)
    sys.path.insert(0, os.path.join(libs_dir, "XbmcSkinUtils.egg"))
    sys.path.insert(0, os.path.join(libs_dir, "CherryPy.egg"))
    sys.path.insert(0, os.path.join(libs_dir, "TaskUtils.egg"))
    sys.path.insert(0, os.path.join(libs_dir, "PyspotifyCtypes.egg"))
    sys.path.insert(0, os.path.join(libs_dir, "PyspotifyCtypesProxy.egg"))
