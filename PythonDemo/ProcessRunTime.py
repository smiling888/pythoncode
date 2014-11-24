#coding:gbk
'''
测试SogouMobileToolUp的运行时间
'''

import subprocess,sys,time
import os

import psutil

processname="SogouMobileToolHelper"


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
            if process.name.lower() ==processname.lower():
                num += 1
        except:
            continue
    return num

def IsProcessExist(processname):
    if GetProcessNum(processname)==0:
        print '进程不存在'
        return

    print '等待进程退出'
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
