#coding=utf-8
import wx
import os

from test import *
import subprocess

class MainUI(wx.Frame):
    def __init__(self,parent,title):
        super(MainUI,self).__init__(parent,title=title,size=(300,400))

        self.IniUI()
        self.Center()
        self.Show()

    def IniUI(self):
        panel=wx.Panel(self)
        panel.SetBackgroundColour("#4f5049")

        vbox=wx.BoxSizer(wx.VERTICAL)

        midPan=wx.Panel(panel)
        midPan.SetBackgroundColour("#ededed")

        vbox.Add(midPan,2,wx.EXPAND|wx.ALL,40)
        panel.SetSizer(vbox)

    def Center(self):
        pass

    def Show(self):
        pass
if __name__=="__main__":
    app=wx.App()
    MainUI(None,title="TestTools")
    app.MainLoop()
    print 'tt'

def funcctionStardan():
    '''
	| ##@函数目的: 编写规范
	| ##@参数说明：
	| ##@返回值：
	| ##@函数逻辑：
    '''
    pass

def RunUpdateServerFileGenerator():
    '''
	| ##@函数目的: 启动服务器文件生成工具
	| ##@参数说明：
	| ##@返回值：
	| ##@函数逻辑：
    '''

    #p = os.popen('UpdateServerFileGenerator.exe','r')# stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    subprocess.call('UpdateServerFileGenerator.exe',shell=True)
   # strout, strerr = p.communicate()
    #return strout

def StopUpdateServerFileGenerator():
    '''
	| ##@函数目的: 关闭服务器文件生成工具
	| ##@参数说明：
	| ##@返回值：
	| ##@函数逻辑：
    '''

    os.system('taskkill /f /im UpdateServerFileGenerator.exe')



