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


import struct, os, sys


def get_platform_path():
    arch = struct.calcsize("P") * 8
    
    if os.name == "nt":
        if arch == 32:
            return 'windows/x86'
            
        elif arch == 64:
            raise OSError('Windows x86_64 is not supported.')
    
    elif os.name == "posix":
        if sys.platform.startswith('linux'):
            if arch == 32:
                return 'linux/x86'
            
            elif arch == 64:
                return 'linux/x86_64'
        
        elif sys.platform == 'darwin':
            return 'osx'


def set_library_path(root):
    #Build the full path and publish it
    full_path = os.path.join(os.path.abspath(root), get_platform_path())
    os.environ["PATH"] = full_path + ";" + os.environ["PATH"]
    sys.path.append(full_path)
