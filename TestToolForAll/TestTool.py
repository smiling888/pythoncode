#coding=utf-8
# -*- coding: utf-8 -*- 

###########################################################################
## Python code generated with wxFormBuilder (version Jun  5 2014)
## http://www.wxformbuilder.org/
##
## PLEASE DO "NOT" EDIT THIS FILE!
###########################################################################

import wx
import wx.xrc

###########################################################################
## Class MyFrame1
###########################################################################

class MyFrame1 ( wx.Frame ):
	
	def __init__( self, parent ):
		wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"快捷方式", pos = wx.DefaultPosition, size = wx.Size( 752,466 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )
		
		self.SetSizeHintsSz( wx.DefaultSize, wx.DefaultSize )
		
		self.m_statusBar1 = self.CreateStatusBar( 1, wx.ST_SIZEGRIP, wx.ID_ANY )
		self.m_menubar2 = wx.MenuBar( 0 )
		self.m_menu1 = wx.Menu()
		self.m_menu11 = wx.Menu()
		self.m_menu1.AppendSubMenu( self.m_menu11, u"新建" )
		
		self.m_menu21 = wx.Menu()
		self.m_menu1.AppendSubMenu( self.m_menu21, u"打开" )
		
		self.m_menuItem3 = wx.MenuItem( self.m_menu1, wx.ID_ANY, u"退出", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu1.AppendItem( self.m_menuItem3 )
		
		self.m_menubar2.Append( self.m_menu1, u"文件" ) 
		
		self.m_menu6 = wx.Menu()
		self.m_menubar2.Append( self.m_menu6, u"MyMenu" ) 
		
		self.m_menu3 = wx.Menu()
		self.m_menubar2.Append( self.m_menu3, u"MyMenu" ) 
		
		self.m_menu4 = wx.Menu()
		self.m_menuItem2 = wx.MenuItem( self.m_menu4, wx.ID_ANY, u"MyMenuItem", wx.EmptyString, wx.ITEM_NORMAL )
		self.m_menu4.AppendItem( self.m_menuItem2 )
		
		self.m_menubar2.Append( self.m_menu4, u"MyMenu" ) 
		
		self.m_menu5 = wx.Menu()
		self.m_menubar2.Append( self.m_menu5, u"MyMenu" ) 
		
		self.SetMenuBar( self.m_menubar2 )
		
		bSizer2 = wx.BoxSizer( wx.VERTICAL )
		
		self.m_notebook3 = wx.Notebook( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )
		self.m_panel2 = wx.Panel( self.m_notebook3, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.m_notebook3.AddPage( self.m_panel2, u"升级", False )
		self.m_panel4 = wx.Panel( self.m_notebook3, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.m_notebook3.AddPage( self.m_panel4, u"安装卸载", False )
		self.m_panel5 = wx.Panel( self.m_notebook3, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.m_notebook3.AddPage( self.m_panel5, u"USBDT", False )
		self.m_panel6 = wx.Panel( self.m_notebook3, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.m_notebook3.AddPage( self.m_panel6, u"其他", False )
		self.m_panel3 = wx.Panel( self.m_notebook3, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.TAB_TRAVERSAL )
		self.m_notebook3.AddPage( self.m_panel3, u"关于", False )
		
		bSizer2.Add( self.m_notebook3, 1, wx.EXPAND |wx.ALL, 5 )
		
		
		self.SetSizer( bSizer2 )
		self.Layout()
		self.m_toolBar1 = self.CreateToolBar( wx.TB_HORIZONTAL, wx.ID_ANY ) 
		self.m_toolBar1.Realize() 
		
		self.m_menu2 = wx.Menu()
		self.Bind( wx.EVT_RIGHT_DOWN, self.MyFrame1OnContextMenu ) 
		
		
		self.Centre( wx.BOTH )
	
	def __del__( self ):
		pass
	
	def MyFrame1OnContextMenu( self, event ):
		self.PopupMenu( self.m_menu2, event.GetPosition() )
		

if __name__=="__main__":
    app=wx.App()
    frame=MyFrame1(None)
    frame.SetPosition( wx.Point( 200, 100 ) )
    frame.Show(True)
    app.MainLoop()
    print 'tt'



