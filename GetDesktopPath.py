#coding=gbk
import os
import getpass
def GetDesktopPath(opt= ""):

    '''
	| ##@����Ŀ��: ��ȡ����Desktop·�������Խű��е�ʹ�õ�Desktop·��ʱͳһ�������ȡ
	| ##@����˵������
	| ##@����ֵ��·��
	| ##@�����߼���ͳһ����Desktop·��
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
        strTmp=sysDriver+os.environ['HOMEPATH']+"\\����"
        if opt != "":
            strTmp = strTmp + opt
    return strTmp
def IsWin7():
    import platform
    version = platform.win32_ver()[1]
    return version.startswith("6.1")

print GetDesktopPath()
