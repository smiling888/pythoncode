#!/usr/bin/env python
#coding=utf-8
'''
该文件负责大助手pingback自动化
 主要调用三个函数
1  Add_Line() 读回pingback准备工作。函数目的是在服务器pingback文件中写字符串，以区分各个case发的pingback
2  WriteResponseLog() 从服务器读回本次操作的pingback。 函数过程，读回pingback之后会将非本case进行判断
3  checkExist() 判断pingback是否存在。需要逐条进行判断，参数说明gifName表示pingback类型，如instevt.gif,sectionName表示sectionName部分的值是否存在（若只有pingback类型，第二个参数可忽略）

'''
import urllib,urllib2,os,sys
from tempfile import gettempdir
import DesktopCommon

def GetPingbackString():
    '''
    |函数目的：从pingback服务器读回pingback
    |输入：无
    |输出：在%tmp%文件夹下输出requestResponse.txt文件
    '''
    ip = DesktopCommon.GetIP()
    req = urllib2.Request("http://10.12.131.54/getlog.php?ip='%s'" % ip)
    res = urllib2.urlopen(req)
    html = res.read()
    res.close()
    return html

def IP2Str():
    '''
    |函数目的：将服务器的ip替换为pdatest,做好pingback之前的准备，在case之前执行
    |输入：无
    |输出：
    '''
    ip = DesktopCommon.GetIP()
    print ip
    url="http://10.12.131.54/dellog.php?ip=%s" % ip
    print url
    req = urllib2.Request("http://10.12.131.54/dellog.php?ip=%s" % ip)
    res = urllib2.urlopen(req)
    html = res.read()
    res.close()
    return html

def Add_Line():
    '''
    |函数目的：将服务器的ip替换为pdatest,做好pingback之前的准备，在case之前执行
    |输入：无
    |输出：
    '''
    ip = DesktopCommon.GetIP()
    print ip
    url="http://10.12.131.54/addline.php?ip=%s" % ip
    print url
    req = urllib2.Request("http://10.12.131.54/addline.php?ip=%s" % ip)
    res = urllib2.urlopen(req)
    html = res.read()
    res.close()
    return html

def GetResponseLogPath():
    '''
    |函数目的：返回%tmp%/requestResponse.txt文件夹路径，pingback保存于次路径下
    |输入：无
    |输出：在%tmp%文件夹下输出requestResponse.txt文件
    '''
    return os.path.join(gettempdir(), "requestResponse.txt")

def WriteResponseLog():
    '''
    |函数目的：从服务器读取大助手pingback
    |输入：无
    |输出：在%tmp%文件夹下输出requestResponse.txt文件
    '''
    html = GetPingbackString()

    logPath = GetResponseLogPath()
    DesktopCommon.WriteFile(logPath, html)

    lines = DesktopCommon.ReadFile(logPath)
    ModifyLocalLog(logPath)
    return lines


def ModifyLocalLog(filepath=""):
    '''
    |函数目的：修改本地的requestResponse.txt将文件---------之前的文件删除
    |输入：无
    |输出：在%tmp%文件夹下输出requestResponse.txt文件
    '''
    ##filepath="d:\\requestResponse.txt"
    f=open(filepath)
    input1=f.readlines()
    f.close()

    startline=0
    index=0
    for line in input1:
        index+=1
        if line.find('----------')!=-1:
            startline=index
            print startline

    output1=input1[startline:]
    f=open(filepath,'w')
    for line in output1:
        f.write(line)
    f.close()


def checkExist(gifName,sectionName="r="):
    '''
    |函数目的：检查pingback是否存在
    |输入：gifName表示pingback类型，如instevt.gif,sectionName表示sectionName部分的值是否存在
    |输出：若存在则输出True，若不存在则输出False
    '''

    logf = open(gettempdir()+"\\requestResponse.txt",'r')
    gifName = str(gifName)
    sectionName = str(sectionName)
    ##f = open(GetServerLogFileName())
    lines=logf.readlines()

    if True:
        for line in lines:
            #print line
            if (line.find(gifName) !=-1) and (line.find(sectionName) != -1):
                print line
                logf.close()
                return True
    else:
        logf.close()
    return False

