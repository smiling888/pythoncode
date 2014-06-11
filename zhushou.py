#coding=utf-8
import os
import traceback
import subprocess
from shutil import copy
import getpass
import string
import ConfigParser
import win32api
import win32con



def GetZhushouVersion():
	'''
	| ##@函数目的: 获取搜狗手机助手的版本，测试脚本中的使用到版本号时统一从这里获取
	| ##@参数说明：无
	| ##@返回值：无
	| ##@函数逻辑：统一设置版本号
	'''
	return "2.5.0.19022"
    
def GetQNum():
    '''
	| ##@函数目的: 获取搜狗手机助手的版本，测试脚本中的使用到版本号时统一从这里获取
	| ##@参数说明：无
	| ##@返回值：无
	| ##@函数逻辑：统一设置版本号
	'''
    return "000000"
    

def ShowCaseNum(num):
    '''
	| ##@函数目的: 显示执行case进度
	| ##@参数说明：无
	| ##@返回值：无
	| ##@函数逻辑：统一设置版本号
	'''
    import ctypes
#    ctypes.windll.user32.MessageBoxA(0,  'case '+str(num),"case number", 0)
    import time
    newpath="d:\\autotest\\log\\"
    if not os. path.isdir(newpath):
        os.makedirs(newpath)
    name=newpath+"log.txt"
    if not fileIsExists(name):
        f=open(name,'w')      
    else:
        f=open(name,'a')
    f.write(time.strftime("%Y-%m-%d:%H-%M-%S",time.localtime(time.time()))+'        case '+str(num))
    f.write("\n")
    f.close()

def GetTempPath(opt= ""):

    '''
	| ##@函数目的: 获取本机temp路径，测试脚本中的使用到temp路径时统一从这里获取
	| ##@参数说明：无
	| ##@返回值：路径
	| ##@函数逻辑：统一返回temp路径
	'''
    str = getpass.getuser()
    strTmp = "C:\\Users\\"
    strTmp = strTmp + str
    strTmp = strTmp + "\\AppData\\Local\\Temp"
    if opt != "":
        strTmp = strTmp + opt
    return strTmp

def fileIsExists(filepath=''):

    '''
	| ##@函数目的: 判断filepath指向的文件是否存在
	| ##@参数说明：无
	| ##@返回值：路径
	| ##@函数逻辑：统一返回temp路径
	'''
    return  os.path.isfile(filepath)
    
def DelSMTShareFiles(path):
    '''
    |##@删除SMTShare目录下的安装包
    | ##@参数说明：无
    | ##@返回值：1
    | ##@函数逻辑：返回1 表示删除完成或者没有该文件
    '''
    allfilesname=os.listdir(path)
    for name in allfilesname:
        if name.find('SogouMobileToolSetup')!=-1:
           fullpath=os.path.join(path,name)
           os.remove(fullpath)
    return 1 
    

def DelTempFile(tmpFileName):

    '''
	| ##@函数目的: 删除temp目录下的文件
	| ##@参数说明：无
	| ##@返回值：1
	| ##@函数逻辑：返回1 表示删除完成或者没有该文件
	'''
    flag = os.path.isfile(tmpFileName)
    if flag == 1:
        try:
            os.remove(tmpFileName)
        except Exception,e:
            print e
    return 1

def GetAppdataPath(opt= ""):

    '''
	| ##@函数目的: 获取本机appdata路径，测试脚本中的使用到appdata路径时统一从这里获取
	| ##@参数说明：无
	| ##@返回值：路径
	| ##@函数逻辑：统一返回appdata路径
	'''
    str = getpass.getuser()
    strTmp = "C:\\Users\\"
    strTmp = strTmp + str
    strTmp = strTmp + "\\AppData\\Roaming\\SogouMobileTool\\SogouMobileToolUp\\Files"
    if opt != "":
        strTmp = strTmp + opt
    return strTmp

def DelAppdataFile(tmpFileName):

    '''
	| ##@函数目的: 删除appdata目录下的文件
	| ##@参数说明：无
	| ##@返回值：1
	| ##@函数逻辑：返回1 表示删除完成或者没有该文件
	'''
    flag = os.path.isfile(tmpFileName)
    if flag == 1:
        os.remove(tmpFileName)
    return 1

def DelAppdataFileHelper():
    '''
    |##@删除目录下的安装包
    | ##@参数说明：无
    | ##@返回值：1
    | ##@函数逻辑：返回1 表示删除完成或者没有该文件
    '''
    appdatafilepath=GetAppdataPath()
    allfilesname=os.listdir(appdatafilepath)
    for name in allfilesname:
        if name.find('SMTHelperModule')!=-1:
           fullpath=os.path.join(appdatafilepath,name)
           os.remove(fullpath)
    return 1
    

def DelAppdataFileExe():
    '''
    |##@删除目录下的安装包
    | ##@参数说明：无
    | ##@返回值：1
    | ##@函数逻辑：返回1 表示删除完成或者没有该文件
    '''
    appdatafilepath=GetAppdataPath()
    allfilesname=os.listdir(appdatafilepath)
    for name in allfilesname:
        if name.find('SogouMobileToolSetup')!=-1:
           fullpath=os.path.join(appdatafilepath,name)
           try:
               os.remove(fullpath)
           except Exception,e:
               print e
    return 1 
    
def DelAppdataFileUp():
    '''
    |##@删除目录下的升级包
    | ##@参数说明：无
    | ##@返回值：1
    | ##@函数逻辑：返回1 表示删除完成或者没有该文件
    '''
    appdatafilepath=GetAppdataPath()
    allfilesname=os.listdir(appdatafilepath)
    for name in allfilesname:
        if name.find('Up')!=-1:
           fullpath=os.path.join(appdatafilepath,name)
           try:
               os.remove(fullpath)
           except Exception,e:
               print e
    return 1 
    
def DelAppdataFileUp():
    '''
	| ##@函数目的: 删除appdata目录下的升级包文件
	| ##@参数说明：无
	| ##@返回值：1
	| ##@函数逻辑：返回1 表示删除完成或者没有该文件
	'''
    appdatafilepath=GetAppdataPath()
    allfilesname=os.listdir(appdatafilepath)
    for name in allfilesname:
        if name.find('Up')!=-1:
            fullpath=os.path.join(appdatafilepath,name)
            os.remove(fullpath)
    return 1

def HasNewestUp(version=""):
    '''
	| ##@函数目的: appdata目录下的升级文件是否是最新的
	| ##@参数说明：up文件版本
	| ##@返回值：True
	| ##@函数逻辑：返回True 表示只剩下最新的升级包或者没有升级包 false
	'''
    appdatafilepath=GetAppdataPath()
    allfilesname=os.listdir(appdatafilepath)
    upfile=0
    newestUp=0
    print version
    for name in allfilesname:
        if name.find('Up')!=-1:
            upfile+=1
            if name.find(version)!=-1:
                newestUp+=1
    return upfile==newestUp

def GetDesktopPath(opt= ""):

    '''
	| ##@函数目的: 获取本机Desktop路径，测试脚本中的使用到Desktop路径时统一从这里获取
	| ##@参数说明：无
	| ##@返回值：路径
	| ##@函数逻辑：统一返回Desktop路径
	'''
    str = getpass.getuser()
    strTmp = "C:\\Users\\"
    strTmp = strTmp + str
    strTmp = strTmp + "\\Desktop"
    if opt != "":
        strTmp = strTmp + opt
    return strTmp

def CopySrcFileToDestFile(src = "",dest = ""):
    '''
	| ##@函数目的: 拷贝文件到file目录
	| ##@参数说明：无
	| ##@返回值：路径
	| ##@函数逻辑：
	'''
    copy(src,dest);
    return 1;

def ChangeUpdateType(opt= "Notify"):

    '''
	| ##@函数目的: 改变升级方式，即改变设置中checkbox的勾选状态
	| ##@参数说明：无
	| ##@返回值：1，当文件不存在时，说明是初次安装，初次安装默认updateType=‘auto’
	| ##@函数逻辑：修改正确，返回1
	'''
    str = getpass.getuser()
    strTmp = "C:\\Users\\"
    strTmp = strTmp + str
    strTmp = strTmp + "\\AppData\\Roaming\\SogouMobileTool\\PDAData\\versionControl.ini"
    if not os.path.isfile(strTmp):
        print 'ChangeUpdateType fisrt install'        
        return 1
    input   = open(strTmp)
    lines   = input.readlines()
    input.close()

    output  = open(strTmp,'w');
    for line in lines:
                #print line
                if not line:
                        break
                if 'updateType=' in line:
                        temp    = "updateType="
                        temp1   = temp + opt
                        temp1 = temp1 + "\n"
                        output.write(temp1)
                else:
                        output.write(line)
    output.close()
    print 'ChangeUpdateType changed'        
    return 1


import DesktopCommon
def GetSikulyPath():
    '''
	| ##@函数目的: 获取斯库里的执行路径，测试脚本中的使用到版本号时统一从这里获取
	| ##@参数说明：无
	| ##@返回值：无
	| ##@函数逻辑：统一返回斯库里路径
	'''
    path = "D:\\sikuli\\runIDE.cmd -r "
    return path

def GetSikulipath():
    '''
	| ##@函数目的: 获取sikuli IDE路径，测试脚本中的使用到IDE路径时统一从这里获取
	| ##@参数说明：无
	| ##@返回值：路径
	| ##@函数逻辑：
	'''
    return "D:\\sikuli\\runIDE.cmd"

def GetSikuliScriptPath():
    '''
	| ##@函数目的: 获取sikuli 脚本的保存路径
	| ##@参数说明：无
	| ##@返回值：路径
	| ##@函数逻辑：
	'''
    return ""

def GetSikuliexePath(opt = "\\updateModule\\update_checkbox.sikuli"):
    '''
	| ##@函数目的: 获取sikuli脚本路径，测试脚本中的使用到路径时统一从这里获取
	| ##@参数说明：无
	| ##@返回值：路径
	| ##@函数逻辑：
	'''
    str = "D:\\autotest\\sikuliscript"
    str = str + opt
    return str

def GetLocalHelperVersion(version=''):
    '''
	| ##@函数目的: 获取指定助手版本下的helper版本，
	| ##@参数说明：已经安装的助手的版本
	| ##@返回值：路径
	| ##@函数逻辑：
	'''
    if version=='':
        version=GetZhushouVersion()
    path=DesktopCommon.GetRegValue("HKEY_CURRENT_USER\\Software\\SogouMobileTool","Path")
    file_name=path+"\\"+version+"\\SMTHelperModule.dll"
    info = win32api.GetFileVersionInfo(file_name, os.sep)
    ms = info['FileVersionMS']
    ls = info['FileVersionLS']
    version = '%d.%d.%d.%04d' % (win32api.HIWORD(ms), win32api.LOWORD(ms), win32api.HIWORD(ls), win32api.LOWORD(ls))
    return version


def GetDesktopZsVersion():

    '''
	| ##@函数目的: 获取在本机桌面上的搜狗手机助手的版本
	| ##@参数说明：无
	| ##@返回值：路径
	| ##@函数逻辑：统一返回Desktop版本
	'''
    vartop = GetDesktopPath()
    varver = GetZhushouVersion()
    vartop = vartop + "\\SogouMobileToolSetup_"
    vartop = vartop + varver
    vartop = vartop + "_"+GetQNum()+".exe"
    return vartop


def GetLoaclh():
    return "BAE74E6A0F6C3E89F979F7EE4589DE83"

def RunCmd(cmd):
	'''
	| ##@函数目的: 运行cmd并输入参数
	| ##@参数说明：在cmd内传入的参数
	| ##@返回值：cmd内的输出
	| ##@函数逻辑：
	'''
        if len(cmd) < 5:
            print "!!!!Command is invalid!!!!"
            return "!!!!Command is invalid!!!!"
	p = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        strout, strerr = p.communicate()

	return strout


def RunSikuli(cmd):
	'''
	| ##@函数目的: 运行sikuli
	| ##@参数说明：调用sikuli的命令行参数
	| ##@返回值：0表示sikuli中case执行成功，-1表示sikuli中case有失败
	| ##@函数逻辑：调用sikuli并读取命令行返回信息，打印错误信息
	| ##@zsret=failed和zsret=succeed是包含在sikuli正确和错误输出
	'''
	#cmd = "D:\\Script\\sikuli\\runIDE.cmd -r C:\\Users\\zhangshuai203407\\Desktop\\123.skl"
	try:
		str1 = RunCmd(cmd).lower()
                print str1
		if str1.find("zsret=failed") != -1:

			return -1
		if str1.find("zsret=succeed") != -1:
			return 0

	except:
            traceback.print_exc()
	return -1




def DisableUSB(vid = ""):
	if vid == "":
		cmd = "devcon.exe disable USB\\VID_****"
		print RunCmd(cmd)
	else:
		cmd = "devcon.exe disable USB\\VID_" + vid + "*"
		print RunCmd(cmd)

def EnableUSB(vid = ""):
	if vid == "":
		cmd = "devcon.exe enable USB\\VID_****"
		print RunCmd(cmd)
	else:
		cmd = "devcon.exe enable USB\\VID_" + vid + "*"
		print RunCmd(cmd)


def CheckZhushouDirFileNum(zsPath):
    import sys
    files = os.listdir(zsPath)
    if len(files) == 20 or len(files) == 21:
        return 0
    return len(files)

def GetProcessNum(processName):
    '''
	| ##@函数目的: 检查指定名字进程的数目
	| ##@参数说明：无
	| ##@返回值：进程数量
	| ##@函数逻辑：遍历比较
	'''
    import psutil
    num = 0
    processList = list(psutil.process_iter())
    for process in processList:
        try:
            if process.name.lower() == processName.lower():
                num += 1
        except:
            continue
    return num

def GetSgMobileToolSetupProcessNum():
    return GetProcessNum("SogouMobileToolSetup_"+GetZhushouVersion()+"_"+GetQNum()+".exe")

def GetZSUninstallNumAndKill(ifKill = False):
    '''
	| ##@函数目的: 获取助手卸载进程数，并通过标志位觉得是否kill
	| ##@参数说明：标志是否kill卸载进程
	| ##@返回值：进程数量
	| ##@函数逻辑：遍历正则比较
	'''
    import psutil
    import re
    # 将正则表达式编译成Pattern对象
#    pattern = re.compile(r'~PA...\.tmp\.exe')
    cnt = 0
    processList = list(psutil.process_iter())
    for process in processList:
        try:
            if process.name.find("~PA")!=-1 and process.name.find(".tmp.exe")!=-1:
            #pattern.match(process.name) != None:
                cnt += 1
                if ifKill:
                    DesktopCommon.StopProcess(process.name)
        except:
            continue
    return cnt

def GetSgMobileUninstallProcessNum():
    return GetProcessNum("SogouPAUnInstall.exe")+GetZSUninstallNumAndKill()


def CheckFeedbackURL(url):
    if len(url)==0:
        print "url len == 0 !!!"
        return False
    paraList = url.split("?")
    if len(paraList) != 2:
        print "url len is wrong!!!!!!!"
        return False
    keyvalues = paraList[1].split("&")
    if len(keyvalues) != 3:
        return False
    for para in keyvalues:
        values = para.split("=")
        if len(values) != 2:
            return False
        if values[0] == "r":
            if values[1] != "000000":
                return False
        elif values[0] == "h":
            if values[1] != GetLoaclh():
                return False
        elif values[0] == "v":
            if values[1] != GetZhushouVersion():
                return False
    return True


def ResetEnv():
    GetZSUninstallNumAndKill(True)
    if DesktopCommon.IsProcessExist("SogouMobileTool.exe"):
        DesktopCommon.StopProcess("SogouMobileTool.exe")
    setupName = "SogouMobileToolSetup_"+GetZhushouVersion()+"_000000.exe"
    if DesktopCommon.IsProcessExist(setupName):
        DesktopCommon.StopProcess(setupName)
    sikulipath = GetSikulyPath()
    zsUninstallString = DesktopCommon.GetRegValue("HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\SogouMobileTool","UninstallString")
    if len(zsUninstallString)!=0:
        RunCmd("\""+zsUninstallString+"\"")
        ret = RunSikuli(sikulipath+"E:\\Install_Uninstall\\UninstallDirectly.skl")

    if DesktopCommon.IsProcessExist("SogouPAUnInstall.exe"):
        DesktopCommon.StopProcess("SogouPAUnInstall.exe")
    if DesktopCommon.IsProcessExist("SogouMobileTool.exe"):
        DesktopCommon.StopProcess("SogouMobileTool.exe")
    setupName = "SogouMobileToolSetup_"+GetZhushouVersion()+"_"+GetQNum()+".exe"
    if DesktopCommon.IsProcessExist(setupName):
        DesktopCommon.StopProcess(setupName)
        
def backupUserData():
    '''
	| ##@函数目的: 备份用户数据，以便之后判断是否改变
	| ##@参数说明：升级类型，渠道号
	| ##@返回值：是否正确
	| ##@函数逻辑：遍历比较
	'''
    src=DesktopCommon.GetAppPath() + "\\SogouMobileTool\\PDAData\\versionControl.ini"
    dest="D:\\versionControl.ini"
    if os.path.isfile(dest):
        os.remove(dest)
    copy(src,dest);
    return 1


def CheckUserData(updateType="Auto",routeNum="000000"):
    '''
	| ##@函数目的: 校验用户数据是否被重置
	| ##@参数说明：升级类型，渠道号
	| ##@返回值：是否正确
	| ##@函数逻辑：遍历比较
	'''

    cf1 = ConfigParser.ConfigParser()
    cf2 = ConfigParser.ConfigParser()
    cf1.read("D:\\versionControl.ini")
    cf2.read(DesktopCommon.GetAppPath() + "\\SogouMobileTool\\PDAData\\versionControl.ini")
    if not os.path.exists("D:\\versionControl.ini"):
        print 'D:\\versionControl.ini does not exists'
    
    print "CheckUserData "
    approute = cf2.get("General","Route")
    if routeNum != approute and "\""+routeNum+"\"" != approute:
        print "routeNum"
        return False
    updateType=cf1.get("Setting","updateType")
    appUpType = cf2.get("Setting","updateType")
    if appUpType != updateType:
        print "appUpType"
        print appUpType
        print updateType
        return False

    autoConn = cf1.get("Setting","autoConn")
    appAutoConn = cf2.get("Setting","autoConn")
    if autoConn != appAutoConn:
        print 'appAutoConn'
        return False

    savePath = cf1.get("Setting","savePath")
    appSavePath = cf2.get("Setting","savePath")
    if savePath != appSavePath:
        print 'savePath'
        return False

    apk1= cf1.get("Setting","apk")
    appApk = cf2.get("Setting","apk")
    if apk1 != appApk:
        print 'apk'
        return False

##    ManuClose = cf1.get("AppUpReminder","ManuClose")
##    appManuClose = cf2.get("AppUpReminder","ManuClose")
##    if ManuClose != appManuClose:
##        print 'ManuClose'
##        return False

##    NoRemind = cf1.get("AppUpReminder","NoRemind")
##    appNoRemind = cf2.get("AppUpReminder","NoRemind")
##    if NoRemind != appNoRemind:
##        print 'NoRemind'
##        return False

##    AppConfirm = cf1.get("ConfirmDlgNoShow","AppConfirm")
##    appAppConfirm = cf2.get("ConfirmDlgNoShow","AppConfirm")
##    if AppConfirm != appAppConfirm:
##        print 'AppConfirm'
##        return False

##    LastExamTime = cf1.get("Optimize","LastExamTime")
##    appLastExamTime = cf2.get("Optimize","LastExamTime")
##    if LastExamTime != appLastExamTime:
##        print 'LastExamTime'
##        return False

    return True

def RenameSrcFileToDestFile(src = "",dest = ""):
    '''
	| ##@函数目的: 重命名文件
	| ##@参数说明：无
	| ##@返回值：
	| ##@函数逻辑：
	'''
    os.rename(src,dest);
    return 1

def RunFiddler():
    '''
	| ##@函数目的: 运行fiddler,
	| ##@参数说明：无
	| ##@返回值：
	| ##@函数逻辑：应先在注册表中写入fiddler的启动项（让fillder开机启动就会有相应的启动项）
	'''
    FiddlerExEPath = DesktopCommon.GetRegValue("HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run","Fiddler")
    DesktopCommon.StartProcess(FiddlerExEPath)
    return 1

def CheckUpdateTypeData(updateType="Auto"):
    '''
	| ##@函数目的: 校验用户数据是否被重置
	| ##@参数说明：升级类型
	| ##@返回值：是否正确
	| ##@函数逻辑：遍历比较
	'''
    cf2 = ConfigParser.ConfigParser()
    cf2.read(DesktopCommon.GetAppPath() + "\\SogouMobileTool\\PDAData\\versionControl.ini")
    appUpType = cf2.get("Setting","updateType")
    if appUpType != updateType:
        return False
    return True

def CheckRouteData(routeNum="000000"):
    '''
	| ##@函数目的: 校验用户数据是否被重置
	| ##@参数说明：渠道号
	| ##@返回值：是否正确
	| ##@函数逻辑：遍历比较
	'''
    cf2 = ConfigParser.ConfigParser()
    cf2.read(DesktopCommon.GetAppPath() + "\\SogouMobileTool\\PDAData\\versionControl.ini")

    approute = cf2.get("General","Route")
    if routeNum != approute and "\""+routeNum+"\"" != approute:
        return False
    return True

def CheckUserIsWhat(opt = "English"):

    '''
	| ##@函数目的: 判断本机账户名是否为英文或者是中文
	| ##@参数说明：无
	| ##@返回值：路径
	| ##@函数逻辑：只对全是英文或全是中文的进行判断，对中英文混合情况不处理
	'''
    str = getpass.getuser()
    #slength = len(str)
    #strTemp  = str.split()
    #for i in range(0, slength-1):
        #strTemp[i]=strTemp[i].decode("utf8")
    if(opt == "English"):
       if(is_alphabet(str[0:1]) == False ):
            return False
    if(opt == "Chinese"):
       if(is_alphabet(str[0:1]) == True ):
            return False
    return True

def is_alphabet(uchar):
    '''
	| ##@函数目的: 判断字符是否为英文字符
	| ##@参数说明：无
	| ##@返回值：
	| ##@函数逻辑：
	'''
    if (uchar >= u'\u0041' and uchar<=u'\u005a') or (uchar >= u'\u0061' and uchar<=u'\u007a'):
        return True
    else:
        return False

def windowsKeyboardImitate(opt1 = "win",opt2 = "d"):
    '''
	| ##@函数目的: 显示桌面，让桌面无遮挡物
	| ##@参数说明：无
	| ##@返回值：
	| ##@函数逻辑：
	'''
    win32api.keybd_event(91,0,0,0)  #win键位码是91
    win32api.keybd_event(68,0,0,0)  #d键位码是68
    win32api.keybd_event(68,0,win32con.KEYEVENTF_KEYUP,0) #释放按键
    win32api.keybd_event(91,0,win32con.KEYEVENTF_KEYUP,0)

def GetAppdataCrashPath(opt= ""):

    '''
	| ##@函数目的: 获取本机appdata路径下的crash文件取
	| ##@参数说明：无
	| ##@返回值：路径
	| ##@函数逻辑：
	'''
    str = getpass.getuser()
    strTmp = "C:\\Users\\"
    strTmp = strTmp + str
    strTmp = strTmp + "\\AppData\\Roaming\\SogouMobileTool\\Log"
    if opt != "":
        strTmp = strTmp + opt
    return strTmp

def delete_file_folder(src):
    '''
	| ##@函数目的: 删除文件夹
	| ##@参数说明：无
	| ##@返回值：1
	| ##@函数逻辑：返回1 表示删除完成或者没有该文件
	'''
    if os.path.isfile(src):
        try:
            os.remove(src)
        except:
            pass
    elif os.path.isdir(src):
        for item in os.listdir(src):
            itemsrc=os.path.join(src,item)
            delete_file_folder(itemsrc)
        try:
            os.rmdir(src)
        except:
            pass

def MonitorCrashAndRename(opt1,opt2):
    '''
	| ##@函数目的: 查看appdata下是否产生crash，如果产生，直接剪切到Perfmonitor目录下的Log日志文件夹中，并重命名为Case编号
	| ##@参数说明：opt1表示crash路径，opt2为casex.zip
	| ##@返回值：
	| ##@函数逻辑：
	'''
    src = opt1 + "\\CrashReport.zip"
    dst = opt1 + "\\" + opt2
    fmpath = DesktopCommon.GetFrameworkPath()
    fmpath = fmpath + "\\util\\Perfmonitor\\log"
    if os.path.isfile(src):
        try:
            RenameSrcFileToDestFile(src,dst)
            CopySrcFileToDestFile(dst,fmpath)
            DelAppdataFile(dst)
        except:
            pass
def CheckReg(quickLaunch=False):
    '''
	| ##@函数目的: 检查注册表各项是否正确
	| ##@参数说明：opt1表示crash路径，opt2为casex.zip
	| ##@返回值：
	| ##@函数逻辑：
	'''
    #检查有的项
    #Path
    value=DesktopCommon.GetRegValue("HKEY_CURRENT_USER\\Software\\SogouMobileTool","Path")
    if DesktopCommon.IsWin7():
        if value!="C:\\Program Files (x86)\\SogouMobileTool":
        print value,'path'
        return False
    elif value!="C:\\Program Files\\SogouMobileTool":
        print value,'path'
        return False
    #Components
    exist=DesktopCommon.IsRegExist("HKEY_CURRENT_USER\\Software\\SogouMobileTool\\Components")
    
    if not exist:
        print exist,'components'
        return False
    
    #pb
    exist=DesktopCommon.IsRegExist("HKEY_CURRENT_USER\\Software\\SogouMobileTool\\pb")
    
    if not exist:
        print exist,'pb'
        return False
    #PopUpConfig助手弹窗设置的
##    exist=DesktopCommon.IsRegExist("HKEY_CURRENT_USER\\Software\\SogouMobileTool\\PopUpConfig")
##    if not exist:
##        print exist
##        return False
    #Update
    exist=DesktopCommon.IsRegExist("HKEY_CURRENT_USER\\Software\\SogouMobileTool\\Update")
    if not exist:
        print exist,'update'
        return False
    #Update 之Desktop
    value=DesktopCommon.GetRegValue("HKEY_CURRENT_USER\\Software\\SogouMobileTool\\Update","Desktop")
    if value!="create":
        print value,'create'
        return False
    #Update 之MainVersion
    value=DesktopCommon.GetRegValue("HKEY_CURRENT_USER\\Software\\SogouMobileTool\\Update","MainVersion")
    if value!=str(GetZhushouVersion()):
        print value,'MainVersion'
        return False
    #Update 之QS 若为创建快捷方式
    value=DesktopCommon.GetRegValue("HKEY_CURRENT_USER\\Software\\SogouMobileTool\\Update","QS")
    if not quickLaunch and value!="nocreate":
        print value,'QS'
        return False
    #Update 之Startmenu
    value=DesktopCommon.GetRegValue("HKEY_CURRENT_USER\\Software\\SogouMobileTool\\Update","Startmenu")
    if value!="create":
        print value,'startmenu'
        return False
    #Update 之UserExperience
    value=DesktopCommon.GetRegValue("HKEY_CURRENT_USER\\Software\\SogouMobileTool\\Update","UserExperience")
    if value!="create":
        print value,'UserExperience'
        return False
    
    #SoDa
    exist=DesktopCommon.IsRegExist("HKEY_CURRENT_USER\\Software\\SogouMobileTool\\SoDa")
    if not exist:
        print exist,'SoDa'
        return False
    #MENG
    exist=DesktopCommon.IsRegExist("HKEY_CURRENT_USER\\Software\\MENG")
    if not exist:
        print exist,'MENG'
        return False
    value=DesktopCommon.GetRegValue("HKEY_CURRENT_USER\\Software\\MENG","sign")
    if str(value)!=str(1):
        print 'Meng',value
        print 'No'
        return False
    
    #Run开机启动项
    value=DesktopCommon.GetRegValue("HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run","SogouMobileTool")
    if DesktopCommon.IsWin7():
        if value!="\"C:\\Program Files (x86)\\SogouMobileTool\\SogouMobileToolHelper.exe\"":
        print value,'Run'
        return False
        
    elif value!="\"C:\\Program Files\\SogouMobileTool\\SogouMobileToolHelper.exe\"":
        print value,'Run'
        return False
    #Uninstall
    value=DesktopCommon.GetRegValue("HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\SogouMobileTool","DisplayIcon")
    if DesktopCommon.IsWin7():
        if value!="C:\\Program Files (x86)\\SogouMobileTool\\"+GetZhushouVersion()+"\\uninstall.exe":
        print value,'Uninstall'
        return False  
    elif value!="C:\\Program Files\\SogouMobileTool\\"+GetZhushouVersion()+"\\uninstall.exe":
        print value,'Uninstall'
        return False
    value=DesktopCommon.GetRegValue("HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\SogouMobileTool","UninstallString")
    if DesktopCommon.IsWin7():
        if value!="C:\\Program Files (x86)\\SogouMobileTool\\"+GetZhushouVersion()+"\\uninstall.exe":
        print value,'Uninstall'
        return False  
    elif value!="C:\\Program Files\\SogouMobileTool\\"+GetZhushouVersion()+"\\uninstall.exe":
        print value,'Uninstall'
        return False
    #检查没有的项
    exist=DesktopCommon.IsRegExist("HKEY_LOCAL_MACHINE\\SOFTWARE\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\SogouMobileTool")
    if exist:
        print '1',exist
        return False  
    exist=DesktopCommon.IsRegExist("HKEY_LOCAL_MACHINE\\SOFTWARE\\SogouMobileTool")
    if exist:
        print '2',exist
        return False
    value=value=DesktopCommon.GetRegValue("HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run","SogouMobileTool")
    if len(value)!=0:
        print '3',exist
        return False
    exist=DesktopCommon.IsRegExist("HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\SogouMobileTool")
    if exist:
        print '4',exist
        return False 
    
    return True
