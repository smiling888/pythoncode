#coding=gbk
import os
import getpass
def GetDesktopPath(opt= ""):

    '''
	| ##@函数目的: 获取本机Desktop路径，测试脚本中的使用到Desktop路径时统一从这里获取
	| ##@参数说明：无
	| ##@返回值：路径
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
def IsWin7():
    import platform
    version = platform.win32_ver()[1]
    return version.startswith("6.1")

print GetDesktopPath()
