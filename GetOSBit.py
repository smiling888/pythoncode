import ctypes,sys
def GetOSBit():
    i = ctypes.c_int() 
    kernel32 = ctypes.windll.kernel32 
    process = kernel32.GetCurrentProcess() 
    kernel32.IsWow64Process(process, ctypes.byref(i)) 
    is64bit = (i.value != 0)
    if (is64bit == True):
        return "64"
    else:
        return "32"
print GetOSBit()
