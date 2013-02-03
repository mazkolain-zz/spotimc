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


import xbmc
import struct, os, sys, platform
from __main__ import __addon_path__



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


def add_library_path(path):
    #Build the full path and publish it
    full_path = os.path.join(__addon_path__, path)
    sys.path.append(full_path)


def set_library_paths(base_dir):
	arch_str = get_architecture()
	
	if xbmc.getCondVisibility('System.Platform.Linux'):
		if arch_str in(None, 'x86'):
			add_library_path(os.path.join(base_dir, 'linux/x86'))
		
		if arch_str in(None, 'x86_64'):
			add_library_path(os.path.join(base_dir, 'linux/x86_64'))
		
		if arch_str in(None, 'armv6'):
			add_library_path(os.path.join(base_dir, 'linux/armv6hf'))
			add_library_path(os.path.join(base_dir, 'linux/armv6'))
	
	elif xbmc.getCondVisibility('System.Platform.Windows'):
		if arch_str in(None, 'x86'):
			add_library_path(os.path.join(base_dir, 'windows/x86'))
		else:
			raise OSError('Sorry, only 32bit Windows is supported.')
	
	elif xbmc.getCondVisibility('System.Platform.OSX'):
		add_library_path(os.path.join(base_dir, 'osx'))
	
	else:
		raise OSError('Sorry, this platform is not supported.')
