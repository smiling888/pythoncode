#coding:gbk
'''
����SogouMobileToolUp������ʱ��
'''

import subprocess,sys,time
import os

import psutil

processname="SogouMobileToolHelper"


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
            if process.name.lower() ==processname.lower():
                num += 1
        except:
            continue
    return num

def IsProcessExist(processname):
    if GetProcessNum(processname)==0:
        print '���̲�����'
        return

    print '�ȴ������˳�'
    time1=0
    while True:
        time.sleep(2)
        time1+=2
        if GetProcessNum(processname)!=0:
            f=open('d:/log.txt',"a+")
            f.write(str(time1)+"\n")
            f.close()
        else:
            break


if __name__=="__main__":
    #ISOTIMEFORMAT='%Y-%m-%d %X'
    #print time.strftime( ISOTIMEFORMAT, time.localtime() )
    #processname=raw_input()
    IsProcessExist(processname)
