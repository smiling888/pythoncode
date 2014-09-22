#coding=utf-8
import wx
import os
import ConfigParser
from Common import *
import subprocess

def GetAppdata():
    ##获得%Appdata%路径
    return os.environ['appdata']

def IsFileExists(path):
    return os.path.exists(path)

class MainUI(wx.Frame):
    def __init__(self,parent,title):
        super(MainUI,self).__init__(parent,title=title,size=(200,400))

        self.IniUI()
        self.Center()

        #self.Show()

    def IniUI(self):
        panel=wx.Panel(self)
        panel.SetBackgroundColour("green")
        #添加Text
        text1=wx.StaticText(panel,-1,u"打开文件夹快捷方式",(10,10))
        text1.SetBackgroundColour('white')
        #添加打开Files按钮
        self.openFilesB=wx.Button(panel,-1,u"打开Files",pos=(10,45))
        self.Bind(wx.EVT_BUTTON,self.OpenFiles,self.openFilesB)

        # 添加打开注册表程序按钮
        self.openRegB=wx.Button(panel,-1,u"打开注册表",pos=(10,75))
        self.Bind(wx.EVT_BUTTON,self.OpenReg,self.openRegB)

        text2=wx.StaticText(panel,-1,u"运行程序快捷方式",(10,115))
        text2.SetBackgroundColour('white')
        #添加运行服务器文件按钮
        self.runSerGen=wx.Button(panel,-1,u"Ser配置文件生成器",pos=(10,135))
        self.Bind(wx.EVT_BUTTON,self.RunUpdateServerFileGenerator,self.runSerGen)
        #添加运行HelpZip工具
        self.helperZip=wx.Button(panel,-1,u"HelperZip工具",pos=(10,165))
        self.Bind(wx.EVT_BUTTON,self.HelperZip,self.helperZip)
        #添加启动GenerateLocalIni工具
        self.generateLocalIni=wx.Button(panel,-1,u"GenerateLocalIni工具",pos=(10,195))
        self.Bind(wx.EVT_BUTTON,self.GenerateLocalIni,self.generateLocalIni)
        #添加启动Fiddler工具
        self.fiddler=wx.Button(panel,-1,u"Fiddler",pos=(10,225))
        self.Bind(wx.EVT_BUTTON,self.Fiddler,self.fiddler)
        #添加启动Winscp工具
        self.winscp=wx.Button(panel,-1,u"Winscp",pos=(10,255))
        self.Bind(wx.EVT_BUTTON,self.Winscp,self.winscp)
        #添加启动SecureCRT工具
        self.secureCRT=wx.Button(panel,-1,u"SecureCRT工具",pos=(10,285))
        self.Bind(wx.EVT_BUTTON,self.SecureCRT,self.secureCRT)
        #vbox=wx.BoxSizer(wx.VERTICAL)
        #midPan=wx.Panel(panel)
        #midPan.SetBackgroundColour("#ededed")

        #vbox.Add(panel,2,wx.EXPAND|wx.ALL,1)
        #panel.SetSizer(vbox)

    def Center(self):
        pass

    def SecureCRT(self,event):
        path=self.GetAppSetting('Setting','SecureCRT')
        subprocess.Popen(path,shell=True)
        return
    def Winscp(self,event):
        path=self.GetAppSetting('Setting','Winscp')
        subprocess.Popen(path,shell=True)
        return
    def Fiddler(self,event):
        path=self.GetAppSetting('Setting','Fiddler')
        subprocess.Popen(path,shell=True)
        return 
    def HelperZip(self,event):
        path=self.GetAppSetting('Setting','HelpZipPath')
        subprocess.Popen(path,shell=True)
        return
    def GenerateLocalIni(self,event):
        path=self.GetAppSetting('Setting','GenerateLocalIni')
        subprocess.Popen(path,shell=True)
        return
    
    

    def OpenFiles(self,event):
        ##打开Files文件
        appdataFiles=GetAppdata()
        cmd='start '+appdataFiles+' /SogouMobileTool'
        os.system(cmd)
        print 'opened'
    def OpenReg(self,event):
        #打开注册表程序
        os.system('regedit')

    def RunUpdateServerFileGenerator(self,event):
        if not os.path.exists("UpdateServerFileGenerator.exe"):
            mes=u'服务器配置文件生成工具（UpdateServerFileGenerator.exe）不在当前目录下'
            dlg=wx.MessageDialog(None,mes,u'运行出错',wx.OK,pos=wx.DefaultPosition)
            retCode=dlg.ShowModal()
            if (retCode == wx.ID_OK):
                print 'yes'
            else:
                print 'no'
            dlg.Destroy()
            return
        import subprocess
        path=os.getcwd()+'/UpdateServerFileGenerator.exe'
        #os.execl(path,'')
        subprocess.Popen(path,shell=True)
        print 'run'
        print dir(event)
        print type(event)
        print event.GetEventType()
        return
    
    def GetAppSetting(self,module="",key=""):
    #解析程序路径配置
        
        cf=ConfigParser.ConfigParser()
        if not os.path.exists("AppSeting.ini") or len(module)==0 or len(key)==0:
            mes=u'AppSeting.ini不在当前目录下'
            dlg=wx.MessageDialog(None,mes,u'运行出错',wx.OK,pos=wx.DefaultPosition)
            retCode=dlg.ShowModal()
            if (retCode == wx.ID_OK):
                print 'yes'
            else:
                print 'no'
            dlg.Destroy()
            return
        cf.read("D:\\versionControl.ini")
        return cf.get(module,key)

if __name__=="__main__":
    app=wx.App()
    frame=MainUI(None,title="TestTools")
    # 设置窗口出现的位置。
    frame.SetPosition( wx.Point( 1000, 100 ) )
    frame.Show(True)
    #frame.Iconize(True)
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



