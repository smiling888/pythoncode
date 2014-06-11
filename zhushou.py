#coding:gbk
import os
import traceback
import subprocess
from shutil import copy
import getpass
import string
import ConfigParser
import win32api
import win32con

import DesktopCommon


def GetZhushouVersion():
	'''
	| ##@����Ŀ��: ��ȡ�ѹ��ֻ����ֵİ汾�����Խű��е�ʹ�õ��汾��ʱͳһ�������ȡ
	| ##@����˵������
	| ##@����ֵ����
	| ##@�����߼���ͳһ���ð汾��
	'''
	return "2.5.0.19092"
def GetOldVersion():
    '''
	| ##@����Ŀ��: ��ȡ�ѹ��ֻ����ֵİ汾�����Խű��е�ʹ�õ��汾��ʱͳһ�������ȡ
	| ##@����˵������
	| ##@����ֵ����
	| ##@�����߼���ͳһ���ð汾��
	'''
    return "2.1.0.11992"

def GetQNum():
	'''
	| ##@����Ŀ��: ��ȡ����������
	| ##@����˵������
	| ##@����ֵ����
	| ##@�����߼���ͳһ���ð汾��
	'''
	return "000000"    

def GetTempPath(opt= ""):

    '''
	| ##@����Ŀ��: ��ȡ����temp·�������Խű��е�ʹ�õ�temp·��ʱͳһ�������ȡ
	| ##@����˵������
	| ##@����ֵ��·��
	| ##@�����߼���ͳһ����temp·��
	'''
    strTmp = os.environ['tmp']
    if opt != "":
        strTmp = strTmp + opt
    return strTmp

def fileIsExists(filepath=''):

    '''
	| ##@����Ŀ��: �ж�filepathָ����ļ��Ƿ����
	| ##@����˵������
	| ##@����ֵ��·��
	| ##@�����߼���ͳһ����temp·��
	'''
    return  os.path.isfile(filepath)
    
def DelSMTShareFiles(path):
    '''
    |##@ɾ��SMTShareĿ¼�µİ�װ��
    | ##@����˵������
    | ##@����ֵ��1
    | ##@�����߼�������1 ��ʾɾ����ɻ���û�и��ļ�
    '''
    allfilesname=os.listdir(path)
    for name in allfilesname:
        if name.find('SogouMobileToolSetup')!=-1:
            fullpath=os.path.join(path,name)
            try:
                os.remove(fullpath)
            except Exception,e:
                print e               
    return 1 
    

def DelTempFile(tmpFileName):

    '''
	| ##@����Ŀ��: ɾ��tempĿ¼�µ��ļ�
	| ##@����˵������
	| ##@����ֵ��1
	| ##@�����߼�������1 ��ʾɾ����ɻ���û�и��ļ�
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
	| ##@����Ŀ��: ��ȡ����appdata·�������Խű��е�ʹ�õ�appdata·��ʱͳһ�������ȡ
	| ##@����˵������
	| ##@����ֵ��·��
	| ##@�����߼���ͳһ����appdata·��
	'''
    strTmp = os.environ['appdata']
##    if not DesktopCommon.IsWin7():
##        strTmp=AddMark2Path(strTmp)
    strTmp = strTmp + "\\SogouMobileTool\\SogouMobileToolUp\\Files"
    if opt != "":
        strTmp = strTmp + opt
    return strTmp

def AddMark2Path(path):
    '''
    | ##@����Ŀ��: ��·�����пո���ֶ��������
    | ##@����˵������C:\Documents and Settings �޸�֮���ΪC:\"Documents and Settings"
    | ##@����ֵ��·��
    | ##@�����߼�����������֮����ֶ� 
    '''
    patharr=path.split("\\")
    path=''
    for e in patharr:
        #print e
        if e.find(' ')!=-1:
            e="\""+e+"\""
        path=path+"\\"+e
    return path[1:]

def DelAppdataFile(tmpFileName):

    '''
	| ##@����Ŀ��: ɾ��appdataĿ¼�µ��ļ�
	| ##@����˵������
	| ##@����ֵ��1
	| ##@�����߼�������1 ��ʾɾ����ɻ���û�и��ļ�
	'''
    flag = os.path.isfile(tmpFileName)
    if flag == 1:
        try:
            os.remove(tmpFileName)
        except Exception,e:
            print e 
    return 1

def DelAppdataFileHelper():
    '''
    |##@ɾ��Ŀ¼�µİ�װ��
    | ##@����˵������
    | ##@����ֵ��1
    | ##@�����߼�������1 ��ʾɾ����ɻ���û�и��ļ�
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
    |##@ɾ��Ŀ¼�µİ�װ��
    | ##@����˵������
    | ##@����ֵ��1
    | ##@�����߼�������1 ��ʾɾ����ɻ���û�и��ļ�
    '''
    appdatafilepath=GetAppdataPath()
    if not os.path.exists(appdatafilepath):
        return 1
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
	| ##@����Ŀ��: ɾ��appdataĿ¼�µ��������ļ�
	| ##@����˵������
	| ##@����ֵ��1
	| ##@�����߼�������1 ��ʾɾ����ɻ���û�и��ļ�
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

def HasNewestUp(version=""):
    '''
	| ##@����Ŀ��: appdataĿ¼�µ������ļ��Ƿ������µ�
	| ##@����˵����up�ļ��汾
	| ##@����ֵ��True
	| ##@�����߼�������True ��ʾֻʣ�����µ�����������û�������� false
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
	| ##@����Ŀ��: ��ȡ����Desktop·�������Խű��е�ʹ�õ�Desktop·��ʱͳһ�������ȡ
	| ##@����˵������
	| ##@����ֵ��·��
	| ##@�����߼���ͳһ����Desktop·��
	'''
    if DesktopCommon.IsWin7():
        str = getpass.getuser()
        strTmp = "C:\\Users\\"
        strTmp = strTmp + str
        strTmp = strTmp + "\\Desktop"
        if opt != "":
            strTmp = strTmp + opt
    else:
        sysDriver=os.getenv("SystemDrive")
        strTmp=sysDriver+os.environ['HOMEPATH']+"\\����"
        if opt != "":
            strTmp = strTmp + opt
    return strTmp

def CopySrcFileToDestFile(src = "",dest = ""):
    '''
	| ##@����Ŀ��: �����ļ���fileĿ¼
	| ##@����˵������
	| ##@����ֵ��·��
	| ##@�����߼���
	'''
    copy(src,dest);
    return 1;

def ChangeUpdateType(opt= "Notify"):

    '''
	| ##@����Ŀ��: �ı�������ʽ�����ı�������checkbox�Ĺ�ѡ״̬
	| ##@����˵������
	| ##@����ֵ��1�����ļ�������ʱ��˵���ǳ��ΰ�װ�����ΰ�װĬ��updateType=��auto��
	| ##@�����߼����޸���ȷ������1
	'''
    
    strTmp=os.environ["appdata"]
    strTmp = strTmp + "\\SogouMobileTool\\PDAData\\versionControl.ini"
    if not os.path.exists(strTmp):
        print strTmp," does not exits!"
    if not os.path.isfile(strTmp):
        print 'ChangeUpdateType fisrt install'        
        return 1
    
    input1   = open(strTmp)
    lines   = input1.readlines()
    input1.close()
    import time
    time.sleep(2)
    output1  = open(strTmp,'w');
    for line in lines:
                #print line
                if not line:
                        break
                if 'updateType=' in line:
                        temp    = "updateType="
                        temp1   = temp + opt
                        temp1 = temp1 + "\n"
                        output1.write(temp1)
                else:
                        output1.write(line)
    output1.close()
    print 'ChangeUpdateType changed'        
    return 1


def GetSikulyPath():
    '''
	| ##@����Ŀ��: ��ȡ˹�����ִ��·�������Խű��е�ʹ�õ��汾��ʱͳһ�������ȡ
	| ##@����˵������
	| ##@����ֵ����
	| ##@�����߼���ͳһ����˹����·��
	'''
    path = "D:\\sikuli\\runIDE.cmd -r "
    return path

def GetSikulipath():
    '''
	| ##@����Ŀ��: ��ȡsikuli IDE·�������Խű��е�ʹ�õ�IDE·��ʱͳһ�������ȡ
	| ##@����˵������
	| ##@����ֵ��·��
	| ##@�����߼���
	'''
    return "D:\\sikuli\\runIDE.cmd"

def GetSikuliScriptPath():
    '''
	| ##@����Ŀ��: ��ȡsikuli �ű��ı���·��
	| ##@����˵������
	| ##@����ֵ��·��
	| ##@�����߼���
	'''
    return ""

def GetSikuliexePath(opt = "\\updateModule\\update_checkbox.sikuli"):
    '''
	| ##@����Ŀ��: ��ȡsikuli�ű�·�������Խű��е�ʹ�õ�·��ʱͳһ�������ȡ
	| ##@����˵������
	| ##@����ֵ��·��
	| ##@�����߼���
	'''
    str = "D:\\autotest\\sikuliscript"
    str = str + opt
    return str


def GetLocalHelperVersion(version=''):
    '''
	| ##@����Ŀ��: ��ȡָ�����ְ汾�µ�helper�汾��
	| ##@����˵�����Ѿ���װ�����ֵİ汾
	| ##@����ֵ��·��
	| ##@�����߼���
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
	| ##@����Ŀ��: ��ȡ�ڱ��������ϵ��ѹ��ֻ����ֵİ汾
	| ##@����˵������
	| ##@����ֵ��·��
	| ##@�����߼���ͳһ����Desktop�汾
	'''
    vartop = GetDesktopPath()
    varver = GetZhushouVersion()
    if not DesktopCommon.IsWin7():
        vartop=AddMark2Path(vartop)
    vartop = vartop + "\\SogouMobileToolSetup_"
    vartop = vartop + varver
    vartop = vartop + "_"+GetQNum()+".exe"
    return vartop


def GetLoaclh():
    return "BAE74E6A0F6C3E89F979F7EE4589DE83"

def RunCmd(cmd):
	'''
	| ##@����Ŀ��: ����cmd���������
	| ##@����˵������cmd�ڴ���Ĳ���
	| ##@����ֵ��cmd�ڵ����
	| ##@�����߼���
	'''
        if len(cmd) < 5:
            print "!!!!Command is invalid!!!!"
            return "!!!!Command is invalid!!!!"
	p = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        strout, strerr = p.communicate()

	return strout


def RunSikuli(cmd):
	'''
	| ##@����Ŀ��: ����sikuli
	| ##@����˵��������sikuli�������в���
	| ##@����ֵ��0��ʾsikuli��caseִ�гɹ���-1��ʾsikuli��case��ʧ��
	| ##@�����߼�������sikuli����ȡ�����з�����Ϣ����ӡ������Ϣ
	| ##@zsret=failed��zsret=succeed�ǰ�����sikuli��ȷ�ʹ������
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
	| ##@����Ŀ��: ���ָ�����ֽ��̵���Ŀ
	| ##@����˵������
	| ##@����ֵ����������
	| ##@�����߼��������Ƚ�
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
	| ##@����Ŀ��: ��ȡ����ж�ؽ���������ͨ����־λ�����Ƿ�kill
	| ##@����˵������־�Ƿ�killж�ؽ���
	| ##@����ֵ����������
	| ##@�����߼�����������Ƚ�
	'''
    import psutil
    import re
    # ��������ʽ�����Pattern����
#    pattern = re.compile(r'~PA...\.tmp\.exe')
    cnt = 0
    processList = list(psutil.process_iter())
    for p in processList:
        try:
            if p.name.find("~PA")!=-1 and p.name.find(".tmp.exe")!=-1:
                cnt += 1
                if ifKill:
                    DesktopCommon.StopProcess(process.name)
        except:
            continue
    return cnt

def KillZSUnistallProcess():
    '''
    ɱ�������ֽ���
    '''
    import psutil
    processList=list(psutil.process_iter())
    for p in processList:
        try:
            if p.name.find("~PA")!=-1 and p.name.find(".tmp.exe"):
                DesktopCommon.StopProcess(p.name)
        except Exception,e:
            print e

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
        print 'keyvalues'
        return False
    for para in keyvalues:
        values = para.split("=")
        if len(values) != 2:
            return False
        if values[0] == "r":
            if values[1] != "000000":
                print 'r'
                return False
        elif values[0] == "h":
            if values[1] != GetLoaclh():
                print 'h'
                return False
        elif values[0] == "v":
            if values[1] != GetZhushouVersion():
                print 'v:'
                return False
    return True


def ResetEnv():
    zsUninstallString = DesktopCommon.GetRegValue("HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\SogouMobileTool","UninstallString")
    #�ж��Ƿ�������
    KillZSUnistallProcess()
    if len(zsUninstallString)!=0:
        if DesktopCommon.IsProcessExist("SogouMobileTool.exe"):
            DesktopCommon.StopProcess("SogouMobileTool.exe")
        setupName = "SogouMobileToolSetup_"+GetZhushouVersion()+"_"+GetQNum()+".exe"
        if DesktopCommon.IsProcessExist(setupName):
            DesktopCommon.StopProcess(setupName)
        sikulipath = GetSikulyPath()
        zsUninstallString = DesktopCommon.GetRegValue("HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\SogouMobileTool","UninstallString")
        if len(zsUninstallString)!=0:
            RunCmd("\""+zsUninstallString+"\"")
            ret = RunSikuli(sikulipath+"E:\\Install_Uninstall\\UninstallDirectly.skl")
        if DesktopCommon.IsProcessExist("SogouPAUnInstall.exe"):
            DesktopCommon.StopProcess("SogouPAUnInstall.exe")
        if DesktopCommon.IsProcessExist("SogouPAUnInstall.exe"):
            DesktopCommon.StopProcess("SogouPAUnInstall.exe")
        if DesktopCommon.IsProcessExist("SogouMobileTool.exe"):
            DesktopCommon.StopProcess("SogouMobileTool.exe")
        setupName = "SogouMobileToolSetup_"+GetZhushouVersion()+"_"+GetQNum()+".exe"
        if DesktopCommon.IsProcessExist(setupName):
            DesktopCommon.StopProcess(setupName)
        
def backupUserData(src='',dest=''):
    '''
	| ##@����Ŀ��: �����û����ݣ��Ա�֮���ж��Ƿ�ı�
	| ##@����˵�����������ͣ�������
	| ##@����ֵ���Ƿ���ȷ
	| ##@�����߼��������Ƚ�
	'''
    if len(src)==0:
        src=DesktopCommon.GetAppPath() + "\\SogouMobileTool\\PDAData\\versionControl.ini"
    if(len(dest)==0):
        dest="D:/versionControl.ini"
    if os.path.isfile(dest):
        os.remove(dest)
    copy(src,dest);
    return 1


def CheckUserData(updateType="Auto",routeNum="000000"):
    '''
	| ##@����Ŀ��: У���û������Ƿ�����
	| ##@����˵�����������ͣ�������
	| ##@����ֵ���Ƿ���ȷ
	| ##@�����߼��������Ƚ�
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

    AppConfirm = cf1.get("ConfirmDlgNoShow","AppConfirm")
    appAppConfirm = cf2.get("ConfirmDlgNoShow","AppConfirm")
    if len(AppConfirm)!=0 and len(appAppConfirm)!=0:
        if AppConfirm != appAppConfirm:
            print 'AppConfirm'
            return False

    LastExamTime = cf1.get("Optimize","LastExamTime")
    appLastExamTime = cf2.get("Optimize","LastExamTime")
    if len(LastExamTime)!=0 and len(appLastExamTime)!=0:
        if LastExamTime != appLastExamTime:
            print 'LastExamTime'
            return False
    return True

def CheckUserSetting(updateType="Auto",routeNum="000000"):
    '''
	| ##@����Ŀ��: У����װ���û������Ƿ�����
	| ##@����˵������װж��ʱʹ�õĺ�����������
	| ##@����ֵ���Ƿ���ȷ
	| ##@�����߼��������Ƚ�
	'''

    cf1 = ConfigParser.ConfigParser()
    cf2 = ConfigParser.ConfigParser()
    cf1.read("D:\\versionControl.ini")
    cf2.read(DesktopCommon.GetAppPath() + "\\SogouMobileTool\\PDAData\\versionControl.ini")
    if not os.path.exists("D:\\versionControl.ini"):
        print 'D:\\versionControl.ini does not exists'
    #���General�µ�ֵ
    #DBHOME
    a1=cf1.get("General","DBHOME")
    a2 = cf2.get("General","DBHOME")
    if a1 != a2:
        print "DBHOME"
        print a1
        print a2
        return False
    #Check
    a1=cf1.get("General","Check")
    a2 = cf2.get("General","Check")
    if a1 != a2:
        print "Check"
        print a1
        print a2
        return False
    #NewDNewDeviceUrl
    a1=cf1.get("General","NewDeviceUrl")
    a2 = cf2.get("General","NewDeviceUrl")
    if a1 != a2:
        print "NewDeviceUrl"
        print a1
        print a2
        return False

    #PingBackUrl
    a1=cf1.get("General","PingBackUrl")
    a2 = cf2.get("General","PingBackUrl")
    if a1 != a2:#"Auto":
        print "PingBackUrl"
        print a1
        print a2
        return False
    
    #Route�ᱻ����
    approute = cf2.get("General","Route")
    num="\""+GetQNum()+"\""
    if  str(approute) !=num:#routeNum != approute and "\""+routeNum+"\"" != approute:
        print "routeNum"
        print approute
        print GetQNum()
        return False

    
    #���Setting�µ�ֵ
    #closeToMinSize
    a1=cf1.get("Setting","closeToMinSize")
    a2 = cf2.get("Setting","closeToMinSize")
    if a1 != a2:#"Auto":
        print "closeToMinSize"
        print a1
        print a2
        return False
    #updateType�ᱻ����
    #a1=cf1.get("Setting","updateType")
    a2 = cf2.get("Setting","updateType")
    if a2 != "Auto":
        print "appUpType"
        print a1
        print a2
        return False

    #autoConn
    a1=cf1.get("Setting","autoConn")
    a2 = cf2.get("Setting","autoConn")
    if a1 != a2:
        print "autoConn"
        print a2
        print a1
        return False
    #savePath
    a1=cf1.get("Setting","savePath")
    a2 = cf2.get("Setting","savePath")
    if a1 != a2:
        print "savePath"
        print a2
        print a1
        return False

    #imageSavePath
    a1=cf1.get("Setting","imageSavePath")
    a2 = cf2.get("Setting","imageSavePath")
    if a1 != a2:
        print "imageSavePath"
        print a2
        print a1
        return False
    #apk
    a1=cf1.get("Setting","apk")
    a2 = cf2.get("Setting","apk")
    if a2 != '1':
        print "apk"
        print a2
        print a1
        return False
    #AutoCheckRelation
    a1=cf1.get("Setting","AutoCheckRelation")
    a2 = cf2.get("Setting","AutoCheckRelation")
    if a2 != a1:
        print "AutoCheckRelation"
        print a2
        print a1
        return False
    #AutoRelation
    a1=cf1.get("Setting","AutoRelation")
    a2 = cf2.get("Setting","AutoRelation")
    if a2 != a1:
        print "AutoRelation"
        print a2
        print a1
        return False
    #installToSD
    a1=cf1.get("Setting","installToSD")
    a2 = cf2.get("Setting","installToSD")
    if a2 != a1:
        print "installToSD"
        print a2
        print a1
        return False
    #installLocalApkPath
    a1=cf1.get("Setting","installLocalApkPath")
    a2 = cf2.get("Setting","installLocalApkPath")
    if a2 != a1:
        print "installLocalApkPath"
        print a2
        print a1
        return False
    #widgetSwitch
    a1=cf1.get("Setting","widgetSwitch")
    a2 = cf2.get("Setting","widgetSwitch")
    if a2 != a1:
        print "widgetSwitch"
        print a2
        print a1
        return False
    #SMTUsedNum
    a1=cf1.get("Setting","SMTUsedNum")
    a2 = cf2.get("Setting","SMTUsedNum")
    if a2 != a1:
        print "SMTUsedNum"
        print a2
        print a1
        return False
    #���AppUpReminder�µ�ֵ
    #ManuClose
    a1=cf1.get("AppUpReminder","ManuClose")
    a2 = cf2.get("AppUpReminder","ManuClose")
    if a2 != a1:
        print "ManuClose"
        print a2
        print a1
        return False
    #NoRemind
    a1=cf1.get("AppUpReminder","NoRemind")
    a2 = cf2.get("AppUpReminder","NoRemind")
    if a2 != a1:
        print "NoRemind"
        print a2
        print a1
        return False
    #LastRemindTime
    a1=cf1.get("AppUpReminder","LastRemindTime")
    a2 = cf2.get("AppUpReminder","LastRemindTime")
    if a2 != a1:
        print "LastRemindTime"
        print a2
        print a1
        return False
    #���Widget
    #wgtAtDft
    a1=cf1.get("Widget","wgtAtDft")
    a2 = cf2.get("Widget","wgtAtDft")
    if a2 != a1:
        print "wgtAtDft"
        print a2
        print a1
        return False
    #WgtConnDft
    a1=cf1.get("Widget","WgtConnDft")
    a2 = cf2.get("Widget","WgtConnDft")
    if a2 != a1:
        print "WgtConnDft"
        print a2
        print a1
        return False
    #widgetTopMost
    a1=cf1.get("Widget","widgetTopMost")
    a2 = cf2.get("Widget","widgetTopMost")
    if a2 != a1:
        print "widgetTopMost"
        print a2
        print a1
        return False
    #widgetTip
    a1=cf1.get("Widget","widgetTip")
    a2 = cf2.get("Widget","widgetTip")
    if a2 != a1:
        print "widgetTip"
        print a2
        print a1
        return False
    #wgtFileAnim
    a1=cf1.get("Widget","wgtFileAnim")
    a2 = cf2.get("Widget","wgtFileAnim")
    if a2 != a1:
        print "wgtFileAnim"
        print a2
        print a1
        return False
    #���ConfirmDlgNoShow
    #AppConfirm
    a1=cf1.get("ConfirmDlgNoShow","AppConfirm")
    a2 = cf2.get("ConfirmDlgNoShow","AppConfirm")
    if a2 != a1:
        print "AppConfirm"
        print a2
        print a1
        return False
 #   ���Optimize
    a1=cf1.get("Optimize","LastExamTime")
    a2 = cf2.get("Optimize","LastExamTime")
    if a2 != a1:
        print "LastExamTime"
        print a2
        print a1
    return True


def RenameSrcFileToDestFile(src = "",dest = ""):
    '''
	| ##@����Ŀ��: �������ļ�
	| ##@����˵������
	| ##@����ֵ��
	| ##@�����߼���
	'''
    os.rename(src,dest);
    return 1

def RunFiddler():
    '''
	| ##@����Ŀ��: ����fiddler,
	| ##@����˵������
	| ##@����ֵ��
	| ##@�����߼���Ӧ����ע�����д��fiddler���������fillder���������ͻ�����Ӧ�������
	'''
    FiddlerExEPath = DesktopCommon.GetRegValue("HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run","Fiddler")
    DesktopCommon.StartProcess(FiddlerExEPath)
    return 1

def CheckUpdateTypeData(updateType="Auto"):
    '''
	| ##@����Ŀ��: У���û������Ƿ�����
	| ##@����˵������������
	| ##@����ֵ���Ƿ���ȷ
	| ##@�����߼��������Ƚ�
	'''
    cf2 = ConfigParser.ConfigParser()
    cf2.read(DesktopCommon.GetAppPath() + "\\SogouMobileTool\\PDAData\\versionControl.ini")
    appUpType = cf2.get("Setting","updateType")
    if appUpType != updateType:
        return False
    return True

def CheckRouteData(routeNum="000000"):
    '''
	| ##@����Ŀ��: У���û������Ƿ�����
	| ##@����˵����������
	| ##@����ֵ���Ƿ���ȷ
	| ##@�����߼��������Ƚ�
	'''
    cf2 = ConfigParser.ConfigParser()
    cf2.read(DesktopCommon.GetAppPath() + "\\SogouMobileTool\\PDAData\\versionControl.ini")

    approute = cf2.get("General","Route")
    if routeNum != approute and "\""+routeNum+"\"" != approute:
        return False
    return True

def CheckUserIsWhat(opt = "English"):

    '''
	| ##@����Ŀ��: �жϱ����˻����Ƿ�ΪӢ�Ļ���������
	| ##@����˵������
	| ##@����ֵ��·��
	| ##@�����߼���ֻ��ȫ��Ӣ�Ļ�ȫ�����ĵĽ����жϣ�����Ӣ�Ļ�����������
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
	| ##@����Ŀ��: �ж��ַ��Ƿ�ΪӢ���ַ�
	| ##@����˵������
	| ##@����ֵ��
	| ##@�����߼���
	'''
    if (uchar >= u'\u0041' and uchar<=u'\u005a') or (uchar >= u'\u0061' and uchar<=u'\u007a'):
        return True
    else:
        return False

def windowsKeyboardImitate(opt1 = "win",opt2 = "d"):
    '''
	| ##@����Ŀ��: ��ʾ���棬���������ڵ���
	| ##@����˵������
	| ##@����ֵ��
	| ##@�����߼���
	'''
    win32api.keybd_event(91,0,0,0)  #win��λ����91
    win32api.keybd_event(68,0,0,0)  #d��λ����68
    win32api.keybd_event(68,0,win32con.KEYEVENTF_KEYUP,0) #�ͷŰ���
    win32api.keybd_event(91,0,win32con.KEYEVENTF_KEYUP,0)

def GetAppdataCrashPath(opt= ""):

    '''
	| ##@����Ŀ��: ��ȡ����appdata·���µ�crash�ļ�ȡ
	| ##@����˵������
	| ##@����ֵ��·��
	| ##@�����߼���
	'''
    strTmp = os.environ['appdata']
    strTmp = strTmp + "\\SogouMobileTool\\Log"
    if opt != "":
        strTmp = strTmp + opt
    return strTmp

def delete_file_folder(src):
    '''
	| ##@����Ŀ��: ɾ���ļ���
	| ##@����˵������
	| ##@����ֵ��1
	| ##@�����߼�������1 ��ʾɾ����ɻ���û�и��ļ�
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
	| ##@����Ŀ��: �鿴appdata���Ƿ����crash�����������ֱ�Ӽ��е�PerfmonitorĿ¼�µ�Log��־�ļ����У���������ΪCase���
	| ##@����˵����opt1��ʾcrash·����opt2Ϊcasex.zip
	| ##@����ֵ��
	| ##@�����߼���
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
	| ##@����Ŀ��: ���ע�������Ƿ���ȷ
	| ##@����˵����opt1��ʾcrash·����opt2Ϊcasex.zip
	| ##@����ֵ��
	| ##@�����߼���
	'''
    #����е���
    #Path
    value=DesktopCommon.GetRegValue("HKEY_CURRENT_USER\\Software\\SogouMobileTool","Path")
    if value!="C:\\Program Files\\SogouMobileTool":
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
    #PopUpConfig���ֵ������õ�
##    exist=DesktopCommon.IsRegExist("HKEY_CURRENT_USER\\Software\\SogouMobileTool\\PopUpConfig")
##    if not exist:
##        print exist
##        return False
    #Update
    exist=DesktopCommon.IsRegExist("HKEY_CURRENT_USER\\Software\\SogouMobileTool\\Update")
    if not exist:
        print exist,'update'
        return False
    #Update ֮Desktop
    value=DesktopCommon.GetRegValue("HKEY_CURRENT_USER\\Software\\SogouMobileTool\\Update","Desktop")
    if value!="create":
        print value,'create'
        return False
    #Update ֮MainVersion
    value=DesktopCommon.GetRegValue("HKEY_CURRENT_USER\\Software\\SogouMobileTool\\Update","MainVersion")
    if value!=str(GetZhushouVersion()):
        print value,'MainVersion'
        return False
    #Update ֮QS ��Ϊ������ݷ�ʽ
    value=DesktopCommon.GetRegValue("HKEY_CURRENT_USER\\Software\\SogouMobileTool\\Update","QS")
    if not quickLaunch and value!="nocreate":
        print value,'QS'
        return False
    #Update ֮Startmenu
    value=DesktopCommon.GetRegValue("HKEY_CURRENT_USER\\Software\\SogouMobileTool\\Update","Startmenu")
    if value!="create":
        print value,'startmenu'
        return False
    #Update ֮UserExperience
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
    
    #Run����������
    value=DesktopCommon.GetRegValue("HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Run","SogouMobileTool")
    if value!="\"C:\\Program Files\\SogouMobileTool\\SogouMobileToolHelper.exe\"":
        print value,'RUn'
        return False
    #Uninstall
    value=DesktopCommon.GetRegValue("HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\SogouMobileTool","DisplayIcon")
    if value!="C:\\Program Files\\SogouMobileTool\\"+GetZhushouVersion()+"\\uninstall.exe":
        print value,'Uninstall'
        return False
    value=DesktopCommon.GetRegValue("HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\SogouMobileTool","UninstallString")
    if value!="C:\\Program Files\\SogouMobileTool\\"+GetZhushouVersion()+"\\uninstall.exe":
        print value,'Uninstall'
        return False
    #���û�е���
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
