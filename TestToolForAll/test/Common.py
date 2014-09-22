#coding=utf-8
import wx
import os
app=wx.App()

if not os.path.exists("UpdateServerFileGenerator.exe"):
    mes=u'服务器配置文件生成工具（UpdateServerFileGenerator.exe）不在当前目录下'
    dlg=wx.MessageDialog(None,mes,u'运行出错',wx.OK,pos=wx.DefaultPosition)
    retCode=dlg.ShowModal()
    if (retCode == wx.ID_OK):
        print 'yes'
    else:
        print 'no'
    dlg.Destroy()
            
