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


import struct, os, sys, platform
from __main__ import __addon_path__


def get_platform():
	if sys.platform.startswith('linux'):
		return 'linux'
	
	elif os.name == 'nt':
		return 'windows'
	
	#TODO: Identify ios and osx properly
	elif sys.platform == 'darwin':
		return 'osx'
	
	#Fail if platform cannot be determined
	else:
		raise OSError('Platform not supported')


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
	platform_str = get_platform()
	arch_str = get_architecture()
    
	if platform_str == 'linux':
		if arch_str in(None, 'x86'):
			add_library_path(os.path.join(base_dir, 'linux/x86'))
		
		if arch_str in(None, 'x86_64'):
			add_library_path(os.path.join(base_dir, 'linux/x86_64'))
		
		if arch_str in(None, 'armv6'):
			add_library_path(os.path.join(base_dir, 'linux/armv6'))
	
	elif platform_str == 'windows':
		if arch_str in(None, 'x86'):
			add_library_path(os.path.join(base_dir, 'windows/x86'))
	
	elif platform_str == 'osx':
		add_library_path(os.path.join(base_dir, 'osx'))
