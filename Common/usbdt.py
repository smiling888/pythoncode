#coding=utf-8
import os
import DesktopCommon
import string
import time

logfile= "d:\\log.txt"
crashfile="d:\\crash.txt"
def USDBT():

    usdbtreg()
    testfilename="d:\\test.txt"
    time1=3
    while True:
        try:
            if os.path.exists(testfilename):
                os.remove(testfilename)
            if not os.path.exists(testfilename):
                break
            if time1==-1:
                print '删除文件失败'
                exit
        except:
            time.sleep(1)
            time1-=1
    ##启动测试程序
    DesktopCommon.StartProcess("D:\\usbdt2.bat")
    ##重启手机
    DesktopCommon.StartProcess("C:\\Users\\Public\\SogouInput\\USBDT\\PhoneService.exe reboot")

    time.sleep(300)

    DesktopCommon.StopProcess("PressureTest.exe")
    if FileHasWod(testfilename,"Android") or FileHasWod(testfilename,"iOS"):
        print "has event"
        writelog()
        ##continue
    else:
        pass


def StartProcess(procPath, param=""):
    '''
    | ##@函数目的: 启动一个程序（支持以特定用户名启动程序）
    | ##@参数说明：procPath：程序路径
    | ##@参数说明：userName: 启动程序使用的机器用户名
    | ##@参数说明：password: 启动程序使用的用户密码
    | ##@返回值：无
    | ##@函数逻辑：
    '''

    if type(procPath) == unicode:
        procPath = procPath.encode("gbk")
        winprocess.WinStartProcess(procPath,param)
    return True

def usdbtreg():
    if DesktopCommon.IsRegValueExist("HKEY_CURRENT_USER\Software\SogouInput\USBDT\CONFIG","csht"):
        print "reg exist"
        writecrash()
        DesktopCommon.DeleteRegValue("HKEY_CURRENT_USER\Software\SogouInput\USBDT\CONFIG","csht")
    else:
        print "not reg"

def FileHasWod(filename,word):
    f=open(filename,"r")
    lines=f.readlines()
    for line in lines:
        if line.find(word)!=-1:
            f.close()
            return True

    f.close()
    return false;

def writecrash():
    f1=open(crashfile,"r")
    lines=f1.readlines()
    f1.close()
    f2=open(crashfile,"w")

    for line in lines:
        num=string.atoi(line)+1
        f2.write(str(num))

    f2.close()

def writelog():
    f1=open(logfile,"r")
    lines=f1.readlines()
    f1.close()
    f2=open(logfile,"w")

    for line in lines:
        num=string.atoi(line)+1
        f2.write(str(num))

    f2.close()

def StartTest():
    IniTest()
    ##count=5
    while True:
        USDBT()
      ##  count-=1

def IniTest():
    if os.path.exists(logfile):
        os.remove(logfile)

    f2=open(logfile,"w")
    f2.write('0')
    f2.close()

    if os.path.exists(crashfile):
        os.remove(crashfile)
    f2=open(crashfile,"w")
    f2.write('0')
    f2.close()
