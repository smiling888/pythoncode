#  -*- coding:utf-8 -*- 

from ctypes import * 

 

# 定义_PROCESS_INFORMATION结构体

class _PROCESS_INFORMATION(Structure):

    _fields_ = [('hProcess', c_void_p),

                ('hThread', c_void_p),

                ('dwProcessId', c_ulong),

                ('dwThreadId', c_ulong)]

 

# 定义_STARTUPINFO结构体

class _STARTUPINFO(Structure):

    _fields_ = [('cb',c_ulong),

                ('lpReserved', c_char_p),

                ('lpDesktop', c_char_p),

                ('lpTitle', c_char_p),

                ('dwX', c_ulong),

                ('dwY', c_ulong),

                ('dwXSize', c_ulong),

                ('dwYSize', c_ulong),

                ('dwXCountChars', c_ulong),

                ('dwYCountChars', c_ulong),

                ('dwFillAttribute', c_ulong),

                ('dwFlags', c_ulong),

                ('wShowWindow', c_ushort),

                ('cbReserved2', c_ushort),

                ('lpReserved2', c_char_p),

                ('hStdInput', c_ulong),

                ('hStdOutput', c_ulong),

                ('hStdError', c_ulong)]

 

NORMAL_PRIORITY_CLASS = 0x00000020 #定义NORMAL_PRIORITY_CLASS

kernel32 = windll.LoadLibrary("kernel32.dll")  #加载kernel32.dll

CreateProcess = kernel32.CreateProcessA   #获得CreateProcess函数地址

ReadProcessMemory = kernel32.ReadProcessMemory #获得ReadProcessMemory函数地址

WriteProcessMemory = kernel32.WriteProcessMemory #获得WriteProcessMemory函数地址

TerminateProcess = kernel32.TerminateProcess

 

# 声明结构体

ProcessInfo = _PROCESS_INFORMATION()

StartupInfo = _STARTUPINFO()

fileName = 'c:/windows/notepad.exe'       # 要进行修改的文件

address = 0x0040103c        # 要修改的内存地址

strbuf = c_char_p("_")        # 缓冲区地址

bytesRead = c_ulong(0)       # 读入的字节数

bufferSize =  len(strbuf.value)     # 缓冲区大小

 

# 创建进程 

CreateProcess(fileName, 0, 0, 0, 0, NORMAL_PRIORITY_CLASS,0, 0, byref(StartupInfo), byref(ProcessInfo))
