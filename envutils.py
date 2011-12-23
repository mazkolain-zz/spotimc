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
