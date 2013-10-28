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
import sys
import os.path
import platform
import xbmc


def set_library_paths():
    #Set local library paths
    libs_dir = os.path.join(__addon_path__, "resources/libs")
    sys.path.insert(0, libs_dir)
    sys.path.insert(0, os.path.join(libs_dir, "xbmc-skinutils/src"))
    sys.path.insert(0, os.path.join(libs_dir, "cherrypy"))
    sys.path.insert(0, os.path.join(libs_dir, "taskutils/src"))
    sys.path.insert(0, os.path.join(libs_dir, "pyspotify-ctypes/src"))
    sys.path.insert(0, os.path.join(libs_dir, "pyspotify-ctypes-proxy/src"))


def has_background_support():
    return True


def get_architecture():
    try:
        machine = platform.machine()

        #Some filtering...
        if machine.startswith('armv6'):
            return 'armv6'

        elif machine.startswith('i686'):
            return 'x86'

    except:
        return None


def add_dll_path(path):
    #Build the full path and publish it
    full_path = os.path.join(__addon_path__, path)
    sys.path.append(full_path)


def set_dll_paths(base_dir):
    arch_str = get_architecture()

    if xbmc.getCondVisibility('System.Platform.Linux'):
        if arch_str in(None, 'x86'):
            add_dll_path(os.path.join(base_dir, 'linux/x86'))

        if arch_str in(None, 'x86_64'):
            add_dll_path(os.path.join(base_dir, 'linux/x86_64'))

        if arch_str in(None, 'armv6'):
            add_dll_path(os.path.join(base_dir, 'linux/armv6hf'))
            add_dll_path(os.path.join(base_dir, 'linux/armv6'))

    elif xbmc.getCondVisibility('System.Platform.Windows'):
        if arch_str in(None, 'x86'):
            add_dll_path(os.path.join(base_dir, 'windows/x86'))
        else:
            raise OSError('Sorry, only 32bit Windows is supported.')

    elif xbmc.getCondVisibility('System.Platform.OSX'):
        add_dll_path(os.path.join(base_dir, 'osx'))

    elif xbmc.getCondVisibility('System.Platform.Android'):
        add_dll_path(os.path.join(base_dir, 'android'))

    else:
        raise OSError('Sorry, this platform is not supported.')
