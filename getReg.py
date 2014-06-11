#coding=utf-8
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
#读取
##key='HKEY_CURRENT_USER'#win32con.HKEY_CURRENT_USER
##subKey='SOFTWARE\\SogouMobileTool'
##valueName='Path'
##value=ReadReg(key,subKey,valueName)
##print value


def getReg():
    
    
    winSourceServer = win32com.client.Dispatch("Sogou_WindowResource.WinResourceRetriver")
    itemName='HKEY_CURRENT_USER\\SOFTWARE\\SogouMobileTool'
    keyName="path"
    result = winSourceServer.GetRegValue(itemName, keyName)
    print result
    
getRe()
