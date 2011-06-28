import struct, os, sys



def set_library_path(root):
    absroot = os.path.abspath(root)
    
    
    #Platform specific paths
    if os.name == "nt":
        plat_chunk = "win32"
    
    #linux == posix, i promise that it's a quirk, not intentional!
    elif os.name == "posix":
        plat_chunk = "linux"
    
    
    #Arch specific paths
    #void pointer size, 32 or 64
    arch = struct.calcsize("P") * 8
    if arch == 32:
        arch_chunk = "x86"
    else:
        arch_chunk = "x86_64"
    
    
    #Build the full path and publish it
    full_path = os.path.join(absroot, plat_chunk, arch_chunk)
    os.environ["PATH"] = full_path + ";" + os.environ["PATH"]
    sys.path.append(full_path)
