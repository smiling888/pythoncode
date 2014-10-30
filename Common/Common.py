#coding=utf-8
'''
   Collection All Code  I Writed
'''
import wx
import os
import sys

def SelfDocStr():
    '''
    | ##@函数目的: 获得本模块功能的描述是对函数/方法/模块所实现功能的简单描述。但当指向具体对象时，会显示此对象从属的类型的构造函数的文档字符串。
    | ##@参数说明：无
    | ##@返回值：Collection All Code  I Writed
    | ##@函数逻辑：
    '''
    return __doc__
def GetSelfFilepath():

    '''
    | ##@函数目的: 返回自己路径
    | ##@参数说明：
    | ##@返回值：假设本文件存在D:\python_workspace目录下，则返回D:\python_workspace\Common.py
    | ##@函数逻辑：
    '''
    return __file__
def LambdaTest(x1,y1):
    #当行的小函数
    g =lambda x,y:x*y
    return g(x1,y1)
    

def GetArgs():
    '''
    | ##@函数目的: 获得执行代码时传入的参数,参数保存在sys.argv(是一个list)中
    | ##@参数说明：
    | ##@返回值：
    | ##@函数逻辑：
    '''
    print 'js:', sys.argv[0]
    #print sys.argv
    #print type(sys.argv)
    for i in range(1,len(sys.argv)):
        print 'canshu:',i,sys.argv[i]

def findStrInPath(path,word):
    '''
    | ##@函数目的: 搜索制定路径path下的所有文件，若文件包含关键字word则进行输出。
    | ##@参数说明：如indStrInPath("C:\\Program Files (x86)\\Desktop_CheckList_TestingTools\\case","wall")
    | ##@返回值：输出包含word文件路径
    | ##@函数逻辑：
    '''
    if not os.path.exists(path):
        print 'path not exits'

    for dirpath,dirnames,filenames in os.walk(path):
        for filename in filenames:
            if filename.find(".txt")!=-1:
                filepath=os.path.join(dirpath,filename)
                f=open(filepath,'r')
                lines=f.readlines()
                for line in lines:
                    if line.find(word)!=-1:
                        print filepath
                        break

def GenLocalIni():
    '''
    | ##@函数目的: 配置升级自动化时使用，生成自动化升级需要的服务器配置文件（用于fiddler转发的）
    | ##@参数说明：path是包含安装包，升级包，helper包相关信息的路径
    | ##@返回值：ini文件夹，文件夹中包含了服务器配置文件
    | ##@函数逻辑：
    '''
    import AutoLocalUpdateIni
    import getpass
    path="c:\\Users\\"+getpass.getuser()+"\\Desktop\\update.ini"
    update=AutoLocalUpdateIni.Update()
    AutoLocalUpdateIni.localupdateini(path,update)
    raw_input("press Enter to finish")

def IsWin7():
    import platform
    version = platform.win32_ver()[1]
    return version.startswith("6.1")

import ctypes
def GetOSBit():
    '''
	| ##@函数目的: 获得机器的位数（32 or 64）
	| ##@参数说明：
	| ##@返回值：返回32 OR 64
	| ##@函数逻辑：
	'''
    i = ctypes.c_int()
    kernel32 = ctypes.windll.kernel32
    process = kernel32.GetCurrentProcess()
    kernel32.IsWow64Process(process, ctypes.byref(i))
    is64bit = (i.value != 0)
    if (is64bit == True):
        return "64"
    else:
        return "32"
def GetDesktopPath(opt= ""):

    '''
	| ##@函数目的: 获取本机（包含xp和win7）Desktop路径，测试脚本中的使用到Desktop路径时统一从这里获取
	| ##@参数说明：无
	| ##@返回值：桌面路径
	| ##@函数逻辑：统一返回Desktop路径
	'''
    if IsWin7():
        str = getpass.getuser()
        strTmp = "C:\\Users\\"
        strTmp = strTmp + str
        strTmp = strTmp + "\\Desktop"
        if opt != "":
            strTmp = strTmp + opt
    else:
        sysDriver=os.getenv("SystemDrive")
        strTmp=sysDriver+os.environ['HOMEPATH']+"\\桌面"
        if opt != "":
            strTmp = strTmp + opt
    return strTmp

def TestUSBDT():
    '''
	| ##@函数目的: 测试USBDT的稳定性时使用
	| ##@参数说明：详情参见usbdt.py
	| ##@返回值：
	| ##@函数逻辑：
	'''
    import usbdt
    usbdt.StartTest()

