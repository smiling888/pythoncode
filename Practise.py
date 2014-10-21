#coding=utf-8
import win32api
import win32con
import win32com.client


def p1():
    '''
    Created on 2013-7-23
    Function: 
    有1、2、3、4个数字能组成多少个互不相同且无重复数字的三位数？都是什么？
    @author: BeginMan
    To me: be a great man.
    -----------------------------------------------------------
    '''
    
    for i in range(1,5):
        for j in range(1,5):
            for k in range(1,5):
                if i!=j and j!=k and i!=k:
                    print i,j,k
def p2():
    '''
    有如下log文件，请打印出独立IP，并统计独立IP数，（提示：可使用python，也可使用shell命令行）:
   log文件内容:
   218.79.251.215 - - [23/May/2006:08:57:44 +0800] "GET /fg172.exe HTTP/1.1" 206 2350253
   220.178.150.3 - - [23/May/2006:08:57:40 +0800] "GET /fg172.exe HTTP/1.1" 200 2350253
   59.42.2.185 - - [23/May/2006:08:57:52 +0800] "GET /fg172.exe HTTP/1.1" 200 2350253
   219.140.190.130 - - [23/May/2006:08:57:59 +0800] "GET /fg172.exe HTTP/1.1" 200 2350253
   221.228.143.52 - - [23/May/2006:08:58:08 +0800] "GET /fg172.exe HTTP/1.1" 206 719996
   221.228.143.52 - - [23/May/2006:08:58:08 +0800] "GET /fg172.exe HTTP/1.1" 206 713242
   221.228.143.52 - - [23/May/2006:08:58:09 +0800] "GET /fg172.exe HTTP/1.1" 206 1200250
    '''
p1()        
