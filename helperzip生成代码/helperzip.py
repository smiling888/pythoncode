#coding=utf-8
import os
import ctypes,sys
import zipfile
import shutil

import win32api
import win32con
import win32com.client


def OpenReg(key,subKey):
    '''
    函数名：打开注册表
    RegOpenKey(key, subKey , reserved , sam)
    RegOpenKeyEx(key, subKey , reserved , sam)
    key：必须为表10-1中列出的项。
    subKey：要打开的子项。
    reserved：必须为0。
    sam：对打开的子项进行的操作，包括win32con.KEY_ALL_ACCESS、win32con.KEY_READ、win32con. KEY_WRITE等。
    '''
##    if len(key)==0:
##        key1=win32con.HKEY_CURRENT_USER
##
##    if len(subKey)==0:
##        subKey='Software'
    key1=win32api.RegOpenKey(key,subKey,0,win32con.KEY_READ)
    #print key1
    return key1

def CloseReg(key):
    '''
    函数名：关闭注册表  
    '''
    win32api.RegCloseKey(key)
    #print key

    
def ReadReg(key,subKey,valueName):
    '''
    函数名：读取注册表
    调用函数名称：RegQueryValue(key, subKey )
                RegQueryValueEx(key, valueName )
    参数解释：
        key：已打开的注册表项的句柄。

        subKey：要操作的子项。

        对于RegQueryValueEx，其参数含义如下。

        key：已经打开的注册表项的句柄。

        valueName：要读取的项值名称。
    '''
    key=OpenReg(key,subKey)
    value=win32api.RegQueryValueEx(key,valueName)
    CloseReg(key)
    return value[0]

def OS_Bit():
    '''
    函数名：获得系统位数
    返回值：64或者32
    '''
## get os bit

    i = ctypes.c_int() 
    kernel32 =ctypes.windll.kernel32 
    process = kernel32.GetCurrentProcess() 
    kernel32.IsWow64Process(process, ctypes.byref(i)) 
    is64bit = (i.value != 0)
    if (is64bit == True):
        return "64"
    else:
        return "32"

def getOSEnviron():
    '''
    函数名：输出系统环境变量
    返回值：
    '''
    l=os.environ.keys()
    for i in l:
        print i,os.environ[i]

        

def getmd5(filepath):
    '''
    函数名：返回文件的md5值
    返回值：
    '''
    import md5
    f = open(filepath,'rb')
    md5obj = md5.md5()
    md5obj.update(f.read())
    hash1 = md5obj.hexdigest()
    f.close()
    return str(hash1)


def getversion():
    '''
    函数名：通过注册表获得助手版本
    返回值：
    '''
    key=win32con.HKEY_CURRENT_USER
    subKey='SOFTWARE\\SogouMobileTool\\update'
    valueName='MainVersion'
    value=ReadReg(key,subKey,valueName)
    print value
    return value

import getpass
def helperzip():
    if(OS_Bit()=="64"):
        path="C:\\Program Files (x86)\\SogouMobileTool\\"
        
    else:
        path="C:\\Program Files\\SogouMobileTool\\"

    desktop="c:\\Users\\"+getpass.getuser()+"\\Desktop"
    savename="SMTHelperModule.zip"
    #压缩完毕默认保存在和该代码相同的目录
    f = zipfile.ZipFile(savename, 'w' ,zipfile.ZIP_DEFLATED)
    for dirpath, dirnames, filenames in os.walk(path, True):
        for filename in filenames:
            if filename=="PopupCond.dll":
                direactory = os.path.join(dirpath,filename)
                print direactory
                
                f.write(direactory,'PopupCond.dll')
            if  filename=="SMTHelperModule.dll":
                direactory = os.path.join(dirpath,filename)
                print direactory
                f.write(direactory,'SMTHelperModule.dll')   
    f.close()

    #将其移动到桌面
    desktopzip=desktop+"\\"+savename
    if os.path.exists(desktopzip):
        os.remove(desktopzip)
    zippath=os.getcwd()+"\\"+savename
    shutil.move(zippath,desktop)

    #计算md5和文件大小
    #version=raw_input('version:')
    hpversion="hpversion="+str(getversion())
    hpfilesize="hpfilesize="+str(os.path.getsize(desktopzip))
    hpmd5="hpmd5="+str(getmd5(desktopzip))
    hpurl="hpurl=http://download.zhushou.sogou.com/SogouMobileTool/SMTHelperModule.zip"
    
    f=open(desktop+"\\update.ini",'w')
    f.write(hpversion+"\n")
    f.write(hpfilesize+"\n")
    f.write(hpmd5+"\n")
    f.write(hpurl+"\n")
    f.close()
helperzip()
raw_input("press Enter to finish")
