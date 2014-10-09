#coding=utf-8
import os,time,sys,win32api,win32gui,win32com,win32com.client,win32con,win32ui
import atf.plugin.DesktopCommon as DesktopCommon
import atf.plugin.SeSmoke as SeSmoke
import atf.lang.winprocess as winprocess
import time,random,tempfile

g_funcAndParamMap = {} #函数和概率、参数的映射
g_preAction = [("PreStartSE","")]       #每个动作前执行的动作。预留了启动浏览器的动作
g_postAction = []      #每个动作后执行的动作
g_ProbilityMap = {}    #建立动作到概率的映射
g_coreType = "auto"
g_processSecurity = ""  #启动进程的默认安全级别
g_semigi = "0"        #是否是mini版本，消息盒子位置变化到扩展栏上
g_logPath = ""

class ProbManager:
    def __init__(self):
	self.funcAndParamMap = {}
	self.totalProbility = 0
	self.probilityMap = {}
	self.actionList = []
	self.actionMode = 1
	self.geneDistFlag = False
	self.actionIdx = 0
    def GetFuncNameByProbility(self,value):
	for key in self.probilityMap.keys():
	    if value < self.probilityMap[key][1] and value >= self.probilityMap[key][0]:
		return key
	return ""

    def GenRandomAction(self):
	return random.randint(0,self.totalProbility-1)

    def GenerateProbilityDistribution(self):
	prob = 0
	for key in self.funcAndParamMap.keys():
	    endRange = prob + self.funcAndParamMap[key][0]
	    self.probilityMap[key] = (prob,endRange)
	    prob = endRange
	self.totalProbility = prob

    #生成下个动作
    def GenNextAction(self):
	if self.actionMode == 1 and  not self.geneDistFlag:
	    self.GenerateProbilityDistribution()
	    self.geneDistFlag = True
	if self.actionMode == 1:
	    return self.GetFuncNameByProbility(self.GenRandomAction())
	else:
	    #按顺序执行
	    if len(self.actionList)>0:
		actionName = self.actionList[self.actionIdx]
		self.actionIdx += 1
		self.actionIdx %= len(self.actionList)
		return actionName
	    else:
		#没有动作，直接失败
		assert 0

winSourceServer = None
def GetWinResourceServer():
    global winSourceServer
    if winSourceServer == None:
        winSourceServer = win32com.client.Dispatch("Sogou_WindowResource.WinResourceRetriver")
    return winSourceServer

sogouTestServer=None
def GetServer():
    global sogouTestServer
    if sogouTestServer == None:
        sogouTestServer = win32com.client.Dispatch("SogouIEAutoTestServer.AutoTestServer")
    return sogouTestServer



g_garbageWndList = ["Internet Explorer","退出登录","通行证登录","网络账户","来自网页的消息","搜狗高速浏览器账户登录",
                    "脱机状态下网页不可用","搜狗高速浏览器错误报告","搜狗高速下载",
                    "搜狗高速浏览器 选项","搜狗高速浏览器 3.0.0.2986 安装","添加到收藏夹","Microsoft Windows"]

def CountProcess(processname):
    return winprocess.CountProcess(processname)

#程序运行前的窗口列表
oldWndList = []
def GetOriWnds():
    global oldWndList
    #将运行过程中出现的新窗口添加到记录中
    curWindows = []
    win32gui.EnumWindows(windowEnumerationHandler, curWindows)
    for wndInfo in curWindows:
	wndText = wndInfo[1]
	if len(wndText)>0 and wndText not in g_garbageWndList and win32gui.IsWindowVisible(wndInfo[0]):
	    oldWndList.append(wndText)

def IsSogou(wndText):
    try:
	handle = win32gui.FindWindow(None,wndText)
	classname = win32gui.GetClassName(handle)
	if classname.find("SE_SogouExplorerFrame")!=-1 or classname.find("SE_AxControl")!=-1:
	    return 1
##	if wndText=="搜狗高速浏览器错误报告":
##	    #需要点击该错误框，使得生成dump
##	    #ClickCtrl(handle,340,320)
##	    return 1
    except:
	#异常情况下，定下的策略是不关闭，免得误操作
	return 2
    return 0

def PreCloseGarbageWnd(args):
    global g_garbageWndList,oldWndList
    import sets,copy
    #将运行过程中出现的新窗口添加到记录中
    curWindows = []
    win32gui.EnumWindows(windowEnumerationHandler, curWindows)
    for wndInfo in curWindows:
	wndText = wndInfo[1]
	if len(wndText)>0 and wndText not in g_garbageWndList and win32gui.IsWindowVisible(wndInfo[0]):
	    if wndText not in oldWndList and wndText.find("任务管理器")==-1:
		#新生成的窗口.判断是否为搜狗浏览器主框架和AxControl
		if IsSogou(wndText) != 1:
		    g_garbageWndList.append(wndText)
    PreCloseWndByName(g_garbageWndList)

def PreCloseWindows(args):
    try:
	for arg in args:
	    DesktopCommon.CloseWindowEx(arg, None)
    except:
	return


#添加每个动作执行前的动作
def AddPreAction(name,*params):
    global g_preAction
    g_preAction.append((name,params))


#添加每个动作执行后的动作
def AddPostAction(name,*params):
    global g_postAction
    g_postAction.append((name,params))


#添加要执行的动作
def AddAction(name,probility,*params):
    global g_funcAndParamMap
    g_funcAndParamMap[name] = [probility,params]



def AddMacroAction(name,probiblity,*params):
    g_funcAndParamMap[name] = [probiblity,params]

def PreCloseWndByName(args):
    for wndname in args:
	try:
	    h = win32gui.FindWindow(None,wndname)
	    if h!=0:
		win32gui.PostMessage(h, win32con.WM_CLOSE, 0, 0)
##		text = win32gui.GetWindowText(h)
##		if text.find("搜狗高速浏览器错误报告")!=-1:
##		    #重启浏览器
##		    DoStartSE(None)
	except:
	    None
    time.sleep(1)

def PreStartSE(args):
    global g_processSecurity
    try:
	for i in xrange(3):
	    #只有一个浏览器进程，则杀掉
	    if CountProcess("SogouExplorer") == 1:
	        DesktopCommon.StopProcess("SogouExplorer")
	        time.sleep(2)
	    else:
		break
    except:
	None
    while not winprocess.WinIsAlive("SogouExplorer"):
	sePath = DesktopCommon.GetSEDir()+"\\SogouExplorer.exe"
	DesktopCommon.OpenProcess(sePath, "", g_processSecurity)
	time.sleep(2)
	handles = DesktopCommon.GetWndHandles("SE_SogouExplorerFrame")
	if handles!=None and len(handles)>0:
	    SetForeground(handles[0][0])
	    MaximizeWnd(handles[0][0])
    try:
	handle = win32gui.FindWindow("SE_SogouExplorerFrame",None)
	if handle != 0 and not win32gui.IsWindowVisible(handle):
	    DesktopCommon.SendScKeys("LCTRL","`")
	    time.sleep(2)
    except:
	None
    try:
	#保证状态栏、菜单栏、扩展工具栏、搜索栏、地址栏等的存在
	classNameToShortCutMapping = {"SE_TuotuoMenuBar":"m","SE_TuotuoToolsBar":"o","SE_TuotuoStatusbarToolbar":"u",
	                              "SE_TuotuoToolbar":"t","SE_TuotuoSearchBarEditContainer":"s","SE_TuotuoAddressBarComboBox":'a'}
	wndInfo = DesktopCommon.GetWndPosEx("SE_SogouExplorerFrame")
	for key in classNameToShortCutMapping.keys():
	    if not DesktopCommon.HasChild(handle,key):
		DesktopCommon.MouseClick(wndInfo[0]+100,wndInfo[1]+10,"RIGHT")
		time.sleep(0.4)
		DesktopCommon.SendScKeys(classNameToShortCutMapping[key])
		time.sleep(0.4)
	win32api.CloseHandle(handle)
    except:
	None


def CopyToPassportUser(filename):
    root = DesktopCommon.GetEnv("appdata")+"\\SogouExplorer"
    subdirs = os.listdir(root)
    for item in subdirs:
	if os.path.isdir(os.path.join(root,item)):
	    if len(item)==32:
		DesktopCommon.Copy(filename,os.path.join(root,item))


def SetMigi(isMigi = "0"):
    global g_semigi
    g_semigi = isMigi

#获取消息盒子的大小
def GetDynBoxPos():
    return DesktopCommon.GetWndPosEx("SE_TuoLiteTooltip")

##def DoCloseSE(args):
##    import win32con
##    try:
##	handle = win32gui.FindWindow("SE_SogouExplorerFrame",None)
##	if handle != 0:
##	    win32gui.PostMessage(handle,win32con.WM_CLOSE,0,0)
##	time.sleep(3)
##	DesktopCommon.StopProcess("SogouExplorer")
##    except:
##	None

def JudgeDynBoxEmpty():
    return False
    from PIL import Image
    import ImageGrab
    im = ImageGrab.grab()
    x,y=GetDynBoxPos()
    monitorX =  x+20
    monitorY = y+40
    width = 100
    height = 100
    f = open("c:/22.txt",'a')
    f.write(str(monitorX)+","+str(monitorY)+":")
    if GetServer().CheckWhiteScreen(monitorX,monitorY,width,height,2) == 1:
	f.write("ok\r\n")
	f.flush()
	return True
    else:
	f.write("no\r\n")
	f.flush()
	return False
##    for i in range(width):
##	for j in range(height):
##	    r,g,b = im.getpixel((monitorX+i,monitorY+j))
##	    f = open("c:/111.txt",'a')
##	    f.write(str(monitorX+i)+","+str(monitorY+j)+":"+str(r)+" ")
##	    f.write(str(g)+" ")
##	    f.write(str(b)+os.linesep)
##	    f.flush()
##	    if r!=255 or g!=255 or b!=255:
##		return False
##    time.sleep(1)
    return True

def windowEnumerationHandler(hwnd, resultList):
    '''Pass to win32gui.EnumWindows() to generate list of window handle, window text tuples.'''
    resultList.append((hwnd, win32gui.GetWindowText(hwnd)))

def IsPassportWindowExist(width=357,height=258,width2=332,height2=190):
    topWindows = []
    win32gui.EnumWindows(windowEnumerationHandler, topWindows)
    try:
	for oneWnd in topWindows:
	    handle = oneWnd[0]
	    className = win32gui.GetClassName(handle)
	    if className == "#32770":
		rect = win32gui.GetClientRect(handle)
		if rect[2] == width and rect[3] == height:
		    return True,False #说明登录通行证窗口存在
		if rect[2] == width2 and rect[3] == height2:
		    return False,True #说明注销通行证窗口存在
    except:
	return False,False
    return False,False

def PreClosePassport(args):
    logonFlag,logoutFlag = IsPassportWindowExist()
    if logonFlag:
	DesktopCommon.ClickOnCtrl("Passport_LogonBtn")
    if logoutFlag:
	DesktopCommon.ClickOnCtrl("Passport_LogoutBtn")

def PreCloseWebDlg(args):
    handle = win32gui.FindWindow(None,"来自网页的消息")
    if handle != 0:
	if DesktopCommon.CtrlExist("Web_Notify_OKBtn"):
	    DesktopCommon.ClickOnCtrl("Web_Notify_OKBtn")

##def GetFuncNameByProbility(value):
##    for key in g_ProbilityMap.keys():
##        if value < g_ProbilityMap[key][1] and value >= g_ProbilityMap[key][0]:
##            return key
##    return ""
##
##def GenRandomAction():
##    global g_totalProbility
##    import random
##    return random.randint(0,g_totalProbility-1)
##
def GenRandom(maxValue,minValue=0):
    import random
    return random.randint(minValue,maxValue)

##执行宏动作
def ExcMacroAction(args):
    #对宏里面的每个动作
    actionString = args[0]
    actionTime = int(args[1])
    beginTime = win32api.GetTickCount()
    actionList = actionString.split(",")
    pm = ProbManager()

    for oneAction in actionList:
	actionAndProb = oneAction.split(":")
	if len(actionAndProb)==1:
	    pm.actionMode = 0 #没有分配概率，所以是顺序执行
	    pm.actionList.append(actionAndProb[0]) #这里没有去重的原因是有可能用户想重复做一些动作。例如新建，关闭，在新建，浏览
	else:
	    pm.funcAndParamMap[actionAndProb[0]] = [int(actionAndProb[1]),g_funcAndParamMap[actionAndProb[0]][1]] #保存动作和概率的映射

    while True:
	DoPreAction()
	actionName = pm.GenNextAction()
	if len(pm.funcAndParamMap)>0:
	    CallFunc(pm.funcAndParamMap,actionName) #递归调用CallFunc
	else:
	    #pm里没有概率映射，说明是顺序执行，但考虑到参数中必须要有到概率和参数的映射，所以这里以全局映射为参数
	    CallFunc(g_funcAndParamMap,actionName)
	time.sleep(0.1)
	DoPostAction()
	if win32api.GetTickCount()-beginTime>=actionTime*1000:
	    break


def AspPreventCloseSE(args):
    action = args
    if action.startswith("DoCloseTabBy"):
	#防止在多窗口模式下关闭唯一的一个浏览器
	handles = DesktopCommon.GetWndHandles("SE_SogouExplorerFrame")
	if handles!=None and len(handles)==1:
	    tabCtrlExist = DesktopCommon.CtrlExistByWin32("SE_TuotuoTabCtrl")
	    if not tabCtrlExist:
		#说明多窗口模式
		return False
    return True

g_curSEHandle = None
def AspActivateOneSE(args):
    #随机激活一个搜狗浏览器，假设有多个的话
    handles = DesktopCommon.GetWndHandles("SE_SogouExplorerFrame",None)
    if handles!=None:
	if len(handles)>1:
	    idx = GenRandom(len(handles)-1)
	    win32gui.ShowWindow(handles[idx][0],win32con.SW_MAXIMIZE)
	    time.sleep(0.1)
	    try:
		#将浏览器窗口设置到前台
		win32gui.SetForegroundWindow(handles[idx][0])
		#g_curSEHandle =  handles[idx][0]
		return True
	    except:
		None
	elif len(handles)==1:
	    #只有一个浏览器
	    for i in range(10):
		try:
		    h = win32gui.GetForegroundWindow()
		    if h != handles[0]:
			#不是前台窗口，则将其置顶
			win32gui.SetForegroundWindow(handles[0][0])
			time.sleep(0.1)
			#g_curSEHandle = handles[0][0]
		    else:
			break
		except:
		    time.sleep(0.2)
	else:
	    None
    return True

g_aspName = ["AspPreventCloseSE","AspActivateOneSE"]
#做横切面动作
def DoAsp(args):
    result = True
    for action in g_aspName:
	status = globals()[action](args)
	if not status:
	    #有一个横切面执行失败，说明横切面后面要执行的动作条件不成立，故而这里修改结果
	    result = status
    return result

def LogAction(name):
    #执行日志记录
    import time
    f = open(DesktopCommon.GetFrameworkPath()+"/action.txt",'a')
    acttime = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
    f.write(os.linesep+name+"\t"+acttime)
    f.flush()

def LogCrash(content, processName = "sogouexplorer.exe"):
    crashPath = os.path.join(DesktopCommon.GetFrameworkPath(), "crash.txt")
    if not DesktopCommon.IsProcessExist(processName):
	DesktopCommon.WriteFile(crashPath, str(content) + "\n", True)

def LogDetail(info=""):
    f = open(DesktopCommon.GetFrameworkPath()+"/action.txt",'a')
    f.write(info)
    f.flush()

def CallFunc(mapname,name):
    start = win32api.GetTickCount()
    LogAction(name)
    try:
	if name in globals():
	    #做具体动作前，先将切面动作完成
	    if DoAsp(name):
	        globals()[name](mapname[name][1])
	else:
	    #宏动作
	    ExcMacroAction(mapname[name][1])
    except:
	import traceback
	LogDetail("exec error:"+ traceback.format_exc() + os.linesep)

    end = win32api.GetTickCount()
    LogDetail("%.2f" % (1.0*(end-start)/1000)+os.linesep)


def CallSerialFunc(listname, name):
    for ele in listname:
        if ele[0] == name:
            globals()[name](ele[1])

g_urls = []

def DoClickStartPage(args,sideBarCtrlName="SideBar"):
    DesktopCommon.CtrlExist("SEUI")
    DesktopCommon.SendScKeys("LCTRL",'t')
    time.sleep(1)
    if DesktopCommon.CtrlExist(sideBarCtrlName):
	#点击固定位置
	for idx in range(11):
	    num = GenRandom(3)
	    if num>0:
	        for i in range(num):
	    	    DesktopCommon.ClickOnCtrlNoFocus("SE_SogouExplorerFrame",596,550)
	    DesktopCommon.ClickOnCtrlNoFocus("SE_SogouExplorerFrame",467,310+idx*25)
	    time.sleep(1)
	    DesktopCommon.SendScKeys("LCTRL","LSHIFT","TAB")
    else:
	#点击固定位置
	DesktopCommon.CtrlExist("SEUI")
	num = GenRandom(3)
	if num>0:
	    for i in range(num):
		DesktopCommon.ClickOnCtrlNoFocus("SE_SogouExplorerFrame",457,550)
	for idx in range(11):
	    DesktopCommon.ClickOnCtrlNoFocus("SE_SogouExplorerFrame",323,310+idx*25)
	    time.sleep(1)
	    DesktopCommon.SendScKeys("LCTRL","LSHIFT","TAB")

def DoNavigateByClickSubPages(args):
    url = args[0]
    DesktopCommon.CreateTabNav(url)
    time.sleep(3)
    randomPoints = [(273, 324), (576, 316), (589, 532), (259, 512), (909, 437), (914, 621), (500, 738), (609, 202), (422, 204)]
    points = random.sample(randomPoints, 5)

    for point in points:
	DesktopCommon.MouseClick(point[0], point[1])
	time.sleep(1)
	DesktopCommon.SendScKeys("F2")
	time.sleep(1)

g_navigateUrl = []
g_navigateUrlLength = 0

##@函数目的: 通过点击网页上的链接访问网站
##@参数说明：
##@返回值：
##@函数逻辑:
def DoNavigateByClickLinks(args):
    url = args[0]
    DesktopCommon.Navigate(url)
    time.sleep(3)

    handle = GetSE_AxControl()
    rect = win32gui.GetWindowRect(handle)

    x = rect[0]
    y = rect[1]
    p = (x, y)
    win32api.SetCursorPos(p)
    time.sleep(0.1)
    cursorInfoBefore = win32gui.GetCursorInfo()
    flag = 0
    points = []
    maxX = rect[2]
    maxY = rect[3]
    if maxX > 1000:
	maxX = 1000
    if maxY > 1000:
	maxY = 1000
    while x < maxX and y < maxY:
	win32api.SetCursorPos(p)
	time.sleep(0.001)
	if IsCursorLink():
	    flag += 1
	    if flag % 2 == 1:
		points.append((x + 2, y + 2))
	x += 1
	y += 1
	p = (x, y)

    point = random.sample(points, 1)[0]
    DesktopCommon.CreateTabNav(url)
    time.sleep(2)
    DesktopCommon.MouseClick(point[0], point[1])
    # 等待页面加载
    time.sleep(1)


def NavigateByCmd():
    global g_navigateUrl,g_urlIdx,g_navigateUrlLength, g_processSecurity
    if g_navigateUrlLength == 0:
	url = "http://www.sina.com.cn"
    else:
	url = g_navigateUrl[GenRandom(g_navigateUrlLength-1)]
    DesktopCommon.OpenProcess(DesktopCommon.GetSEDir()+"\\SogouExplorer.exe", url, g_processSecurity)

# 传入URL进行浏览
def DoNavigateWithURL(args):
    urlList = []
    if len(args) == 0:
	urlList = ["http://10.12.220.117/response/405.php", "http://10.12.220.117/response/404.php"]
    else:
	for arg in args:
	    urlList.append(arg)
    for url in urlList:
	LogDetail("\t"+url)
	DesktopCommon.CreateTabNav(url)
	handle = DesktopCommon.FindWindow("SE_SogouExplorerFrame")
	if handle != 0:
	    addressBarHandle = DesktopCommon.GetChildHandle(handle, "SE_TuotuoAddressBar")
	    if addressBarHandle != 0:
		rect = win32gui.GetWindowRect(addressBarHandle)
		DesktopCommon.MouseClick(rect[2] - 50, rect[1] + 13)
		# 等待页面显示
		time.sleep(2)
		DesktopCommon.MouseClick(rect[2] - 50, rect[1] + 13)

g_current = 1
def DoNavigateSequence(args):
    global g_current
    urlPath = os.path.join(DesktopCommon.GetFrameworkPath(), r"case\SeStability\url.txt")
    if len(args) > 0:
	urlPath = args[0]
    import linecache
    url = linecache.getline(urlPath, g_current)
    g_current += 1
    DesktopCommon.ClickOnCtrlWithWin32("SE_SogouExplorerFrame", 300, 20, "lefttop")
    time.sleep(1)
    DesktopCommon.CreateTabNav(url)

    lines = DesktopCommon.ReadFile(urlPath)
    if g_current >= len(lines):
	g_current = 1


def DoNavigate(args):
    #url = GetUrl(args[0])
    global g_navigateUrl,g_urlIdx,g_navigateUrlLength
    if g_navigateUrlLength == 0:
        f = open(args[0])
        for url in f:
            g_navigateUrl.append(url.strip())
        f.close()
	g_navigateUrlLength = len(g_navigateUrl)
    #url = g_navigateUrl[g_urlIdx % len(g_navigateUrl)]
    url = g_navigateUrl[GenRandom(g_navigateUrlLength-1)]
    LogDetail("\t" + url)
    DesktopCommon.CreateTabNav(url)

def DoNavigateByCmd(args):
    url = GetUrl(args[0])
    DesktopCommon.StartSE(url)


def DoAddToFav(args):
    global g_urlsForFav
    url = GetUrl(args[0],g_urlsForFav)
    DesktopCommon.CreateTabNav(url)
    time.sleep(2)
    DesktopCommon.SendScKeys("LCTRL","d")
    if DesktopCommon.CtrlExist("Fav_Add"):
	DesktopCommon.ClickOnCtrl("Fav_Add_Btn")
	time.sleep(0.5)
	if DesktopCommon.CtrlExist("Fav_Add_Overwrite_Btn"):
	    DesktopCommon.ClickOnCtrl("Fav_Add_Overwrite_Btn")

def DoAddAllToFav(args):
    handle = GetSE_AxControl()
    DesktopCommon.ClickOnHandle(handle, 100, 100)
    time.sleep(1)
    DesktopCommon.SendScKeys("LCTRL","LSHIFT","d")
    time.sleep(0.5)
    favWnd = DesktopCommon.GetWndHandles("#32770", "添加到收藏夹")
    if favWnd != -1 and len(favWnd) > 0:
	DesktopCommon.SendScKeys("ENTER")
    time.sleep(0.1)

    # 临时添加一个删除的操作
    DoOpenSideBar()
    for i in range(2):
	DeleteFavUrlBySideBar()


def DoImportDynData(args):
    DesktopCommon.CtrlExist("SEUI")
    DesktopCommon.SendScKeys("LALT","h")
    time.sleep(1)
    DesktopCommon.SendScKeys('w')
    if DesktopCommon.CtrlExist("UserWizard_Wnd"):
	DesktopCommon.ClickOnCtrl("UserWizard_Skip_Btn")
	DesktopCommon.ClickOnCtrl("UserWizard_Done_Btn")

def CreateTabAndInputUrl(url):
    DesktopCommon.SendScKeys("LCTRL",'t')
    time.sleep(1)
    DesktopCommon.SendScKeys("LCTRL",'l')
    DesktopCommon.CtrlC(url)
    time.sleep(0.5)
    DesktopCommon.CtrlV(url)
    time.sleep(0.3)

#导入ie收藏
def DoImportData(args):
    if os.path.isfile(args[0]):
	f = open(args[0])
	for line in f:
	    sp = line.strip().split()
	    try:
		SeSmoke.AddIEFav(sp[0], sp[1], sp[2])
	    finally:
		#LogAction("\t".join(sp))
		None
	f.close()
    SeSmoke.ClickSEMenuBar(186, 8)
    time.sleep(0.5)
    DesktopCommon.SendScKeys("i")
    time.sleep(0.5)
    DesktopCommon.SendScKeys("i")
    handle = DesktopCommon.GetHandle("#32770", "从IE浏览器导入收藏夹", 2)
    DesktopCommon.ClickOnHandle(handle, 45, 48)
    time.sleep(1)
    DesktopCommon.ClickCtrlEx(handle, "Button", "导入")
    time.sleep(1)

def DoImportDataFromFile(args):
    path = os.path.join(tempfile.gettempdir(), "Bookmark.htm")
    if not os.path.exists(path):
	DoExportDataToFile()
    if not os.path.exists(path):
	return
    SeSmoke.ClickSEMenuBar(186, 8)
    time.sleep(0.5)
    DesktopCommon.SendScKeys("i")
    time.sleep(0.5)
    DesktopCommon.SendScKeys("f")
    time.sleep(0.5)

    mainHandle = DesktopCommon.GetWindowHandle("#32770", "从文件导入收藏")
    if mainHandle != 0:
	DesktopCommon.ClickCtrlEx(mainHandle, "Button", "浏览...")
	openHandle = DesktopCommon.GetWindowHandle("#32770", "打开")
	if openHandle != 0:
	    DesktopCommon.SetCtrlTextEx(openHandle, "Edit", None, path)
	    DesktopCommon.ClickCtrlEx(openHandle, "Button", "打开(&O)")
	    DesktopCommon.ClickOnHandle(mainHandle, 54, 98)
	    DesktopCommon.ClickCtrlEx(mainHandle, "Button", "导入")
	    DesktopCommon.SendScKeys("ENTER")

	    time.sleep(2)
	    for i in range(3):
		DesktopCommon.SendScKeys("ENTER")
		time.sleep(1)
	# 防止出错
    DesktopCommon.SendScKeys("ESC")
    DesktopCommon.SendScKeys("ESC")



# 导出文件到IE
def DoExportDataToIE(args):
    SeSmoke.ClickSEMenuBar(186, 8)
    time.sleep(0.5)
    DesktopCommon.SendScKeys("e")
    time.sleep(0.5)
    DesktopCommon.SendScKeys("i")
    time.sleep(0.5)
    DesktopCommon.SendScKeys("ENTER")

# 导出文件到File
def DoExportDataToFile(args):
    SeSmoke.ClickSEMenuBar(186, 8)
    time.sleep(0.5)
    DesktopCommon.SendScKeys("e")
    DesktopCommon.SendScKeys("e")
    time.sleep(0.5)
    DesktopCommon.SendScKeys("f")

    mainHandle = DesktopCommon.GetWindowHandle("#32770", "导出收藏夹")
    if mainHandle != 0:
	editHandle = DesktopCommon.GetChildHandle(mainHandle, "Edit")

	# 构建路径
	path = os.path.join(tempfile.gettempdir(), "Bookmark.htm")
	DesktopCommon.SetCtrlTextEx(mainHandle, "Edit", None, path)

	DesktopCommon.WaitWindowChildVisiable(mainHandle, "导出", 5)
	DesktopCommon.ClickCtrlEx(mainHandle, "Button", "导出")

	DesktopCommon.SendScKeys("ENTER")

	time.sleep(2)
	for i in range(3):
	    DesktopCommon.SendScKeys("ENTER")
	    time.sleep(1)
    DesktopCommon.SendScKeys("ESC")

g_dynNotifyCtrlInAddressBarInterface = None
def DoNavigateAndAddToFocus(args):
    dynTimeout = args[1]
    global g_dynNotifyCtrlInAddressBarInterface
    if g_dynNotifyCtrlInAddressBarInterface==None:
	g_dynNotifyCtrlInAddressBarInterface = DesktopCommon.GetCtrlInterface("dyn")
    url = GetUrl(args[0])
    #开始浏览
    time.sleep(1)
    DesktopCommon.SendScKeys("LCTRL",'t')
    time.sleep(1)
    DesktopCommon.SendScKeys("LCTRL",'l')
    DesktopCommon.CtrlC(url)
    time.sleep(0.5)
    DesktopCommon.CtrlV(url)
    time.sleep(0.3)
    lastWidth = DesktopCommon.GetWidthEx(g_dynNotifyCtrlInAddressBarInterface)
    DesktopCommon.SendScKeys("ENTER")
    #判断小飞机是否出现了
    startTime = win32api.GetTickCount()
    endTime = win32api.GetTickCount()
    while (endTime-startTime<dynTimeout*1000):
	#判断小飞机是否出现，如果出现，则退出
	currentWidth = DesktopCommon.GetWidthEx(g_dynNotifyCtrlInAddressBarInterface)
	if (currentWidth!=-1 and currentWidth!=lastWidth):
	    #出现了小飞机，需要点击
	    DesktopCommon.ClickOnCtrl("dyn","LEFT","5*5")
	    time.sleep(2)
	    DesktopCommon.SendScKeys("ENTER")
	    if DesktopCommon.CtrlExist("Dyn_OK"):
		DesktopCommon.ClickOnCtrl("Dyn_OK")
	    break
	time.sleep(1)
	endTime = win32api.GetTickCount()


def DoCancelFocusFromAddressBar(args,width=290,height=119,posx=69,posy=82):
    global g_dynNotifyCtrlInAddressBarInterface
    if g_dynNotifyCtrlInAddressBarInterface==None:
	g_dynNotifyCtrlInAddressBarInterface = DesktopCommon.GetCtrlInterface("dyn")
    url = GetUrl(args[0])
    if len(args)>1:
	width = args[1]
	height = args[2]
    #开始浏览
    time.sleep(1)
    CreateTabAndInputUrl(url)
    lastWidth = DesktopCommon.GetWidthEx(g_dynNotifyCtrlInAddressBarInterface)
    DesktopCommon.SendScKeys("ENTER")
    #判断小飞机是否出现了
    startTime = win32api.GetTickCount()
    endTime = win32api.GetTickCount()
    while (endTime-startTime<3000):
	#判断小飞机是否出现，如果出现，则退出
	currentWidth = DesktopCommon.GetWidthEx(g_dynNotifyCtrlInAddressBarInterface)
	if (currentWidth!=-1 and currentWidth!=lastWidth):
	    #出现了小飞机，需要点击
	    DesktopCommon.ClickOnCtrl("dyn","LEFT","5*5")
	    time.sleep(2)
	    #点击取消
	    topWindows = []
	    win32gui.EnumWindows(windowEnumerationHandler, topWindows)
	    for handle in topWindows:
		rect = win32gui.GetClientRect(handle[0])
		if rect[2] == width and rect[3] == height:
		    #点击取消
		    DesktopCommon.ClickOnCtrlNoFocusByHandle(handle[0],posx,posy)
		    time.sleep(1)
		    if DesktopCommon.CtrlExist("Dyn_CancelFocus_OKBtn"):
			DesktopCommon.ClickOnCtrl("Dyn_CancelFocus_OKBtn")
		    return

	time.sleep(1)
	endTime = win32api.GetTickCount()


def PreCloseDynDlgFromAddressBar(args):
    title = args[0]
    try:
        handle = win32gui.FindWindow(None,title)
	if handle != 0:
	    DesktopCommon.ClickOnCtrl("Dyn_OK")
	    win32api.CloseHandle(handle)
    except:
	None

# 获取句柄
def GetSubHandle(parentHandle, cls, title = None, waitTime = 5):
    for i in range(waitTime):
	try:
	    if parentHandle == 0:
		handle = win32gui.FindWindow(cls, title)
	    else:
		handle = win32gui.FindWindowEx(parentHandle, 0, cls, title)
	    if handle != 0:
		return handle
	    else:
		time.sleep(1)
	except:
	    time.sleep(1)
    return handle

# 获取窗口位置
def GetRect(parentHandle, cls, title = None, waitTime = 5):
    try:
	handle = GetSubHandle(parentHandle, cls, title, waitTime)
	if handle != 0:
	    return win32gui.GetWindowRect(handle)
	else:
	    return None
    except:
	return None

# 前进 后退等操作
def DoClickTuotuoToolbar(args):
    # 获取随机url并启动浏览器浏览
    url = GetUrl(args[0])
    if not DesktopCommon.IsProcessExist("SogouExplorer.exe"):
	DesktopCommon.StartSE(url)
    else:
	DesktopCommon.Navigate(url)

    # 获取第二个url，并浏览
    url = GetUrl(args[0])
    DesktopCommon.Navigate(url)

    # 获取主窗口句柄
    mainHandle = GetSubHandle(0, "SE_SogouExplorerFrame")
    if mainHandle != 0:
	SetForeground(mainHandle)

	# 依次点击相应按钮
	points = (20, 40, 60, 95, 125, 158, 192, 245)
	reBarHandle = GetSubHandle(mainHandle, "SE_TuotuoRebar")
	if reBarHandle != 0:
	    rect = GetRect(reBarHandle, "SE_TuotuoToolbar")
	    if rect != None:
		for i in points:
		    DesktopCommon.MouseClick(rect[0] + i,rect[1] + 15)
		    time.sleep(1)

	    # 收藏所有页面
	    DesktopCommon.SendScKeys("b")
	    time.sleep(1)
	    DesktopCommon.SendScKeys("ENTER")


def DoCrashSE(args):
    NewTabByCmd("http://10.12.220.117/crash/CrashActiveX10.html")
    DesktopCommon.Sleep(2)
    ieDlg = ["Internet Explorer"]
    for title in ieDlg:
	try:
	    h = win32gui.FindWindow("#32770",title)
	    if h > 0:
		DesktopCommon.SendScKeys("y")
	except:
	    None
    wndInfo = DesktopCommon.GetWndPosEx("SE_AxControl")

    # 检测y的坐标位置
    x = wndInfo[0]
    y = wndInfo[1]
    p = (x, y)
    win32api.SetCursorPos(p)
    time.sleep(0.1)
    cursorInfoBefore = win32gui.GetCursorInfo()
    while x < 100:
	y += 2
	x += 5
	p = (x, y)
	win32api.SetCursorPos(p)
	time.sleep(0.001)
	cursorInfoAfter = win32gui.GetCursorInfo()
	if int(cursorInfoAfter[1]) != int(cursorInfoBefore[1]):
	    break
    for i in range(0, 500, 30):
	DesktopCommon.MouseClick(i, y)

# 点击状态栏修复图标
def DoClickRepair(args):
    wndInfo = DesktopCommon.GetWndPosEx("SE_TuotuoStatusbarToolbar")
    if wndInfo!=-1:
	ClickCtrl(wndInfo[-1],125,15)
	handle = DesktopCommon.GetWindowHandle("SGDUI", "搜狗浏览器修复工具", None, 2)
	if handle == 0:
	    ClickCtrl(wndInfo[-1],105,15)
    time.sleep(1)

# 查看网站的验证信息
def DoClickAuthInfo(args):
    handle = InvokeBrowseOptionDlg(50, 395)
    trackHandle = DesktopCommon.GetChildHandle(handle, "msctls_trackbar32", None)
    for i in range(2):
	DesktopCommon.ClickOnHandle(trackHandle, 11, 15)
    DesktopCommon.ClickCtrlEx(handle, "Button", "确定")

    # 浏览
    DoNavigate(args)

    # 点击验证信息
    DesktopCommon.Sleep(2)
    DesktopCommon.ClickOnCtrlWithWin32("SE_TuotuoAddrAdditionalToolBar", 10, 10, "righttop")
    DesktopCommon.Sleep(0.5)
    DesktopCommon.ClickWindow(None, 61, 106, "SE_ToolTip")
    DesktopCommon.Sleep(0.5)
    DesktopCommon.ClickWindow(None, 61, 117, "SE_ToolTip")

# 查看安全设置
def DoClickSafeOption(args):
    handle = InvokeBrowseOptionDlg(50, 395)
    trackHandle = DesktopCommon.GetChildHandle(handle, "msctls_trackbar32", None)
    for i in range(2):
	DesktopCommon.ClickOnHandle(trackHandle)
    DesktopCommon.ClickCtrlEx(handle, "Button", "确定")

    # 浏览
    DoNavigate(args)

    # 点击验证信息
    DesktopCommon.Sleep(2)
    DesktopCommon.ClickOnCtrlWithWin32("SE_TuotuoAddrAdditionalToolBar", 10, 10, "righttop")
    DesktopCommon.Sleep(0.5)
    DesktopCommon.ClickWindow(None, 264, 90, "SE_ToolTip")
    DesktopCommon.Sleep(1)

# 网速优化
def DoWebOptimization(args):
    # 点击右下角“搜狗加速器”
    wndInfo = DesktopCommon.GetWndHandles("SE_TuotuoStatusBarProgressCtrl")
    DesktopCommon.ClickOnHandle(wndInfo[0][0])
    DesktopCommon.Sleep(0.5)

    # 点击“网速优化”
    handle = win32gui.FindWindow("SE_TuoLiteTooltip",None)
    DesktopCommon.Sleep(0.5)
    pos = DesktopCommon.GetWndPos(handle)
    x = pos[0] + 362
    y = pos[1] + 158
    DesktopCommon.Sleep(0.5)
    DesktopCommon.MouseClick(x, y)
    DesktopCommon.Sleep(0.5)

    # 弹出“网速优化对话框”
    dialogHandle = win32gui.FindWindow("SE_TuoLiteTooltip", "网速优化")
    DesktopCommon.Sleep(0.5)
    dialogPos = DesktopCommon.GetWndPos(dialogHandle)

    # 点击 重新检测
    DesktopCommon.MouseClick(dialogPos[0] + 431, dialogPos[1] + 72)
    DesktopCommon.Sleep(8)

    dx = 517
    dy = 140
    celldy = 27
    num = 0
    DesktopCommon.MouseClick(dialogPos[0] + dx, dialogPos[1] + dy + celldy * num)

    # 保存设置
    DesktopCommon.MouseClick(dialogPos[0] + dx, dialogPos[1] + 72)

# 点击修复窗口中的升级
def DoRepairUpdate(args):
    DoClickRepair(args)
    className = "_SGDUIFoundation_"
    wndName = args[0]
    wndInfo = DesktopCommon.GetWndPosEx(className,wndName)
    if wndInfo != -1:
	ClickCtrl(wndInfo[-1],250,280)
    time.sleep(1)

# 点击修复窗口中的自动修复
def DoRepairAuto(args):
    DoClickRepair(args)
    className = "_SGDUIFoundation_"
    wndName = args[0]
    wndInfo = DesktopCommon.GetWndPosEx(className,wndName)
    if wndInfo!=-1:
	ClickCtrl(wndInfo[-1], 250, 108)
    time.sleep(1)
    DesktopCommon.SendScKeys("ENTER")
    time.sleep(1)

# 点击修复窗口中的手动修复
def DoRepairManual(args):
    DoClickRepair(args)
    className = "_SGDUIFoundation_"
    wndName = args[0]
    wndInfo = DesktopCommon.GetWndPosEx(className,wndName)
    if wndInfo!=-1:
	ClickCtrl(wndInfo[-1], 250, 188)
	time.sleep(1)
	click = GenRandom(1)
	points = []
	if click == 0:
	    ClickCtrl(wndInfo[-1], 476, 300)
	    time.sleep(1)
	    points = [140, 180, 270]
	else:
	    points = [180, 270, 310, 350]
	repairs = random.sample(points, 2)
	for repair in repairs:
	    ClickCtrl(wndInfo[-1], 404, repair - 20)
	    time.sleep(1)
	    DesktopCommon.SendScKeys("ENTER")
	    time.sleep(1)

# 更新提醒地址栏小飞机--添加关注
def DoClickAircraft(args):
    wndPos = DesktopCommon.GetWndPosEx("SE_TuotuoAddrAdditionalToolBar")
    if wndPos[-1] == 0:
	return
    DesktopCommon.MouseClick(wndPos[0] + 5, wndPos[1] + 5)
    time.sleep(1)

remindUrls = ["http://tv.sohu.com/drama/", "http://www.yihaodian.com/1/", "http://bbs.hupu.com/", "http://blog.sohu.com/", "http://bj.meituan.com/"]
# 更新提醒地址栏小飞机--取消关注
def DoClickAircraftToCance(args):
    url = random.sample(remindUrls, 1)[0]
    DesktopCommon.CreateTabNav(url)
    time.sleep(4)
    DoClickAircraft(args)
    handle = GetHandle(None, "SE_ToolTip", 3)
    if handle == 0:
	return
    rect = win32gui.GetWindowRect(handle)
    DesktopCommon.MouseClick(rect[0] + 72, rect[1] + 80)
    time.sleep(0.5)
    DesktopCommon.SendScKeys("ENTER")


# 更新提醒地址栏小飞机--编辑
def DoClickAircraftToModify(args):
    url = random.sample(remindUrls, 1)[0]
    DesktopCommon.CreateTabNav(url)
    time.sleep(4)
    DoClickAircraft(args)
    handle = GetHandle(None, "SE_ToolTip", 3)
    if handle == 0:
	return
    rect = win32gui.GetWindowRect(handle)
    DesktopCommon.MouseClick(rect[0] + 220, rect[1] + 80)

    # 弹出网页更新提醒对话框
    dialogHandle = GetHandle("#32770", "网页更新提醒", 3)
    if dialogHandle == 0:
	return
    dialogRect = win32gui.GetWindowRect(dialogHandle)

    # 设置标题，点击是否弹出气泡
    titles = ["asdfghj", "敖德萨该发生的鬼地方华国锋", "!@#@$^%&*^*&)*)_sfd", "﹌﹋＇﹠﹪﹨﹎﹉*", "⒐⒑⒃⒅⑥㈥Ⅵ", "1234567890"]
    title = random.sample(titles, 1)[0]
    DesktopCommon.SendScKeys("LCTRL", "a")
    DesktopCommon.CtrlV(title)
    DesktopCommon.ClickCtrlEx(dialogHandle, "Button", "当页面有更新时，弹出气泡")

    # 随机设置更新周期
    flag = GenRandom(1)
    if flag == 0:
	DesktopCommon.ClickCtrlEx(dialogHandle, "Button", "智能更新周期")
    else:
	DesktopCommon.ClickCtrlEx(dialogHandle, "Button", "手动设定每隔")
	childList = []
	DesktopCommon.EnumAllChildWindows(dialogHandle, childList, 2)
	for child in childList:
	    if child[1] == "msctls_updown32":
		dy = random.sample([5, 17], 1)[0]
		num = GenRandom(8)
		childRect = win32gui.GetWindowRect(child[0])
		for i in range(num):
		    DesktopCommon.MouseClick(childRect[0] + 11, childRect[1] + dy)
		    time.sleep(0.5)
    # 点击确定
    DesktopCommon.ClickCtrlEx(dialogHandle, "Button", "确定")


# 修改双核加速默认模式
def DoModifyDefaultMode(args):
    core = random.sample(["auto", "ie", "webkit"], 1)[0]
    if len(args) >= 1:
	core = args[0]

    if core == "auto":
	ClickAccCore(50, 80)
    elif core == "ie":
	ClickAccCore(50, 275)
    else:
	ClickAccCore(50, 175)


# 在兼容核下使用打印预览
def DoPrintReview(args):
    if not DesktopCommon.IsIECore():
	ClickAccCore(50, 275)
	DoNavigate(args)
	time.sleep(3)
    SeSmoke.ClickSEMenuBar(74, 8)
    time.sleep(0.5)
    DesktopCommon.SendScKeys("v")
    time.sleep(2)
    DesktopCommon.SendScKeys("LALT", "l")
    time.sleep(1)
    DesktopCommon.SendScKeys("LALT", "o")


##@函数目的: 获取给定ClassName和title的主窗口句柄
##@参数说明：
##@返回值：
##@函数逻辑:
def GetHandle(clsName = "SE_SogouExplorerFrame", title = None, waitTime = 3):
    for i in range(waitTime):
	try:
	    seHwnd =  win32gui.FindWindow(clsName, title)
	    if seHwnd != 0:
		return seHwnd
	    else:
		time.sleep(1)
	except:
	    time.sleep(1)
    return 0

##@函数目的: 获取浏览器主窗口句柄
##@参数说明：
##@返回值：
##@函数逻辑:
def GetSEHandle(waitTime = 5):
    return GetHandle("SE_SogouExplorerFrame", None, waitTime)

##@函数目的: 获取浏览器选项对话框句柄
##@参数说明：
##@返回值：
##@函数逻辑:
def GetSEOptionHandle(waitTime = 5):
    return GetHandle("#32770", "搜狗高速浏览器 选项", waitTime)

##@函数目的: 点击给定clsName及text的控件，
##@参数说明：
##@返回值：
##@函数逻辑: 暂时只搜索一层，后面可以进行修改，递归搜索
def MouseClick(parentHwnd, clsName, text = None, offset = None, waitTime = 5):
    for i in range(waitTime):
	try:
	    restoreAllDefaultButtonHwnd = win32gui.FindWindowEx(parentHwnd, None, clsName, text)
	    if restoreAllDefaultButtonHwnd != 0:
		rect = win32gui.GetWindowRect(restoreAllDefaultButtonHwnd)
		if offset == None:
		    DesktopCommon.MouseClick((rect[0] + rect[2])/2, (rect[1] + rect[3])/2)
		else:
		    DesktopCommon.MouseClick(rect[0] + offset[0], rect[1] + offset[1])
		break
	    else:
		time.sleep(1)
	except:
	    time.sleep(1)

##@函数目的: 点击浏览器选项中的“恢复全部默认”
##@参数说明：
##@返回值：
##@函数逻辑:
def DoClickRestoreAllDefault(args):
    seHwnd = GetSEHandle(3)
    SetForeground(seHwnd)
    SeSmoke.ClickSEMenuBar(247, 5)
    DesktopCommon.SendScKeys("s")

    optionHwnd = GetSEOptionHandle()

    MouseClick(optionHwnd, "Button", "恢复全部默认")
    MouseClick(optionHwnd, "Button", "取消")

##@函数目的: 点击浏览器选项中左侧所有控件
##@参数说明：
##@返回值：
##@函数逻辑:
def DoClickAllTabs(args):
    seHwnd = GetSEHandle(2)
    SetForeground(seHwnd)
    DesktopCommon.SendScKeys("LALT", "t")
    DesktopCommon.SendScKeys("s")

    optionHwnd = GetSEOptionHandle()
    for i in range(18):
	MouseClick(optionHwnd, "SysListView32", "", (15, 10 + i * 24))
##    tabs = ("常规", "快捷键", "标签设置", "标签外观", "鼠标手势", "隐私保护", "页面设置", "地址栏", "搜索栏", "收藏设定", "网络连接", "下载", "广告过滤", "智能填表", "安全", "网页更新提醒", "账户", "高级")
##    for tab in tabs:

#点击Toobar的相对位置
def ClickTooBarOffset(handle, offsetx = 0, offsety = 0):
    if handle != 0:
	toobarHandle = DesktopCommon.GetChildHandle(handle, "SE_TuotuoToolsBar")
	if toobarHandle != 0:
	    rect = win32gui.GetWindowRect(toobarHandle)
	    DesktopCommon.MouseClick(rect[0] + offsetx, rect[1] + offsety)

g_screenshotFlag = True

# 点击工具栏上的截图按钮
def ClickScreenshotBtn():
    global g_screenshotFlag
    handle = GetHandle()
    if handle == 0:
	return
    if g_screenshotFlag:
	ClickTooBarOffset(handle, 284, 10)
	g_screenshotFlag = False
    else:
	SetForeground(handle)
	DesktopCommon.SendScKeys("CTRL", "SHIFT", "x")
	g_screenshotFlag = True

# 区域截图(100, 100)到(400, 400)
def DoClickScreenshot(args):
    ClickScreenshotBtn()
    time.sleep(1)
    DesktopCommon.MouseTo(100, 100)
    DesktopCommon.MouseDown()
    time.sleep(1)

    DesktopCommon.MouseTo(400, 400)
    DesktopCommon.MouseUp()

    time.sleep(1)
    DesktopCommon.MouseDbClick(300,300)

    # 防止动作失效
    DesktopCommon.SendScKeys("ESC")
    DesktopCommon.SendScKeys("ESC")

# 将网页保存为图片
def DoSavePages(args):
    handle = GetHandle()
    if handle == 0:
	return
    ClickTooBarOffset(handle, 312, 10)
    ClickTooBarOffset(handle, 295, 75)

    # 另存为
    saveHandle = GetHandle("#32770", "另存为")
    if saveHandle == 0:
	return

    # 设置保存路径
    editHandle = DesktopCommon.GetChildHandle(saveHandle, "Edit", None)
    edit = win32ui.CreateWindowFromHandle(editHandle)
    path = os.path.join(tempfile.gettempdir(), "image.jpg")
    edit.SendMessage(win32con.WM_SETTEXT, path)
    DesktopCommon.ClickCtrlEx(saveHandle, "Button", "保存(&S)")


    if DesktopCommon.WaitForWnd("#32770", "确认另存为", 5):
	dialogHandle = GetHandle("#32770", "确认另存为")
	if dialogHandle != 0:
	    DesktopCommon.ClickCtrlEx(dialogHandle, "Button", "是(&Y)")

     # 防止动作失效
    DesktopCommon.SendScKeys("ESC")

def DoClickBubble(args):
    DoClickAircraftToCance(args)
    DoClickAircraft(args)

    #如果气泡存在，则点击气泡
    height = DesktopCommon.GetHandle("SE_WKNW", None, 8)
    DesktopCommon.ClickOnCtrlWithWin32("SE_WKNW", 98, 65, "righttop")

g_urls = []
g_urlsForFav = []
def GetUrl(urlFilePath,urls = g_urls):
    #if len(urls) == 0:
    if not os.path.isfile(urlFilePath):
	urlFilePath = os.path.join(DesktopCommon.GetFrameworkPath(), r"case\SeStability\url.txt")
    count = -1
    #读取url文件
    for count,line in enumerate(open(urlFilePath,'rU')):
	count+=1
	urls.append(line.strip())
    if count == 0:
	urls.append("http://www.sohu.com")
    url = urls[GenRandom(len(urls)-1)]
    return url

def GetUrlForFav(urlFilePath):
    global g_urlsForFav
    return GetUrl(urlFilePath,g_urlsForFav)

def DoPreAction():
    for preaction in g_preAction:
	try:
	    CallSerialFunc(g_preAction,preaction[0])
	except:
	    f = open(DesktopCommon.GetFrameworkPath()+"/action.txt",'a')
	    f.write(preaction[0]+"\t")
	    import traceback
	    f.write("exec error:"+ traceback.format_exc() + os.linesep)
	    f.flush()


def DoPostAction():
    for postaction in g_postAction:
        CallSerialFunc(g_postAction,postaction[0])

def DoOpenSideBar(sideBarCtrlName="SE_TuotuoSidebar"):
    exist = DesktopCommon.CtrlExistByWin32("SE_TuotuoSidebar")
    if not exist:
	DesktopCommon.SendScKeys("LCTRL","i")
	time.sleep(1)
	if not DesktopCommon.CtrlExistByWin32("SE_TuotuoSidebar"):
	    DesktopCommon.ClickOnCtrlWithWin32("SE_TuotuoTabCtrl", 10, 8, "lefttop")
	    time.sleep(1)


def DoOpenHistorySidebar(args):
    #打开历史记录
    #试图重现3689崩溃栈：
    #SogouExplorer_40000000!ATL::CTimeEx::TimeToTm+0x10
    #SogouExplorer_40000000!ATL::CTimeEx::CTimeEx+0x15
    #SogouExplorer_40000000!CHistoryContentTreeCtrl::CHistoryContentTreeCtrl+0x5c
    DoOpenSideBar()
    wndInfo = DesktopCommon.GetWndPosEx("SE_TuotuoSidebar")
    ClickCtrl(wndInfo[-1],10,55)
    time.sleep(1)
    dateOrSite = GenRandom(1)
    if dateOrSite == 0:
	#点击日期视图
	ClickCtrl(wndInfo[-1],wndInfo[2]-100,40)
    else:
	#点击站点视图
	ClickCtrl(wndInfo[-1],wndInfo[2]-30,40)
    #在视图区随意点击吧。
    ClickCtrl(wndInfo[-1],50,100)
    time.sleep(1)
    ClickCtrl(wndInfo[-1],50,120)
    time.sleep(1)
    for i in range(10):
	posy = GenRandom(wndInfo[3]-20,100)
	ClickCtrl(wndInfo[-1],50,posy)
	time.sleep(1)

# 返回智能填表管理器的句柄和范围
def ShowAndGetTableManager():
    mainHandle = GetHandle()
    if mainHandle == 0:
	return
    SetForeground(mainHandle)
    DesktopCommon.ClickWindow("SE_TuotuoMenuBar", 245, 10)
    time.sleep(0.2)
    DesktopCommon.SendScKeys("f")
    time.sleep(0.2)
    DesktopCommon.SendScKeys("o")
    time.sleep(0.2)

    handle = GetSubHandle(0, None, "智能填表管理器")
    if handle != 0:
	rect = win32gui.GetWindowRect(handle)
    return (handle, rect)

##@函数目的: 智能填表管理器
##@参数说明：
##@返回值：
##@函数逻辑:
def DoClickTableManager(args):
    rect = ShowAndGetTableManager()[-1]
    if rect == None:
	return

    DesktopCommon.MouseClick(rect[0] + 400, rect[1] + 110)
    DesktopCommon.SendScKeys("LCTRL", "a")
    DesktopCommon.InputText("sogoutest")

    time.sleep(1)
    DesktopCommon.MouseClick(rect[2] - 56, rect[3] - 50)
    DesktopCommon.MouseClick(rect[2] - 56, rect[3] - 50)

    DesktopCommon.MouseClick(rect[2] - 20, rect[1] + 8)
    DesktopCommon.SendScKeys("ESC")
    DesktopCommon.SendScKeys("ESC")

##@函数目的: 点击帮助带单中的用户向导
##@参数说明：
##@返回值：
##@函数逻辑:
def DoClickUserGuide(args):
    mainHandle = GetHandle()
    if mainHandle == 0:
	return
    SetForeground(mainHandle)
    DesktopCommon.SendScKeys("LALT", "h")
    time.sleep(1)
    DesktopCommon.SendScKeys("w")
    DesktopCommon.SendScKeys("w")

    dialogHandle = GetHandle("#32770", "搜狗高速浏览器设置向导")
    if dialogHandle != 0:
	SetForeground(dialogHandle)
	subDialogHandle = GetSubHandle(dialogHandle, "#32770", "")
	if subDialogHandle != 0:
	    rect = win32gui.GetWindowRect(subDialogHandle)
	    points = (40, 60, 80)
	    for i in points:
		DesktopCommon.MouseClick(rect[0] + 95, rect[1] + i)

    nextButtonHandle = GetSubHandle(dialogHandle, "Button", "下一步")
    ClickCtrl(nextButtonHandle, 25, 10)
    ClickCtrl(nextButtonHandle, 25, 10)
    defaultButtonHandle = GetSubHandle(dialogHandle, "Button", "恢复默认")
    ClickCtrl(defaultButtonHandle, 25, 10)
    ClickCtrl(nextButtonHandle, 25, 10)
    ClickCtrl(nextButtonHandle, 25, 10)
    ClickCtrl(nextButtonHandle, 25, 10)
    DesktopCommon.SendScKeys("ESC")

def DoOpenDynPageOnSideBar(sideBarCtrlName="SideBar",dynToolBarCtrlName="DynToolbar"):
    #if not DesktopCommon.CtrlExist(dynToolBarCtrlName):
    #DesktopCommon.ClickOnCtrl(sideBarCtrlName,"LEFT","10*80")
    try:
	wndInfo = DesktopCommon.GetWndPosEx("SE_TuotuoSidebar")
	handle = wndInfo[-1]
	ClickCtrl(handle,10,80)
	return handle
    except:
	None


def DoClickDynPageOnSideBar(args,sideBarCtrlName="SE_TuotuoSidebar",dynToolBarCtrlName="DynToolbar",startPosx=70,startPosy=85):
    DoOpenSideBar(sideBarCtrlName)
    idx = GenRandom(args[0])
    handle = DoOpenDynPageOnSideBar(sideBarCtrlName,dynToolBarCtrlName)
    #pos = str(startPosx)+"*"+str(startPosy+idx*22)
    #DesktopCommon.ClickOnCtrl(sideBarCtrlName,"LEFT",pos)
    ClickCtrl(handle,startPosx,startPosy+idx*22)
    #win32api.CloseHandle(handle)

def DoOpenDynPageOnSideBarByRightClick(args,sideBarCtrlName="SideBar",dynToolBarCtrlName="DynToolbar",startPosx=70,startPosy=85):
    DoOpenSideBar(sideBarCtrlName)
    handle = DoOpenDynPageOnSideBar(sideBarCtrlName,dynToolBarCtrlName)
    idx = GenRandom(args[0])
    #pos = str(startPosx)+"*"+str(startPosy+idx*22)
    #DesktopCommon.ClickOnCtrl(sideBarCtrlName,"RIGHT",pos)
    ClickCtrl(handle,startPosx,startPosy+idx*22,"RIGHT")
    time.sleep(2)
    DesktopCommon.SendScKeys("o")

def DoEditDynPageOnSideBarByRightClick(maxIdx,sideBarCtrlName="SideBar",dynToolBarCtrlName="DynToolbar",startPosx=70,startPosy=85):
    DoOpenSideBar(sideBarCtrlName)
    handle = DoOpenDynPageOnSideBar(sideBarCtrlName,dynToolBarCtrlName)
    idx = GenRandom(maxIdx)
    #pos = str(startPosx)+"*"+str(startPosy+idx*22)
    #DesktopCommon.ClickOnCtrl(sideBarCtrlName,"RIGHT",pos)
    ClickCtrl(handle,startPosx,startPosy+idx*22,"RIGHT")
    time.sleep(1)
    DesktopCommon.SendScKeys("e")

def DoCancelFocusDynPageOnSideBarByRightClick(args,sideBarCtrlName="SideBar",dynToolBarCtrlName="DynToolbar",startPosx=70,startPosy=85):
    DoOpenSideBar(sideBarCtrlName)
    handle = DoOpenDynPageOnSideBar(sideBarCtrlName,dynToolBarCtrlName)
    idx = GenRandom(args[0])
    #pos = str(startPosx)+"*"+str(startPosy+idx*22)
    #DesktopCommon.ClickOnCtrl(sideBarCtrlName,"RIGHT",pos)
    ClickCtrl(handle,startPosx,startPosy+idx*22,"RIGHT")
    time.sleep(1)
    DesktopCommon.SendScKeys("d")
    time.sleep(1)
    DesktopCommon.SendScKeys("ENTER")
    win32api.CloseHandle(handle)


#点击更新全部
def DoUpdateAll(args,sideBarCtrlName="SideBar",dynToolBarCtrlName="DynToolbar"):
    DoOpenSideBar(sideBarCtrlName)
    handle = DoOpenDynPageOnSideBar(sideBarCtrlName, dynToolBarCtrlName)
    #DesktopCommon.ClickOnCtrl(dynToolBarCtrlName,"LEFT","30*15")
    ClickCtrl(handle, 45, 30)
    win32api.CloseHandle(handle)
    time.sleep(2)

def DoEditDynPage(args,text=""):
    maxIdx = args[0]
    value = args[1]
    idx = GenRandom(maxIdx)
    DoEditDynPageOnSideBarByRightClick(idx)
    DesktopCommon.ClickOnCtrl("Dyn_Setting_ManualSetInterval_CheckBox")
    time.sleep(0.5)
    DesktopCommon.SetCtrlText("Dyn_Setting_IntervalValue_TextBox",value)
    time.sleep(0.5)
    DesktopCommon.ClickOnCtrl("Dyn_Setting_Minus_Updown")
    time.sleep(0.5)
    DesktopCommon.ClickOnCtrl("Dyn_Setting_OK")

def GenDragPos(start,end):
    #产生水平方向上的拖拽位置
    import random
    return random.randint(start,end)

def DoDragAndDropToolBarItem(args):
    wndPosInfo = DesktopCommon.GetWndPosEx("SE_TuotuoToolsBar")
    oldx = GenDragPos(wndPosInfo[0],wndPosInfo[0] + wndPosInfo[2]/2 - 10)
    newx = GenDragPos(wndPosInfo[0],wndPosInfo[0] + wndPosInfo[2] - 10) #新位置
    y = wndPosInfo[1] + 4
    SeSmoke.MouseDrag(oldx, y, newx, y)
    time.sleep(1)
    SeSmoke.MouseDrag(newx, y, oldx, y)

# final版反复打开和关闭工具盒子
def DoOpenAndCloseExtBox(args):
    ClickToolBox()
    time.sleep(0.5)
    DesktopCommon.MouseClick(628, 18)


# 工具栏上卸载插件
def DoUninstallExt(args):
    #进行拖拽，只进行水平方向上的拖拽
    className = "SE_TuotuoToolsBar"
    #开始进行拖拽
    ToolBoxPos = DesktopCommon.GetWndPosEx(className)
    times = GenRandom(5)
    for i in range(times+1):
	DesktopCommon.MouseClick(ToolBoxPos[0]+90, ToolBoxPos[1]+10,"RIGHT")
	time.sleep(0.5)
	DesktopCommon.SendScKeys("u")
	time.sleep(0.5)
	DesktopCommon.SendScKeys("ENTER")
	time.sleep(0.5)

def CloseAllDialog():
    dialogs = DesktopCommon.EnumAllWindows()
    for dialog in dialogs:
	if dialog[1] == "#32770" and win32gui.IsWindowVisible(dialog[0]) == 1:
	    DesktopCommon.CloseWindowByHandle(dialog[0])

# 通过命令行安装插件
def DoInstallExtByCMD(args):
    path = ""
    if len(args) > 0:
	path = args[0]
    else:
	path = os.path.join(os.environ["appdata"], r"SogouExplorer\Extension")
    extList = []
    if os.path.exists(path):
	for root, dirs, files in os.walk(path):
	    for filename in files:
		if filename.endswith("sext"):
		    extList.append(os.path.join(root, filename))
    if len(extList) == 0:
	return

    maxNum = min(5, len(extList))
    num = GenRandom(maxNum, 1)
    exts = random.sample(extList, num)
    for extpath in exts:
	DesktopCommon.OpenProcess(DesktopCommon.GetSEDir()+"\\SogouExplorer.exe", extpath)
	time.sleep(1)
	DesktopCommon.SendScKeys("ENTER")

# final版安装插件
def DoInstallExtFinal(args):
    ClickToolBox()
    time.sleep(1)
    #  点击推荐工具
    handle = DesktopCommon.GetWindowHandle("SGDUI.*", None, None, 2)
    if handle == 0:
	return
    DesktopCommon.ClickOnHandle(handle, 130, 17)

    time.sleep(1)
    x = 198
    y = 61
    for i in range(5):
	for j in range(2):
	    DesktopCommon.ClickOnHandle(handle, x + 229 * j, y + 24 * i)

# 点击插件盒子
def ClickExtBox(itemdy = 10, boxOffsetX = 64, isClick = False):
    ClickToolBox()
    time.sleep(1)

    #  点击管理
    handle = DesktopCommon.GetWindowHandle("SGDUI.*", None, None, 2)
    if handle == 0:
	return
    rect = win32gui.GetWindowRect(handle)
    DesktopCommon.MouseClick(rect[2] - 33, rect[3] - 14)
    time.sleep(0.5)
    DesktopCommon.MouseClick(rect[2] - 30, rect[3] + itemdy)

    # 随机点击几个左上角
    boxOffsetY = 47
    dx = 75
    dy = 71
    num = GenRandom(5, 1)
    for i in range(num):
	row = GenRandom(1)
	col = GenRandom(5)
	DesktopCommon.MouseClick(rect[0] + boxOffsetX + dx * col, rect[1] + boxOffsetY + dy * row)
	time.sleep(0.5)
	if isClick:
	    DesktopCommon.MouseClick((rect[0] + rect[2])/2 + 28, (rect[1] + rect[3])/2 + 56)
	    time.sleep(0.5)
    time.sleep(0.5)
    # 点击完成
    DesktopCommon.MouseClick(rect[2] - 30, rect[3] - 14)

# final版在盒子中卸载插件
def DoUninstallExtInBox(args):
    ClickExtBox(35, 25, True)

# Final版启用和停用插件
def DoClickExtToolBoxUseIconFinal(args):
    ClickExtBox(10, 59)

# Final版显示或隐藏插件
def DoShowOrHideExtUseIconFinal(args):
    ClickExtBox(-5, 59)

# 点击插件盒子
def ClickExtBoxOld(itemdy = 10, boxOffsetX = 64, flag = False):
    ClickToolBox()
    time.sleep(1)

    #  点击管理
    handle = DesktopCommon.GetWindowHandle("SE_TuoLiteTooltip", None, None, 2)
    if handle == 0:
	return
    rect = win32gui.GetWindowRect(handle)

    DesktopCommon.MouseClick(rect[0] + 25, rect[3] - 20)
    time.sleep(0.5)
    DesktopCommon.MouseClick(rect[0] + 25, rect[3] - 20)
    time.sleep(0.5)
    DesktopCommon.MouseClick(rect[0] + 65, rect[3] - itemdy)
    time.sleep(0.5)


    # 随机点击几个左上角
    boxOffsetY = 40
    dx = 80
    dy = 70
    num = GenRandom(5, 1)
    for i in range(num):
	row = GenRandom(2)
	col = GenRandom(4)
	DesktopCommon.MouseClick(rect[0] + boxOffsetX + dx * col, rect[1] + boxOffsetY + dy * row)
	if flag:
	    DesktopCommon.MouseClick(rect[0] + 210, rect[1] + 213)
    time.sleep(0.5)
    # 点击完成
    DesktopCommon.MouseClick(rect[2] - 40, rect[3] - 18)


#启用和停用工具
def DoClickExtToolBoxUseIcon(args,className="SE_TuoLiteTooltip"):
    ClickExtBoxOld(56, 64)

# 显示和隐藏工具
def DoShowOrHideExtUseIcon(args):
    ClickExtBoxOld(82, 64)

# 在盒子中卸载插件
def DoUninstallExtInBoxOld(args):
    ClickExtBoxOld(31, 32, True)

# 安装插件
def DoInstallExt(args):
    #可以改成从命令行安装的实现。如何把所有的插件都删除
    ClickToolBox()
    #开始点击推荐工具
    time.sleep(2)
    wndInfo = DesktopCommon.GetWndPosEx("SE_TuoLiteTooltip")
    extTabPosx = wndInfo[0]+110
    extTabPosy = wndInfo[1]+20
    DesktopCommon.MouseClick(extTabPosx,extTabPosy)
    time.sleep(2)
    startx = wndInfo[0]+wndInfo[2]-30
    starty = wndInfo[1]+30
    for i in range(wndInfo[3]/30):
	pos = (startx, starty+i*15)
	win32api.SetCursorPos(pos)
	time.sleep(0.01)
	if IsCursorLink():
	    #如果发现插件安装按钮
	    DesktopCommon.MouseClick(pos[0],pos[1])
	    time.sleep(1)
	    SetForeground(wndInfo[-1])
	time.sleep(0.2)


def ClickToolBox(x=14,y=80):
    toolBarPos = [x,y]
    newPos = DesktopCommon.GetWndPosEx("SE_TuotuoToolsBar")
    if -1 != newPos:
        toolBarPos = newPos
    DesktopCommon.MouseClick(toolBarPos[0]+30,toolBarPos[1])

# 点击插件盒子中插件图标的右上角
def DoClickExtBoxLeftTop(args):
    ClickToolBox()
    time.sleep(1)

    #  点击我的工具
    handle = DesktopCommon.GetWindowHandle("SGDUI.*", None, None, 2)
    if handle == 0:
	return
    DesktopCommon.ClickOnHandle(handle, 130, 20)
    DesktopCommon.ClickOnHandle(handle, 40, 20)
    rect = win32gui.GetWindowRect(handle)

    x = 58
    y = 53
    dx = 75
    dy = 71
    for i in range(5):
	xx = rect[0] + x + dx * GenRandom(5)
	yy = rect[1] + y + dy * GenRandom(1)
	DesktopCommon.MouseClick(xx, yy)
	time.sleep(0.5)
	DesktopCommon.SendScKeys("ESC")

    DesktopCommon.ClickOnHandle(handle, 130, 20)
    DesktopCommon.MouseClick(rect[2] - 50, rect[3] - 13)

# 点击插件盒子中插件图标的右上角
def DoClickExtBoxLeftTopOld(args):
    ClickToolBox()
    time.sleep(1)

    #  点击我的工具
    handle = DesktopCommon.GetWindowHandle("SE_TuoLiteTooltip", None, None, 2)
    if handle == 0:
	return
    DesktopCommon.ClickOnHandle(handle, 130, 20)
    DesktopCommon.ClickOnHandle(handle, 40, 20)
    rect = win32gui.GetWindowRect(handle)

    x = 63
    y = 38
    dx = 80
    dy = 70
    for i in range(5):
	xx = rect[0] + x + dx * GenRandom(4)
	yy = rect[1] + y + dy * GenRandom(2)
	DesktopCommon.MouseClick(xx, yy)
	time.sleep(0.5)
	DesktopCommon.SendScKeys("ESC")

    DesktopCommon.ClickOnHandle(handle, 130, 20)
    DesktopCommon.MouseClick(rect[2] - 50, rect[3] - 13)


# 点击插件盒子的随机位置
def DoClickExtBoxFinal(args):
    ClickToolBox()
    time.sleep(1)
    #  点击我的工具
    handle = DesktopCommon.GetWindowHandle("SGDUI.*", None, None, 2)
    if handle == 0:
	handle = DesktopCommon.GetWindowHandle("SE_TuoLiteTooltip", None, None, 2)
	if handle == 0:
	    return
    DesktopCommon.ClickOnHandle(handle, 40, 20)
    rect = win32gui.GetWindowRect(handle)

    for i in range(5):
	x = GenRandom(rect[2], rect[0])
	y = GenRandom(rect[3], rect[1])

	DesktopCommon.MouseClick(x, y)
	time.sleep(0.5)
	DesktopCommon.SendScKeys("ESC")

# 在插件盒子中进行拖拽
def DoDragAndDropItemInExtBoxFinal(args):
    ClickToolBox()
    time.sleep(1)
    #  点击我的工具
    handle = DesktopCommon.GetWindowHandle("SGDUI.*", None, None, 2)
    if handle == 0:
	return
    DesktopCommon.ClickOnHandle(handle, 40, 20)
    rect = win32gui.GetWindowRect(handle)

    x = 43
    y = 69
    dx = 75
    dy = 71
    for i in range(5):
	startX = rect[0] + x + dx * GenRandom(5)
	startY = rect[1] + y + dy * GenRandom(1)
	endX = rect[0] + x + dx * GenRandom(5)
	endY = rect[1] + y + dy * GenRandom(1)
	SeSmoke.MouseDrag(startX, startY, endX, endY)


def DoDragAndDropItemInExtBox(args,className="SE_TuoLiteTooltip"):
    #进行拖拽，只进行水平方向上的拖拽
    try:
        handle = win32gui.FindWindow(className,None)
    except:
        handle = 0
    if handle == 0:
        #工具盒窗口不在，所以需要点击该盒子
        ClickToolBox()
        win32api.CloseHandle(handle)
	time.sleep(1)
    #开始进行拖拽
    ToolBoxPos = DesktopCommon.GetWndPosEx(className)
    ItemInToolBoxPosStartX = ToolBoxPos[0] + 40
    ItemInToolBoxPosEndX = ToolBoxPos[0] + 296
    ItemInToolBoxPosStartY = ToolBoxPos[1] + 47
    ItemInToolBoxPosEndY = ToolBoxPos[1] + 181
    startx = GenDragPos(ItemInToolBoxPosStartX,ItemInToolBoxPosEndX)
    starty = GenDragPos(ItemInToolBoxPosStartY,ItemInToolBoxPosEndY)
    endx = GenDragPos(ItemInToolBoxPosStartX,ItemInToolBoxPosEndX)
    endy = GenDragPos(ItemInToolBoxPosStartY,ItemInToolBoxPosEndY)
    SeSmoke.MouseDrag(startx,starty,endx,endy)


UnRestoredIconArray = [] #没有恢复的工具列表
XDistanceBetweenShowIcon = 64                   #每个图标之间的水平距离
YDistanceBetweenShowInco = 64                   #每个图标之间的垂直距离
#点击“在工具栏显示按钮”后，点击各插件右上角的显示状态
def ClickShowIcon(xIndex,yIndex,startx,starty):
    DesktopCommon.MouseClick(startx+xIndex*XDistanceBetweenShowIcon,
               starty + yIndex*YDistanceBetweenShowInco)

def RandomClickItemInBox(startx,className,restore=True):
    UnRestoredIconArray = []
    randCount = 1+random.randint(0,5) #每次随机点6次以内
    ToolBoxPos = DesktopCommon.GetWndPosEx(className)
    time.sleep(1)
    YesToUninstallButtonX = ToolBoxPos[0] + 200   #确定删除的按钮
    YesToUninstallButtonY = ToolBoxPos[1] + 175   #取消删除的按钮
    FirstShowInToolBarStartY = ToolBoxPos[1] + 40
    for i in range(randCount):
        xIndx = random.randint(0,4)
        yIndx = random.randint(0,2)
        ClickShowIcon(xIndx,yIndx,startx,FirstShowInToolBarStartY)
        if restore:
            UnRestoredIconArray.append((xIndx,yIndx))
        else:
            #不需要恢复，说明是卸载，所以需要点击确定删除按钮
            DesktopCommon.MouseClick(YesToUninstallButtonX,YesToUninstallButtonY)
        time.sleep(0.5)
    if restore:
        for pair in UnRestoredIconArray:
            ClickShowIcon(pair[0],pair[1],startx,FirstShowInToolBarStartY)

def GetDynBoxHandle(classname = "SE_AxControl", minLeft = 450, maxRight = 2000):
    return DesktopCommon.GetDynBoxHandle(classname, minLeft, maxRight, 1)

def DoClickDynBox(className="SE_TuoLiteTooltip",x=15,y=16):
    global g_semigi
    retryTime = 0

    while retryTime < 3:
	if g_semigi == "0":
	    try:
		wndInfo = GetDynBoxHandle()
		if wndInfo == 0:
		    # 安装插件
		    extpath = os.path.join(DesktopCommon.GetFrameworkPath(), r"case\SeStability\messageBox.sext")
		    DesktopCommon.OpenProcess(DesktopCommon.GetSEDir()+"\\SogouExplorer.exe", extpath)

		    handle = GetHandle("SE_TuoInstExt", "安装搜狗浏览器插件", 2)
		    DesktopCommon.ClickCtrlEx(handle, "Button", "是")
		    #wndInfo = DesktopCommon.GetWndPosEx("SE_TuotuoToolsBar")

		    # 点击状态栏
		    wndInfo = DesktopCommon.GetWndPosEx("SE_TuotuoStatusbarToolbar")
		    ClickCtrl(wndInfo[-1], 12, 11)
		    time.sleep(0.5)
		    retryTime += 1
		else:
		    return wndInfo
	    except:
		time.sleep(1)
		retryTime += 1
	else:
	    try:
		handle = win32gui.FindWindow(className, None)
		if handle==0:
		    #DesktopCommon.ClickOnCtrl("seStatusBar","LEFT",str(x)+"*"+str(y))
		    wndInfo = DesktopCommon.GetWndPosEx("SE_TuotuoStatusbarToolbar")
		    ClickCtrl(wndInfo[-1],x,y)
		    time.sleep(1)
		    retryTime += 1
		else:
		    break
	    except:
		DesktopCommon.ClickOnCtrl("seStatusBar","LEFT",str(x)+"*"+str(y))
		time.sleep(1)
		retryTime += 1



def DoBlindClickDynBox(className="SE_TuoLiteTooltip",x=5,y=5):
    #DesktopCommon.ClickOnCtrl("seStatusBar","LEFT",str(x)+"*"+str(y))
    wndInfo = DesktopCommon.GetWndPosEx("SE_TuotuoStatusbarToolbar")
    ClickCtrl(wndInfo[-1],x,y)
    time.sleep(2)


#def DoClickPassport(x=38, y=10):
#   #DesktopCommon.ClickOnCtrl("seStatusBar","LEFT",str(x)+"*"+str(y))
#   DesktopCommon.ClickOnCtrlWithWin32("SE_TuoHeadPortrait",20,20, "Lefttop")
#  time.sleep(1)
def DoClickPassport():
    DesktopCommon.SendScKeys("LALTDOWN","u")
    time.sleep(0.5)
    DesktopCommon.SendScKeys("i")


def WriteCrash(info):
    return
    f = open(DesktopCommon.GetFrameworkPath()+"\\loginfo.txt",'a')
    f.write(info+os.linesep)
    f.flush()


#退出通行证

def DoLogonPassport(args,user="setest1215@sohu.com",ps="sohutest",wndName="网络账户登录"):
    if len(args)>0:
	user = args[0]
	ps = args[1]
	wndName = args[2]
	return
    if not IsLogged():
	DoClickPassport()
	DesktopCommon.WaitForWndVisible("#32770", None, 5)
	time.sleep(0.5)
	DesktopCommon.ClickOnCtrlWithWin32("#32770",300,200,"lefttop")
	DesktopCommon.SendScKeys("TAB")
	time.sleep(0.2)
	DesktopCommon.SendScKeys("LCTRL","a")
	time.sleep(0.2)
	DesktopCommon.CtrlV(user)
	time.sleep(0.2)
	DesktopCommon.SendScKeys("TAB")
	time.sleep(0.2)
	DesktopCommon.SendScKeys("LCTRL","a")
	time.sleep(0.2)
	DesktopCommon.CtrlV(ps)
	DesktopCommon.SendScKeys("ENTER")
    else:
	return
	#说明已经登陆，不再登陆
    print "already logged"



def DoLogoutPassportEx(uiCtrlName="SE_Passport_LogoutWnd"):
    DoClickPassport()
    time.sleep(1)
    #DesktopCommon.ClickOnCtrl(uiCtrlName,"LEFT","280*168")
    wndInfo = DesktopCommon.GetWndPosEx(None, "网络账户")
    ClickCtrl(wndInfo[-1], 280, 168)

#登录通行证
def DoLogonPassportOld(user,ps,uiCtrlName="Passport_PromptLogonCbx"):
    DoClickPassport()
    if IsLogged():
	DesktopCommon.ClickOnCtrl("Passport_LogoutBtn")
	time.sleep(4)
	DoClickPassport()
    time.sleep(1)
##    DesktopCommon.SetCtrlText("Passport_UserName",user)
##    time.sleep(1)
##    DesktopCommon.SendScKeys("TAB")
##    time.sleep(1)
##    DesktopCommon.InputText(ps)
##    time.sleep(1)
##    DesktopCommon.ClickOnCtrl("Passport_LogonBtn")
##    time.sleep(10)
##    if DesktopCommon.CtrlExist("强行登陆按钮"):
##	DesktopCommon.ClickOnCtrl("强行登陆按钮")
##	time.sleep(1)
    if DesktopCommon.CtrlExist("网络账户登陆"):
	DesktopCommon.ClickOnCtrl("网络账户登陆","LEFT","150*110")
	time.sleep(10)
	DesktopCommon.ClickOnCtrl("网络账户登陆","LEFT","300*241")
	time.sleep(5)
	DesktopCommon.ClickOnCtrl("网络账户登陆","LEFT","150*130")
	time.sleep(1)
	DesktopCommon.SendScKeys("LCTRL","a")
	time.sleep(1)
	DesktopCommon.CtrlV(user)
	time.sleep(1)
	DesktopCommon.ClickOnCtrl("网络账户登陆","LEFT","150*180")
	time.sleep(1)
	DesktopCommon.SendScKeys("LCTRL","a")
	time.sleep(1)
	DesktopCommon.CtrlV(ps)
	DesktopCommon.ClickOnCtrl("网络账户登陆","LEFT","200*220")
	DesktopCommon.CheckCbx("下次自动登录",False)
	time.sleep(15)

#判断是否登录了通行证
# True --- 代表已经登录
# Flase --- 代表没有登录
def IsLogged():
    import string
    retrytimes = 0
    while retrytimes<2:
	DesktopCommon.SendScKeys("F5")
	try:
	    handle = win32gui.FindWindow("SE_SogouExplorerFrame",None)
	    text = win32gui.GetWindowText(handle)
	    print text.decode('gbk')
	    strTemp = text.decode('gbk')
	    strExpect = u"高速"
	    if string.find(strTemp, strExpect)==-1:
	    #没有找到高速两字，说明已经登录通行证
		print "logged"
		return True
	    else:
		print "not logged"
	        return False
	except:
	    time.sleep(1)
	    retrytimes+=1
    return

#等待通行证登录完毕
def WaitLogon(times=10):
    retryTimes = 0
    while retryTimes<times:
	if IsLogged():
	    return True
	time.sleep(1)
	retryTimes+=1
    return False


    #退出通行证
def DoLogoutPassport():
    if not IsLogged():
	#如果没有登录，则没必要退出了
	time.sleep(0.2)
	return
    DesktopCommon.SendScKeys("LALT","u")
    time.sleep(0.2)
    DesktopCommon.SendScKeys("o")

    ##def DoLogoutPassport(args):
	#if not IsLogged():
	    ##如果没有登录，则没必要退出了
	    #time.sleep(0.2)
	    #return
	#DoClickPassport()
	#try:
	    #wndName = args[0]
	#except:
	    #wndName = "网络账户"
	#rect = -1
	#for i in range(10):
	    #try:
		#rect = DesktopCommon.GetWndPosEx(None,wndName)
		#if rect==-1:
		    #time.sleep(0.4)
		#else:
		    #break
	    #except:
		#time.sleep(0.4)
	#if rect!=-1 and len(rect)>=4:
	    #DesktopCommon.MouseClick(rect[0]+280,rect[1]+128)


    time.sleep(2)

def DoLogonAndOutPassport(args):
    DoLogonPassport(args[0],args[1])
##    DoClickDynPageOnSideBar([1])
##    DoEditDynPage([2,1])
##    DoOpenDynPageOnSideBarByRightClick([3])
    InPassportStartTest(30) #登录通行证后操作30秒
    DoLogoutPassport()

def ClickHead():
    handle = GetSEHandle()
    DesktopCommon.ClickOnHandle(handle, 30, 30)
    DesktopCommon.Sleep(1)

def DoClickHeadNavigateFav(args):
    if not IsLogged():
	return
    ClickHead()

    handle = GetSEHandle()

    for i in range(5):
	DesktopCommon.ClickOnHandle(handle, 118, 211 + 20 * GenRandom(10))
	DesktopCommon.Sleep(0.5)

def DoClickHeadNavigateOften(args):
    if not IsLogged():
	return
    ClickHead()

    handle = GetSEHandle()

    DesktopCommon.ClickOnHandle(handle, 214, 165)
    DesktopCommon.Sleep(1)
    for i in range(5):
	DesktopCommon.ClickOnHandle(handle, 118, 211 + 20 * GenRandom(10))
	DesktopCommon.Sleep(0.5)

def DoClickHeadRefresh(args):
    if not IsLogged():
	return
    ClickHead()

    DesktopCommon.ClickOnCtrlWithWin32("SE_HeadPortraitMain", 35, 23, "righttop")
    DesktopCommon.Sleep(0.5)

def DoClickHeadTab(args):
    if not IsLogged():
	return
    ClickHead()

    for i in range(5):
	DesktopCommon.ClickOnCtrlWithWin32("SE_HeadPortraitMain", 83, 109, "lefttop")
	DesktopCommon.Sleep(1)
	DesktopCommon.ClickOnCtrlWithWin32("SE_HeadPortraitMain", 211, 109, "lefttop")
	DesktopCommon.Sleep(1)

def DoClickHeadSet(args):
    if not IsLogged():
	return
    ClickHead()

    DesktopCommon.ClickOnCtrlWithWin32("SE_HeadPortraitMain", 15, 23, "righttop")
    DesktopCommon.Sleep(0.5)

    DesktopCommon.ClickOnCtrlWithWin32("SE_HeadPortraitMain", -50, 11 + 20 * GenRandom(3), "righttop")
    DesktopCommon.Sleep(0.5)

    handle = GetSEOptionHandle(2)
    if handle != 0:
	allChecks = ["收藏夹","退出账户","网址访问","用户定义","智能填表","网页更新","工具盒子"]
	tempnum = GenRandom(len(allChecks), 1)
	lists = random.sample(allChecks, tempnum)
	for name in lists:
	    DesktopCommon.ClickCtrlEx(handle, "Button", name)
	    time.sleep(0.5)

    DesktopCommon.SendScKeys("ENTER")
    DesktopCommon.Sleep(0.5)

def DoClickHead(args):
    if not IsLogged():
	return
    for i in range(5):
	ClickHead()


#关闭消息盒子窗口
def PostCloseDynBox(args,className="SE_TuoLiteTooltip",x = 310,y=18):
    try:
	#handle = win32gui.FindWindow(ctrlName,None)
	wndInfo = DesktopCommon.GetWndPosEx(className)
	if handle!=0:
	    DesktopCommon.ClickOnCtrlNoFocus(ctrlName,x,y)

    except:
	None

#点击消息盒子的某项
def DoClickItemInDynBox(args,ctrlName="SE_TuoLiteTooltip",x=50,y=42):
    global g_semigi
    DoClickBubble(args)
    DoClickDynBox()

    if g_semigi == "0":
	wndInfo = GetDynBoxHandle()
	time.sleep(0.5)
	ClickCtrl(wndInfo, 186, 29)
	time.sleep(0.5)
	for i in range(5):
	    idx = GenRandom(5)
	    ClickCtrl(wndInfo, 72, 134 + 31 * idx)
	    time.sleep(0.5)
	    rect = DesktopCommon.GetRectByHandle(wndInfo)
	    DesktopCommon.MouseClick(rect[2] - 47, rect[3] - 55)
    else:
	itemHeight = args[1]
	#if JudgeDynBoxEmpty():
	    #return
	idx = GenRandom(args[0])
	DesktopCommon.ClickOnCtrlNoFocus(ctrlName,x,y+idx*itemHeight)


#清空消息盒子里的某个url下所有变化项
def DoClickClearItemInDynBox(args,ctrlName="SE_TuoLiteTooltip",x=293,y=42,itemHeight = 112):
    DoClickBubble(args)
    DoClickDynBox()
    idx = GenRandom(args[0])
    if idx == 0:
	DesktopCommon.ClickOnCtrlNoFocus(ctrlName,x,y)
    else:
	DesktopCommon.ClickOnCtrlNoFocus(ctrlName,x,y+86+(idx-1)*itemHeight)

# 打开关闭消息盒子
def DoCloseDynBoxByLoseFocus(args):
    global g_semigi
    if g_semigi == "0":
	DoClickBubble(args)
	DoClickDynBox()
	time.sleep(0.5)
	wndInfo = GetDynBoxHandle()
	ClickCtrl(wndInfo, -40, 120)
	time.sleep(0.5)

	DoClickDynBox()
	time.sleep(0.5)
	wndInfo = GetDynBoxHandle()
	rect = win32gui.GetWindowRect(wndInfo)
	DesktopCommon.MouseClick(rect[2] - 10, rect[1] - 15)
	time.sleep(0.5)

# 切换盒子中的功能页
def DoSwitchDynBoxItems(args):
    global g_semigi
    if g_semigi == "0":
	DoClickBubble(args)
	DoClickDynBox()
	time.sleep(0.5)
	wndInfo = GetDynBoxHandle()
	lists = [178, 285, 390]
	for i in range(8):
	    x = random.sample(lists, 1)[0]
	    ClickCtrl(wndInfo, x, 30)
	    time.sleep(0.5)

# 切换消息盒子中的网页列表
def DoSwitchDynBoxWebLists(args):
    global g_semigi
    if g_semigi == "0":
	DoClickBubble(args)
	DoClickDynBox()
	time.sleep(0.5)
	wndInfo = GetDynBoxHandle()
	ClickCtrl(wndInfo, 173, 30)
	time.sleep(0.5)
	ClickCtrl(wndInfo, 70, 80)
	time.sleep(0.5)
	for i in range(6):
	    idx = GenRandom(5)
	    if idx == 0:
		ClickCtrl(wndInfo, 70, 80)
	    else:
		ClickCtrl(wndInfo, 70, 134 + (idx - 1) * 30)
	    time.sleep(0.5)

#点击消息盒子里的变化项
def DoClickChangedItemInDynBox(args,ctrlName="SE_TuoLiteTooltip",x=50,y=42,itemHeight=112):
    global g_semigi
    DoClickBubble(args)
    DoClickDynBox()
    if g_semigi == "0":
	wndInfo = GetDynBoxHandle()
	rect = win32gui.GetWindowRect(wndInfo)
	ClickCtrl(wndInfo, 185, 34)
	idx = GenRandom(args[0])
	ran1 = GenRandom(2)
	ran2 = GenRandom(2)
	for i in range(5):
	    ClickCtrl(wndInfo, 247, 114 + ran1 * 23 + ran2 * 140 + 15 * i)
	    time.sleep(0.5)
    else:
	if JudgeDynBoxEmpty():
	    return
	idx = GenRandom(args[0])
	if idx == 0:
	    DesktopCommon.ClickOnCtrlNoFocus(ctrlName,x,y+25)
	else:
	    DesktopCommon.ClickOnCtrlNoFocus(ctrlName,x,y+(idx-1)*itemHeight+25)
	PostCloseDynBox(args)

def DoAddToFocusFromDynBox(args, ctrlName="SE_TuoLiteTooltip", x=48, y=385):
    global g_semigi
    DoClickBubble(args)
    DoClickDynBox()
    if g_semigi == "0":
	wndInfo = GetDynBoxHandle()
	if wndInfo == None:
	    return
	ClickCtrl(wndInfo, 279, 25)
	time.sleep(0.5)
	ClickCtrl(wndInfo, 64, 82 + 27 * GenRandom(9))
	time.sleep(0.5)
	rect = DesktopCommon.GetRectByHandle(wndInfo)
	for i in range(5):
	    DesktopCommon.MouseClick(rect[2] - 30 - 189 * GenRandom(1), rect[1] + 145 + 72 * GenRandom(4))
	    time.sleep(0.5)
    else:
	wndInfo = DesktopCommon.GetWndPosEx(ctrlName)
	DesktopCommon.ClickOnCtrlNoFocus(ctrlName,x,wndInfo[3]-20)
	time.sleep(0.5)
	DesktopCommon.ClickOnCtrlNoFocus(ctrlName,262,200)
	time.sleep(0.5)
	PostCloseDynBox(args)


def DoClickNextPage(args,ctrlName="SE_TuoLiteTooltip",x=319,y=353):
    global g_semigi
    DoClickBubble(args)
    DoClickDynBox()
    time.sleep(0.5)
    if g_semigi == "0":
	wndInfo = GetDynBoxHandle()
	ClickCtrl(wndInfo, 185, 34)
	time.sleep(0.5)
	ClickCtrl(wndInfo, 70, 80)

	# 点击全部更新
	x = 210
	y = 188
	dy = 144
	time.sleep(0.5)
	idx = GenRandom(3)
	ClickCtrl(wndInfo, x, y + idx * 111)

	# 点击url
	for i in range(6):
	    idx = GenRandom(6)
	    ClickCtrl(wndInfo, x, 122 + idx * 39)
	    time.sleep(0.5)
	    rect = DesktopCommon.GetRectByHandle(wndInfo)
	    DesktopCommon.MouseClick(rect[2] - 47, rect[3] - 55)
    else:
	if (JudgeDynBoxEmpty()):
	    return
	DesktopCommon.ClickOnCtrlNoFocus(ctrlName,x,y)
	time.sleep(1.5)

#触发元搜索
def DoMetasearch(args):
    #DesktopCommon.CreateTabNav(args[0])
    #DoNavigate(args)
    url = GetUrl(args[0])
    rnd = GenRandom(2)
    if rnd==0:
	DesktopCommon.CreateTabNav(url)
    else:
	wndInfo = DesktopCommon.GetWndPosEx("SE_TuotuoSearchBar")
	DesktopCommon.MouseClick(wndInfo[0]+70,wndInfo[1]+10)
	time.sleep(0.2)
	DesktopCommon.CtrlC(url)
	DesktopCommon.CtrlV(url)
	time.sleep(0.2)
	DesktopCommon.SendScKeys("ENTER")
    time.sleep(3)


#触发浏览器升级
def DoUpdateSE(args):
    global g_processSecurity
    sepath = DesktopCommon.GetSEDir()
    upPath = ""
    for root, dirs, files in os.walk(sepath):
	for filename in files:
	    if filename.lower() == "sogouexplorerup.exe":
		upPath = os.path.join(root, filename)
    DesktopCommon.OpenProcess(upPath, "", g_processSecurity)

#点击消息盒子里的“展开列表"
def ExpandDynBoxItem(idx,ctrlName="SE_TuoLiteTooltip",x=50,y=42,itemHeight=112):
    global g_semigi
    DoClickDynBox()
    time.sleep(0.5)
    if g_semigi == "0":
	wndInfo = GetDynBoxHandle()
	ClickCtrl(wndInfo, 185, 34)
	time.sleep(0.5)
	ClickCtrl(wndInfo, 70, 80)
	# 点击查看全部更新
	x = 218
	y = 190
	dy = 112
	time.sleep(0.5)
	idx = GenRandom(3)
	ClickCtrl(wndInfo, x, y + idx * 111)
    else:
	if idx == 0:
	    DesktopCommon.ClickOnCtrlNoFocus(ctrlName,x,y+86)
	else:
	    DesktopCommon.ClickOnCtrlNoFocus(ctrlName,x,y+86+(idx-1)*itemHeight)


#点击消息盒子里的“收起列表”
def CollapseDynBoxItem(idx,ctrlName="SE_TuoLiteTooltip",x=15,y=42,itemHeight=112):
    global g_semigi
    DoClickDynBox()
    if g_semigi == "0":
	wndInfo = GetDynBoxHandle()
	ClickCtrl(wndInfo, 185, 34)
	time.sleep(0.5)
	rect = DesktopCommon.GetRectByHandle(wndInfo)
	DesktopCommon.MouseClick(rect[2] - 47, rect[3] - 55)
    else:
	if idx == 0:
	    DesktopCommon.ClickOnCtrlNoFocus(ctrlName,x,y+86)
	else:
	    DesktopCommon.ClickOnCtrlNoFocus(ctrlName,x,y+86+(idx-1)*itemHeight)

def DoExpandDynBoxItemAndCollapse(args,ctrlName="SE_TuoLiteTooltip",x=50,y=42,expandHeight=86,itemHeight=112):
    global g_semigi
    DoClickDynBox()
    idx = GenRandom(args[0])
    ExpandDynBoxItem(idx)
    if g_semigi == "0":
	ctrlName = "SE_WKWExtSW"
	x = 70
	y = 160
    for i in range(5):
	DesktopCommon.ClickOnCtrlNoFocus(ctrlName,x,y + idx * expandHeight + i*30)
	time.sleep(0.5)
    CollapseDynBoxItem(idx)
    PostCloseDynBox(args, ctrlName, 469, 11)

#关闭一定数量的标签页
def DoCloseTab(args):
    cnt = args[0]
    import random
    for i in range(cnt):
	tabCount = GetWinResourceServer().GetTabCount
	if tabCount>9:
	    tabCount = 9
	if tabCount <= 1:
	    return
	rndIdx = random.randint(1,tabCount)
	DesktopCommon.SendScKeys("LCTRL",str(rndIdx))
	DesktopCommon.SendScKeys("LCTRL",'w')

def DoCloseTabExcept(args):
    title = args[0]
    num = args[1]
    tabCount = SeSmoke.GetSETabCount()
    if tabCount <= num:
	#只有一个tab，不做动作
	time.sleep(0.3)
	return
    DesktopCommon.SendScKeys("LCTRL", "3")
    time.sleep(1)
    wndTitle = DesktopCommon.GetSETitle()
    if wndTitle.find(title) == -1:
	DesktopCommon.SendScKeys("LCTRL",'w')
##    sehandles = DesktopCommon.GetWndHandles("SE_SogouExplorerFrame")
##    time.sleep(1)
##    try:
##	for wndinfo in sehandles:
##	    h = wndinfo[0]
##	    if wndinfo[1].find(title)!= -1:
##		#要操作的是需要避免关闭的页面
##		return
##	    else:
##		#DesktopCommon.SendScKeys("LCTRL",'w')
##		DoCloseTabByMenu(None)
##		time.sleep(1)
##		break
##    except:
##	None

##    rndIdx = random.randint(2,tabCount)
##    DesktopCommon.SendScKeys("LCTRL",str(rndIdx))
##    sehandles = DesktopCommon.GetWndHandles("SE_SogouExplorerFrame")
##    time.sleep(1)
##    f.write(os.linesep+"here3"+os.linesep)
##    f.flush()
##    if True:
##	fghandle = win32gui.GetForegroundWindow()
##	f.write("主框架个数:"+str(len(sehandles))+os.linesep)
##	f.flush()
##	f.write("前台句柄:"+str(fghandle)+os.linesep)
##	for wndinfo in sehandles:
##	    h = wndinfo[0]
##	    if h == fghandle:
##		#获取前台的浏览器框架句柄
##		f.write("title:"+wndinfo[1]+os.linesep)
##		f.flush()
##		if wndinfo[1].find(title)!= -1:
##		    #要操作的是需要避免关闭的页面
##		    f.write("cancel action"+os.linesep)
##		    f.flush()
##		    return
##		else:
##		    f.write("close"+os.linesep)
##		    f.flush()
##		    DesktopCommon.SendScKeys("LCTRL",'w')
##		    break
##    else:
##	None

##@函数目的: 当Action日志文件超过特定大小(args[0]M)时，备份文件
##@参数说明：
##@返回值：
##@函数逻辑：
def PreBackupLog(args):
    import shutil
    maxSize = args[0]
    actionPath = DesktopCommon.GetFrameworkPath()+"/action.txt"
    filesize = os.path.getsize(actionPath) / 1024 / 1024
    timeStr = time.strftime("_%Y_%m_%d_%H_%M_%S", time.localtime())
    actionBakPath = actionPath.replace(".txt", timeStr + ".txt")
    if filesize > maxSize:
	shutil.move(actionPath, actionBakPath)

#关闭超过args[0]个数的标签
def PreCloseAbuTab(args):
    cnt = args[0]
    title = ""
    if len(args) > 1:
	title = args[1]
    import random,win32con
    tabCount = GetWinResourceServer().GetTabCount
    if tabCount < 2:
	return
    if tabCount > cnt:
	for i in xrange(2,tabCount/2):
	    DesktopCommon.SendScKeys("LCTRL",str(i))
	    time.sleep(1)
	    seHandles = DesktopCommon.GetWndHandles("SE_TuotuoChildFrame")
	    LogAction("handle:"+str(seHandles[i][0]))
	    if title != "":
		seTitle = win32gui.GetWindowText(seHandles[i][0])
		if seTitle.lower().find(title.lower()) != -1:
		    continue
	    win32api.PostMessage(seHandles[i][0],win32con.WM_CLOSE,0,0)
    try:
	handle = win32gui.FindWindow(None,"网页更新提醒")
	if handle!=0:
	    win32api.PostMessage(handle,win32con.WM_CLOSE,0,0)
    except:
	None


####新建关闭动作

###验证在起始页的搜索框里按Alt F4的bug
##def DoTestAltF4InStartPageBug(args):
##    DoNewFrame(args)
##    try:
##	time.sleep(1)
##	h = win32gui.FindWindow("SE_SogouExplorerFrame",None)
##	win32gui.ShowWindow(h,win32con.SW_MAXIMIZE)
##	time.sleep(1)
##	DesktopCommon.NavigateSE("http://123.sogou.com")
##	time.sleep(5)
##	DesktopCommon.MouseClick(416,250)
##	time.sleep(1)
##	DesktopCommon.SendScKeys("LALT","F4")

#从一个进程拖动标签到另外一个进程中

#通过撤销新建标签。之前有bug，所以这里要覆盖
def DoNewTabByCancel(args):
    clickType = GenRandom(1)
    sehandle,chandle = GetSEHandleAndChildHandle("SE_TuotuoToolbar")
    if clickType == 0:
	ClickCtrl(chandle,146,18)
    else:
	ClickCtrl(chandle,158,20)
	time.sleep(0.2)
	ClickCtrl(chandle,158,40)
	time.sleep(0.2)

#通过快捷键新建标签
def DoNewTabByKey(args):
    DesktopCommon.SendScKeys("LCTRL","t")

def DoFind(args):
    #DesktopCommon.CreateTabNav("http://www.sohu.com")
    DoNavigate(args)
    time.sleep(3)
    if not DesktopCommon.WaitForWnd("SE_TuotuoFindBar",None,2):
	DesktopCommon.SendScKeys("LCTRL","f")
    wndInfo = DesktopCommon.GetWndHandles("SE_TuotuoFindBar")
    if wndInfo!=-1 and len(wndInfo)>0:
	ClickCtrl(wndInfo[0][0],200,10)
	time.sleep(0.5)
	DesktopCommon.SendScKeys("LCTRL", "a")
	time.sleep(0.5)
	DesktopCommon.CtrlV("s")
	time.sleep(0.5)
	cnt = GenRandom(4)
	for i in range(cnt):
	    DesktopCommon.SendScKeys("ENTER")
	    time.sleep(0.2)


#文件菜单新建标签
def DoNewTabByMenu(args):
    sehandle,chandle = GetSEHandleAndChildHandle("SE_TuotuoMenuBar")
    DesktopCommon.Sleep(0.3)
    ClickCtrl(chandle,60,10)
    time.sleep(0.3)
    ClickCtrl(chandle,60,30)
    time.sleep(2)

#新建浏览器窗口
def DoNewFrame(args):
    DesktopCommon.SendScKeys("LCTRL",'m')

#通过地址栏新建标签
def DoNewTabByAddrBar(args):
    #本动作需要设定浏览器在地址栏输入浏览的url时，总是新打开标签浏览
    DesktopCommon.SetXmlAttribute()
    url = GetUrl(args[0])
    DoNavigate(url)

#通过浏览搜狗论坛新建标签
def DoNewTabByBBS(args):
    DesktopCommon.SendScKeys("LALT",'h')
    DesktopCommon.Sleep(1)
    DesktopCommon.SendScKeys("d")


def GetAxControInfo():
    rectTabCtrl = DesktopCommon.GetWndPosEx("SE_TuotuoTabCtrl")
    rectStatusbar = DesktopCommon.GetWndPosEx("SE_TuotuoStatusbar")
    rectAll = DesktopCommon.GetWndPosEx("SE_SogouExplorerFrame")
    result = []
    result.append(rectAll[0],rectTabCtrl[1]+rectTabCtrl[3],rectAll[2],rectAll[3]-rectStatusbar[3]-rectTabCtrl[1]-rectTabCtrl[3])


def DoCloseTabEx(args):
    #保持几个标签.必须小于10
    if args!=None and len(args)>0:
	seTabRemain = args[0]
    else:
	seTabRemain = 1
    tabCount = SeSmoke.GetSETabCount()
    if tabCount>seTabRemain:
	time.sleep(1)
	DesktopCommon.SendScKeys("LCTRL",'w')


def ClickAccCore(groupx,itemx):
    wndInfo = DesktopCommon.GetWndHandles("SE_TuotuoStatusBarProgressCtrl")
    DesktopCommon.ClickOnHandle(wndInfo[0][0])
    DesktopCommon.Sleep(0.5)
    handle = win32gui.FindWindow("SE_TuoLiteTooltip",None)
    DesktopCommon.Sleep(0.5)
    pos = DesktopCommon.GetWndPos(handle)
    x = pos[0]
    y = pos[1]+185
    DesktopCommon.Sleep(0.5)
    DesktopCommon.MouseClick(x+groupx,y)
    DesktopCommon.Sleep(0.5)
    DesktopCommon.MouseClick(x+itemx,y+65)
    DesktopCommon.Sleep(0.5)
    DesktopCommon.MouseClick(x-10,y+65)

def GetSEInstallDir():
    return DesktopCommon.GetRegValue(r"HKEY_LOCAL_MACHINE\SOFTWARE\SogouExplorer","")

##@函数目的: 获取卸载程序的路径
##@参数说明：
##@返回值：
##@函数逻辑：
def GetSEUnInstallPath():
    seVersion = DesktopCommon.GetSEVersion()
    seDir = GetSEInstallDir()
    if seVersion.startswith("3.2") or seVersion.startswith("3.1") or seVersion.startswith("2."):
	return os.path.join(seDir, "Uninstall.exe")
    else:
	for root, dirs, files in os.walk(seDir):
	    for filename in files:
		if filename == "UninsSE.exe":
		    return os.path.join(root, filename)

# 打开修复工具
def DoOpenRepairTool(args):
    sePath = GetSEUnInstallPath()
    DesktopCommon.StartProcess(sePath)

    # 暂时不考虑3.2之前的版本
    mainHandle = DesktopCommon.GetWindowHandle("#32770", "搜狗高速浏览器 卸载程序")
    DesktopCommon.SetWindowTopMost(mainHandle)
    DesktopCommon.WaitWindowChildVisiable(mainHandle, "修复浏览器", 5)
    DesktopCommon.ClickCtrlEx(mainHandle,"Button", "修复浏览器")
    DesktopCommon.ClickCtrlEx(mainHandle,"Button", "继续")

    # 点击自动修复
##    mainHandle = DesktopCommon.GetHandle(None, "搜狗浏览器修复工具")
##    rect = win32gui.GetWindowRect(mainHandle)
##    DesktopCommon.MouseClick(rect[0] + 236, rect[1] + 110)
##    DesktopCommon.Sleep(2)

    win32gui.SendMessage(mainHandle, win32con.WM_CLOSE, 0, 0)

# 开启全网加速
def DoOpenWebAcc(args):
    sePath = GetSEUnInstallPath()
    DesktopCommon.StartProcess(sePath)

    # 暂时不考虑3.2之前的版本
    mainHandle = DesktopCommon.GetWindowHandle("#32770", "搜狗高速浏览器 卸载程序")
    DesktopCommon.SetWindowTopMost(mainHandle)

    DesktopCommon.WaitWindowChildVisiable(mainHandle, "恢复IE为默认浏览器", 5)
    resultList = []
    DesktopCommon.EnumAllChildWindows(mainHandle, resultList, 3)
    tempHandle = 0
    for window in resultList:
	print window[2]
	if window[2] == "恢复IE为默认浏览器":
	    tempHandle = window[0]
	    break
    rect = win32gui.GetWindowRect(tempHandle)
    time.sleep(0.5)
    DesktopCommon.MouseClick(rect[2] - 29, rect[1] + 32)
    time.sleep(0.5)
    win32gui.SendMessage(mainHandle, win32con.WM_CLOSE, 0, 0)


##@函数目的: 开启网速保护
##@参数说明：
##@返回值：
##@函数逻辑：
def DoTurnOnNetProtect(args):
    ClickAccCore(300,80)

##@函数目的:  关闭网速保护
##@参数说明：
##@返回值：
##@函数逻辑：
def DoTurnOffNetProtect(args):
    ClickAccCore(300,200)

##@函数目的: 点击打开预获取
##@参数说明：
##@返回值：
##@函数逻辑：
def DoClickPreGet(args):
    ClickAccCore(180,210)

##@函数目的: 点击打开预连接
##@参数说明：
##@返回值：
##@函数逻辑：
def DoClickPreConnect(args):
    ClickAccCore(180,50)


##@函数目的: 开启全网加速 forSE3.x Version
##@参数说明：
##@返回值：
##@函数逻辑：
def DoTurnOnAcc(args):
    ClickAccCore(240,60)

##@函数目的: 关闭全网加速 forSE3.x Version
##@参数说明：
##@返回值：
##@函数逻辑：
def DoTurnOffAcc(args):
    ClickAccCore(240,200)

def GetTimeStr():
    import time
    timeStr = str(time.localtime())
    timeStr = timeStr.replace("(","_")
    timeStr = timeStr.replace(",","_")
    timeStr = timeStr.replace(")","")
    timeStr = timeStr.replace(" ","")
    return timeStr

def ZipResourceFile(logDir):
    global g_resource_detail,g_dbFlag
    files = os.listdir(logDir)
    import zipfile
    zFile = DesktopCommon.GetFrameworkPath()+"\\temp\\stab_"+GetTimeStr() + ".zip"
    #zFile = r"c:\stab_"+GetTimeStr() + ".zip"
    z = zipfile.ZipFile(zFile,"w",zipfile.ZIP_DEFLATED)
    for f in files:
	if f.find(".txt")!=-1:
	    z.write(os.path.join(logDir,f),f)
    z.close()
    if len(z.filelist) == 0:
	return
    import time
    time.sleep(2)
    f = open(zFile,"rb")
    g_resource_detail = f.read()

    f.close()
    g_dbFlag = 1
    import base64
    g_resource_detail = base64.b64encode(g_resource_detail)

    return zFile

def GetIP(brief=False):
    from socket import socket, SOCK_DGRAM, AF_INET
    result = ""
    try:
	s =  socket(AF_INET, SOCK_DGRAM)
	s.connect(('www.sogou.com', 0))
	result = s.getsockname()[0]
	s.close()
	if not brief:
	    result += " "+os.environ["COMPUTERNAME"]
    except:
	result = os.environ["COMPUTERNAME"]
    return result

g_start_time = "2011-1-1"
g_end_time = "2011-1-1"
g_logDir = ""
g_dbFlag = 0

def GetStanderTime():
    import time
    t = time.localtime()
    timeStr = str(t[0]) + "-" + str(t[1]) + "-" + str(t[2]) + " " + str(t[3]) + ":" + str(t[4]) + ":" + str(t[5])
    return timeStr

def GetCurrentCaseId():
    from tempfile import gettempdir
    f = open(gettempdir()+"\\atf_current_exec_caseid.txt")
    caseid = f.readline().strip()
    f.close()
    return caseid

def InsertLogToDB():
    import base64,_winreg
    global g_start_time,g_end_time,g_resource_detail,g_dbFlag
    g_reserved1 = ""
    g_reserved2 = ""
    g_reserved3 = ""
    g_reserved4 = ""
    g_reserved5 = ""
    g_isDeleted = 0
    g_dbFlag = 1
    g_machineName = GetIP(True)

    tempPath = os.environ["temp"]
    allCaseFile = tempPath + "\\atf_current_exec_caseids.txt"
    currentCaseFile = tempPath + "\\atf_current_exec_caseid.txt"
    f = open(allCaseFile,"r")
    line = f.readline()
    firstCase = line.strip()
    f.flush()
    f.close()
    f = open(currentCaseFile,"r")
    line = f.readline()
    currentCase = line.strip()
    f.flush()
    f.close()
    execidFile = tempPath + "\\atf_perf_test_id.txt"
    if currentCase == firstCase:
	g_execid = str(time.time()).split(".")[0]
	f = open(execidFile,"w")
	f.write(str(g_execid) + os.linesep)
	f.flush()
	f.close()
    else:
	f = open(execidFile,"r")
	line = f.readline()
	g_execid = line.strip()
	f.flush()
	f.close()

    global g_coreType
    if g_logDir == "" or not os.path.exists(g_logDir):
	#资源目录不存在，直接退出
	return
    g_execid = str(time.time()).split(".")[0]
    caseName = str(GetCurrentCaseId())
    g_caseID = caseName.strip("#").split('-')[0]
    if caseName.find("-") != -1:
	import base64
	g_caseName = base64.b64encode(caseName.strip("#").split('-')[1])
    else:
	g_caseName = ""
    g_browserType = "SogouExplorer"
    #g_coreType = "auto"
    key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE,r"Software\SogouExplorer" ,0,_winreg.KEY_ALL_ACCESS)
    g_version,type = _winreg.QueryValueEx(key,"Version")
    g_logType = 0   #资源占用
    g_logContent = ""
    g_logDetail = ""
    g_pageLoadTimeout = 0

    ZipResourceFile(g_logDir)

    if g_dbFlag == 0:
	return
    import MySQLdb
    conn = MySQLdb.connect(host="database.desktopqa.com",user="root",passwd="linfei")
    try:
	conn.select_db("pageloadtest")
	sqlcmd = "insert into sestability(machinename,execid,caseid,case_name,browser_name,core_type,version,log_type,start_time,end_time,log_content,log_detail,timeout,reserved1,reserved2,reserved3,reserved4,isdeleted,resource_detail,reserved5) "
	sqlcmd = sqlcmd + " values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%d','%s','%s','%s','%s','%d','%s','%s')" % (g_machineName,g_execid,g_caseID,g_caseName,g_browserType,g_coreType,g_version.encode("gbk"),str(g_logType),g_start_time,g_end_time,base64.b64encode(g_logContent),base64.b64encode(g_logDetail),g_pageLoadTimeout,g_reserved1,g_reserved2,g_reserved3,g_reserved4,g_isDeleted,g_resource_detail,g_reserved5)
	cursor = conn.cursor()
	n = cursor.execute(sqlcmd)
	conn.commit()
    except:
	import traceback
	exception_info = sys.exc_info()
	tb_list = traceback.format_exception(exception_info[0], exception_info[1], exception_info[2])
	tbLog	= ""
	ff = open("c:/test.txt",'w')
	for tbf in tb_list:
	    tbLog += tbf
	ff.write(tbLog)
	ff.flush()

    conn.close()

##g_logDir = r"C:\se\NewCloseTabLog\新建关闭__2011_8_25_21_48_11_3_237_0"
##InsertLogToDB()


def SetBrowserCore(core):
    global g_coreType
    g_coreType = str(core)
    DesktopCommon.SetBrowserCore(core)

def StartMonitor(logdir,title,timeout=2000,conbineFlag=0):
    global g_logDir
    StopMonitor()
    if not os.path.exists(logdir):
	os.makedirs(logdir)
    timeStr = GetTimeStr()
    try:
	logpath = os.path.join(logdir.encode("gbk"),title+"_"+timeStr)
    except:
	logpath = os.path.join(logdir,title+"_"+timeStr)
    os.makedirs(logpath)
    if type(logpath)== unicode:
	logpath = logpath.encode("gbk")

    fmpath = DesktopCommon.GetFrameworkPath()
    if type(fmpath) == unicode:
	fmpath = fmpath.encode("gbk")
    cmd = "\""+fmpath+"\\util\\Perfmonitor\\PerformanceMonitor.exe\" SogouMobileTool"  + " 1000 "+str(conbineFlag)+" \"" + logpath + "/\" \"" + logpath +"\""
    DesktopCommon.OpenProcess(cmd)
    #cmd = "\""+fmpath+"\\util\\Crashdumpmonitor.exe\" \""+ logpath + "\" " + str(timeout)
    #DesktopCommon.OpenProcess(cmd)
    #os.system(cmd)
    g_logDir = logpath

def StartMonitorHelper(logdir,title,timeout=2000,conbineFlag=0):
    global g_logDir
    StopMonitor()
    if not os.path.exists(logdir):
	os.makedirs(logdir)
    timeStr = GetTimeStr()
    try:
	logpath = os.path.join(logdir.encode("gbk"),title+"_"+timeStr)
    except:
	logpath = os.path.join(logdir,title+"_"+timeStr)
    os.makedirs(logpath)
    if type(logpath)== unicode:
	logpath = logpath.encode("gbk")

    fmpath = DesktopCommon.GetFrameworkPath()
    if type(fmpath) == unicode:
	fmpath = fmpath.encode("gbk")
    cmd = "\""+fmpath+"\\util\\Perfmonitor\\PerformanceMonitor.exe\" SogouMobileToolHelper"  + " 1000 "+str(conbineFlag)+" \"" + logpath + "/\" \"" + logpath +"\""
    DesktopCommon.OpenProcess(cmd)
    #cmd = "\""+fmpath+"\\util\\Crashdumpmonitor.exe\" \""+ logpath + "\" " + str(timeout)
    #DesktopCommon.OpenProcess(cmd)
    #os.system(cmd)
    g_logDir = logpath

def StopMonitor():
    try:
	WM_STOP = win32con.WM_USER + 0x1002;
	perfHandle = win32gui.FindWindow(None, "性能检测工具")

	if perfHandle != 0:
	    win32api.PostMessage(perfHandle, WM_STOP, 0, 0)
	    win32api.PostMessage(perfHandle, win32con.WM_CLOSE, 0, 0)
	#DesktopCommon.StopProcess("CrashDumpMonitor")
	DesktopCommon.StopProcess("PerformanceMonitor")
    except:
	pass


#通过鼠标手势创建标签
def DoNewTabByMG(args):
    rect = DesktopCommon.GetWndPosEx("SE_AxControl")
    if rect!=-1:
	x = rect[0]
	y = rect[1]
	if rect[2]<10 or rect[3]<10:
	    #窗口太小就不做手势了
	    return
	dist = rect[2] / 10
	DesktopCommon.MouseGesture(x+dist-1,y+5,x+1,y+5,x+dist-1,y+5)
    time.sleep(1)

def GetSEHandleAndChildHandle(childClassName,seClassName="SE_SogouExplorerFrame",forgroundFlag=True):
    handles = DesktopCommon.GetWndHandles(seClassName)
    if handles!=None and len(handles)>0:
	rndidx = GenRandom(len(handles)-1)

    sehandle = handles[rndidx][0]
    childHandle = DesktopCommon.GetChildHandle(sehandle,childClassName)
    if forgroundFlag:
	SetForeground(sehandle)
    return sehandle,childHandle

def ClickCtrl(handle,x,y,clicktype="LEFT"):
    if IsVisible(handle):
	rect = DesktopCommon.GetWndPosByHandle(handle)
	if rect!=-1:
	    DesktopCommon.MouseClick(rect[0]+x,rect[1]+y,clicktype)

def ClickCtrlByClassName(classname,windowname,x,y,clicktype="LEFT"):
    handles = DesktopCommon.GetWndHandles(classname,windowname)
    if handles!=None and len(handles)>0:
	ClickCtrl(handles[0][0],x,y,clicktype)

#通过点击主页新建标签
def DoNewTabByHome(args):
    #DesktopCommon.ClickOnCtrl("SE_ToolBar","LEFT","165*15")
    sehandle,chandle = GetSEHandleAndChildHandle("SE_TuotuoToolbar")
    DesktopCommon.Sleep(0.4)
    ClickCtrl(chandle,165,15)
    time.sleep(3)

def IsVisible(handle):
    try:
	result = win32gui.IsWindowVisible(handle)
    except:
	result = False
    return result

def DoCloseSEForce(args):
    #关闭所有的SE
    handles= DesktopCommon.GetWndHandles("SE_SogouExplorerFrame")
    if handles != None and len(handles)>0:
	for h in handles:
	    win32api.PostMessage(h[0],win32con.WM_CLOSE,0,0)

def DoCloseSE(args):
    handles= DesktopCommon.GetWndHandles("SE_SogouExplorerFrame")
    if handles != None and len(handles)>0:
	sehandle = handles[0][0]
	rect = DesktopCommon.GetWndPosByHandle(sehandle)
	SetForeground(sehandle)
	ClickCtrl(sehandle,rect[2]-5,-5)
	rnd = GenRandom(5)
	if rnd<1:
	    time.sleep(0.5)
	    DesktopCommon.StopProcess("SogouExplorer")

def DoStartSE(args):
    PreStartSE(args)


def DoNewTabByOften(args):
    hisUrlDb = DesktopCommon.GetEnv("APPDATA")+"\\SogouExplorer\\historyurl.db"
    DesktopCommon.Sleep(2)
    #DesktopCommon.ExecSql(hisUrlDb,"delete from often")
    #insertSts = "insert into often values(\"http://www.baidu.com\",\"baidu\",120)"
    #DesktopCommon.ExecSql(hisUrlDb,insertSts)
    #DesktopCommon.ClickOnCtrl("SE_RecentBar","LEFT","81*10")
    sehandle,rhandle = GetSEHandleAndChildHandle("SE_TuotuoRecentBar")
    DesktopCommon.Sleep(0.4)
    if rhandle!=0 and IsVisible(rhandle):
	ClickCtrl(rhandle,81,10)

#通过链接新建标签
def DoNewTabByLink(args):
    #存在页面	正在加载无法点击链接的问题，不过问题不是太大
    #DesktopCommon.ClickOnCtrl("SE_AxControl","LEFT","1004*225")
    #sehandle,chandle = GetSEHandleAndChildHandle("SE_AxControl")
    sehandles = DesktopCommon.GetWndHandles("SE_SogouExplorerFrame")
    SetForeground(sehandles[0][0])
    DesktopCommon.CreateTabNav("http://123.sogou.com")
    DesktopCommon.Sleep(3)
    MaximizeWnd(sehandles[0][0])
    axhandles = DesktopCommon.GetWndHandles("SE_AxControl")
    DesktopCommon.Sleep(0.2)
    ClickCtrl(axhandles[0][0],1004,225)

#通过命令行浏览url
def DoNewTabByCmd(args):
    global g_processSecurity
    url = GetUrl(args[0])
    DesktopCommon.OpenProcess(DesktopCommon.GetSEDir()+"\\SogouExplorer.exe", url, g_processSecurity)

def NewTabByCmd(url):
    global g_processSecurity
    DesktopCommon.OpenProcess(DesktopCommon.GetSEDir()+"\\SogouExplorer.exe", url, g_processSecurity)

def DoSleep(args):
    time.sleep(args[0])

#通过搜索栏搜索创建新标签
def DoNewTabBySearchBar(args):
    import string
    values = "问中国多一些中文为什么呢1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ`~!@#$%^&*()_+=-|\\}]{[\"':;?/><.,"
    word = string.join(random.sample(values, 5)).replace(" ", "")
    #可能用户会直接使用本动作
    if len(args) >= 1:
	word = args[0]
    if DesktopCommon.CtrlExistByWin32("SE_TuotuoSearchBar"):
	#只有存在搜索栏控件时才进行动作
	rect = DesktopCommon.GetWndPosEx("SE_TuotuoSearchBar")
	try:
	    DesktopCommon.MouseDbClick(rect[0]+50,rect[1]+10)
	    DesktopCommon.SendScKeys("LCTRL", "a")
	    DesktopCommon.CtrlV(word)
	    DesktopCommon.MouseClick(rect[0]+rect[2]-10,rect[1]+5)
	except:
	    None



#通过侧边栏收藏夹打开链接
def DoNewTabByFavSidebar(args):
    if len(args)>0:
	className=args[0]
    else:
	className = "SE_TuotuoSidebar"

    DoOpenSideBar(className)
    #mode = GenRandom(1)

    mode = 1
    #获取侧边栏位置
    rect = DesktopCommon.GetWndPosEx(className)
    if rect == -1 or rect[0] < -100 or rect[1]<-100:
	#不合理情况
	rect = (0,175)
    for i in range(3):
	if not DesktopCommon.CtrlExistByWin32("SE_FavorContentToolbar"):
	    DesktopCommon.MouseClick(rect[0]+10,rect[1]+10)
	else:
	    time.sleep(0.3)
    if mode == 0:
	#点击某个链接
	pass
    else:
	#打开所有链接
	DesktopCommon.MouseClick(rect[0]+60,rect[1]+100,"RIGHT")
	DesktopCommon.Sleep(0.3)
	DesktopCommon.SendScKeys("o")


def InvokeSetting():
    for i in range(3):
	DesktopCommon.SendScKeys("LCTRL","LSHIFT","s")
	time.sleep(0.1)
	if DesktopCommon.CtrlExistByWin32("搜狗高速浏览器 选项"):
	    break
	else:
	    time.sleep(0.1)

def CloseSetting():
    for i in range(3):
	DesktopCommon.SendScKeys("ENTER")
	time.sleep(0.1)
	if not DesktopCommon.CtrlExistByWin32("搜狗高速浏览器 选项"):
	    break
	else:
	    rect = DesktopCommon.GetWndPosEx("搜狗高速浏览器 选项")
	    if rect!=-1 and len(rect)>0:
		DesktopCommon.MouseClick(rect[0] + 60,rect[1] + 5)
		time.sleep(0.1)

#进入多窗口模式
def DoEnterWndMode(args):
    if args!=None and len(args)>0:
	tabCnt = int(args[0])
    else:
	tabCnt = 30
    realCnt = SeSmoke.GetSETabCount()
    if tabCnt>realCnt:
	for i in range(tabCnt-realCnt):
	    DoNewTabByKey(args)
	    time.sleep(0.1)
    DoSetTabModeToWnd(args)

#多窗口模式下关闭一个或者多个框架（也就是一个主窗口)
def DoCloseTabBySE(args):
    handles = DesktopCommon.GetWndHandles("SE_SogouExplorerFrame",None)
    if handles!=None and len(handles)>0:
	secnt = len(handles)
	cntToClose = GenRandom(secnt-1)
	#随机关闭框架
	for i in range(cntToClose):
	    win32gui.PostMessage(handles[i],win32con.WM_CLOSE,0,0)
	    time.sleep(0.1)

#进入多标签模式
def DoEnterTabMode(args):
    handles = DesktopCommon.GetWndHandles("SE_SogouExplorerFrame",None)
    if handles != None and len(handles) > 0:
	#留一个做种...
	for i in range(len(handles) - 1):
	    win32gui.PostMessage(handles[i][0], win32con.WM_CLOSE,0,0)
	    time.sleep(0.1)
    DoSetTabModeToTab(args)



#设置成多窗口模式
def DoSetTabModeToWnd(args):
    InvokeSetting()
    rect = DesktopCommon.GetWndPosEx(None,"多窗口模式")
    if rect != -1 and len(rect) > 0:
	DesktopCommon.MouseClick(rect[0] + 10,rect[1] + 5)
    CloseSetting()
    time.sleep(2)

#设置成多标签模式
def DoSetTabModeToTab(args):
    InvokeSetting()
    rect = DesktopCommon.GetWndPosEx(None, "多标签模式")
    if rect != -1 and len(rect) > 0:
	DesktopCommon.MouseClick(rect[0] + 10,rect[1] + 5)
    CloseSetting()
    time.sleep(2)

#通过侧边栏收藏夹打开更新快递链接以创建标签
def DoNewTabByDynSidebar(args):
    if len(args)>0:
	className=args[0]
    else:
	className = "SE_TuotuoSidebar"

    DoOpenSideBar(className)

    #获取侧边栏位置
    rect = DesktopCommon.GetWndPosEx(className)
    if rect == -1 or rect[0] < -100 or rect[1]<-100:
	#不合理情况
	rect = (0,175)
    #打开所有链接
    #如果不是更新快递页面，则先点击更新快递页面：
    if not DesktopCommon.CtrlExistByWin32("SE_DynmarkContentToolbar"):
	DesktopCommon.MouseClick(rect[0]+15,rect[1]+78)
    DesktopCommon.Sleep(0.3)
    idx = GenRandom(20)
    DesktopCommon.MouseClick(rect[0]+60,rect[1]+90+idx*20)


#点击切核按钮
def DoSwitchCore(args):
    SeSmoke.ClickSwitchCore()


#点击小号窗口
def DoNewTabByMini(args):
    sehandle,chandle = GetSEHandleAndChildHandle("SE_TuotuoToolbar")
    ClickCtrl(chandle,60,10)
    DesktopCommon.Sleep(0.5)
    ClickCtrl(chandle,60,70)
    DesktopCommon.Sleep(0.5)
    ClickCtrl(chandle,30,130)

def DragTo(sx,sy,dx,dy,interval=0.1):
    detx = (dx-sx)/10
    dety = (dy-sy)/10
    if detx ==0: detx = 1
    if dety == 0: dety = 1
    for i in range(10):
	DesktopCommon.MouseTo(sx+i*detx,sy+i*dety)
	time.sleep(interval)
    DesktopCommon.MouseTo(dx,dy)

def DragSearch(sx,sy,dx,dy):
    DesktopCommon.MouseTo(sx,sy)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    detx = 1.0 * (dx - sx) / 20
    dety = 1.0 * (dy - sy) / 20
    try:
	for i in range(20):
	    win32api.SetCursorPos((int(sx + i * detx),int(sy + i * dety)))
	    time.sleep(0.03)
    except:
	None
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    DesktopCommon.MouseTo(sx+10,sy)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.1)
    DesktopCommon.MouseTo(sx+10,sy-25)
    time.sleep(0.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

def DoNewTabByDrag(args):
    if args!=None and len(args)>0:
	url = args[0]
    else:
	url = "http://123.sogou.com/"
    DesktopCommon.NavigateSE(url)
    #拖拽
    SeSmoke.MaximizeSE()
    time.sleep(1.5)
    cnt = GenRandom(10)
    for i in range(cnt):
	DragSearch(484,365,541,365)
	time.sleep(0.1)
    time.sleep(2)


def GetSECount():
    try:
	handles = DesktopCommon.GetWndHandles("SE_SogouExplorerFrame",None)
	if handles!=None:
	    return len(handles)
	else:
	    return -1
    except:
	return -1


def MaximizeWnd(handle):
    win32gui.ShowWindow(handle,win32con.SW_MAXIMIZE)

# 设置日志目录
def SetLogDir(path = ""):
    global g_logPath
    if path == "":
	path = os.path.join(DesktopCommon.GetFrameworkPath(), r"log\stab\testNavigate")
    if not os.path.exists(path):
	os.makedirs(path)
    dateStr = time.strftime("%Y_%m_%d_%H_%M_%S")
    g_logPath = os.path.join(path, "navigate_" + dateStr + ".log")

def StartNavigate(url = "", timeout = 36000, delay = 2, chagedTimeout = 15):
    global g_logPath
    startTime = time.clock()
    durationStartTime = time.clock()
    lastSETitle = ""
    lastUrl = ""
    tridentCount = 0
    sameCount = 0
    GetOriWnds()
    while time.clock() - startTime < timeout:
	try:
##	    import shutil
##	    # 临时添加
##	    setaskPath = os.path.join(os.environ["temp"], "setask.zip")
##	    sePath = os.path.join(os.environ["temp"], "se.zip")
##	    explorerPath = os.path.join(os.environ["temp"], "SogouExplorer.zip")
##	    if os.path.exists(setaskPath):
##		despath = os.path.join(r"D:\temp\crash", "setask_" + time.strftime("%Y_%m_%d_%H_%M_%S") + ".zip")
##		shutil.copyfile(setaskPath, despath)
##		os.remove(setaskPath)
##	    if os.path.exists(sePath):
##		despath = os.path.join(r"D:\temp\crash", "se_" + time.strftime("%Y_%m_%d_%H_%M_%S") + ".zip")
##		shutil.copyfile(sePath, despath)
##		os.remove(sePath)
##	    if os.path.exists(explorerPath):
##		despath = os.path.join(r"D:\temp\crash", "sogouexplorer_" + time.strftime("%Y_%m_%d_%H_%M_%S") + ".zip")
##		shutil.copyfile(explorerPath, despath)
##		os.remove(explorerPath)
	    # 判断浏览器是否存在
	    seHandle = DesktopCommon.FindWindow("SE_SogouExplorerFrame")
	    if not DesktopCommon.IsProcessExist("SogouExplorer") or seHandle == 0:
		DesktopCommon.StopSE()
		time.sleep(2)
		if lastUrl != "":
		    DesktopCommon.WriteLog(g_logPath, "SogouExplorer Error:" + lastUrl)
		DesktopCommon.StartSE(url)

	    # 将浏览器设置到前端
	    SetForeground(seHandle)

	    # 获取浏览器url以及当前的标题
	    seURL = ""
	    seURL = DesktopCommon.GetTextFromAddressBar("SEAddr")

	    seTitle = ""
	    seTitle = DesktopCommon.GetSETitle()

	    # 记录日志
	    errorHandle = DesktopCommon.FindWindow("#32770", "搜狗高速浏览器")
	    if errorHandle != 0:
		DesktopCommon.WriteLog(g_logPath, "SETask Error:" + seURL)
	    else:
		DesktopCommon.WriteLog(g_logPath, "Info:" + seURL)

	    # 点击下载
	    handle = DesktopCommon.FindWindow("#32770", "搜狗高速下载")
	    SetForeground(handle)
	    if handle != 0:
		DesktopCommon.ClickCtrlEx(handle, "Button", "下载")

	    # Outlook需要确认
	    handle = DesktopCommon.FindWindow("#32770", "Microsoft Office Outlook")
	    SetForeground(handle)
	    if handle != 0:
		DesktopCommon.ClickCtrlEx(handle, "Button", "否(&N)")

	    # 关闭对话框
	    PreCloseGarbageWnd(1)

	    # 网页无法访问，重新浏览
	    if seTitle.find("该网页无法访问") != -1:
		DesktopCommon.NavigateSEWithWin32(url)

	    # 当一个页面的浏览时间超过设定的值时，重新浏览
	    if lastSETitle != seTitle:
		sameCount = 0
		durationStartTime = time.clock()
	    duration = time.clock() - durationStartTime
	    if lastSETitle == seTitle and duration > chagedTimeout:
		sameCount += 1
		DesktopCommon.NavigateSEWithWin32(url)
		durationStartTime = time.clock()

	    time.sleep(delay)
	    lastUrl = seURL
	    lastSETitle = seTitle

	    if seURL.lower().find("trident") != -1:
		tridentCount += 1
	    if tridentCount > 3:
		DesktopCommon.ClickOnCtrl("SE_TuotuoAddressBar", 48, 13, "rightbottom")
		tridentCount = 0

	    # 浏览器浏览功能出现问题、或访问不了服务器
	    if sameCount > 3:
		DesktopCommon.StopSE()
	except:
	    time.sleep(delay)


def SetWndPos(handle,x,y,width=0,height=0):
    win32gui.SetWindowPos(handle, win32con.HWND_TOPMOST, 0,0,width,height, win32con.SWP_NOMOVE | win32con.SWP_NOACTIVATE| win32con.SWP_NOOWNERZORDER|win32con.SWP_SHOWWINDOW)

def DoDragBetweenTab(args):
    DoSetTabModeToTab(args)
    for i in range(10):
	NavigateByCmd()
    wndInfo = DesktopCommon.GetWndPosEx("SE_TuotuoTabCtrl",None)
    for i in range(5):
	rndStart = GenRandom(wndInfo[2],40)
	rndEnd = GenRandom(wndInfo[2],40)
	DesktopCommon.MouseTo(wndInfo[0]+rndStart,wndInfo[1]+10)
	time.sleep(1)
	DesktopCommon.MouseDown()
	DragTo(rndStart,wndInfo[1]+10, rndEnd,wndInfo[1]+10,0.05)
	time.sleep(0.1)
	DesktopCommon.MouseUp()

def DoDragBetweenSE(args):
    DoSetTabModeToTab(args)
    handles = DesktopCommon.GetWndHandles("SE_SogouExplorerFrame",None)
    if handles!=None and len(handles)<2:
	DoNewFrame(args)
	time.sleep(0.3)
	for i in range(8):
	    #第二个标签上多加几个标签
	    NavigateByCmd()
	#DoNawFrame(args)
    #对这两个搜狗浏览器设置位置。各占一半空间
    time.sleep(0.2)
    if args!=None and len(args)>0:
	timeout = args[0]
    else:
	timeout = 30

    for i in range(10):
	handles = DesktopCommon.GetWndHandles("SE_SogouExplorerFrame",None)
	if handles!=None and len(handles)>=2:
	    #保证两个或者以上的搜狗浏览器
	    break
	else:
	    time.sleep(0.2)
	    if i == 9:
		#没有两个搜狗浏览器，因此退出
		return
    beginTime = win32api.GetTickCount()
    MyLog("1"+os.linesep)
    while win32api.GetTickCount()-beginTime<timeout*1000:
	handles = DesktopCommon.GetWndHandles("SE_SogouExplorerFrame",None)
	if len(handles)<2:
	    break

	rect1 = DesktopCommon.GetWndPosByHandle(handles[0][0])
	rect2 = DesktopCommon.GetWndPosByHandle(handles[1][0])
	handle1 = handles[0][0]
	handle2 = handles[1][0]

	if rect1[0]>rect2[0]:
	    rect1,rect2 = rect2,rect1
	    handle1,handle2 = handle2,handle1
	tabHandle1 = DesktopCommon.GetChildHandle(handle1,"SE_TuotuoTabCtrl",None)
	tabHandle2 = DesktopCommon.GetChildHandle(handle2,"SE_TuotuoTabCtrl",None)
	rect1 = DesktopCommon.GetWndPosByHandle(tabHandle1)
	rect2 = DesktopCommon.GetWndPosByHandle(tabHandle2)
	time.sleep(2)

	try:
	    try:
		win32gui.SetForegroundWindow(handle1)
	    except:
		None
	    time.sleep(0.2)
	    try:
		win32gui.SetForegroundWindow(handle2)
	    except:
		None
	    import random
	    if rect2[0]<0:
		break

	    rndx = random.randint(rect2[0]+30,rect2[0]+rect2[2]-40)

	    DesktopCommon.MouseTo(rndx,rect2[1]+15)
	    time.sleep(1)
	    if rect1[0]<0:
		break
	    DesktopCommon.MouseDown()
	    try:
		#点击大的浏览器后，小的会被隐藏，所以要重新激活
		win32gui.SetForegroundWindow(handle1)
	    except:
		None
	    time.sleep(2)

	    dstx = random.randint(rect1[0]+30,rect1[0]+rect1[2]-40)
	    DragTo(rndx,rect2[1]+15, dstx,rect1[1]+15)
	    time.sleep(1)
	    DesktopCommon.MouseUp()
	    rect1 = DesktopCommon.GetWndPosByHandle(tabHandle1)
	    rect2 = DesktopCommon.GetWndPosByHandle(tabHandle2)
	    time.sleep(1)
	    if rect2[0]<0:
		break
	    if rect1[0]<0:
		break
	    DesktopCommon.MouseDown()
	    try:
		#点击大的浏览器后，小的会被隐藏，所以要重新激活
		win32gui.SetForegroundWindow(handle2)
	    except:
		None
	    time.sleep(2)

	    rndx = random.randint(rect2[0]+30,rect2[0]+rect2[2]-40)
	    DragTo(dstx,rect1[1]+15,rndx,rect2[1]+15)
	    time.sleep(1)
	    DesktopCommon.MouseUp()
	except:
	    import traceback
	    MyLog(traceback.format_exc())

	time.sleep(3)
    handles = DesktopCommon.GetWndHandles("SE_SogouExplorerFrame",None)
    if handles!=None and len(handles)>0:
	#留一个做种...
	for i in range(len(handles)-1):
	    win32gui.PostMessage(handles[i][0],win32con.WM_CLOSE,0,0)
	    time.sleep(0.1)
	MaximizeWnd(handles[-1][0])

def DoCloseTabByPassport(args):
    pass

#点击标签栏空白处（标签超过10个时是+号）
def DoNewTabByTabCtrl(args):
    if len(args)>0:
	classname = args[0]
    else:
	classname = "SE_TuotuoTabCtrl"
    #rect的结果是x、y坐标、宽度、高度
    rect = DesktopCommon.GetWndPosEx(classname)
    posx = rect[0]+rect[2] - 10
    posy = rect[1]+rect[3]/2
    DesktopCommon.MouseDbClick(posx,posy)
    import time
    time.sleep(1)

#点击标签栏空白处（标签超过10个时是+号）
def DoCloseTabByTabCtrl(args):
    import time
    if len(args)>0:
	classname = args[0]
    else:
	classname = "SE_TuotuoTabCtrl"
    #rect的结果是x、y坐标、宽度、高度
    rect = DesktopCommon.GetWndPosEx(classname)
    if rect==-1 or rect[0]<-1000:
	return
    x = GenRandom(rect[0]+rect[2],rect[0]+40)  #
    y = rect[1]+rect[3]/2
    closetype = GenRandom(6)
    tabCount = SeSmoke.GetSETabCount()
    if tabCount<10:
	for i in range(10-tabCount):
	    DoNewTabByKey([])
    if closetype == 0:
	DesktopCommon.MouseDbClick(x,y)
    elif closetype == 1:
	DesktopCommon.MouseClick(x,y,"RIGHT")
	time.sleep(0.2)
	DesktopCommon.SendScKeys("c")
    elif closetype == 2:
	#关闭左边
	DesktopCommon.MouseClick(x,y,"RIGHT")
	time.sleep(0.2)
	DesktopCommon.SendScKeys("z")
    elif closetype == 3:
	#关闭右边
	DesktopCommon.MouseClick(x,y,"RIGHT")
	time.sleep(0.2)
	DesktopCommon.SendScKeys("x")
    elif closetype == 4:
	#关闭其他标签
	DesktopCommon.MouseClick(x,y,"RIGHT")
	time.sleep(0.2)
	DesktopCommon.SendScKeys("o")
    elif closetype == 5:
	#关闭其他标签
	DesktopCommon.MouseClick(x,y,"RIGHT")
	time.sleep(0.2)
	DesktopCommon.SendScKeys("w")
    else:
	DesktopCommon.MouseClick(x,y,"RIGHT")
	time.sleep(0.2)
	DesktopCommon.SendScKeys("d")


#通过快捷键关闭浏览器
def DoCloseTabByKey(args):
    closetype = GenRandom(4)
    if closetype!=0:
	DesktopCommon.SendScKeys("LCTRL",'w')
    else:
	#20%的概率下关闭所有标签
	DesktopCommon.SendScKeys("LCTRL","LSHIFT",'w')

# 依次执行各鼠标手势
def DoMouseGesture(args):
    DoNavigate(args)
    time.sleep(2)
    flag = GenRandom(8)
    DesktopCommon.SendScKeys("ESC")
    # 滚屏到页尾
    if flag == 0:
	DesktopCommon.MouseGesture(500,300,500,350)
    # 滚屏到页首
    elif flag == 1:
	DesktopCommon.MouseGesture(500,350,500,300)
    # 前进
    elif flag == 2:
	DesktopCommon.MouseGesture(500,350,550,350)
    # 后退
    elif flag == 3:
	DesktopCommon.MouseGesture(500,350,450,350)
    # 打开前一个标签
    elif flag == 4:
	DesktopCommon.MouseGesture(500,350,500,300,450,300)
    # 打开后一个标签
    elif flag == 5:
	DesktopCommon.MouseGesture(450,350,450,300,500,300)
    # 刷新
    elif flag == 6:
	DesktopCommon.MouseGesture(500,300,500,350,500,300)
    # 新建页面
    elif flag == 7:
	DesktopCommon.MouseGesture(500,350,450,350,500,350)
    # 撤销关闭页面
    elif flag == 8:
	DesktopCommon.MouseGesture(500,350,550,350,500,350)

#鼠标手势关闭所有标签
def DoCloseAllTabsByMG(args):
    DesktopCommon.SendScKeys("ESC")
    DesktopCommon.MouseGesture(500,300,500,350,450,350)

#鼠标手势关闭浏览器
def DoCloseTabByMG(args):
    DesktopCommon.SendScKeys("ESC")
    DesktopCommon.MouseGesture(400,300,400,600,600,600)


def SetForeground(handle):#,classname = "SE_SogouExplorerFrame"):
    try:
	#handle = win32gui.FindWindow(classname)
	curForeHandle = win32gui.GetForegroundWindow()
	#if win32gui.IsIconic(handle) and handle!=curForeHandle:
	win32gui.SetForegroundWindow(handle)
	win32gui.SetActiveWindow(handle)
    except:
	pass


#全屏
def DoFullScreen(args):
    wndPosInfo = DesktopCommon.GetWndPosEx("SE_AxControl")
    if wndPosInfo!=-1 and wndPosInfo[1]>60:
	DesktopCommon.SendScKeys("F11")

def DoExitFullScreen(args):
    wndPosInfo = DesktopCommon.GetWndPosEx("SE_AxControl")
    if wndPosInfo!=-1 and wndPosInfo[1]<60:
	DesktopCommon.SendScKeys("F11")

# 使用F1弹出RepairTools对话框
def DoShowRepairToolsByF1(args):
    DesktopCommon.SendScKeys("F1")

# 收藏夹排序
def DoSortFavUrls(args):
    #菜单栏
    SeSmoke.ClickSEMenuBar(186, 8)
    time.sleep(1)
    DesktopCommon.SendScKeys("m")
    time.sleep(1)
    hwnd = win32gui.FindWindow(None,"整理收藏夹")
    if hwnd == 0:
	return
    rect = win32gui.GetWindowRect(hwnd)

    DesktopCommon.MouseClick(rect[0] + 150, rect[1] + 39)
    dx = 180
    dy = random.sample([65, 87, 106], 1)[0]
    time.sleep(0.5)
    DesktopCommon.MouseClick(rect[0] + dx, rect[1] + dy)
    time.sleep(3)

#通过鼠标手势创建标签
def DoCloseTabByMG(args):
    rect = DesktopCommon.GetWndPosEx("SE_AxControl")
    if rect!=-1:
	x = rect[0]
	y = rect[1]
	if rect[2]<50 or rect[3]<50:
	    #窗口太小就不做手势了
	    return
	DesktopCommon.MouseGesture(x+10,y+5,x+10,y+30,x+50,y+30)

def DoCloseTabByMenu(args):
    #DesktopCommon.ClickOnCtrl("SE_MenuBar","LEFT","60*10")
    SeSmoke.ClickSEMenuBar(70, 8)
    time.sleep(0.5)
    DesktopCommon.SendScKeys("c")

def DoCloseSEByMenu(args):
    SeSmoke.ClickSEMenuBar(70, 8)
    time.sleep(0.5)
    DesktopCommon.SendScKeys("x")

# 提取flash页面
def DoOpenFlashPlayer(args):
    url = "http://10.12.220.117/flash/flash_embedSWF_autoPlay.html"
    if len(args) > 0:
	url = args[0]
    DesktopCommon.CreateTabNav(url)
    time.sleep(5)
    handle = DesktopCommon.FindWindow("SE_AxControl")
    if handle != 0:
	ran = GenRandom(2)
	SeSmoke.ExtraVideo(ran)
	handle=SeSmoke.FindWindowBySubClass("SGDUI", 10)
	rect=DesktopCommon.GetWindowRect(handle)
	DesktopCommon.MouseClick(rect[2] - 118,rect[1] + 15)
	DesktopCommon.Sleep(1)
	DesktopCommon.MouseClick(rect[2] - 74,rect[1] + 15)
	DesktopCommon.Sleep(1)


def DoBossKey(args):
    #暂时只发送LCTRL+~吧
    if True:
	handle = win32gui.FindWindow("SE_SogouExplorerFrame",None)
	if handle!=0 and win32gui.IsWindowVisible(handle):
	    #界面已经存在，所以直接发送boss键进行隐藏
	    DesktopCommon.SendScKeys("LCTRL","`")
    else		:
	None
    time.sleep(3)
    #再次发送boss键进行恢复
    #DesktopCommon.SendScKeys("LCTRL","`")




g_urlFileCount = 0
#------------------------------在地址栏中输入url,并打开
def DoOpenUrlByAddressBar(args):
    global g_urlFileCount
    urlFile = args[0]
    url = ""
    if g_urlFileCount == 0:
	f = open(urlFile,"r")
	url = f.readline().strip()
	for line in f:
	    line = line.strip()
	    if len(line)>0:
		g_urlFileCount += 1
	f.close()

    if url == "":
	import random
	index = random.randint(0,g_urlFileCount-1)
	f = open(urlFile, "r")
	for x in xrange(index):
	    f.next()
	for line in f:
	    line = line.strip()
	    if len(line)>0:
		url = str(line)
		break
	f.close()

    DesktopCommon.Navigate(url)
    time.sleep(1)


#----------------------------------------------------------------------
def MyLog(value,newFlag=False):
    f= None
    dirName = os.path.dirname(os.getenv("WINDIR"))
    if newFlag:
	f = open(dirName +"a.txt","w")
    else:
	f = open(dirName+"a.txt","a")
    f.write(str(value) + os.linesep)
    f.close()


#----------------------------------------------------------------------点击地址栏的下拉列表
def DoClickDropDwonListOnAddressBar(args):
    #hwnd = win32gui.FindWindow("SE_TuotuoAddressBarComboBox",None)
    parentWindow = win32gui.FindWindow("SE_SogouExplorerFrame",None)
    hwnd = DesktopCommon.SearchSubWindowByClassName(parentWindow, "SE_TuotuoAddressBarComboBox")
    if hwnd == 0:
	return
    rect = win32gui.GetWindowRect(hwnd)

    if len(rect) != 4:             #如果rect数组的值不是4
	return
    x = rect[2] - 10
    y = (rect[1] + rect[3]) / 2

    DesktopCommon.MouseClick(x,y)
    time.sleep(1)
    #随机点击一个链接
    import random
    index = random.randint(1,8)
    height = 44
    yOffset = 44 / 2
    x = (rect[2] - rect[0]) / 2 + rect[0]
    yStart = rect[3]
    y = yStart + (index - 1) * height + yOffset

    DesktopCommon.MouseClick(x,y)
    time.sleep(1)

#----------------------------------------------------------------------在当前页面点击一个链接
def DoClickUrlOnCurPage(args):
    global g_tabCount
    count = args[0]
    timeout = args[1]
    pageHwnd = win32gui.FindWindow("SE_AxControl",None)
    if pageHwnd == 0:
	return
    browserRect = win32gui.GetWindowRect(pageHwnd)
    mouseWidth = 900 #鼠标点击区域宽度定义为900
    leftScreen = (browserRect[2] - mouseWidth)/2 + browserRect[0]
    TopScreen = browserRect[1] - 10
    wndTitle = DesktopCommon.GetWndTitle("SE_SogouExplorerFrame")
    for i in xrange(int(count)):
	p = RandomValueablePoint(leftScreen,TopScreen)
	if len(p) != 2:
	    break
	DesktopCommon.MouseClick(p[0],p[1])
	time.sleep(1)



#----------------------------------------------------------------------在页面上随机找到一个链接
def RandomValueablePoint(leftScreen,TopScreen):
    x = leftScreen + random.randint(0, 500)
    y = TopScreen + random.randint(0, 400)
    dx = 0
    dy = 0
    while dx < 100 and dy < 100:
	dx += 1
	dy += 1
	px = x + dx
	py = y + dy
	if x > 600:
	    px = x - dx
	if y > 450:
	    py = y - dy
	p = (px, py)
	win32api.SetCursorPos(p)
	time.sleep(0.001)
	if IsCursorLink():
	    return p
    return (400, 500)


    #----------------------------------------------------------------------在侧边栏的收藏夹，最近访问和历史数据上点击，打开url
def DoClickUrlOnSideBar(args):
    global g_tabCount
    count = args[0]
    timeout = args[1]
    time.sleep(1)
    seui = win32gui.FindWindow("SE_SogouExplorerFrame",None)

    #打开搜藏夹
    DesktopCommon.SendScKeys("LCTRL",'i')
    time.sleep(1)
    hwnd = DesktopCommon.SearchSubWindowByClassName(seui,"SE_TuotuoSidebar")
    if hwnd == 0:
	return
    rect = win32gui.GetWindowRect(hwnd)
    import random
    for i in xrange(int(count)):
	winText = tempText = win32gui.GetWindowText(seui)
	failCount = 0 #失败次数大于10次就返回
	while winText == tempText and failCount < 10:
	    index = random.randint(0,20)
	    x = rect[0] + 70
	    y = rect[1] + 165 + index * 20
	    DesktopCommon.MouseClick(x, y)
	    time.sleep(timeout)
	    tempText = win32gui.GetWindowText(seui)
	    failCount += 1
	if winText != tempText: #如果页面跳转，点击成功，tab总数加1
	    g_tabCount += 1

	#打开最常访问
	x = rect[0] + 10
	y = rect[1] + 35
	DesktopCommon.MouseClick(x, y)
	time.sleep(0.5)
	winText = tempText = win32gui.GetWindowText(seui)
	failCount = 0
	while winText == tempText and failCount < 10:
	    index = random.randint(0,20)
	    x = rect[0] + 70
	    y = rect[1] + 55 + index * 20
	    DesktopCommon.MouseClick(x, y)
	    time.sleep(timeout)
	    tempText = win32gui.GetWindowText(seui)
	    failCount += 1
	if winText != tempText: #如果页面跳转，点击成功，tab总数加1
	    g_tabCount += 1

	#打开历史记录
	DesktopCommon.SendScKeys("LCTRL",'h')
	time.sleep(1)
	#点击资源视图，不按照日期视图
	x = rect[0] + 200
	y = rect[1] + 40
	DesktopCommon.MouseClick(x, y)
	time.sleep(2)
	winText = tempText = win32gui.GetWindowText(seui)
	failCount = 0
	while winText == tempText and failCount < 10:
	    index = random.randint(0,20)
	    x = rect[0] + 70
	    y = rect[1] + 55 + index * 20
	    DesktopCommon.MouseClick(x, y)
	    time.sleep(1)
	    DesktopCommon.MouseClick(x, y+22) #展开站点，点击第一个
	    time.sleep(timeout)
	    tempText = win32gui.GetWindowText(seui)
	    failCount += 1
	if winText != tempText: #如果页面跳转，点击成功，tab总数加1
	    g_tabCount += 1


	#打开更新提醒
	x = rect[0] + 10
	y = rect[1] + 75
	DesktopCommon.MouseClick(x, y)
	time.sleep(0.5)
	winText = tempText = win32gui.GetWindowText(seui)
	failCount = 0
	while winText == tempText and failCount < 10:
	    index = random.randint(0,20)
	    x = rect[0] + 70
	    y = rect[1] + 55 + index * 20
	    DesktopCommon.MouseClick(x, y)
	    time.sleep(timeout)
	    tempText = win32gui.GetWindowText(seui)
	    failCount += 1
	if winText != tempText: #如果页面跳转，点击成功，tab总数加1
	    g_tabCount += 1

    #关闭侧边栏
    DesktopCommon.SendScKeys("LCTRL",'i')
    time.sleep(1)
    DesktopCommon.SendScKeys("LCTRL",'i')


#----------------------------------------------------------------------后退
def DoGoBackPage(args):
    if len(args)>0:
	count = args[0]
    else:
	count = 1
    DesktopCommon.Navigate("http://www.sogou.com/")
    time.sleep(2)
    DesktopCommon.SendScKeys("LALT",'d')
    DesktopCommon.Navigate("http://www.sohu.com/")
    time.sleep(3)
    for i in xrange(int(count)):
	time.sleep(1)
	DesktopCommon.SendScKeys("LALT",'LEFT')
    time.sleep(1)

# 完全刷新
def DoRefresh(args):
    DesktopCommon.SendScKeys("LCTRL","F5")

# 全部页面刷新
def DoRefreshAll(args):
    DesktopCommon.SendScKeys("LSHIFT","F5")

# 停止所有页面
def DoStopAll(args):
    DesktopCommon.SendScKeys("LSHIFT","ESC")

def DoPopupCancelList(args):
    try:
	wndInfo = DesktopCommon.GetWndPosEx("SE_TuotuoToolbar")
	for i in range(10):
	    ClickCtrl(wndInfo[-1],wndInfo[2]-46,10)
	    time.sleep(0.2)
	time.sleep(1)
    except:
	None

def DoLogonPassportAndRefresh(args):
    DoLogonPassport([])
    if not IsLogged():
	#如果没有登录，则没必要退出了
	time.sleep(0.2)
	return
    DoClickPassport()
    wndName = "网络账户"
    rect = -1
    for i in range(10):
	try:
	    rect = DesktopCommon.GetWndPosEx(None, wndName)
	    if rect==-1:
	        time.sleep(0.4)
	    else:
		break
	except:
	    time.sleep(0.4)
    if rect != -1 and len(rect) >= 4:
	DesktopCommon.MouseClick(rect[0]+40,rect[1]+130)



def DoPopupFavOnToolBar(args):
    #点击工具栏中的收藏夹按钮。试图重现下拉菜单的崩溃。
    #版本：3689版本。
    #堆栈信息：
    #SogouExplorer_40000000!PopupFavDropDownMenu+0x9c
    #SogouExplorer_40000000!CBrowserToolBarCtrl::OnFavDropDown+0x37
    #SogouExplorer_40000000!CBrowserToolBarCtrl::_ProcessWindowMessage+0x194
    #SogouExplorer_40000000!CBrowserToolBarCtrl::ProcessWindowMessage+0x23
    #SogouExplorer_40000000!ATL::CWindowImplBaseT >::WindowProc+0x44
    #SogouExplorer_40000000!CTuoToolBarCtrl::OnLButtonDown+0x19a
    try:
	wndInfo = DesktopCommon.GetWndPosEx("SE_TuotuoToolbar")
	for i in range(5):
	    ClickCtrl(wndInfo[-1],wndInfo[2]-10,10)
	    time.sleep(0.2)
	time.sleep(1)
    except:
	None

def DoPopupFavOnMenuBar(args):
    #点击菜单栏中的收藏夹按钮。试图重现下拉菜单的崩溃。
    #版本：3689版本。
    #堆栈信息：
    #SogouExplorer_40000000!CTuotuoMenuBarCtrl::OnDropDown+0xbc
    #SogouExplorer_40000000!CTuotuoMenuBarCtrl::_ProcessWindowMessage+0x1e0
    #SogouExplorer_40000000!CTuotuoMenuBarCtrl::ProcessWindowMessage+0x28
    #SogouExplorer_40000000!ATL::CWindowImplBaseT >::WindowProc+0x44
    #SogouExplorer_40000000!CTuoToolBarCtrl::OnLButtonDown+0x19a
    try:
	for i in range(5):
	    SeSmoke.ClickSEMenuBar(26 + 45 * random.randint(0, 6), 8)
	    time.sleep(0.2)
	time.sleep(1)
    except:
	None


def DoPopupToolBoxOnToolBar(args):
    try:
	wndInfo = DesktopCommon.GetWndPosEx("SE_TuotuoToolsBar")
	for i in range(5):
	    ClickCtrl(wndInfo[-1],69,10)
	    time.sleep(0.2)
	time.sleep(1)
    except:
	None

def DoPopupFavOnFavBar(args):
    try:
	wndInfo = DesktopCommon.GetWndPosEx("SE_TuotuoFavoriteBar")
	for i in range(5):
	    ClickCtrl(wndInfo[-1], 69, 10)
	    time.sleep(0.2)
	time.sleep(1)
    except:
	None

def DoUseExt(args):
    #使用各插件。有个坑。截图插件比较bt，导致浏览器失去响应。因此每次操作都需要发esc消息
    try:
	wndInfo = DesktopCommon.GetWndPosEx("SE_TuotuoToolsBar")
	startPosx = 120
	endPosx = wndInfo[2]
	for i in range(10):
	    rndPosx = GenRandom(endPosx, startPosx)
	    ClickCtrl(wndInfo[-1], rndPosx, 10)
	    time.sleep(1)
	    DesktopCommon.SendScKeys("DOWN")
	    time.sleep(0.5)
	    DesktopCommon.SendScKeys("ENTER")
	    time.sleep(2)
	    for i in range(2):
		DesktopCommon.SendScKeys("ESC")
		time.sleep(1)
    except:
	None


def DoAutoSwitchCore(args):
    global g_processSecurity
    #点击一个页面链接时自动从高速核自动切换到ie核
    #版本：3689版本。
    #堆栈信息：
    #SogouExplorer_40000000!CChildFrame::ResetAxControlWnd+0x39
    #SogouExplorer_40000000!CCoreCmdAux::OnSwitchCoreFromWebkit+0x79
    if len(args)>0:
	url = args[0]
    else:
	url = "http://10.11.195.211/Tools/switchcore.html"
    for i in range(6):
	DesktopCommon.OpenProcess(DesktopCommon.GetSEDir()+"\\SogouExplorer.exe", url, g_processSecurity)
	time.sleep(2)
	DoSwitchCore(args)
	time.sleep(2)
	handle = DesktopCommon.GetDynBoxHandle("SE_AxControl", -1, 2000, 1)
	#wndInfo = DesktopCommon.GetWndPosEx("SE_AxControl")
	rnd = GenRandom(15)
	DesktopCommon.ClickOnHandle(handle, 50, 20 * (rnd + 10))
	#ClickCtrl(wndInfo[-1],50,20*(rnd+10))
	time.sleep(2)


def DoSleep(args):
    if args!=None and len(args)>0:
	t = args[0]
    time.sleep(t)

#----------------------------------------------------------------------前进
def DoGoForwardPage(args):
    if len(args)>0:
	count = args[0]
    else:
	count = 1
    DesktopCommon.Navigate("http://www.sogou.com/")
    time.sleep(1)
    DesktopCommon.SendScKeys("LALT",'d')
    DesktopCommon.Navigate("http://www.sohu.com/")
    time.sleep(2)
    DesktopCommon.SendScKeys("LALT",'LEFT')
    time.sleep(1)
    for i in xrange(int(count)):
	time.sleep(1)
	DesktopCommon.SendScKeys("LALT",'RIGHT')
    time.sleep(1)



#----------------------------------------------------------------------打开上次未关闭页面
def OpenUrlsOfLastClosed(args):
    global g_tabCount
    time.sleep(1)
    DesktopCommon.SendScKeys("LCTRL",'t')
    time.sleep(1)
    DesktopCommon.Navigate("http://www.sohu.com/")
    time.sleep(3)
    DesktopCommon.SendScKeys("LCTRL",'w')
    time.sleep(1)
    #打开关闭页面后回退
    seui = win32gui.FindWindow("SE_SogouExplorerFrame",None)
    hwnd = DesktopCommon.SearchSubWindowByClassName(seui,"SE_TuotuoToolbar")
    if hwnd == 0:
	return
    rect = win32gui.GetWindowRect(hwnd)
    offset = [190,15]
    x = rect[0] + offset[0]
    y = rect[1] + offset[1]
    DesktopCommon.MouseClick(x, y)
    time.sleep(1)
    g_tabCount += 1


g_keywordCount = 0
#----------------------------------------------------------------------通过搜索栏搜索
def DoSearchBySearchBar(args):
    #global g_keywordCount
    keywordFile = args[0]
    keyword = ""
    '''
    if g_keywordCount == 0:
	f = open(urlFile,"r")
	keyword = f.readline().strip()
	for line in f:
	    line = line.strip()
	    if len(line)>0:
		g_keywordCount += 1
	f.close()

    if keyword == "":
	import random
	index = random.randint(0,g_keywordCount-1)
	f = open(keywordFile, "r")
	for x in xrange(index):
	    f.next()
	for line in f:
	    line = line.strip()
	    if len(line)>0:
		keyword = str(line)
		break
	f.close()
    '''

    keywords = DesktopCommon.ReadFileToArray(keywordFile)
    keywordCount = len(keywords)
    import random
    index = random.randint(0,keywordCount-1)
    keyword = keywords[int(index)]

    DesktopCommon.SendScKeys("LCTRL","e")
    DesktopCommon.Navigate(keyword)
    keywords = []
    time.sleep(2)


#清空历史记录
def DoClearHistory(args):
    None

def InvokeSkinManager():
    DesktopCommon.ClickOnCtrlWithWin32("SE_TuotuoMenuBar", 10, 10, "righttop")
    handle = DesktopCommon.GetHandle("SE_TuoLiteTooltip", None, 2)
    if handle == 0:
	DesktopCommon.ClickOnCtrlWithWin32("SE_TuotuoSystemButtonBar", 10, 10, "lefttop")
	handle = DesktopCommon.GetHandle("SE_TuoLiteTooltip", None, 2)

def ClickOnSkinManager(wndPosInfo):
    #出现皮肤管理器
    startx = wndPosInfo[0]+80
    starty = wndPosInfo[1] + 80
    for i in range(3):
	for j in range(3):
	    DesktopCommon.MouseClick(startx+i*200,starty+j*150)
	    time.sleep(1)
    randx = GenRandom(3)
    randy = GenRandom(3)
    DesktopCommon.MouseClick(startx+randx*200,starty+randy*150)
    ClickCtrl(wndPosInfo[-1],550,480)

# 切换主题背景的页数
def DoChangeBackgroudPage(args):
    InvokeSkinManager()
    handle = DesktopCommon.GetHandle("SE_TuoLiteTooltip", None, 1)
    if handle == 0:
	return
    DesktopCommon.ClickOnHandle(handle, 78, 49)
    DesktopCommon.Sleep(0.5)
    for i in range(5):
	rect = win32gui.GetWindowRect(handle)
	DesktopCommon.MouseClick(rect[0] + 256 + 45 * i, rect[3] - 29)
	DesktopCommon.Sleep(0.5)

# 切换主题背景的类别
def DoChangeBackgroudCatory(args):
    InvokeSkinManager()
    handle = DesktopCommon.GetHandle("SE_TuoLiteTooltip", None, 1)
    if handle == 0:
	return
    DesktopCommon.ClickOnHandle(handle, 78, 49)
    DesktopCommon.Sleep(0.5)
    for i in range(5):
	DesktopCommon.ClickOnHandle(handle, 122 + 72 * i, 96)
	DesktopCommon.Sleep(0.5)


#修改背景
def DoChangeBackground(args):
    InvokeSkinManager()
    wndPosInfo = DesktopCommon.GetWndPosEx("SE_TuoLiteTooltip")
    if wndPosInfo!=-1 and wndPosInfo[2]>700 and wndPosInfo[3]>500:
	ClickOnSkinManager(wndPosInfo)


def DoChangeSkin(args):
    InvokeSkinManager()
    wndPosInfo = DesktopCommon.GetWndPosEx("SE_TuoLiteTooltip")
    if wndPosInfo!=-1 and wndPosInfo[2]>700 and wndPosInfo[3]>500:
	 #出现皮肤管理器
	DesktopCommon.MouseClick(wndPosInfo[0]+200,wndPosInfo[1]+25)
	time.sleep(1)
	ClickOnSkinManager(wndPosInfo)

def DoRefreshSkin(args):
    InvokeSkinManager()
    wndPosInfo = DesktopCommon.GetWndPosEx("SE_TuoLiteTooltip")
    if wndPosInfo!=-1 and wndPosInfo[2]>700 and wndPosInfo[3]>500:
	 #出现皮肤管理器
	ClickCtrl(wndPosInfo[-1],wndPosInfo[2]-50,19)

# 点击选项对话框特定位置
def InvokeBrowseOptionDlg(dx, dy):
    DesktopCommon.SendScKeys("LALT", "t")
    time.sleep(0.5)
    DesktopCommon.SendScKeys("LALT", "t")
    time.sleep(0.5)
    DesktopCommon.SendScKeys("s")
    time.sleep(0.5)
    handle = GetHandle("#32770", "搜狗高速浏览器 选项", 3)
    if handle == 0:
	return 0
    rect = win32gui.GetWindowRect(handle)
    DesktopCommon.MouseClick(rect[0] + dx, rect[1] + dy)
    time.sleep(0.5)
    return handle

# 调出Internet选项
def DoOpenInternetOptions(args):
    DesktopCommon.SendScKeys("LALT", "t")
    time.sleep(0.5)
    DesktopCommon.SendScKeys("LALT", "t")
    time.sleep(0.5)
    DesktopCommon.SendScKeys("o")
    time.sleep(0.5)
    DesktopCommon.SendScKeys("ESC")

# 设置搜狗高速浏览器为默认
def DoSetSEDefault(args):
    handle = InvokeBrowseOptionDlg(50, 55)
    DesktopCommon.ClickCtrlEx(handle, "Button", "设置搜狗高速浏览器为默认")
    time.sleep(0.5)
    DesktopCommon.SendScKeys("ENTER")
    time.sleep(0.5)
    DesktopCommon.ClickCtrlEx(handle, "Button", "确定")

# 高级设置
def DoSetAdvancedOptions(args):
    handle = InvokeBrowseOptionDlg(50, 466)
    options = [ "开启网速保护功能", "开启局域网模式", "开启CPU优化", "开启内存优化", "启动搜狗网页评级功能",\
               "开启网页加速推荐提示气泡", "启用Windows 7的任务栏预览功能", "自动开启小号窗口功能", "智能自动选择浏览模式", "默认使用高速模式", "默认使用兼容模式",\
               "提示升级", "自动升级", "手动升级", "在兼容模式下使用“高级渲染特性” 和GPU加速"]

    # 随机选择6项进行点击
    num = GenRandom(18)
    tempOptions = random.sample(options, num)
    for tempName in tempOptions:
	DesktopCommon.ClickCtrlEx(handle, "Button", tempName)
	time.sleep(0.6)
    DesktopCommon.ClickCtrlEx(handle, "Button", "确定")

# 设置缓存文件存储位置和最大占用空间
def DoSetCacheLocationAndSize(args):
    handle = InvokeBrowseOptionDlg(50, 466)
    time.sleep(0.5)
    DesktopCommon.ClickCtrlEx(handle, "Button", "设置", True)
    time.sleep(0.5)

    flag = GenRandom(1)
    dlgHandle = GetHandle("#32770", "视频加速设置", 5)
    if flag == 1:
	tempPath = os.path.join(os.environ["appdata"], "SogouExplorer1")
	DesktopCommon.SetCtrlTextEx(dlgHandle, "Edit", None, tempPath)
	time.sleep(0.5)
	clickNum = GenRandom(10)
	for i in range(clickNum):
	    DesktopCommon.ClickCtrlEx(dlgHandle, "msctls_trackbar32")
    else:
	DesktopCommon.ClickCtrlEx(dlgHandle, "Button", "默认")

    time.sleep(0.5)
    DesktopCommon.ClickCtrlEx(dlgHandle, "Button", "确定")
    time.sleep(0.5)
    DesktopCommon.ClickCtrlEx(handle, "Button", "确定")

# 粘贴并打开
def DoPasteAndNavigate(args):
    handle = GetHandle()
    if handle != 0:
	SetForeground(handle)
    urlFile = args[0]
    url = GetUrl(urlFile)
    flag = GenRandom(1)
    if flag == 0:
	url = random.sample(["搜狗", "acdgfh", "@3$%^&@!%*(&^", "12345", "\t\y\n", "<tr></tr>"], 1)[0]
    DesktopCommon.CtrlC(url)
    DesktopCommon.SendScKeys("LCTRL", "t")
    time.sleep(0.5)
    DesktopCommon.SendScKeys("LCTRL", "LSHIFT", "v")

# 点击审查元素对话框的特定位置
def ClickReviewElementsDlg(offsetx = 0, offsety = 0):
    handle = GetHandle("SE_AxControl", None, 5)
    if handle == 0:
	return
    rect = win32gui.GetWindowRect(handle)
    dx = 20
    dy = 120
    DesktopCommon.MouseClick(rect[2] - dx, rect[1] + dy, "RIGHT")
    time.sleep(0.5)
    DesktopCommon.SendScKeys("UP")
    time.sleep(0.5)
    DesktopCommon.SendScKeys("UP")
    time.sleep(0.5)
    DesktopCommon.SendScKeys("ENTER")
    #DesktopCommon.MouseClick(rect[2] - dx, rect[1] + dy + 267)

    # 查找对话框是否弹出
    dlgHandle = DesktopCommon.GetWindowHandle("ATL", None, None, 3)
    if dlgHandle == 0:
	return
    dlgRect = win32gui.GetWindowRect(dlgHandle)
    DesktopCommon.MouseClick(dlgRect[0] + offsetx, dlgRect[1] + offsety)
    time.sleep(0.5)

# 打开审查元素并点击某个子项
def DoOpenReviewElements(args):
    ranOffsetX = random.sample([45, 107, 166, 218, 278, 334, 389, 431], 1)[0]
    offsetY = 45
    ClickReviewElementsDlg(ranOffsetX, offsetY)

# 恢复默认位置
def DoSetToolbarDefault(args):
    handle = GetHandle("SE_SogouExplorerFrame")
    if handle == 0:
	return
    rect = win32gui.GetWindowRect(handle)
    dx = GenRandom(900)
    DesktopCommon.MouseClick(rect[0] + dx, rect[1] + 15, "RIGHT")
    time.sleep(0.5)
    DesktopCommon.SendScKeys("p")
    time.sleep(0.2)

# 智能填表管理器-手动添加通用表单信息
def DoTableManagerManualAdd(args):
    handle, rect = ShowAndGetTableManager()
    if rect == None:
	return
    num = GenRandom(8, 1)
    for i in range(num):
	DesktopCommon.MouseClick(rect[0] + 38, rect[1] + 40)
	time.sleep(0.5)

    # 随机选取几个添加信息
    addInfoNum = GenRandom(5, 1)
    locations = random.sample([93, 117, 138, 165, 190], addInfoNum)
    for dy in locations:
	DesktopCommon.MouseClick(rect[0] + 60, rect[1] + dy)
	time.sleep(0.5)
	DesktopCommon.MouseClick(rect[0] + 334, rect[1] + 106)
	time.sleep(0.2)
	DesktopCommon.SendScKeys("LCTRL", "a")
	DesktopCommon.CtrlV("setest")
	time.sleep(0.2)
	DesktopCommon.SendScKeys("TAB")
	time.sleep(0.2)
	DesktopCommon.SendScKeys("LCTRL", "a")
	DesktopCommon.CtrlV("setest001@#$%^&*()_+|{}:<")
	time.sleep(0.2)
	DesktopCommon.SendScKeys("TAB")
	time.sleep(0.2)
	DesktopCommon.SendScKeys("LCTRL", "a")
	DesktopCommon.CtrlV("setest@sohu.com")
	time.sleep(0.5)
	DesktopCommon.MouseClick(rect[2] - 416, rect[3] - 50)
	time.sleep(0.5)
	DesktopCommon.MouseClick(rect[2] - 56, rect[3] - 50)
	time.sleep(0.2)
    win32gui.SendMessage(handle, win32con.WM_CLOSE, 0, 0)

# 智能填表管理器-删除通用表单信息
def DoTableManagerDelete(args):
    handle, rect = ShowAndGetTableManager()
    if rect == None:
	return
    num = GenRandom(8)
    for i in range(num):
	DesktopCommon.MouseClick(rect[0] + 101, rect[1] + 40)
	time.sleep(0.5)
	DesktopCommon.SendScKeys("ENTER")
    win32gui.SendMessage(handle, win32con.WM_CLOSE, 0, 0)

# 智能填表管理器-重命名通用表单信息
def DoTableManagerModify(args):
    handle, rect = ShowAndGetTableManager()
    if rect == None:
	return
    num = GenRandom(5, 1)
    locations = random.sample([93, 117, 138, 165, 190], num)
    for dy in locations:
	DesktopCommon.MouseClick(rect[0] + 60, rect[1] + dy, "RIGHT")
	time.sleep(0.5)
	DesktopCommon.MouseClick(rect[0] + 60 + 39, rect[1] + dy + 37)
	time.sleep(0.5)
	name = random.sample(["hello", "sohu.com", r"@123$%^&*()_+|}{:\"<>?","'www.c123.com#'"], 1)[0]
	DesktopCommon.CtrlV(name)
	time.sleep(0.3)
    win32gui.SendMessage(handle, win32con.WM_CLOSE, 0, 0)

#下载后直接打开
def DoDownloadOpen(args):
    urlFile = args[0]
    url = GetUrl(urlFile)
    DesktopCommon.StartSE(url)
    DesktopCommon.WaitForWnd(None,"搜狗高速下载", 3)
    handles = DesktopCommon.GetWndHandles(None,"搜狗高速下载")
    if len(handles)>0:
	ClickCtrl(handles[0][0],194,177)

#下载文件
def DoDownload(args):
    urlFile = args[0]
    url = GetUrl(urlFile)
    ret = DownloadURL(url)

# 下载管理器中搜索
def DoSearchDownload(args):
    SeSmoke.ClickSEMenuBar(239, 5)
    DesktopCommon.Sleep(0.5)
    DesktopCommon.SendScKeys("m")
    DesktopCommon.Sleep(1)

    dhandle = DesktopCommon.GetWindowHandle("SGDUI.*", ".*下载.*", None,  3)
    rect = DesktopCommon.GetRectByHandle(dhandle)

    DesktopCommon.MouseClick(rect[2] - 199, rect[3] - 33)
    DesktopCommon.Sleep(0.5)
    DesktopCommon.SendScKeys("LCTRL", "a")
    DesktopCommon.Sleep(0.5)
    DesktopCommon.inputOneLine('ab')


# 下载管理栏中右键随机操作
def DoClickDownloadRightMouse(args):
    urlFile = args[0]
    url = GetUrl(urlFile)
    ret = DownloadURL(url)
    if not ret:
	return False

    DesktopCommon.Sleep(1)
    dhandle = DesktopCommon.GetWindowHandle("SGDUI.*", ".*下载.*", None,  3)

    rect = DesktopCommon.GetRectByHandle(dhandle)

    ran = GenRandom(4)
    DesktopCommon.MouseClick(rect[0] + 175 , rect[1] + 58 + 62 * ran, "RIGHT")

    num = GenRandom(9)
    for i in range(num):
	DesktopCommon.SendScKeys("DOWN")
	DesktopCommon.Sleep(0.5)
    DesktopCommon.SendScKeys("ENTER")

g_filePath = DesktopCommon.GetTemp()
def Set(url, localPath):
    global g_filePath
    g_filePath = localPath
    return (url,)

#下载文件-暂停-开始
def DoDownloadAndPause(args):
    print args
    urlFile = args[0]
    if not os.path.exists(urlFile):
	url = args[0]
    else:
	url = GetUrl(urlFile)
    ret = DownloadURL(url)
    if not ret:
	return False

    DesktopCommon.Sleep(1)
    dhandle = DesktopCommon.GetWindowHandle("SGDUI.*", ".*下载.*", None,  3)

    rect = DesktopCommon.GetRectByHandle(dhandle)
    startx = rect[2] - 65
    starty = rect[1] + 10
    step = 20
    for i in range(10):
	SetForeground(dhandle)
	pos = (startx,starty+i*step)
	win32api.SetCursorPos(pos)
	time.sleep(0.1)
	if IsCursorLink():
	    DesktopCommon.MouseClick(pos[0],pos[1])
	    time.sleep(1)
	    DesktopCommon.MouseClick(pos[0],pos[1])
	    time.sleep(1)



#判断x,y坐标下的鼠标形状是否是链接
def IsCursorLink():
    cursorInfo = win32gui.GetCursorInfo()
    return cursorInfo[1] == 65581 or cursorInfo[1] == 65567

#链接页面链接，以触发下载
def DoClickDownload(args):
    url = args[0]
    DesktopCommon.NavigateSE(url)
    wndInfo = DesktopCommon.GetWndPosEx("SE_AxControl")
    rndx = wndInfo[0] + 20
    starty = wndInfo[1] + 10
    endy = wndInfo[1] + wndInfo[3] - 10
    for i in range(5):
	rndy = GenRandom(endy,starty)
	DesktopCommon.MouseClick(rndx,rndy)
	time.sleep(1)
	DownloadCore()
    time.sleep(2)

def DoDownloadDelete(args):
    urlFile = args[0]
    url = GetUrl(urlFile)
    ret = DownloadURL(url)
    if not ret:
	return False
    time.sleep(3)
    #休眠后打开
    dhandle = DesktopCommon.GetWindowHandle("SGDUI.*", ".*下载.*", None,  3)
    #检查鼠标形状的变化来打开文件
    rect = DesktopCommon.GetRectByHandle(dhandle)
    startx = rect[0]+438
    starty = rect[1]+18
    step = 20
    for i in range(10):
	SetForeground(dhandle)
	pos = (startx,starty+i*step)
	win32api.SetCursorPos(pos)
	time.sleep(0.1)
	if IsCursorLink():
	    #如果发现“删除”
	    DesktopCommon.MouseClick(pos[0],pos[1])
	    time.sleep(1)

	    wndInfo = DesktopCommon.GetWndHandles(None,"删除下载任务")
	    if wndInfo!=-1 and len(wndInfo):
		posInfo = DesktopCommon.GetWndPosByHandle(wndInfo[0][0])
		time.sleep(0.1)
		DesktopCommon.MouseClick(posInfo[0]+100,posInfo[1]+120)
		time.sleep(1)

def DownloadURL(url):
    DesktopCommon.StartSE(url)
    fileName = url[url.rfind("/") + 1:]
    ret = DownloadCore(fileName)
    LogCrash("Download %s" % url)
    return ret


def DownloadCore(fileName = "temp.xxx"):
    global g_filePath
    DesktopCommon.WaitForWnd(None,"搜狗高速下载", 3)
    handles = DesktopCommon.GetWndHandles(None,"搜狗高速下载")
    if len(handles)>0:
	handle = handles[0][0]
	ClickCtrl(handle,364,110)

	dialogHandle = DesktopCommon.GetHandle("#32770", "另存为", 1)
	if dialogHandle == 0:
	    return
	if not os.path.exists(g_filePath):
	    os.makedirs(g_filePath)
	DesktopCommon.SetCtrlTextEx(dialogHandle, "Edit", None, g_filePath + "\\%s" % fileName)
	time.sleep(1)

	DesktopCommon.ClickCtrlEx(dialogHandle, "Button", "保存")
	time.sleep(1)

	ClickCtrl(handle,275,182)
	time.sleep(1)

	DesktopCommon.SendScKeys("ENTER")

	return True
    return False


#下载文件后在下载管理器里打开
def DoDownloadAndOpen(args):
    urlFile = args[0]
    url = GetUrl(urlFile)
    ret = DownloadURL(url)
    if not ret:
	return False
    time.sleep(5)
    #休眠后打开
    dhandle = DesktopCommon.GetWindowHandle("SGDUI.*", ".*下载.*", None,  3)
    #检查鼠标形状的变化来打开文件
    rect = DesktopCommon.GetRectByHandle(dhandle)
    startx = rect[0]+338
    starty = rect[1]+18
    step = 2
    for i in range(100):
	SetForeground(dhandle)
	pos = (startx,starty+i*step)
	win32api.SetCursorPos(pos)
	time.sleep(0.01)
	if IsCursorLink():
	    #如果发现“删除”
	    DesktopCommon.MouseClick(pos[0],pos[1])
	    time.sleep(1)
	    SetForeground(wndInfo[-1])

##@函数目的: 视频提取和还原
##@参数说明：
##@args[0]: 使用的url文件
##@args[1]: 提取和还原次数
##@args[2]: 提取前的等待时间。防止部分视频有广告
##@返回值：无
##@函数逻辑：略
def DoVideoExtract(args):
    global g_processSecurity
    if len(args)>0:
	url = GetUrl(args[0])
    else:
	url = "http://v.youku.com/v_show/id_XMzEyMzYwOTE2.html"
    waittime = args[2]
    times = args[1] #连续提取多少次

    DesktopCommon.CreateTabNav(url)

    time.sleep(waittime)
    for i in range(times):
	DesktopCommon.SendScKeys("LCTRL","q")
	posInfo = DesktopCommon.GetWndPosEx("SE_TuotuoPopupFrame")
	if posInfo!=-1:
	    ClickCtrl(posInfo[-1],posInfo[2]-70,-10) #点击还原按钮
	time.sleep(0.2)

##@函数目的: 在收藏栏调整url位置
##@参数说明：
##@args[0]: 调整次数
##@返回值：无
##@函数逻辑：略
def DoDragDropFavItemOnFavBar(args):
    None

#清空下载列表
def DoClearDownload(args):
    SeSmoke.ClickSEMenuBar(245,5)
    DesktopCommon.Sleep(0.5)
    DesktopCommon.SendScKeys("m")
    handle = DesktopCommon.GetWindowHandle("SGDUI.*", ".*下载.*", None, 5)
    if handle == 0:
	return
    SetForeground(handle)
    DesktopCommon.ClickOnHandle(handle, 49, 328)

    dialogHandle = DesktopCommon.GetWindowHandle("SGDUI.*", "清空.*", None, 2)
    DesktopCommon.ClickOnHandle(dialogHandle, 104, 123)


#浏览后停止
def DoStop(args):
    DoNavigate(args)
    DesktopCommon.SendScKeys("ESC")

#页面静音
def DoMute(args):
    wndInfo = DesktopCommon.GetWndHandles("SE_TuotuoStatusbarToolbar")
    ClickCtrl(wndInfo[0][0],106,10)
    ClickCtrl(wndInfo[0][0],80,10)
    time.sleep(0.1)

#点击页面链接
def DoClickPageLink(args):
    DoNavigate(args)
    time.sleep(8)
    DoClickUrlOnCurPage(args[1:])


#放大页面
def DoZoomIn(args):
    count = GenRandom(3)
    for i in range(count+1):
	DesktopCommon.SendScKeys("LCTRL","=")


#缩小页面
def DoZoomOut(args):
    count = GenRandom(3)
    for i in range(count+1):
	DesktopCommon.SendScKeys("LCTRL","-")


#工具箱的操作
def DoToolBox(args):
    #工具箱操作
    None

# 侧边栏打开经常访问的网站，点击其中内容
def DoClickOftenOnSideBar(args):
    DoOpenSideBar()
    wndInfo = DesktopCommon.GetWndPosEx("SE_TuotuoSidebar")
    ClickCtrl(wndInfo[-1], 10, 31)
    time.sleep(1)
    for i in range(8):
	posy = GenRandom(wndInfo[3] - 20, 100)
	ClickCtrl(wndInfo[-1], 50, posy)
	time.sleep(0.5)

# 侧边栏打开“经常访问的网站”，重命名、删除项
def DoOftenActionsBySideBar(args):
    DoOpenSideBar()
    wndInfo = DesktopCommon.GetWndPosEx("SE_TuotuoSidebar")
    ClickCtrl(wndInfo[-1], 10, 31)
    time.sleep(1)
    for i in range(3):
	posy = GenRandom(wndInfo[3] - 20, 100)
	ClickCtrl(wndInfo[-1], 50, posy, "RIGHT")
	time.sleep(0.5)
	DesktopCommon.SendScKeys("r")
	time.sleep(0.5)
	name = random.sample(["ss", "ww.b.com", "*()&^$@#@$#!@$^(&)+|}{P:><JKHK<", "网络", "sogou", "1+1=2"], 1)[0]
	DesktopCommon.CtrlV(name)
	time.sleep(0.5)
	DesktopCommon.SendScKeys("ENTER")
    for i in range(3):
	posy = GenRandom(wndInfo[3] - 20, 100)
	ClickCtrl(wndInfo[-1], 50, posy, "RIGHT")
	time.sleep(0.5)
	DesktopCommon.SendScKeys("d")
	time.sleep(0.5)
	DesktopCommon.SendScKeys("ENTER")

# 查看源代码（使用view-source:url）
def DoViewSourceWithNavigate(args):
    if len(args)>0:
	url = GetUrl(args[0])
    else:
	url = "http://v.youku.com/v_show/id_XMzEyMzYwOTE2.html"
    url = "view-source:" + url
    DesktopCommon.CreateTabNav(url)

# 点击右侧的滚动条
def DoClickScroll(args):
    handle = GetHandle("SE_SogouExplorerFrame", None, 3)
    rect = win32gui.GetWindowRect(handle)
    for i in range(8):
	y = GenRandom(rect[3] - 10, 200)
	DesktopCommon.MouseClick(rect[2] - 5, y)
	time.sleep(0.5)


#点击侧边栏收藏夹
def DoClickFavOnSideBar(args):
    DoOpenSideBar()
    wndInfo = DesktopCommon.GetWndPosEx("SE_TuotuoSidebar")
    ClickCtrl(wndInfo[-1],10,17)
    time.sleep(1)
    dateOrSite = GenRandom(1)
    #在视图区随意点击吧。
    time.sleep(1)
    for i in range(8):
	posy = GenRandom(wndInfo[3]-20,100)
	ClickCtrl(wndInfo[-1],50,posy)
	time.sleep(1)
    None

#在侧边栏收藏夹中搜索
def DoSearchOnSideFavBar(args):
    DoOpenSideBar()
    wndInfo = DesktopCommon.GetWndPosEx("SE_TuotuoSidebar")
    ClickCtrl(wndInfo[-1],10,17)
    time.sleep(1)
    ClickCtrl(wndInfo[-1],50,65)
    time.sleep(0.5)
    DesktopCommon.CtrlC("的")
    DesktopCommon.CtrlV("的")
    DesktopCommon.SendScKeys("ENTER")
    #在视图区随意点击吧。
    posy  = GenRandom(200,150)
    ClickCtrl(wndInfo[-1],50,posy)
    time.sleep(1)
    ClickCtrl(wndInfo[-1],50,65)
    DesktopCommon.SendScKeys("BACKSPACE")

#----------------------------------------------------------------------通过鼠标拖拽打开新标签
def DoOpenUrlByMouseDrag(args):
    global g_tabCount
    count = args[0]
    timeout = args[1]
    #seui = win32gui.FindWindow("SE_SogouExplorerFrame",None)
    #pageHwnd = DesktopCommon.SearchSubWindowByClassName(seui,"SE_AxControl")
    pageHwnd = win32gui.FindWindow("SE_AxControl",None)
    if pageHwnd == 0:
	return
    browserRect = win32gui.GetWindowRect(pageHwnd)
    mouseWidth = 900 #鼠标点击区域宽度定义为900
    leftScreen = (browserRect[2] - mouseWidth)/2 + browserRect[0]
    TopScreen = browserRect[1] - 10
    for i in xrange(int(count)):
	p = RandomValueablePoint(leftScreen,TopScreen)
	if len(p) != 2:
	    continue

	win32api.SetCursorPos(p)
	DesktopCommon.MouseDown()
	time.sleep(0.5)
	win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 30, 30, 0, 0)
	time.sleep(0.5)
	DesktopCommon.MouseUp()
	time.sleep(timeout)
	g_tabCount += 1



g_tabCount = 0     #记录打开标签个数
#----------------------------------------------------------------------
def DoPostTabActions(args):
    global g_tabCount
    import random
    index = random.randint(1,10)

    if index >= 1 and index <=3:
	DoPostTabAction1()
    elif index == 4:
	DoPostTabAction2(20)
    elif index >= 5 and index <=8:
	DoPostTabAction3(20)
    elif index == 9:
	DoPostTabAction2(40)
    elif index == 10:
	DoPostTabAction3(40)

    if g_tabCount >= 40: #标签大于40个时全部关闭
	DesktopCommon.SendScKeys("LCTRL","LSHIFT","w")
	time.sleep(2)
	g_tabCount = 1

#----------------------------------------------------------------------
def DoPostTabAction1(): #新建关闭标签动作1
    DesktopCommon.SendScKeys("LCTRL","t")
    time.sleep(1)
    DesktopCommon.Navigate("http://www.sogou.com/")
    time.sleep(2)
    DesktopCommon.SendScKeys("LCTRL","w")
    time.sleep(1)
    DesktopCommon.SendScKeys("LCTRL","t")
    time.sleep(1)
    DesktopCommon.Navigate("http://www.sohu.com/")
    time.sleep(3)


def DoPostTabAction2(tabCount): #新建关闭标签动作2
    global g_tabCount
    if g_tabCount < tabCount:
	return
    DesktopCommon.SendScKeys("LCTRL","LSHIFT","w")
    time.sleep(2)
    DesktopCommon.SendScKeys("LCTRL","t")
    time.sleep(1)
    DesktopCommon.Navigate("http://www.sohu.com/")
    time.sleep(5)
    g_tabCount =1 #全部关闭后打开1个标签



def DoPostTabAction3(tabCount): #新建关闭标签动作3
    global g_tabCount
    if g_tabCount < tabCount:
	return
    import random
    #随机关闭几个标签页
    count = random.randint(2,6)
    for x in xrange(count):
	value = random.randint(1,g_tabCount)
	for i in xrange(value):
	    DesktopCommon.SendScKeys("LCTRL","TAB")
	    time.sleep(0.5)
	DesktopCommon.SendScKeys("LCTRL","w")
	time.sleep(1)

    g_tabCount -= count
    time.sleep(1)
    DesktopCommon.SendScKeys("LCTRL","t")
    time.sleep(1)
    DesktopCommon.Navigate("http://www.sohu.com/")
    g_tabCount += 1
    time.sleep(5)



def DoOtherMouseAction(args):
    count1 = int(args[0])
    count2 = int(args[1])
    count3 = int(args[2])
    count4 = int(args[3])

    #seui = win32gui.FindWindow("SE_SogouExplorerFrame",None)
    #pageHwnd = DesktopCommon.SearchSubWindowByClassName(seui,"SE_AxControl")
    pageHwnd = win32gui.FindWindow("SE_AxControl",None)
    if pageHwnd == 0:
	return

    browserRect = win32gui.GetWindowRect(pageHwnd)
    mouseWidth = 900 #鼠标点击区域宽度定义为900
    leftScreen = (browserRect[2] - mouseWidth)/2 + browserRect[0]
    TopScreen = browserRect[1] - 10
    for i in xrange(count1):
	p = RandomValueablePoint(leftScreen,TopScreen)
	time.sleep(0.3)

    #获取一个空白点
    p = []
    p.append(browserRect[2] - 100)
    p.append(browserRect[1] + 300)
    y = browserRect[1] + 300
    win32api.SetCursorPos(p)
    cursorInfo = win32gui.GetCursorInfo()

    while str(cursorInfo[1]) == "65581": #如果是链接继续
	y  += 2
	p[1] = y
	win32api.SetCursorPos(p)
	time.sleep(0.3)
	cursorInfo = win32gui.GetCursorInfo()

    #空白处点击50次
    for i in xrange(count2):
	DesktopCommon.MouseClick(p[0], p[1])
	time.sleep(0.2)

    #滚轮操作50次
    for i in xrange(count3):
	win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL,0,0,win32con.WHEEL_DELTA)
	time.sleep(0.2)
	win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL,0,0,-win32con.WHEEL_DELTA)
	time.sleep(0.2)

    #随机发送点击键盘50次
    a = 97
    import random
    for i in xrange(count4):
	key = random.randint(0,25)
	key = a + key
	value = chr(key)
	DesktopCommon.SendScKeys(str(value))
	time.sleep(0.2)


#----------------------------------------------------------------------
def DoFavActionsBySideBar(args):  #通过侧边栏添加，编辑，删除收藏夹
    urlFile = args[0] #参数1，url路径
    count = args[1] #参数2，执行次数
    urls = DesktopCommon.ReadFileToArray(str(urlFile))
    urlCount = len(urls)
    index = 0
    #侧边栏
    DoOpenSideBar()
    for i in xrange(int(count)):
	if index >= urlCount:
	    index = 0
	url = str(urls[index])
	MyLog(url,False)
	AddUrlToFavBySideBar(url,url)
	time.sleep(1)
	EditFavUrlBySideBar("SideBar" + str(i))
	time.sleep(1)
	DeleteFavUrlBySideBar()
	index += 1
    DesktopCommon.SendScKeys("LCTRL","i")


#----------------------------------------------------------------------
def DoFavActionsByFavBar(args):  #通过收藏栏添加，编辑，删除收藏项
    urlFile = args[0] #参数1，url路径
    count = args[1] #参数2，执行次数
    url = GetUrl(urlFile)
    index = 0
    #收藏栏
    for i in xrange(count):
	#url = str(urls[index])
	AddUrlToFavByFavBar(url,url)
	time.sleep(1)
	EditFavUrlByFavBar("FavBar" + str(i))
	time.sleep(1)
	DeleteFavUrlByFavBar()
	index += 1


#----------------------------------------------------------------------
def DoFavActionsByFavManager(args):  #通过菜单管理添加，编辑，删除收藏项
    urlFile = args[0] #参数1，url路径
    count = args[1] #参数2，执行次数
    urls = DesktopCommon.ReadFileToArray(str(urlFile))
    urlCount = len(urls)

    index = 0
    #菜单栏
    SeSmoke.ClickSEMenuBar(186, 8)
    time.sleep(1)
    DesktopCommon.SendScKeys("m")
    time.sleep(1)
    hwnd = win32gui.FindWindow(None,"整理收藏夹")
    if hwnd == 0:
	return
    rect = win32gui.GetWindowRect(hwnd)
    p_create = []
    p_create.append(rect[0] + 20)
    p_create.append(rect[1] + 40)
    p_edit = []
    p_edit.append(rect[0] + 60)
    p_edit.append(rect[1] + 40)
    p_delete = []
    p_delete.append(rect[0] + 100)
    p_delete.append(rect[1] + 40)
    p_click = []
    p_click.append(rect[0] + 400)
    p_click.append(rect[1] + 85)

    for i in xrange(count):
	if index >= urlCount:
	    index = 0
	url = str(urls[index])
	AddUrlToFavByFavManager(p_create,url,url)
	time.sleep(1)
	EditFavUrlByFavManager(p_edit,p_click,"FavManager" + str(i))
	time.sleep(1)
	DeleteFavUrlByFavManager(p_delete,p_click)
	index += 1
    DesktopCommon.MouseClick(rect[0] + 200, rect[1] + 15, "RIGHT")
    time.sleep(1)
    DesktopCommon.SendScKeys("c") #关闭收藏夹管理对话框

#----------------------------------------------------------------------
def AddUrlToFavBySideBar(caption,url):  #通过侧边栏添加收藏项
    if url == "":
	return

    seui = win32gui.FindWindow("SE_SogouExplorerFrame",None)
    pageHwnd = DesktopCommon.SearchSubWindowByClassName(seui,"SE_TuotuoSidebar")
    if pageHwnd == 0:
	return
    #pageHwnd = win32gui.FindWindow("SE_TuotuoSidebar",None)
    rect = win32gui.GetWindowRect(pageHwnd)
    #DesktopCommon.SendScKeys("LCTRL","i")
    x = rect[0] + 50
    y = rect[1] + 40
    DesktopCommon.MouseClick(x, y)
    AddUrlToFav(str(caption), str(url))
    #DesktopCommon.SendScKeys("LCTRL","i")


#----------------------------------------------------------------------
def EditFavUrlBySideBar(content): #通过侧边栏编辑收藏项
    if content == "":
	return
    seui = win32gui.FindWindow("SE_SogouExplorerFrame",None)
    pageHwnd = DesktopCommon.SearchSubWindowByClassName(seui,"SE_TuotuoSidebar")
    if pageHwnd == 0:
	return
    rect = win32gui.GetWindowRect(pageHwnd)
    clickOffset = [60,120]
    x = rect[0] + clickOffset[0]
    y = rect[1] + clickOffset[1]
    DesktopCommon.MouseClick(x, y, "RIGHT")
    time.sleep(1)
    DesktopCommon.SendScKeys("e")
    EditFavUrl(content)


#----------------------------------------------------------------------
def DeleteFavUrlBySideBar(): #通过侧边栏删除收藏项
    seui = win32gui.FindWindow("SE_SogouExplorerFrame",None)
    pageHwnd = DesktopCommon.SearchSubWindowByClassName(seui,"SE_TuotuoSidebar")
    if pageHwnd == 0:
	return
    rect = win32gui.GetWindowRect(pageHwnd)
    clickOffset = [144,273]
    x = rect[0] + clickOffset[0]
    y = rect[1] + clickOffset[1]
    DesktopCommon.MouseClick(x, y, "RIGHT")
    time.sleep(1)
    DesktopCommon.SendScKeys("d")
    time.sleep(1)
    DesktopCommon.SendScKeys("ENTER")
    time.sleep(1)


#----------------------------------------------------------------------
def EditFavUrl(content): #编辑url对话框
    time.sleep(1)
    favHwnd = win32gui.FindWindow(None,"编辑收藏项")
    if favHwnd == 0:
	return
    try:
	win32gui.SetForegroundWindow(favHwnd)
	win32gui.SetActiveWindow(favHwnd)
    except:
	None

    for i in xrange(3):
	DesktopCommon.SendScKeys("TAB")
	time.sleep(0.5)
    DesktopCommon.SetClipboardData(str(content)) #设置标题
    time.sleep(0.5)
    DesktopCommon.SendScKeys("LCTRL","v")
    time.sleep(0.5)
    DesktopCommon.SendScKeys("ENTER")
    time.sleep(1)

g_setButtonPos = []  # 页面内“设置”按钮的位置
g_picPathList = []   # 图片路径，在设置皮肤时用到
g_myfavorButtonPos = [] # 页面内“我的最爱”按钮的位置
g_categoryButtonPos = [] # 页面内“常用网址”按钮的位置
g_newsButtonPos = [] # 页面内“新闻资讯”按钮的位置
g_setFavorPagesPos = []   # 保存8个“自定义网址”按钮坐标
g_deleteFavorPagesPos = []   # 保存8个“删除”按钮坐标
g_pinkBtnPos = []           # 保持8个pink按钮坐标
g_urlList = []              # 保存从url文件中读取的url列表

g_point_default = []
g_favorPagesRect = []
g_favorPageWindowText = ""
g_versionFlag = 1 #1为新版本起始页，0为旧版本的九宫格起始页
#----------------------------------------------------------------------
def InitStartPageTest(flag = 2):
    global g_point_default, g_favorPagesRect, g_favorPageWindowText, g_versionFlag
    global g_urlList, g_setButtonPos, g_picPathList, g_myfavorButtonPos, g_categoryButtonPos, g_newsButtonPos, g_setFavorPagesPos, g_deleteFavorPagesPos, g_pinkBtnPos
    g_versionFlag = flag
    seui = win32gui.FindWindow("SE_SogouExplorerFrame",None)
    if seui == 0:
	return False
    try:
	win32gui.SetForegroundWindow(seui)
	win32gui.SetActiveWindow(seui)
    except:
	None
    g_favorPageWindowText = win32gui.GetWindowText(seui)
    pageHwnd = win32gui.FindWindow("SE_AxControl",None)
    if pageHwnd == 0:
	return False
    rect = win32gui.GetWindowRect(pageHwnd)
    #如果是旧版本，九宫格扫描线
    if g_versionFlag == 0:
	startPoint = [rect[0],rect[1]]
	endPoint = [rect[2],rect[3]]
	win32api.SetCursorPos(startPoint)
	time.sleep(1)
	x = rect[0] + 100
	y = rect[1] + 20
	p = []
	p.append(0)
	p.append(y)
	g_point_default.append(x)
	g_point_default.append(y)
	while x < rect[2]:
	    win32api.SetCursorPos(p)
	    time.sleep(0.001)
	    cursorInfo = win32gui.GetCursorInfo()
	    if str(cursorInfo[1]) == "65581":
		g_point_default[0] = x
		break
	    x += 1
	    p[0] = x

	if g_point_default[0] == 0: #判断“恢复默认”的x坐标是否有效
	    return False
	g_point_default[0] += 20 #向右平移20个单位

	p[0] = g_point_default[0]#设置起始位置,画竖直扫描线
	y = g_point_default[1]
	p[1] = y
	favorPageY = []
	startFlag = False
	yStart = 0
	yEnd = 0
	while y < rect[3]:
	    win32api.SetCursorPos(p)
	    time.sleep(0.001)
	    cursorInfo = win32gui.GetCursorInfo()
	    if str(cursorInfo[1]) == "65581": #鼠标手势的标识
		if not startFlag:
		    yStart = y
		    startFlag = True
	    else:
		yEnd = y
		startFlag = False
		if (yEnd - yStart) > 100 and yStart != 0:
		    favorPageY.append(yStart)
		    favorPageY.append(yEnd)
		yStart = y
	    y += 1
	    p[1] = y

	if len(favorPageY) != 6:
	    return False

	#设置水平扫描线的起始点
	x = rect[0] + 100
	p[0] = x
	p[1] = (favorPageY[3] - favorPageY[2]) / 2 + favorPageY[2]
	favorPageX = []
	startFlag = False
	xStart = 0
	xEnd = 0
	while x < rect[2]:
	    win32api.SetCursorPos(p)
	    time.sleep(0.001)
	    cursorInfo = win32gui.GetCursorInfo()
	    if str(cursorInfo[1]) == "65581": #鼠标手势的标识
		if not startFlag:
		    xStart = x
		    startFlag = True
	    else:
		xEnd = x
		startFlag = False
		if (xEnd - xStart) > 100 and xStart != 0:
		    favorPageX.append(xStart)
		    favorPageX.append(xEnd)
		xStart = x
	    x += 1
	    p[0] = x

	if len(favorPageX) < 6:
	    return False

	for i in xrange(3):
	    a = []
	    g_favorPagesRect.append(a)
	    for j in xrange(3):
		tempRect = []
		tempRect.append(favorPageX[j*2])
		tempRect.append(favorPageY[i*2])
		tempRect.append(favorPageX[j*2+1])
		tempRect.append(favorPageY[i*2+1])
		g_favorPagesRect[i].append(tempRect)
	return True
    elif g_versionFlag == 1:
	startPoint = [rect[0],rect[1]]
	endPoint = [rect[2],rect[3]]
	win32api.SetCursorPos(startPoint)
	time.sleep(1)
	x = (rect[2] - rect[0]) / 2 + rect[0]
	y = rect[1] + 170
	p = []
	p.append(0)
	p.append(y)
	g_point_default.append(x)
	g_point_default.append(y)
	while x < rect[2]:
	    win32api.SetCursorPos(p)
	    time.sleep(0.001)
	    cursorInfo = win32gui.GetCursorInfo()
	    if str(cursorInfo[1]) == "65581":
		g_point_default[0] = x
		break
	    x += 1
	    p[0] = x

	if g_point_default[0] == 0: #判断“恢复默认”的x坐标是否有效
	    return False
	g_point_default[0] += 20 #向右平移20个单位

	p[0] = g_point_default[0]#设置起始位置,画竖直扫描线
	y = g_point_default[1]
	p[1] = y
	favorPageY = []
	startFlag = False
	yStart = 0
	yEnd = 0
	while y < rect[3]:
	    win32api.SetCursorPos(p)
	    time.sleep(0.001)
	    cursorInfo = win32gui.GetCursorInfo()
	    if str(cursorInfo[1]) == "65581": #鼠标手势的标识
		if not startFlag:
		    yStart = y
		    startFlag = True
	    else:
		yEnd = y
		startFlag = False
		if (yEnd - yStart) > 100 and yStart != 0:
		    favorPageY.append(yStart)
		    favorPageY.append(yEnd)
		yStart = y
	    y += 1
	    p[1] = y



	if len(favorPageY) != 4:
	    return False

	#设置水平扫描线的起始点
	x = rect[0] + 100
	p[0] = x
	p[1] = (favorPageY[3] - favorPageY[2]) / 2 + favorPageY[2]
	favorPageX = []
	startFlag = False
	xStart = 0
	xEnd = 0
	while x < rect[2]:
	    win32api.SetCursorPos(p)
	    time.sleep(0.001)
	    cursorInfo = win32gui.GetCursorInfo()
	    if str(cursorInfo[1]) == "65581": #鼠标手势的标识
		if not startFlag:
		    xStart = x
		    startFlag = True
	    else:
		xEnd = x
		startFlag = False
		if (xEnd - xStart) > 100 and xStart != 0:
		    favorPageX.append(xStart)
		    favorPageX.append(xEnd)
		xStart = x
	    x += 1
	    p[0] = x

	if len(favorPageX) < 8:
	    return False

	for i in xrange(2):
	    a = []
	    g_favorPagesRect.append(a)
	    for j in xrange(4):
		tempRect = []
		tempRect.append(favorPageX[j*2])
		tempRect.append(favorPageY[i*2])
		tempRect.append(favorPageX[j*2+1])
		tempRect.append(favorPageY[i*2+1])
		g_favorPagesRect[i].append(tempRect)
	return True

    # 4.0版本我的最爱页面
    elif g_versionFlag == 2:

	g_picPathList = GetPicturePathList()
	g_urlList = GetURLList()
	print "start:",len(g_urlList)
	if len(g_urlList) <= 0:
	    return False
	startPoint = [rect[0],rect[1]]
	endPoint = [rect[2],rect[3]]
	win32api.SetCursorPos(startPoint)
	time.sleep(0.2)

	# 获取“我的最爱”及“分类导航”按钮的位置
	x = startPoint[0] + 300
	y = endPoint[1] - 85
	mouseChangeCount = 0

	p = []
	p.append(x)
	p.append(y)
	win32api.SetCursorPos(p)
	DesktopCommon.Sleep(0.2)
	cursorInfoBefore = win32gui.GetCursorInfo()
	while x < endPoint[0]:
	    win32api.SetCursorPos(p)
	    time.sleep(0.01)
	    cursorInfoAfter = win32gui.GetCursorInfo()
	    # 第一次鼠标样式发生变化为移动到“新闻资讯”按钮
	    if mouseChangeCount == 0 and int(cursorInfoBefore[1]) != int(cursorInfoAfter[1]):
		g_newsButtonPos.append(x + 20)
		g_newsButtonPos.append(y)
		cursorInfoBefore = cursorInfoAfter
		break;
	    x += 1
	    p[0] = x

	if len(g_newsButtonPos) != 2:
	    return False
	g_myfavorButtonPos = [g_newsButtonPos[0] + 120, g_newsButtonPos[1] ]
	if len(g_myfavorButtonPos) != 2:
	    return False
	g_categoryButtonPos = [g_newsButtonPos[0] + 240, g_newsButtonPos[1]]
	if len(g_categoryButtonPos) != 2:
	    return False

	DoClickMyFavBtn(0)

	g_setButtonPos = [rect[2] - 48, rect[1] + 26]
	## 获取设置按钮的坐标位置
	#x = endPoint[0] - 10
	#y = startPoint[1] + 10



	#p = []
	#p.append(x)
	#p.append(y)
	#win32api.SetCursorPos(p)
	#time.sleep(0.5)
	#cursorInfoBefore = win32gui.GetCursorInfo()
	#while x > startPoint[0]:
	    #win32api.SetCursorPos(p)
	    #time.sleep(0.001)
	    #cursorInfoAfter = win32gui.GetCursorInfo()
	    #if int(cursorInfoBefore[1]) != int(cursorInfoAfter[1]):
		#g_setButtonPos.append(x - 10)
		#g_setButtonPos.append(y)
		#break
	    #x -= 3
	    #p[0] = x
	#DesktopCommon.MouseClick(g_setButtonPos[0], g_setButtonPos[1])
	#DesktopCommon.MouseClick(g_setButtonPos[0] + 15, g_setButtonPos[1] + 35)
	#if len(g_setButtonPos) != 2:
	    #return False

	# 获取“我的最爱”的下边缘坐标
	x = startPoint[0] + 300
	y = endPoint[1] - 100

	tempBottom = 0
	p = []
	p.append(x)
	p.append(y)
	win32api.SetCursorPos(p)
	DesktopCommon.Sleep(1)
	flag = True
	if DesktopCommon.IsCursorLink():
	    flag = False
	while y > startPoint[1]:
	    win32api.SetCursorPos(p)
	    time.sleep(0.01)
	    if not DesktopCommon.IsCursorLink():
		flag = True
	    if flag and DesktopCommon.IsCursorLink():
		tempBottom = y
		break
	    y -= 1
	    p[1] = y
	if tempBottom == 0:
	    return False

	# 获取“我的最爱”的左边缘坐标
	x = startPoint[0] + 100
	y = (startPoint[1] + endPoint[1]) / 2

	tempLeft = 0
	p = []
	p.append(x)
	p.append(y)
	win32api.SetCursorPos(p)
	DesktopCommon.Sleep(0.2)
	cursorInfoBefore = win32gui.GetCursorInfo()
	while x < endPoint[0]:
	    win32api.SetCursorPos(p)
	    time.sleep(0.01)
	    cursorInfoAfter = win32gui.GetCursorInfo()
	    if int(cursorInfoBefore[1]) != int(cursorInfoAfter[1]):
		tempLeft = x
		break
	    x += 1
	    p[0] = x
	if tempLeft == 0:
	    return False

	# 单个框的大小及自定义网址、删除小按钮的位置相对于左下点的偏移(此处在不同的电脑上可能会发生变化)
	tempRectSize = [244, 150]
	dx = 15
	dy = 15
	for i in range(1, 5):
	    for j in range(3):
		g_setFavorPagesPos.append([tempLeft + tempRectSize[0] * i - 50, tempBottom - tempRectSize[1] * j - 15])
		g_deleteFavorPagesPos.append([tempLeft + tempRectSize[0] * i - 20, tempBottom - tempRectSize[1] * j - 15])
		g_pinkBtnPos.append([tempLeft + (tempRectSize[0] + dx) * i - dx - 10, tempBottom + (tempRectSize[1] + dy) * j + tempRectSize[1] + 10])
	return True

#----------------------------------------------------------------------
##@函数目的: 获取文件中的url列表
##@参数说明：urlPath为保存url的文件路径，默认为%FrameworkPath%\lib\atf\plugin\url.txt
##@返回值：url列表
##@函数逻辑：读取文件，追加到列表中
def GetURLList(urlPath = ""):
    urlList = []
    if urlPath == "":
	urlPath = os.path.join(DesktopCommon.GetFrameworkPath(), r"lib\atf\plugin\url.txt")
    urlFile = file(urlPath, "r")
    for url in urlFile:
	urlList.append(url.strip())
    urlFile.close()
    return urlList


#----------------------------------------------------------------------
##@函数目的: 获取文件夹下的图片路径列表
##@参数说明：picDir为需要遍历的文件夹，默认为%Appdata%\SogouExplorer\Thumbnails
##@返回值：图片路径列表
##@函数逻辑：遍历文件夹，提取.jpg后缀的文件路径
def GetPicturePathList(picDir = ""):
    # 注：此文件夹用于保存我的最爱页面的图片缩略图
    picList = []
    if picDir == "":
	picDir = os.path.join(DesktopCommon.GetAppPath(), r"SogouExplorer\Thumbnails")
    for root, dirs, files in os.walk(picDir):
	for fileName in files:
	    if fileName.endswith('.jpg'):
		picList.append(os.path.join(root, fileName))
    return picList

def DoPinkPage(args):
    global g_pinkBtnPos
    DoClickMyFavBtn(args)
    index = GenRandom(len(g_pinkBtnPos))
    point = g_pinkBtnPos[index]
    DesktopCommon.MouseClick(point[0], point[1])
    # 处理弹出的对话框
    EditDialogOperation()

#----------------------------------------------------------------------
##@函数目的: 搜索框内输入关键词触发suggestion功能
##@参数说明：传入需要输入到搜索框的字符串
##@返回值：
##@函数逻辑：
def DoSearchSuggestion(args):
    DoClickMyFavBtn(args)
    DesktopCommon.SendScKeys("LCTRL","F5")
    DesktopCommon.Sleep(2)  # 在远程机器上执行时，若不sleep会出现输入不进去的情况
    if len(args) > 0:
	SeSmoke.inputOneLine(args[0])
    else:
	SeSmoke.inputOneLine("abc")
    DesktopCommon.SendScKeys("LCTRL","F5")

#----------------------------------------------------------------------
##@函数目的: 切换TAB各功能的稳定性
##@参数说明：
##@返回值：
##@函数逻辑：先点击“分类导航”后点击“我的最爱”
def DoSwitchPages(args):
    global g_categoryButtonPos, g_myfavorButtonPos
    DoClickNewsBtn(args)
    DoClickOftenURLBtn(args)
    DoClickMyFavBtn(args)
    DoClickOftenURLBtn(args)
    DoClickNewsBtn(args)
    DoClickMyFavBtn(args)

#----------------------------------------------------------------------
##@函数目的: 更换背景
##@参数说明：
##@返回值：
##@函数逻辑：先点击“设置”，后点选随机的皮肤，当第一次点击右下角皮肤时，需要设置一张图片
def DoSetSkin(args):
    global g_picPathList, g_setButtonPos, g_versionFlag
    if g_versionFlag != 2 or len(g_setButtonPos) == 0:
	return

    DoClickMyFavBtn(args)
    #offsetBySetButtonPos = [-5, 60]   # 右上角皮肤相对于设置按钮的偏移
    #distanceOfSkin = [-85, 50]        # 皮肤与皮肤之间的偏移

    DesktopCommon.MouseClick(g_setButtonPos[0], g_setButtonPos[1])

    row = random.randint(0, 1)
    column = random.randint(0, 2)
    #DesktopCommon.MouseClick(g_setButtonPos[0] + offsetBySetButtonPos[0] + distanceOfSkin[0] * column, g_setButtonPos[1] + offsetBySetButtonPos[1] + distanceOfSkin[1] * row)

    DesktopCommon.MouseClick(g_setButtonPos[0] - 24 - 68 * column, g_setButtonPos[1] + 76 + 50 * row)

    # 先检查图片路径列表是否为空
    if len(g_picPathList) == 0:
	# 重新获取Thumbnails文件夹下的图片路径
	g_picPathList = GetPicturePathList()
	DesktopCommon.SendScKeys("ESC")
	DesktopCommon.SendScKeys("LCTRL","F5")
	return

    # 检查是否有“打开”窗口弹出
    timeout = 2  #2秒钟超时
    openWindowHandle = 0
    for x in xrange(timeout):
	openWindowHandle = win32gui.FindWindow("#32770","打开")
	if openWindowHandle != 0:
	    break
	else:
	    time.sleep(1)
    if openWindowHandle == 0:
	DesktopCommon.SendScKeys("LCTRL","F5")
	return

    # 若有“打开”窗口，设置图片路径
    picPath = random.sample(g_picPathList, 1)[0]

    childWindows = []
    DesktopCommon.EnumAllChildWindows(openWindowHandle, childWindows, 9)
    for childWindowInfo in childWindows:
	if childWindowInfo[1] == "Edit":
	    openFileTextBox = win32ui.CreateWindowFromHandle(childWindowInfo[0])
	    openFileTextBox.SendMessage(win32con.WM_SETTEXT, picPath)
	    break
    DesktopCommon.Sleep(0.1)
    handle = DesktopCommon.GetHandle("#32770", "打开", 2)
    DesktopCommon.ClickCtrlEx(handle, "Button", "打开(&O)")
    DesktopCommon.Sleep(0.1)

    # 若出现图片路径错误的情况，需要按两下ESC
    DesktopCommon.SendScKeys("ESC")
    DesktopCommon.Sleep(0.01)
    DesktopCommon.SendScKeys("ESC")
    DesktopCommon.Sleep(0.01)
    DesktopCommon.SendScKeys("LCTRL", "F5")

#----------------------------------------------------------------------
def DoClickRefreshButton(args): #点击refresh按钮
    time.sleep(1)
    #打开关闭页面后回退
    seui = win32gui.FindWindow("SE_SogouExplorerFrame",None)
    if seui == 0:
	return
    hwnd = DesktopCommon.SearchSubWindowByClassName(seui,"SE_TuotuoToolbar")
    if hwnd == 0:
	return
    rect = win32gui.GetWindowRect(hwnd)
    offset = [125,15] #点击刷新按钮
    x = rect[0] + offset[0]
    y = rect[1] + offset[1]
    DesktopCommon.MouseClick(x, y)
    time.sleep(1)


#----------------------------------------------------------------------
def DoClickDefaultOnFavorPage(args): #点击起始页的“恢复默认”
    global g_point_default
    DesktopCommon.MouseClick(g_point_default[0], g_point_default[1])
    time.sleep(1)
    DesktopCommon.SendScKeys("ENTER")
    time.sleep(1)

def PreNavigateMyFav(args):
    title = DesktopCommon.GetSETitle()
    if title.find("我的最爱") == -1:
	DesktopCommon.NavigateSE("se:favor")


def DoClickOftenURLBtn(args):     # 点击常用网址按钮
    global g_categoryButtonPos
    DesktopCommon.MouseClick(g_categoryButtonPos[0], g_categoryButtonPos[1])
    time.sleep(0.5)

def DoClickMyFavBtn(args):     # 点击我的最爱按钮
    global g_myfavorButtonPos
    DesktopCommon.MouseClick(g_myfavorButtonPos[0], g_myfavorButtonPos[1])
    time.sleep(0.5)

def DoClickNewsBtn(args):     # 点击新闻资讯按钮
    global g_newsButtonPos
    DesktopCommon.MouseClick(g_newsButtonPos[0], g_newsButtonPos[1])
    time.sleep(0.5)

def SwitchToNewsPageAndGetRect():
    DoClickNewsBtn(0)
    DesktopCommon.SendScKeys("LCTRL", "F5")

    pageHwnd = win32gui.FindWindow("SE_AxControl",None)
    if pageHwnd == 0:
	return None
    rect = win32gui.GetWindowRect(pageHwnd)
    return rect

def GenNewsCategoryPos(centerPoint = (0, 0)):
    return (centerPoint[0] - 312 + 114 * GenRandom(5), centerPoint[1] - 158 + 42 * GenRandom(3))

# 刷新频道\订阅频道
def DoSubChannel(args):
    rect = SwitchToNewsPageAndGetRect()
    centerPoint = ((rect[0] + rect[2])/2, (rect[1] + rect[3])/2)

    DesktopCommon.MouseClick(centerPoint[0] + 383, centerPoint[1] - 272)
    DesktopCommon.Sleep(0.5)
    DesktopCommon.MouseClick(centerPoint[0] + 434, centerPoint[1] - 272)
    DesktopCommon.Sleep(0.5)
    DesktopCommon.MouseClick(centerPoint[0] - 424, centerPoint[1] - 142)
    DesktopCommon.Sleep(0.5)
    for i in range(3):
	index = GenRandom(7)
	DesktopCommon.MouseClick(centerPoint[0], rect[1] + 256 + 40 * index)
	DesktopCommon.Sleep(0.5)
    DesktopCommon.MouseClick(centerPoint[0] + 424, centerPoint[1] - 212)

# 拖拽调整频道顺序
def DoDragNewsCategory(args):
    rect = SwitchToNewsPageAndGetRect()
    centerPoint = ((rect[0] + rect[2])/2, (rect[1] + rect[3])/2)

    DesktopCommon.MouseClick(centerPoint[0] + 434, centerPoint[1] - 272)
    DesktopCommon.Sleep(0.5)
    DesktopCommon.MouseClick(centerPoint[0] - 424, centerPoint[1] - 172)
    DesktopCommon.Sleep(0.5)
    for i in range(3):
	index = GenRandom(7)
	startPoint = GenNewsCategoryPos(centerPoint)
	endPoint = GenNewsCategoryPos(centerPoint)
	DesktopCommon.MouseDrag(startPoint[0], startPoint[1], endPoint[0], endPoint[1])
	DesktopCommon.Sleep(0.5)
    deletePoint = GenNewsCategoryPos(centerPoint)
    DesktopCommon.MouseDrag(deletePoint[0], deletePoint[1], centerPoint[0], centerPoint[1] + 212)
    DesktopCommon.Sleep(0.5)
    DesktopCommon.MouseClick(centerPoint[0] + 424, centerPoint[1] - 212)

# 点击新闻资讯的恢复默认
def DoClickDefaultCategory(args):
    rect = SwitchToNewsPageAndGetRect()
    centerPoint = ((rect[0] + rect[2])/2, (rect[1] + rect[3])/2)

    DesktopCommon.MouseClick(centerPoint[0] + 434, centerPoint[1] - 272)
    DesktopCommon.Sleep(0.5)
    DesktopCommon.MouseClick(centerPoint[0] - 374, centerPoint[1] - 172)
    DesktopCommon.Sleep(0.5)
    DesktopCommon.MouseClick(centerPoint[0] + 324, centerPoint[1] - 212)
    DesktopCommon.Sleep(0.5)
    DesktopCommon.MouseClick(centerPoint[0] + 424, centerPoint[1] - 212)

# 在阅读新闻页面内切换类别
def DoClickOtherCategory(args):
    rect = SwitchToNewsPageAndGetRect()
    centerPoint = ((rect[0] + rect[2])/2, (rect[1] + rect[3])/2)

    dx = GenRandom(380, -380)
    dy = GenRandom(170, -170)

    DesktopCommon.MouseClick(centerPoint[0] + dx, centerPoint[1] + dy)
    DesktopCommon.Sleep(0.5)
    DesktopCommon.MouseClick(centerPoint[0], centerPoint[1] - 272)

    DesktopCommon.Sleep(0.5)
    DesktopCommon.MouseClick(centerPoint[0], centerPoint[1] - GenRandom(210))


# 阅读新闻
def DoReadNews(args):
    global g_favorPageWindowText
    rect = SwitchToNewsPageAndGetRect()
    centerPoint = ((rect[0] + rect[2])/2, (rect[1] + rect[3])/2)

    dx = GenRandom(380, -380)
    dy = GenRandom(170, -170)

    DesktopCommon.MouseClick(centerPoint[0] + dx, centerPoint[1] + dy)
    DesktopCommon.Sleep(0.5)
    # 点击刷新
    clickNum = GenRandom(5, 1)
    for i in range(clickNum):
	DesktopCommon.MouseClick(centerPoint[0] + 434, centerPoint[1] - 272)
	DesktopCommon.Sleep(0.5)

    # 点击切换页面
    for i in range(5):
	DesktopCommon.MouseClick(centerPoint[0] + i * 20, centerPoint[1] + 235)
	DesktopCommon.Sleep(0.5)

    # 点击新闻标题
    for i in range(10):
	indexX = GenRandom(2)
	indexY = GenRandom(2)
	DesktopCommon.MouseClick(centerPoint[0] + (indexX - 1) * 290, centerPoint[1] - 225 + 160 * indexY)
	DesktopCommon.Sleep(0.5)
	winText = DesktopCommon.GetSETitle()
	if winText == g_favorPageWindowText: #如果页面没变，返回
	    continue
	else:
	    DesktopCommon.SendScKeys("F2")
	    DesktopCommon.Sleep(0.5)

    # 点击回退
    DesktopCommon.MouseClick(centerPoint[0] - 430, centerPoint[1] - 272)
    DesktopCommon.Sleep(0.5)

#----------------------------------------------------------------------
def DoMouseDragFavorPage(args): #在起始页九宫格中拖拽
    global g_deleteFavorPagesPos
    DoClickMyFavBtn(args)
    count = len(g_deleteFavorPagesPos)

    startPoint = g_deleteFavorPagesPos[GenRandom(count)]
    endPoint = g_deleteFavorPagesPos[GenRandom(count)]
    DesktopCommon.MouseDrag(startPoint[0] - 20,startPoint[1] - 20,endPoint[0] - 20,endPoint[1] - 20)

##    #先随机出拖拽的方向,1,2,3,4分别为左，上，右，下
##    width = g_favorPagesRect[0][0][2] - g_favorPagesRect[0][0][0]
##    height = g_favorPagesRect[0][0][3] - g_favorPagesRect[0][0][1]
##    import random
##    dire = random.randint(1,4)
##    offset = []
##    i = 0
##    j = 0
##    if g_versionFlag == 0:
##	if dire == 1: #left
##	    i = random.randint(0,2)
##	    j = random.randint(1,2)
##	    offset = [0-width, 0]
##	elif dire == 2: #top
##	    i = random.randint(1,2)
##	    j = random.randint(0,2)
##	    offset = [0, 0-height-45]
##	elif dire == 3: #right
##	    i = random.randint(0,2)
##	    j = random.randint(0,1)
##	    offset = [width, 0]
##	elif dire == 4: #down
##	    i = random.randint(0,1)
##	    j = random.randint(0,2)
##	    offset = [0, height+45]
##    elif g_versionFlag  == 1:
##	if dire == 1: #left
##	    i = random.randint(0,1)
##	    j = random.randint(1,3)
##	    offset = [0-width, 0]
##	elif dire == 2: #top
##	    i = 1
##	    j = random.randint(0,3)
##	    offset = [0, 0-height-45]
##	elif dire == 3: #right
##	    i = random.randint(0,1)
##	    j = random.randint(0,2)
##	    offset = [width, 0]
##	elif dire == 4: #down
##	    i = 0
##	    j = random.randint(0,3)
##	    offset = [0, height+45]
##    rect = g_favorPagesRect[i][j]
##    centerPoint = [(rect[2]-rect[0])/2+rect[0],(rect[3]-rect[1])/2+rect[1]]
##    DesktopCommon.MouseDrag(centerPoint[0],centerPoint[1],centerPoint[0]+offset[0],centerPoint[1]+offset[1])
##    time.sleep(1)



#----------------------------------------------------------------------
def DoModifyFavorPage(args): #修改九宫格中的我的最爱页面
    global g_favorPagesRect, g_versionFlag, g_setFavorPagesPos, g_urlList
    import random
    import copy
    import win32ui
    i = 0
    j = 0
    rect = [0,0]
    p = []
    if g_versionFlag == 0:
	i = random.randint(0,2)
	j = random.randint(0,2)
	rect = g_favorPagesRect[i][j]
	offset = [-43, 13] #修改图标相对右上角的偏移量
	p.append(rect[2]+offset[0])
	p.append(rect[1]+offset[1])
    elif g_versionFlag == 1:
	i = random.randint(0,1)
	j = random.randint(0,3)
	rect = g_favorPagesRect[i][j]
	offset = [-35, 20] #修改图标相对右下角的偏移量
	p.append(rect[2]+offset[0])
	p.append(rect[3]+offset[1])
    elif g_versionFlag == 2:
	i = random.randint(0, 11)
	p = copy.deepcopy(g_setFavorPagesPos[i])
	DoClickMyFavBtn(args)

    win32api.SetCursorPos(p)
    DesktopCommon.MouseClick(p[0], p[1])

    # 处理弹出的对话框
    EditDialogOperation()

def IsMousePosLink(x,y):
    cursorInfo = win32gui.GetCursorInfo()
    return cursorInfo[1] == 65581

def DoSearchPic(args):
    f = open(args[0])
    urls = []
    if len(args)<5:
	xstart = 250
	ystart = 200
	xinterval = 170
	yinterval = 190
    else:
	xstart = args[1]
	ystart = args[2]
	xinterval = args[3]
	yinterval = args[4]
    for line in f:
	urls.append(line.strip())
    f.close()
    idx = GenRandom(len(urls)-1)
    url = "http://pic.sogou.com/pics?query="+urls[idx]
    DesktopCommon.StartSE(url)
    wndPosInfo = DesktopCommon.GetWndPosEx("SE_AxControl")
    xstart = wndPosInfo[0]+xstart
    ystart = wndPosInfo[1]+ystart
    for row in range(3):
	startx = xstart
	for col in range(7):
	    DesktopCommon.MouseTo(startx,ystart)
	    #if IsMousePosLink(startx,ystart):
	    time.sleep(3.5)
	    startx += xinterval
	ystart = ystart+yinterval



#----------------------------------------------------------------------
def DoDeleteFavorPage(args): #删除九宫格中的我的最爱页面
    global g_favorPagesRect, g_versionFlag, g_deleteFavorPagesPos, g_urlList
    import random
    import copy
    i = 0
    j = 0
    rect = [0,0]
    p = []
    if g_versionFlag == 0:
	i = random.randint(0,2)
	j = random.randint(0,2)
	rect = g_favorPagesRect[i][j]
	offset = [-15, 13] #修改图标相对右上角的偏移量
	p.append(rect[2]+offset[0])
	p.append(rect[1]+offset[1])
    elif g_versionFlag == 1:
	i = random.randint(0,1)
	j = random.randint(0,3)
	rect = g_favorPagesRect[i][j]
	offset = [-12, 20] #修改图标相对右下角的偏移量
	p.append(rect[2]+offset[0])
	p.append(rect[3]+offset[1])
    elif g_versionFlag == 2:
	i = random.randint(0,11)
	p = copy.deepcopy(g_deleteFavorPagesPos[i])
	DoClickMyFavBtn(args)
    win32api.SetCursorPos(p)
    DesktopCommon.MouseClick(p[0], p[1])

    # 处理弹出的对话框
    EditDialogOperation()

#----------------------------------------------------------------------
##@函数目的: 处理弹出的“我的最爱”设置框
##@参数说明：editWindowHandle为主窗体的句柄值
##@返回值：
##@函数逻辑：设置两个文本框为随机的url
def EditDialogOperation():
    global g_versionFlag, g_urlList

    editWindowHandle = DesktopCommon.GetHandle("#32770","“我的最爱”设置", 2)
    if editWindowHandle == 0:
	return
    if g_versionFlag != 2:
	winRect = win32gui.GetWindowRect(editWindowHandle)
	xStart = winRect[0] + 135
	yStart = winRect[1] + 155
	height = 22
	index = random.randint(1,10)
	y = yStart + 22/2 + (index-1)*22
	DesktopCommon.MouseClick(xStart,y)
	time.sleep(0.2)
	DesktopCommon.SendScKeys("ENTER")
	time.sleep(0.1)
    else:
	tempURL = g_urlList[random.randint(0, len(g_urlList) - 1)]

	childWindows = []
	DesktopCommon.EnumAllChildWindows(editWindowHandle, childWindows, 3)
	for childWindowInfo in childWindows:
	    if childWindowInfo[1] == "Edit":
		editURLWnd = win32ui.FindWindowEx(editWindowHandle, None, "Edit", None)
		editURLWnd.SendMessage(win32con.WM_SETTEXT, tempURL)

		editTitleWnd = win32ui.FindWindowEx(editWindowHandle, childWindowInfo[0], "Edit", None)
		editTitleWnd.SendMessage(win32con.WM_SETTEXT, "1")
		break
	time.sleep(0.2)
	handle = DesktopCommon.GetHandle("#32770", "“我的最爱”设置", 2)
	DesktopCommon.ClickCtrlEx(handle, "Button", "确定")


#----------------------------------------------------------------------
def DoFavorPagePostAction(args):
    global g_favorPageWindowText
    seui = win32gui.FindWindow("SE_SogouExplorerFrame",None)
    if seui != 0:
	try:
	    win32gui.SetForegroundWindow(seui)
	    win32gui.SetActiveWindow(seui)
	except:
	    None
	winText = win32gui.GetWindowText(seui)
	if winText == g_favorPageWindowText: #如果页面没变，返回
	    return
	else:
	    DesktopCommon.SendScKeys("LCTRL","LSHIFT","w")
	    time.sleep(1)
	    DesktopCommon.Navigate("se://favor.sogou.com/")
	    time.sleep(2)
    else:
	DesktopCommon.StopSE()
	time.sleep(1)
	DesktopCommon.StartSE()
	time.sleep(2)
	DesktopCommon.Navigate("se://favor.sogou.com/")
	time.sleep(2)



#----------------------------------------------------------------------
def AddUrlToFavByFavManager(point,caption,url):  #通过菜单栏添加收藏项
    if url == "":
	return
    DesktopCommon.MouseClick(point[0], point[1])
    time.sleep(1)
    DesktopCommon.MouseClick(point[0], point[1] + 25)
    AddUrlToFav(str(caption), str(url))

#----------------------------------------------------------------------
def EditFavUrlByFavManager(p1,p2,caption): #通过菜单栏编辑收藏项
    if caption == "":
	return
    DesktopCommon.MouseClick(p2[0], p2[1])
    time.sleep(0.5)
    DesktopCommon.MouseClick(p1[0], p1[1])
    EditFavUrl(caption)


#----------------------------------------------------------------------
def DeleteFavUrlByFavManager(p1,p2): #通过菜单栏删除收藏项
    DesktopCommon.MouseClick(p2[0], p2[1])
    time.sleep(0.5)
    DesktopCommon.MouseClick(p1[0], p1[1])
    time.sleep(1)
    DesktopCommon.SendScKeys("ENTER")



#----------------------------------------------------------------------
def AddUrlToFavByFavBar(caption, url):  #通过收藏栏添加收藏项
    if url == "":
	return
    seui = win32gui.FindWindow("SE_SogouExplorerFrame",None)
    favHwnd = DesktopCommon.SearchSubWindowByClassName(seui,"SE_TuotuoFavoriteBar")
    if favHwnd == 0:
	return
    rect = win32gui.GetWindowRect(favHwnd)
    x = rect[0]+ 68
    y = rect[1] + 10
    DesktopCommon.MouseClick(x, y)
    time.sleep(1)
    DesktopCommon.SendScKeys("a")
    time.sleep(1)
    AddUrlToFav(str(caption), str(url))


#----------------------------------------------------------------------
def EditFavUrlByFavBar(caption): #通过收藏栏编辑收藏项
    if caption == "":
	return
    seui = win32gui.FindWindow("SE_SogouExplorerFrame",None)
    favHwnd = DesktopCommon.SearchSubWindowByClassName(seui,"SE_TuotuoFavoriteBar")
    if favHwnd == 0:
	return
    rect = win32gui.GetWindowRect(favHwnd)
    x = rect[0] + 120
    y = rect[1] + 10

    DesktopCommon.MouseClick(x, y, "RIGHT")
    time.sleep(1)
    DesktopCommon.SendScKeys("e")
    EditFavUrl(caption)


#----------------------------------------------------------------------
def DeleteFavUrlByFavBar(): #通过收藏栏删除收藏项
    seui = win32gui.FindWindow("SE_SogouExplorerFrame",None)
    favHwnd = DesktopCommon.SearchSubWindowByClassName(seui,"SE_TuotuoFavoriteBar")
    if favHwnd == 0:
	return
    rect = win32gui.GetWindowRect(favHwnd)
    x = rect[0] + 120
    y = rect[1] + 10

    DesktopCommon.MouseClick(x, y, "RIGHT")
    time.sleep(1)
    DesktopCommon.SendScKeys("d")
    time.sleep(1)
    DesktopCommon.SendScKeys("ENTER")
    time.sleep(1)




def AddUrlToFav(caption="空白页", url="about:blank"): #添加收藏项对话框
    time.sleep(1)
    favHwnd = win32gui.FindWindow(None,"添加到收藏夹")
    if favHwnd == 0:
	return
    try:
	win32gui.SetForegroundWindow(favHwnd)
	win32gui.SetActiveWindow(favHwnd)
    except:
	None
    DesktopCommon.ClickOnHandle(favHwnd, 140, 110)
    DesktopCommon.CtrlV(str(caption)) #设置标题
    time.sleep(0.5)
    DesktopCommon.ClickOnHandle(favHwnd, 140, 140)
    DesktopCommon.CtrlV(str(url))
    time.sleep(0.5)
    DesktopCommon.SendScKeys("ENTER")
    try:
	handle = win32gui.FindWindow("#32770","确认")
	if handle!=0:
	    DesktopCommon.SendScKeys("ENTER")
    except:
	None
    time.sleep(1)



#----------------------------------------------------------------------
def DoDragFavItem(args):  #拖动收藏项
    count = args[0] #参数 执行次数

    #菜单栏
    SeSmoke.ClickSEMenuBar(186, 8)
    time.sleep(1)
    DesktopCommon.SendScKeys("m")
    time.sleep(1)
    hwnd = win32gui.FindWindow(None,"整理收藏夹")
    if hwnd == 0:
	return
    rect = win32gui.GetWindowRect(hwnd)
    p_create = []
    p_create.append(rect[0] + 20)
    p_create.append(rect[1] + 40)
    p_edit = []
    p_edit.append(rect[0] + 60)
    p_edit.append(rect[1] + 40)
    p_delete = []
    p_delete.append(rect[0] + 100)
    p_delete.append(rect[1] + 40)
    p_click = []
    p_click.append(rect[0] + 400)
    p_click.append(rect[1] + 85)

    #添加几个收藏项
    AddUrlToFavByFavManager(p_create,"搜狗","http://www.sogou.com/")
    AddUrlToFavByFavManager(p_create,"搜狐","http://www.sohu.com/")
    AddUrlToFavByFavManager(p_create,"谷歌","http://www.google.com.hk/")
    AddUrlToFavByFavManager(p_create,"新浪","http://www.sina.com.cn/")
    AddUrlToFavByFavManager(p_create,"百度","http://www.baidu.com/")

    for i in xrange(count):
	win32api.SetCursorPos(p_click)
	DesktopCommon.MouseDown()
	time.sleep(0.5)
	win32api.mouse_event(win32con.MOUSEEVENTF_MOVE, 0, 100, 0, 0)
	time.sleep(0.5)
	DesktopCommon.MouseUp()
	time.sleep(1)

    DesktopCommon.MouseClick(rect[0] + 200, rect[1] + 15, "RIGHT")
    time.sleep(1)
    DesktopCommon.SendScKeys("c") #关闭收藏夹管理对话框

# 使用CTRL+F W新建窗口
# 通过拖拽标签新建窗口
def DoCreateNewWindow(args):
    flag = GenRandom(2)
    DoNavigate(args)
    if flag == 0:
	SeSmoke.ClickSEMenuBar(76, 8)
	time.sleep(0.2)
	DesktopCommon.SendScKeys("w")
    else:
	mainHandle = GetHandle()
	if mainHandle == 0:
	    return
	MaximizeWnd(mainHandle)
	rect = GetRect(mainHandle, "SE_TuotuoTabCtrl")
	DesktopCommon.MouseTo(rect[0] + 155, rect[1] + 10)
	time.sleep(0.5)
	DesktopCommon.MouseDown()
	time.sleep(0.5)
	DesktopCommon.MouseTo(200, 400)
	time.sleep(0.5)
	DesktopCommon.MouseUp()
    # 保留一个浏览器页面
    seHandles = DesktopCommon.GetWndHandles("SE_SogouExplorerFrame")
    seHandles.pop(0)
    if seHandles != None and len(seHandles) > 1:
	for h in seHandles:
	    win32api.PostMessage(h[0], win32con.WM_CLOSE, 0, 0)

# 打开账户注册页面
def DoRegUser(args):
    SeSmoke.ClickSEMenuBar(15, 8)
    time.sleep(0.5)
    DesktopCommon.SendScKeys("r")

# 新建剪贴板中的地址
def DoCreateFromPasteBoard(args):
    url = GetUrl(args[0])
    DesktopCommon.CtrlC(url)
    time.sleep(1)
    flag = GenRandom(2)
    if flag == 0:
	SeSmoke.ClickSEMenuBar(76, 8)
	time.sleep(0.5)
	DesktopCommon.SendScKeys("n")
	time.sleep(0.5)
	DesktopCommon.SendScKeys("b")
    else:
	DesktopCommon.SendScKeys("CTRL", "SHIFT", "c")

#新建“复制当前页”
def DoCopyCurrentPage(args):
    DoNavigate(args)
    time.sleep(1)
    SeSmoke.ClickSEMenuBar(76, 8)
    time.sleep(0.5)
    DesktopCommon.SendScKeys("n")
    time.sleep(0.5)
    DesktopCommon.SendScKeys("c")

# 新建“主页”
def DoCreateMainPage(args):
    SeSmoke.ClickSEMenuBar(76, 8)
    time.sleep(0.5)
    DesktopCommon.SendScKeys("n")
    time.sleep(0.5)
    DesktopCommon.SendScKeys("h")

# 新建“小号窗口”
def DoCreateSmallWindow(args):
    SeSmoke.ClickSEMenuBar(76, 8)
    time.sleep(0.5)
    DesktopCommon.SendScKeys("n")
    time.sleep(0.5)
    DesktopCommon.SendScKeys("m")

# 保存网页
def DoSaveHtml(args):
    flag = GenRandom(2)
    path = os.path.join(tempfile.gettempdir(), "dosavehtml_temp.htm")
    if os.path.exists(path):
	os.remove(path)

    # 等待页面加载
    time.sleep(3)
    if flag == 0:
	SeSmoke.ClickSEMenuBar(76, 8)
	time.sleep(0.3)
	DesktopCommon.SendScKeys("s")
	time.sleep(0.3)
    else:
	DesktopCommon.SendScKeys("CTRL", "s")

    mainHandle = GetHandle("#32770", "保存网页", 2)
    if mainHandle == 0:
	mainHandle = GetHandle("#32770", "另存为", 2)
    if mainHandle != 0:
	DesktopCommon.SetCtrlTextEx(mainHandle, "Edit", None, path)
	time.sleep(0.2)
	DesktopCommon.ClickCtrlEx(mainHandle, "Button", "保存(&S)")
	time.sleep(2)
    DesktopCommon.SendScKeys("ENTER")
    DesktopCommon.SendScKeys("ESC")

# 另存为图片
def DoSaveHtmlToPic(args):
    pos = random.sample([".gif", ".jpg", ".jpeg", ".png", ".bmp"], 1)[0]
    path = os.path.join(tempfile.gettempdir(), "DoSaveHtmlToPic_temp" + pos)
    if os.path.exists(path):
	os.remove(path)

    mainHandle = GetHandle()
    if mainHandle != 0:
	childHandle = DesktopCommon.GetChildHandle(mainHandle, "SE_TuotuoMenuBar")
	rect = win32gui.GetWindowRect(childHandle)
	if rect != None:
	    DesktopCommon.MouseClick(rect[0] + 90, rect[1] + 10)
	    time.sleep(0.5)
	    DesktopCommon.MouseClick(rect[0] + 122, rect[1] + 140)

	    # 保存
	    dialogHandle = GetHandle("#32770", "另存为", 2)
	    if dialogHandle != 0:
		DesktopCommon.SetCtrlTextEx(dialogHandle, "Edit", None, path)
		time.sleep(0.3)
		DesktopCommon.ClickCtrlEx(dialogHandle, "Button", "保存(&S)")
		time.sleep(0.2)
		DesktopCommon.SendScKeys("ENTER")

# 打开文件
def DoOpenFile(args):
    # 先放在这里吧，后面可以放到文件中
    urls = ["http://pic1a.nipic.com/2009-02-26/200922601527648_2.gif", "http://pic4.nipic.com/20091116/3285852_152113093591_2.jpg", "http://10.11.195.211/smoketest/file/file_datapack1_3.1.txt", "http://10.11.195.211/smoketest/corechoose_files/online.aw", "http://www.sohu.com/", "http://www.baidu.com/", "http://www.sina.com/"]
    url = random.sample(urls, 1)[0]

    DesktopCommon.SendScKeys("CTRL", "o")
    dialogHandle = GetHandle("#32770", "打开")
    if dialogHandle != 0:
	DesktopCommon.SetCtrlTextEx(dialogHandle, "Edit", None, url)
	time.sleep(0.5)
	DesktopCommon.ClickCtrlEx(dialogHandle, "Button", "打开(&O)")
	time.sleep(3)

# 查看页面属性
def DoViewPageProperty(args):
    flag = GenRandom(1)
    if flag == 0:
	SeSmoke.ClickSEMenuBar(76, 8)
	time.sleep(0.3)
	DesktopCommon.SendScKeys("r")
	time.sleep(0.2)
	DesktopCommon.SendScKeys("r")
    else:
	mainHandle = GetHandle("SE_AxControl")
	if mainHandle != 0:
	    rect = win32gui.GetWindowRect(mainHandle)
	    DesktopCommon.MouseClick(rect[0] + 58, rect[1] + 147, "RIGHT")
	    time.sleep(0.2)
	    DesktopCommon.SendScKeys("p")
	    time.sleep(0.2)

# 脱机工作
def DoOfflineWork(args):
    SeSmoke.ClickSEMenuBar(76, 8)
    time.sleep(0.3)
    DesktopCommon.SendScKeys("g")
    time.sleep(0.2)
    DesktopCommon.SendScKeys("g")

# 锁定工具栏
def DoLockToolBar(args):
    flag = GenRandom(1)
    if flag == 0:
	SeSmoke.ClickSEMenuBar(135, 8)
	time.sleep(0.5)
	DesktopCommon.SendScKeys("t")
	time.sleep(0.5)
	DesktopCommon.SendScKeys("l")
    else:
	handle = GetHandle("SE_SogouExplorerFrame")
	if handle != 0:
	    rect = win32gui.GetWindowRect(handle)
	    DesktopCommon.MouseClick(rect[0] + 500, rect[1] + 10, "RIGHT")
	    time.sleep(0.5)
	    DesktopCommon.SendScKeys("l")

# 无痕浏览
def DoTrackManager(args):
    seui = win32gui.FindWindow("SE_SogouExplorerFrame",None)
    statusHwnd = DesktopCommon.SearchSubWindowByClassName(seui,"SE_TuotuoStatusbarToolbar")
    if statusHwnd == 0:
	return
    rect = win32gui.GetWindowRect(statusHwnd)
    DesktopCommon.MouseClick(rect[0] + 162, rect[1] + 13)
    time.sleep(0.5)
    DesktopCommon.MouseClick(rect[0] + 178, rect[1] + 13)
    time.sleep(0.5)
    DesktopCommon.SendScKeys("ESC")

# 查看源代码
def DoViewSource(args):
    rect = DesktopCommon.GetRectByHandle(GetSE_AxControl())
    x = random.randint(50, 100)
    y = random.randint(100, 400)
    DesktopCommon.MouseClick(rect[0] + x, rect[1] + y, "RIGHT")
    time.sleep(0.5)
    DesktopCommon.SendScKeys("v")

# 设置文字大小
def DoSetFontSize(args):
    SeSmoke.ClickSEMenuBar(135, 8)
    time.sleep(0.5)
    DesktopCommon.SendScKeys("x")
    size = random.sample(["g", "l", "s", "m", "a"], 1)[0]
    time.sleep(0.5)
    DesktopCommon.SendScKeys(size)

# 清除浏览记录
def DoClearNavigateHistory(args):
    SeSmoke.ClickSEMenuBar(237, 8)
    time.sleep(0.5)
    DesktopCommon.SendScKeys("d")
    time.sleep(2)
    handle = GetHandle("#32770", "清除浏览记录", 5)
    if handle == 0:
	return
    tempnum = GenRandom(7, 1)
    lists = random.sample(["网页缓存","Cookies","历史记录","最近关闭","下拉列表","下载记录","表单"], tempnum)
    for name in lists:
	DesktopCommon.ClickCtrlEx(handle, "Button", name)
	time.sleep(0.5)
    DesktopCommon.ClickCtrlEx(handle, "Button", "立即清除")
    DesktopCommon.ClickCtrlEx(handle, "Button", "关闭")

# 查看过滤结果并清空列表
def DoViewFilterResult(args):
    SeSmoke.ClickSEMenuBar(237, 8)
    time.sleep(0.5)
    DesktopCommon.SendScKeys("a")
    time.sleep(0.5)
    DesktopCommon.SendScKeys("h")
    time.sleep(2)
    handle = GetHandle("#32770", "广告过滤记录", 5)
    if handle == 0:
	return
    DesktopCommon.ClickCtrlEx(handle, "Button", "清空列表")
    time.sleep(1)
    win32gui.SendMessage(handle, win32con.WM_CLOSE, 0, 0)

# 开启或关闭窗口拦截
def DoOpenBlocker(args):
    SeSmoke.ClickSEMenuBar(237, 8)
    time.sleep(0.5)
    DesktopCommon.SendScKeys("a")
    time.sleep(0.5)
    DesktopCommon.SendScKeys("p")
    time.sleep(1)

# 开启或关闭ActiveX安装提示
def DoOpenActiveX(args):
    SeSmoke.ClickSEMenuBar(237, 8)
    time.sleep(0.5)
    DesktopCommon.SendScKeys("a")
    time.sleep(0.5)
    DesktopCommon.SendScKeys("x")
    time.sleep(1)

# 设置用户体验改进计划
def DoUserExpModify(args):
    SeSmoke.ClickSEMenuBar(286, 8)
    time.sleep(0.5)
    DesktopCommon.SendScKeys("e")

    handle = DesktopCommon.GetHandle("#32770", "用户体验改进计划", 5)
    if handle == 0:
	return
    DesktopCommon.ClickCtrlEx(handle, "Button", "我愿意帮助改善搜狗高速浏览器的产品体验")
    DesktopCommon.ClickCtrlEx(handle, "Button", "确定")

# 查找SE_AxControl的句柄；去除后台SE_AxControl的影响
def GetSE_AxControl():
    windows = DesktopCommon.GetWndHandles("SE_AxControl", None)
    for window in windows:
	rect = win32gui.GetWindowRect(window[0])
	if rect[0] < 500 and rect[0] >= 0:
	    return window[0]
    return 0

# 基本的登录方式
def NavigateAndLogin(url = "http://passport.tianya.cn/login.jsp", dx = 474, dy = 172, user = "setest0001", pwd = "asdf123", checked = True):
    DoClcikURL(url, dx, dy)
    time.sleep(0.5)
    DesktopCommon.SendScKeys("LCTRL", "a")
    time.sleep(0.5)
    if url.find("58") != -1:
	for i in range(len(user)):
	    DesktopCommon.SendScKeys("BACKSPACE")
	    time.sleep(0.3)
    DesktopCommon.inputOneLine(user)
    time.sleep(0.5)
    DesktopCommon.SendScKeys("TAB")
    time.sleep(0.5)
    DesktopCommon.SendScKeys("LCTRL", "a")
    time.sleep(0.5)
    DesktopCommon.inputOneLine(pwd)
    time.sleep(0.5)
    DesktopCommon.SendScKeys("TAB")
    time.sleep(0.5)
    if checked:
	DesktopCommon.SendScKeys("SPACE")
	time.sleep(0.5)
    DesktopCommon.SendScKeys("TAB")
    time.sleep(0.5)
    DesktopCommon.SendScKeys("ENTER")

# 点击网页的某个偏移的位置
def DoClcikURL(url, dx = 0, dy = 0):
    DesktopCommon.CreateTabNav(url)
    time.sleep(3)
    handle = GetSE_AxControl()
    if handle == 0:
	return
    rect = win32gui.GetWindowRect(handle)
    DesktopCommon.MouseClick(rect[0] + dx, rect[1] + dy)

# 登录天涯
def DoLoginTianya(args):
    NavigateAndLogin("http://passport.tianya.cn/login.jsp", 474, 172, "setest0001", "asdf123", True)

# 登录百度
def DoLoginBaidu(args):
    NavigateAndLogin("https://passport.baidu.com/v2/?login&tpl=mn", 1024, 133, "sogoutest123", "asdf123", True)

# 登录搜狐
def DoLoginSohu(args):
    DoClcikURL("http://mail.sohu.com/", 529, 15)
    NavigateAndLogin("http://mail.sohu.com/", 844, 197, "setest001", "sohutest", False)

# 登录58同城
def DoLogin58tongcheng(args):
    DoClcikURL("https://passport.58.com/login", 839, 13)
    NavigateAndLogin("https://passport.58.com/login", 978, 176, "setest001", "asdf123", False)

# 点击保存按钮
def SaveTableInfo():
    handle = GetSE_AxControl()
    if handle == 0:
	return
    seTuoTopTipHandle = DesktopCommon.GetWindowHandle("SGDUI", None, None, 3)
    if seTuoTopTipHandle == 0:
	return
    DesktopCommon.ClickOnHandle(seTuoTopTipHandle, 1179, 23)

# 登录网站
def DoLoginWeb(args):
    flag = GenRandom(3)
    if flag == 0:
	DoLoginTianya(args)
    elif flag == 1:
	DoLoginSohu(args)
    elif flag == 2:
	DoLoginSohu(args)
    else:
	DoLogin58tongcheng(args)

# 智能填表管理器-自动保存表单
def DoSaveTableInfo(args):
    DoLoginWeb(args)
    handle = GetSE_AxControl()
    if handle == 0:
	return
    time.sleep(1)
    seTuoTopTipHandle = DesktopCommon.GetWindowHandle("SGDUI", None, None, 3)
    if seTuoTopTipHandle == 0:
	return

    flag = GenRandom(2)
    if flag == 0:
	DesktopCommon.ClickOnHandle(seTuoTopTipHandle, 1179, 23)
    elif flag == 1:
	DesktopCommon.ClickOnHandle(seTuoTopTipHandle, 1240, 23)
    else:
	DesktopCommon.ClickOnHandle(seTuoTopTipHandle, 1420, 23)

# 智能填表选项设置
def DoSetTableManager(args):
    handle = InvokeBrowseOptionDlg(50, 366)
    options = ["显示密码保存提示", "自动填写已保存表单", "在同级域名之外模糊填写表单"]

    # 随机选择1-3项进行点击
    num = GenRandom(3, 1)
    tempOptions = random.sample(options, num)
    for tempName in tempOptions:
	DesktopCommon.ClickCtrlEx(handle, "Button", tempName)
	time.sleep(0.6)
    DesktopCommon.ClickCtrlEx(handle, "Button", "确定")

# 智能填表管理器-删除已保存表单
def DoTableManagerDeleteTableInfo(args):
    handle, rect = ShowAndGetTableManager()
    if rect == None:
	return
    num = GenRandom(3)
    for i in range(num):
	DesktopCommon.MouseClick(rect[0] + 90, rect[1] + 251, "RIGHT")
	time.sleep(0.5)
	DesktopCommon.MouseClick(rect[0] + 100, rect[1] + 255)
	time.sleep(0.5)
	DesktopCommon.SendScKeys("ENTER")
    win32gui.SendMessage(handle, win32con.WM_CLOSE, 0, 0)

# 智能填表管理器-自动填写/手动填写
def DoTableManagerWriteTable(args):
    flag = GenRandom(3)
    url = ""
    dx = 474
    dy = 172
    if flag == 0 or flag == 1:
	DoLogin58tongcheng(args)
	url = "https://passport.58.com/login"
	dx = 1000
	dy = 215
    elif flag == 2:
	DoLoginSohu(args)
	url = "http://mail.sohu.com/"
	dx = 844
	dy = 197
    else:
	DoLoginTianya(args)
	url = "http://passport.tianya.cn/login.jsp"
    SaveTableInfo()
    time.sleep(0.5)
    if flag == 0:
	DoClcikURL("https://passport.58.com/login", 839, 13)
    elif flag == 2:
	DoClcikURL("http://mail.sohu.com/", 529, 15)
    DesktopCommon.CreateTabNav(url)
    time.sleep(3)
    DesktopCommon.SendScKeys("LALT", "q")
    handle = GetSE_AxControl()
    if handle == 0:
	return
    rect = win32gui.GetWindowRect(handle)
    DesktopCommon.MouseClick(rect[0] + dx, rect[1] + dy)
    time.sleep(0.5)
    for i in range(3):
	DesktopCommon.SendScKeys("TAB")
	time.sleep(0.5)
    DesktopCommon.SendScKeys("ENTER")

# 打开Flash加速
def DoOpenFlashAcc(args):
    handle = InvokeBrowseOptionDlg(50, 200)
    DesktopCommon.ClickCtrlEx(handle, "Button", "开启Flash加速功能")
    DesktopCommon.ClickCtrlEx(handle, "Button", "确定")

# 打开视频加速
def DoOpenVideoAcc(args):
    handle = InvokeBrowseOptionDlg(50, 466)
    DesktopCommon.ClickCtrlEx(handle, "Button", "开启视频加速")
    DesktopCommon.ClickCtrlEx(handle, "Button", "确定")

# 打开全网加速、Flash加速、视频加速功能
def DoOpenAcc(args):
    configPath = os.path.join(os.environ["appdata"], r"SogouExplorer\config.xml")
    commcfgPath = os.path.join(os.environ["appdata"], r"SogouExplorer\CommCfg.xml")
    flashacc = DesktopCommon.GetXmlAttribute(configPath, "flashacc")
    if flashacc.lower() != "true":
	DoOpenFlashAcc(args)
    webacc = DesktopCommon.GetXmlAttribute(commcfgPath, "webacc")
    if webacc.lower() != "true":
	DoTurnOnAcc(args)
    videoacc = DesktopCommon.GetXmlAttribute(commcfgPath, "videoacc")
    if videoacc.lower() != "true":
	DoOpenVideoAcc(args)

# 关闭全网加速、Flash加速、视频加速功能
def DoCloseAcc(args):
    configPath = os.path.join(os.environ["appdata"], r"SogouExplorer\config.xml")
    commcfgPath = os.path.join(os.environ["appdata"], r"SogouExplorer\CommCfg.xml")
    flashacc = DesktopCommon.GetXmlAttribute(configPath, "flashacc")
    if flashacc.lower() != "false":
	DoOpenFlashAcc(args)
    webacc = DesktopCommon.GetXmlAttribute(commcfgPath, "webacc")
    if webacc.lower() != "false":
	DoTurnOffAcc(args)
    videoacc = DesktopCommon.GetXmlAttribute(commcfgPath, "videoacc")
    if videoacc.lower() != "false":
	DoOpenVideoAcc(args)


#----------------------------------------------------------------------
def DoClickUpdateMsgBox(args): #点击更新快递消息盒子
    count = args[0] #执行次数
    seui = win32gui.FindWindow("SE_SogouExplorerFrame",None)
    statusHwnd = DesktopCommon.SearchSubWindowByClassName(seui,"SE_TuotuoStatusbarToolbar")
    if statusHwnd == 0:
	return
    rect = win32gui.GetWindowRect(statusHwnd)
    x = rect[0] + 10
    y = rect[1] + 10
    for i in xrange(int(count)):
	DesktopCommon.MouseClick(x, y)
	time.sleep(1)
	DesktopCommon.MouseClick(x, y)
	time.sleep(1)



#----------------------------------------------------------------------
def DoFinishPreSogouRankData(args):  #完成准备SogouRank的数据
    seui = win32gui.FindWindow("SE_SogouExplorerFrame",None)
    rect = win32gui.GetWindowRect(seui)
    x = rect[2] - 20
    y = rect[1] + 10
    DesktopCommon.MouseClick(x, y)
    time.sleep(6) #等待进程关闭
    DesktopCommon.SetForegroundOpenNewTab(False) #设置后台打开标签
    DesktopCommon.StartSE()
    time.sleep(2)
    DesktopCommon.Navigate("http://123.sogou.com/")
    time.sleep(3)
    DesktopCommon.SendScKeys("PAGEDOWN")
    time.sleep(1)


#----------------------------------------------------------------------
def DoSetSEForeground(args):
    seui = win32gui.FindWindow("SE_SogouExplorerFrame",None)
    if seui == 0:
	return
    try:
	win32gui.SetForegroundWindow(seui)
	win32gui.SetActiveWindow(seui)
    except:
	None



#----------------------------------------------------------------------
def DoPreSogouRankTest(args): #预制操作
    favPath = args[0] #fav 数据库
    dynPath = args[1] #更新盒子数据库
    DesktopCommon.StopProcess('SogouExplorer.exe')
    DesktopCommon.CopyFileToSEAppData(str(favPath))
    DesktopCommon.CopyFileToSEAppData(str(dynPath))
    time.sleep(1)
    DesktopCommon.StartSE()
    time.sleep(2)

def CloseAllTabExceptFirst():
    idx = 0
    while idx<100 and SeSmoke.GetSETabCount()>1:
        DesktopCommon.SendScKeys("LCTRL","w")
        DesktopCommon.Sleep(1)
        idx += 1

#---------------------------------------------
def ClearEnv():
    #清理环境
    fwpath = DesktopCommon.GetFrameworkPath()
    tempdir = fwpath + "\\temp"
    newdownloaddir = fwpath + "\\temp\\download"
    try:
	if os.path.exists(tempdir):
	    files = os.listdir(tempdir)
	    for fname in files:
		if fname.find(".zip")!= -1 or fname.find(".exe")!=-1 or fname.find(".msi")!=-1 or fname.find(".rar")!=-1:
		    fullname = os.path.join(tempdir,fname)
		    DesktopCommon.Delete(fullname)
	DesktopCommon.Rmdir(newdownloaddir)
    except:
	None

def StartTest(time_s):
    global g_start_time,g_end_time
    g_start_time = GetStanderTime()
    beginTime = win32api.GetTickCount()
    pm = ProbManager()
    pm.funcAndParamMap = g_funcAndParamMap
    pm.GenerateProbilityDistribution()  #生成概率分布
    AddPreAction("PreCloseGarbageWnd")
    GetOriWnds()
    ClearEnv()
    while win32api.GetTickCount() - beginTime < time_s * 1000:
        action = pm.GenNextAction()
        DoPreAction()
        CallFunc(g_funcAndParamMap,action)
	LogCrash("action:%s" % action)
        DoPostAction()
    g_end_time = GetStanderTime()
    InsertLogToDB()

def InPassportStartTest(time_s):
    beginTime = win32api.GetTickCount()
    while win32api.GetTickCount()-beginTime < time_s*1000:
        action = GenNextAction()
	if action.find("Passport")!=-1:
	    #通行证有关的操作屏蔽掉
	    continue
        DoPreAction()
        CallFunc(g_funcAndParamMap,action)
        DoPostAction()

# 设置进程启动权限级别
def SetSecurity(security = ""):
    global g_processSecurity
    g_processSecurity = security


def Printb(args):
    print args[0]


def Printc(args):
    print "hc"

def Print(args):
    print 'hp'

def Printd(args):
    print 'hd'


# 在网页中点击右键
def DoClickRightMouse(args):
    handle = GetSE_AxControl()
    rect = win32gui.GetWindowRect(handle)

    for i in range(10):
	x = GenRandom(rect[2], rect[0])
	y = GenRandom(rect[3], rect[1])
	DesktopCommon.MouseClick(x, y, "RIGHT")
	time.sleep(1)

def ClickMenu(dx, dy, *keys):
    SeSmoke.ClickSEMenuBar(dx, dy)
    for key in keys:
	DesktopCommon.SendScKeys(key)
	DesktopCommon.Sleep(0.5)

def DoClickMenuRandom(args):
    x = 26
    y = 8
    dx = 50

    keys = (("i", "r"), ("t", "w", "o", "s", "f", "z", "p", "r", "g", "c", "a"), ("r", "q", "a", "p", "o", "c", "h"), ("a", "b", "n", "m"), ("k", "t", "d", "v", "p", "m", "s", "o"), ("i", "w", "p", "d", "t", "r", "s", "e", "a"))
    i = GenRandom(len(keys) - 1)
    j = GenRandom(len(keys[i]) - 1)
    ClickMenu(x + dx * i, y, keys[i][j])
    DesktopCommon.Sleep(0.5)
    DesktopCommon.SendScKeys("ENTER")


# 点击帮助-进入论坛、报告错误、反馈意见
def DoNavigateToBBS(args):
    for key in ["r", "s", "d", "i"]:
	SeSmoke.ClickSEMenuBar(35, 10, "righttop")
	DesktopCommon.SendScKeys(key)

# 调出About对话框
def DoSEAboutDlg(args):
    SeSmoke.ClickSEMenuBar(35, 10, "righttop")
    DesktopCommon.SendScKeys("a")

# 按住F5一段时间
def DoPressF5(args):
    DesktopCommon.KeyDown("F5")
    DesktopCommon.Sleep(5)
    DesktopCommon.KeyUp("F5")

# 快速点击F5
def DoClickF5Fast(args):
    for i in range(10):
	DesktopCommon.SendScKeys("F5")
	DesktopCommon.Sleep(0.3)

#######################################探索发现稳定性动作#########################
def NavigateAndShowDiscovery(url):
    DesktopCommon.CreateTabNav(url)

    handle = GetSE_AxControl()
    rect = win32gui.GetWindowRect(handle)
    DesktopCommon.MouseClick(rect[0] + 36, rect[3] - 50)
    time.sleep(0.5)

    ran = GenRandom(1)
    if ran == 0:
	for i in xrange(5):
	    win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL,0,0, - win32con.WHEEL_DELTA)
	    time.sleep(1)
    else:
	DesktopCommon.Sleep(2)
	DesktopCommon.ClickOnCtrlWithWin32("SE_TuotuoStatusbar", 15, 10, "lefttop")

def GetRandomDisURL(default, args):
    url = default
    if len(args) > 0:
	filePath = args[0]
	url = GetUrl(filePath, [])
    return url

def DoShowDiscovery(defaultURL, args):
    url = GetRandomDisURL(defaultURL, args)
    NavigateAndShowDiscovery(url)

def ClickNewsBottomBar(args, dx = 200):
    defaultURL = "http://news.sohu.com/20130408/n371896490.shtml"
    DoShowDiscovery(defaultURL, args)
    handle = GetSE_AxControl()
    rect = win32gui.GetWindowRect(handle)
    DesktopCommon.MouseClick(rect[0] + dx, rect[3] - 39)
    time.sleep(1)
    return rect

# 点击新闻底栏
def DoClickNews(args):
    rect = ClickNewsBottomBar(args)

    # 点击列表内新闻
    for i in range(3):
	DesktopCommon.MouseClick(rect[0] + 300 + 300 * i, rect[3] - 39)
	time.sleep(1)

    # 点击新闻左右翻页按钮
    for i in range(3):
	ran = GenRandom(1)
	x = rect[0] + 85
	if ran == 0:
	    x = rect[2] - 85

	DesktopCommon.MouseClick(x, rect[1] + 344)
	time.sleep(1)

    # 点击新闻列表左右翻页按钮
    for i in range(3):
	ran = GenRandom(1)
	x = rect[0] + 162
	if ran == 0:
	    x = rect[2] - 109

	DesktopCommon.MouseClick(x, rect[3] - 31)
	time.sleep(1)

    # 点击浮层关闭按钮
    DesktopCommon.MouseClick(rect[2] - 226, rect[1] + 34)
    time.sleep(1)

# 点击新闻标题
def DoClickNewsTitle(args):
    rect = ClickNewsBottomBar(args)

    DesktopCommon.MouseClick(rect[0] + 700, rect[1] + 76)
    time.sleep(1)

# 点击查看原文链接
def DoClickNewsViewLink(args):
    rect = ClickNewsBottomBar(args)
    DesktopCommon.MouseClick(rect[0] + 742, rect[1] + 98)
    time.sleep(1)

# 点击新闻图片
def DoClickNewsPicInContent(args):
    rect = ClickNewsBottomBar(args)
    DesktopCommon.MouseClick(rect[0] + 711, rect[1] + 232)
    time.sleep(1)

# 点击关闭新闻图片
def DoCloseNewsPicInContent(args):
    rect = ClickNewsBottomBar(args)

    DesktopCommon.MouseClick(rect[0] + 711, rect[1] + 232)
    time.sleep(1)
    DesktopCommon.MouseClick(rect[0] + 711, rect[1] + 350)
    time.sleep(1)

# 点击图片底栏
def DoClickNewsPic(args):
    rect = ClickNewsBottomBar(args, 511)

    # 点击缩略图
    for i in range(3):
	DesktopCommon.MouseClick(rect[0] + 256 + 260 * i, rect[3] - 39)
	time.sleep(1)

    # 点击图片左右翻页按钮
    for i in range(3):
	ran = GenRandom(1)
	x = rect[0] + 161
	if ran == 0:
	    x = rect[2] - 161

	DesktopCommon.MouseClick(x, rect[1] + 344)
	time.sleep(1)

    # 点击缩略图左右翻页按钮
    for i in range(3):
	ran = GenRandom(1)
	x = rect[0] + 158
	if ran == 0:
	    x = rect[2] - 106

	DesktopCommon.MouseClick(x, rect[3] - 31)
	time.sleep(1)

    # 点击浮层关闭按钮
    DesktopCommon.MouseClick(rect[2] - 352, rect[1] + 126)
    time.sleep(1)

#2.1.5.点击图片标题
def DoClickNewsPicTitle(args):
    rect = ClickNewsBottomBar(args, 511)

    DesktopCommon.MouseClick(rect[0] + 682, rect[1] + 35)
    time.sleep(1)

#2.1.6.点击图片查看原图链接
def DoClickNewsPicViewLink(args):
    rect = ClickNewsBottomBar(args, 511)

    x = rect[2] - 300
    y = rect[1] + 70

    while x > (rect[2] - rect[0]) / 2 :
	x = x - 10
	p = (x, y)
	win32api.SetCursorPos(p)
	time.sleep(0.01)
	if IsCursorLink():
	    DesktopCommon.MouseClick(p[0] - 20, p[1])
	    break
    DesktopCommon.Sleep(5)

    x = rect[0] + 300
    y = rect[1] + 70

    while x < (rect[2] - rect[0]) / 2:
	x = x + 10
	p = (x, y)
	win32api.SetCursorPos(p)
	time.sleep(0.01)
	if IsCursorLink():
	    DesktopCommon.MouseClick(p[0] + 20, p[1])
	    break


# 引导层内点击（两组图之间）无跳转
def DoClickNewsPicGuide(args):
    DoShowDiscovery("http://pic.news.sohu.com/911195/911297/group-428244.shtml#1", [])
    handle = GetSE_AxControl()
    rect = win32gui.GetWindowRect(handle)
    DesktopCommon.MouseClick(rect[0] + 511, rect[3] - 39)
    time.sleep(1)

    for i in range(40):
	DesktopCommon.MouseClick(rect[0] + 1047, rect[1] + 300)
	time.sleep(0.2)

# 点击视频底栏
def DoClickVideo(args):
    defaultURL = "http://news.sohu.com/20130407/n371885423.shtml"
    DoShowDiscovery(defaultURL, args)
    handle = GetSE_AxControl()
    rect = win32gui.GetWindowRect(handle)

    videoHandle = 0
    index = 0
    while index < 5 and videoHandle == 0:
	DesktopCommon.MouseClick(rect[2] - 248 - 200 * index, rect[3] - 39)
	time.sleep(1)
	index += 1
	videoHandle = DesktopCommon.GetHandle("SE_WKWExtSW")

    if videoHandle ==0:
	return

    for i in range(6):
	DesktopCommon.SetWindowTopMost(videoHandle)
	videoRect = DesktopCommon.GetRectByHandle(videoHandle)
	ran = GenRandom(3)
	if ran == 0:
	    # 暂停与播放
	    DesktopCommon.MouseClick(videoRect[0] + 30, videoRect[3] - 33)
	    DesktopCommon.Sleep(1)
	    DesktopCommon.MouseClick(videoRect[0] + 30, videoRect[3] - 33)
	    DesktopCommon.Sleep(1)
	if ran == 1:
	    # 点击列表
	    for j in range(2):
		DesktopCommon.MouseClick(videoRect[2] - 100, videoRect[1] + 76 + j * 120)
		DesktopCommon.Sleep(4)
	if ran == 2:
	    # 最大化
	    DesktopCommon.MouseClick(videoRect[2] - 65, videoRect[1] + 10)
	if ran == 3:
	    # 最小化
	    DesktopCommon.MouseClick(videoRect[2] - 95, videoRect[1] + 10)

    # 点击关闭按钮
    DesktopCommon.SetWindowTopMost(videoHandle)
    videoRect = DesktopCommon.GetRectByHandle(videoHandle)

    DesktopCommon.MouseClick(videoRect[2] - 25, videoRect[1] + 10)

#点击软件下载按钮
def DoClickSoftDownLoad(args):
    defaultURL = "http://www.onlinedown.net/soft/50032.htm"
    DoShowDiscovery(defaultURL, args)
    handle = GetSE_AxControl()
    rect = win32gui.GetWindowRect(handle)
    DesktopCommon.MouseClick(rect[0] + 353, rect[3] - 39)
    time.sleep(1)

#点击购物类目页促销推荐商品
def DoClickShopCategory(args):
    defaultURL = "http://list.taobao.com/itemlist/market/nvzhuang2011a.htm?spm=1.1000386.252633.23.8Q6R08#!cat=16&isprepay=1&sd=1&viewIndex=1&as=0&ver=pts3&atype=b&style=grid&q=%E7%89%9B%E4%BB%94&same_info=1&tid=0&olu=yes&isnew=2&json=on&tid=0"
    DoShowDiscovery(defaultURL, args)

    handle = GetSE_AxControl()
    rect = win32gui.GetWindowRect(handle)
    i = GenRandom(3)
    DesktopCommon.MouseClick(rect[0] + 410 + 200 * i, rect[3] - 39)
    time.sleep(1)

    # 点击购物类目页促销推荐浮层关闭按钮
    DesktopCommon.MouseClick(rect[2] - 47, rect[1] + 34)
    time.sleep(1)

    # 点击购物类目页促销推荐浮层商品
    i = GenRandom(3)
    DesktopCommon.MouseClick(rect[0] + 410 + 200 * i, rect[3] - 39)
    time.sleep(1)

    DesktopCommon.MouseClick(rect[0] + 374, rect[3] - 144)
    time.sleep(1)



#点击购物类目页促销推荐商品查看全部
def DoClickShopCategoryViewAll(args):
    defaultURL = "http://list.taobao.com/itemlist/market/nvzhuang2011a.htm?spm=1.1000386.252633.23.8Q6R08#!cat=16&isprepay=1&sd=1&viewIndex=1&as=0&ver=pts3&atype=b&style=grid&q=%E7%89%9B%E4%BB%94&same_info=1&tid=0&olu=yes&isnew=2&json=on&tid=0"
    DoShowDiscovery(defaultURL, args)

    handle = GetSE_AxControl()
    rect = win32gui.GetWindowRect(handle)
    DesktopCommon.MouseClick(rect[2] - 130, rect[3] - 32)
    time.sleep(1)

#4.1.1.点击百科
def DoClickDiscoveryWiki(args):
    url = "http://news.sohu.com/20130405/n371764127.shtml"
    if len(args) > 0:
	url = args[0]
    DoShowDiscovery(url, [])

    handle = GetSE_AxControl()
    rect = win32gui.GetWindowRect(handle)
    ran = GenRandom(2)
    if ran == 0:
	DesktopCommon.MouseClick(rect[2] - 443, rect[3] - 35)
	DesktopCommon.Sleep(1)
    else:
	DesktopCommon.MouseTo(rect[2] - 443, rect[3] - 35)
	DesktopCommon.Sleep(1)
	if ran == 1:
	    DesktopCommon.MouseClick(rect[2] - 449, rect[3] - 449)
	    DesktopCommon.Sleep(1)
	else:
	    DesktopCommon.MouseClick(rect[2] - 540, rect[3] - 413)
	    DesktopCommon.Sleep(1)

#4.1.2.点击网友评论
def DoClickDiscoveryComment(args):
    url = "http://news.sohu.com/20130408/n371900036.shtml"
    if len(args) > 0:
	url = args[0]
    DoShowDiscovery(url, [])

    handle = GetSE_AxControl()
    rect = win32gui.GetWindowRect(handle)
    DesktopCommon.MouseClick(rect[2] - 677, rect[3] - 35)
    DesktopCommon.Sleep(1)
    DesktopCommon.MouseClick(rect[2] - 521, rect[3] - 423)
    DesktopCommon.Sleep(1)


#4.1.2.1点击铁血论坛
def DoClickDiscoveryCommentTiexue(args):
    url = "http://mil.huanqiu.com/world/2013-06/4073728.html"
    if len(args) > 0:
	url = args[0]
    DoShowDiscovery(url, [])

    handle = GetSE_AxControl()
    rect = win32gui.GetWindowRect(handle)
    DesktopCommon.MouseClick(rect[2] - 370, rect[3] - 35)
    DesktopCommon.Sleep(1)
    DesktopCommon.MouseClick(rect[2] - 326, rect[3] - 264)
    DesktopCommon.Sleep(1)
    for i in xrange(10):
	win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL,0,0, - win32con.WHEEL_DELTA)
	time.sleep(0.5)
    DesktopCommon.MouseClick(rect[2] - 406, rect[3] - 107)
    DesktopCommon.Sleep(1)



#4.1.3.点击电视剧集标题
def DoClickDiscoveryTVDramaTitle(args):
    url = "http://tv.sohu.com/20130404/n371738647.shtml"
    if len(args) > 0:
	url = args[0]
    DoShowDiscovery(url, [])

    handle = GetSE_AxControl()
    rect = win32gui.GetWindowRect(handle)
    DesktopCommon.MouseClick(rect[0] + 805, rect[3] - 35)
    DesktopCommon.Sleep(1)
    ran = GenRandom(1)
    if ran == 0:
	DesktopCommon.MouseClick(rect[2] - 609, rect[3] - 448)
	DesktopCommon.Sleep(1)
    else:
	DesktopCommon.MouseClick(rect[2] - 716, rect[3] - 417)
	DesktopCommon.Sleep(1)

#4.13.点击电视剧集集数
def DoClickDiscoveryTVDramaEpisole(args):
    url = "http://tv.sohu.com/20130404/n371738647.shtml"
    if len(args) > 0:
	url = args[0]
    DoShowDiscovery(url, [])

    handle = GetSE_AxControl()
    rect = win32gui.GetWindowRect(handle)
    DesktopCommon.MouseClick(rect[0] + 813, rect[3] - 35)
    DesktopCommon.Sleep(1)

    DesktopCommon.MouseClick(rect[0] + 745, rect[3] - 325)
    DesktopCommon.Sleep(1)

    ran = GenRandom(5)
    ran1 = GenRandom(4)
    DesktopCommon.MouseClick(rect[0] + 678 + 55 * ran, rect[3] - 148 - 35 * ran1)
    DesktopCommon.Sleep(1)

#4.13.点击电视剧集集数其他站点
def DoClickDiscoveryTVDramaSite(args):
    url = "http://tv.sohu.com/20130404/n371738647.shtml"
    if len(args) > 0:
	url = args[0]
    DoShowDiscovery(url, [])

    handle = GetSE_AxControl()
    rect = win32gui.GetWindowRect(handle)
    DesktopCommon.MouseClick(rect[0] + 498, rect[3] - 35)
    DesktopCommon.Sleep(1)
    ran = GenRandom(2)
    DesktopCommon.MouseClick(rect[0] + 488 + 63 * i, rect[3] - 206)
    DesktopCommon.Sleep(1)

def DoClickDiscoveryTVIntroTitle(args):
    url = "http://tv.sohu.com/20121127/n358820358.shtml"
    if len(args) > 0:
	url = args[0]
    DoShowDiscovery(url, [])
    handle = GetSE_AxControl()
    rect = win32gui.GetWindowRect(handle)
    DesktopCommon.MouseClick(rect[0] + 476, rect[3] - 35)
    DesktopCommon.Sleep(1)
    ran = GenRandom(1)
    if ran == 0:
	DesktopCommon.MouseClick(rect[0] + 533, rect[3] - 450)
	DesktopCommon.Sleep(1)
    else:
	DesktopCommon.MouseClick(rect[0] + 385, rect[3] - 414)
	DesktopCommon.Sleep(1)

def DoClickDiscoveryTVIntroEpisole(args):
    url = "http://tv.sohu.com/20130530/n377571008.shtml"
    if len(args) > 0:
	url = args[0]
    DoShowDiscovery(url, [])

    handle = GetSE_AxControl()
    rect = win32gui.GetWindowRect(handle)
    DesktopCommon.MouseClick(rect[0] + 496, rect[3] - 35)
    DesktopCommon.Sleep(1)

    for i in range(GenRandom(2)):
	DesktopCommon.MouseClick(rect[0] + 719, rect[3] - 110)
	DesktopCommon.Sleep(1)

    ran = GenRandom(5)
    DesktopCommon.MouseClick(rect[0] + 352 + 55 * ran, rect[3] - 109)
    DesktopCommon.Sleep(1)

def DoClickDiscoveryTVIntroDetail(args):
    url = "http://tv.sohu.com/20121127/n358820358.shtml"
    if len(args) > 0:
	url = args[0]
    DoShowDiscovery(url, [])
    handle = GetSE_AxControl()
    rect = win32gui.GetWindowRect(handle)
    DesktopCommon.MouseClick(rect[0] + 476, rect[3] - 35)
    DesktopCommon.Sleep(1)
    DesktopCommon.MouseClick(rect[0] + 476, rect[3] - 200)

    for i in xrange(30):
	win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL,0,0, - win32con.WHEEL_DELTA)
	time.sleep(0.3)
    DesktopCommon.MouseClick(rect[0] + 689, rect[3] - 143)

def DoClickDiscoveryTVIntroNum(args):
    url = "http://tv.sohu.com/20121127/n358820358.shtml"
    if len(args) > 0:
	url = args[0]
    DoShowDiscovery(url, [])
    handle = GetSE_AxControl()
    rect = win32gui.GetWindowRect(handle)
    DesktopCommon.MouseClick(rect[0] + 476, rect[3] - 35)
    DesktopCommon.Sleep(1)
    ran = GenRandom(4)
    DesktopCommon.MouseClick(rect[0] + 396 + 111 * ran, rect[3] - 110)
    DesktopCommon.Sleep(1)

def DoClickDiscoveryTVIntroSomePart(args):
    url = "http://tv.sohu.com/20130301/n367557849.shtml"
    if len(args) > 0:
	url = args[0]
    DoShowDiscovery(url, [])
    handle = GetSE_AxControl()
    rect = win32gui.GetWindowRect(handle)
    DesktopCommon.MouseClick(rect[0] + 228, rect[3] - 35)
    DesktopCommon.Sleep(1)

    ran = GenRandom(4)
    DesktopCommon.MouseClick(rect[0] + 105 + 60 * ran, rect[3] - 323)

def DoClickDiscoverySimilarTV(args):
    url = "http://tv.sohu.com/20130401/n371353907.shtml"
    if len(args) > 0:
	url = args[0]
    DoShowDiscovery(url, [])
    handle = GetSE_AxControl()
    rect = win32gui.GetWindowRect(handle)
    DesktopCommon.MouseClick(rect[0] + 470, rect[3] - 35)
    DesktopCommon.Sleep(1)

    ran = GenRandom(3)
    for i in range(ran):
	DesktopCommon.MouseClick(rect[0] + 806, rect[3] - 353)
	DesktopCommon.Sleep(1)

    ran = GenRandom(3)
    for i in range(ran):
	DesktopCommon.MouseClick(rect[0] + 694, rect[3] - 353)
	DesktopCommon.Sleep(1)

    ran = GenRandom(4)
    DesktopCommon.MouseClick(rect[0] + 223 + 140 * ran, rect[3] - 254)

#4.1.6.点击影评
def DoClickDiscoveryMovieComment(args):
    url = "http://tv.sohu.com/20130401/n371352249.shtml"
    if len(args) > 0:
	url = args[0]
    DoShowDiscovery(url, [])

    handle = GetSE_AxControl()
    rect = win32gui.GetWindowRect(handle)
    DesktopCommon.MouseClick(rect[0] + 791, rect[3] - 35)
    DesktopCommon.Sleep(1)
    DesktopCommon.MouseClick(rect[0] + 675, rect[3] - 448)

#4.1.7.点击电影播放
def DoClickDiscoveryMoviePlay(args):
    url = "http://v.youku.com/v_show/id_XNTIzNjI0Mjcy.html"
    if len(args) > 0:
	url = args[0]
    DoShowDiscovery(url, [])

    handle = GetSE_AxControl()
    rect = win32gui.GetWindowRect(handle)
    DesktopCommon.MouseClick(rect[0] + 753, rect[3] - 35)
    DesktopCommon.Sleep(1)
    ran = GenRandom(2)
    if ran == 0:
	DesktopCommon.MouseClick(rect[0] + 827, rect[3] - 144)
    elif ran == 1:
	DesktopCommon.MouseClick(rect[0] + 692, rect[3] - 199)
    else:
	DesktopCommon.MouseClick(rect[0] + 802, rect[3] - 282)

#4.1.8.点击综艺
def DoClickDiscoveryVariety(args):
    url = "http://v.youku.com/v_show/id_XNTIzNjI0Mjcy.html"
    if len(args) > 0:
	url = args[0]
    DoShowDiscovery(url, [])

    handle = GetSE_AxControl()
    rect = win32gui.GetWindowRect(handle)
    DesktopCommon.MouseClick(rect[0] + 762, rect[3] - 35)
    DesktopCommon.Sleep(1)
    ran = GenRandom(2)
    if ran == 0:
	ran2 = GenRandom(3)
	DesktopCommon.MouseClick(rect[0] + 763, rect[3] - 133 - 70* ran2)
    elif ran == 1:
	DesktopCommon.MouseClick(rect[0] + 785, rect[3] - 449)
    else:
	DesktopCommon.MouseClick(rect[0] + 720, rect[3] - 430)

#4.1.9.点击淘宝比价
def DoClickDiscoveryTaobaoParity(args):
    url = "http://item.taobao.com/item.htm?spm=a2106.m944.1000384.d19.b52pB9&id=19570271722&scm=1029.newlist-0.bts1.50474007&ppath"
    if len(args) > 0:
	url = args[0]
    DoShowDiscovery(url, [])

    handle = GetSE_AxControl()
    rect = win32gui.GetWindowRect(handle)
    DesktopCommon.MouseClick(rect[0] + 196, rect[3] - 35)
    DesktopCommon.Sleep(1)

    DesktopCommon.MouseClick(rect[2] - 79, rect[3] - 382)
    DesktopCommon.Sleep(1)
    DesktopCommon.MouseClick(rect[2] - 191, rect[3] - 382)
    ran = GenRandom(2)
    if ran == 0:
	ran2 = GenRandom(4)
	DesktopCommon.MouseClick(rect[0] + 413 + ran2 * 200, rect[3] - 279)
    elif ran == 1:
	ran2 = GenRandom(3)
	DesktopCommon.MouseClick(rect[0] + 83, rect[3] - 156 - 54 * ran2)
    else:
	DesktopCommon.MouseTo(rect[0] + 80, rect[1] + 80)
	DesktopCommon.Sleep(1)
	DesktopCommon.MouseClick(rect[2] - 57, rect[3] - 98)
	DesktopCommon.Sleep(1)
	DesktopCommon.MouseClick(rect[2] - 116, rect[3] - 98)
	DesktopCommon.Sleep(1)
	ran2 = GenRandom(3)
	DesktopCommon.MouseClick(rect[2] - 86, rect[3] - 195 - 120 * ran2)

#4.1.10.点击商城比价
def DoClickDiscoveryShopParity(args):
    url = "http://www.amazon.cn/gp/product/B00B1OLPJO/ref=s9_pop_gw_g201_ir03?pf_rd_m=A1AJ19PSB66TGU&pf_rd_s=center-3&pf_rd_r=1MVAJV3DRZW3MEZZCEQA&pf_rd_t=101&pf_rd_p=58223012&pf_rd_i=899254051"
    if len(args) > 0:
	url = args[0]
    DoShowDiscovery(url, [])

    handle = GetSE_AxControl()
    rect = win32gui.GetWindowRect(handle)
    DesktopCommon.MouseClick(rect[0] + 196, rect[3] - 35)
    DesktopCommon.Sleep(1)

    DesktopCommon.MouseClick(rect[2] - 79, rect[3] - 382)
    DesktopCommon.Sleep(1)
    DesktopCommon.MouseClick(rect[2] - 191, rect[3] - 382)
    ran = GenRandom(2)
    if ran == 0:
	ran2 = GenRandom(4)
	DesktopCommon.MouseClick(rect[0] + 413 + ran2 * 200, rect[3] - 279)
    elif ran == 1:
	ran2 = GenRandom(3)
	DesktopCommon.MouseClick(rect[0] + 83, rect[3] - 156 - 54 * ran2)
    else:
	DesktopCommon.MouseTo(rect[0] + 80, rect[1] + 80)
	DesktopCommon.Sleep(1)
	DesktopCommon.MouseClick(rect[2] - 57, rect[3] - 98)
	DesktopCommon.Sleep(1)
	DesktopCommon.MouseClick(rect[2] - 116, rect[3] - 98)
	DesktopCommon.Sleep(1)
	ran2 = GenRandom(3)
	DesktopCommon.MouseClick(rect[2] - 86, rect[3] - 195 - 120 * ran2)

#4.1.11.点击价格走势
def DoClickDiscoveryPriceMovements(args):
    url = "http://www.amazon.cn/gp/product/B00BSJVKTW/ref=s9_pop_gw_g14_ir05?pf_rd_m=A1AJ19PSB66TGU&pf_rd_s=center-3&pf_rd_r=1MVAJV3DRZW3MEZZCEQA&pf_rd_t=101&pf_rd_p=58223012&pf_rd_i=899254051"
    if len(args) > 0:
	url = args[0]

    DoShowDiscovery(url, [])
    handle = GetSE_AxControl()
    rect = win32gui.GetWindowRect(handle)
    DesktopCommon.MouseClick(rect[0] + 688, rect[3] - 35)
    DesktopCommon.Sleep(1)

    # 点击商城
    ran = GenRandom(2)
    DesktopCommon.MouseClick(rect[2] - 446, rect[3] - 177 - ran * 20)
    DesktopCommon.Sleep(1)

    # 点击价格
    ran = GenRandom(2)
    DesktopCommon.MouseClick(rect[2] - 312, rect[3] - 177 - ran * 20)
    DesktopCommon.Sleep(1)

#4.1.12.点击购买建议
def DoClickDiscoveryBuy(args):
    url = "http://item.taobao.com/item.htm?spm=2013.1.14869321253.04.wEH7GP&id=13809376280"
    if len(args) > 0:
	url = args[0]

    DoShowDiscovery(url, [])
    handle = GetSE_AxControl()
    rect = win32gui.GetWindowRect(handle)
    DesktopCommon.MouseClick(rect[0] + 595, rect[3] - 35)
    DesktopCommon.Sleep(1)
    DesktopCommon.MouseClick(rect[2] - 76, rect[3] - 388)
    DesktopCommon.Sleep(1)
    DesktopCommon.MouseClick(rect[2] - 184, rect[3] - 389)

    ran = GenRandom(1)
    if ran == 0:
	DesktopCommon.MouseClick(rect[2] - 216, rect[3] - 222)
	DesktopCommon.Sleep(1)
    else:
	DesktopCommon.MouseTo(rect[0] + 50, rect[1] + 50)
	ran2 = GenRandom(3)
	DesktopCommon.MouseClick(rect[2] - 76, rect[3] - 190 - 125 * ran2)


#5.1.点击关闭按钮
def DoCloseDiscovery(args):
    defaultURL = "http://tv.sohu.com/20130407/n371892572.shtml"
    DoShowDiscovery(defaultURL, args)

    handle = GetSE_AxControl()
    rect = win32gui.GetWindowRect(handle)
    DesktopCommon.MouseClick(rect[2] - 23, rect[3] - 33)
    time.sleep(1)
    DesktopCommon.MouseClick(rect[0] + 12, rect[3] - 12)
    time.sleep(1)

    DesktopCommon.MouseClick(rect[2] - 23, rect[3] - 73)
    time.sleep(1)
    DesktopCommon.MouseClick(rect[2] - 40, rect[3] - 107)
    time.sleep(1)
    DesktopCommon.MouseClick(rect[0] + 12, rect[3] - 12)
    time.sleep(1)
    DesktopCommon.MouseClick(rect[2] - 23, rect[3] - 73)
    time.sleep(1)
    DesktopCommon.MouseClick(rect[2] - 56, rect[3] - 134)
    time.sleep(1)

#5.2.点击意见反馈
def DoClickDiscoveryFeedBack(args):
    defaultURL = "http://tv.sohu.com/20130407/n371892572.shtml"
    DoShowDiscovery(defaultURL, args)

    handle = GetSE_AxControl()
    rect = win32gui.GetWindowRect(handle)
    DesktopCommon.MouseClick(rect[2] - 23, rect[3] - 73)
    time.sleep(1)
    DesktopCommon.MouseTo(rect[0] + 100, rect[1] + 100)
    time.sleep(1)
    DesktopCommon.MouseClick(rect[2] - 23, rect[3] - 73)
    time.sleep(1)
    DesktopCommon.MouseClick(rect[2] - 23, rect[3] - 73)
    time.sleep(1)



if __name__=="__main__":
    #DoNavigate(["D:\\TestMarkYellow\\url.txt"])
##    handle = win32gui.FindWindow("SE_TuoLiteTooltip",None)
##    if handle!=0:
##	text = win32gui.GetWindowText(handle)
##	rect = win32gui.GetClientRect(handle)
##        rect = win32gui.ClientToScreen(handle,(rect[0],rect[1]))
##    AddPreAction("Pre",300)
##    AddPostAction("Post",400)
##    DesktopCommon.InitDCO(r"D:\TestMarkYellow\CtrlNames.xls")
##    DesktopCommon.StartProcess(DesktopCommon.GetSEDir()+"\\SogouExplorer.exe")
##    time.sleep(2)
##    for i in range(4):
##	DoOpenDynPage()
##	time.sleep(1)
    #DesktopCommon.StartProcess(DesktopCommon.GetSEDir()+"\\SogouExplorer.exe")
    time.sleep(3)
    DoOpenSideBar("SE_TuotuoSidebar")
    AddAction("Print",10)
    AddAction("Printb",15,1,2)
    AddAction("Printc",20,"helloworld",2000)
    AddAction("Printd",20,"helloworld",2000)
    AddMacroAction("宏1",10,"Print:2,Printb:3",3)
    AddMacroAction("宏2",10,"Printc,Printd",3)
    AddMacroAction("大宏",100000,"宏1,宏2",1000)
##    pm = ProbManager()
##    pm.funcAndParamMap = g_funcAndParamMap
##    pm.GenerateProbilityDistribution()  #生成概率分布
##    name = pm.GenNextAction()
##    print name
    StartTest(10000)

