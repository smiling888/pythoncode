#coding=utf-8
import os
import ctypes,sys
import zipfile
import shutil

def OS_Bit():

## get os bit

    i = ctypes.c_int() 
    kernel32 =ctypes.windll.kernel32 
    process = kernel32.GetCurrentProcess() 
    kernel32.IsWow64Process(process, ctypes.byref(i)) 
    is64bit = (i.value != 0)
    if (is64bit == True):
        return "64"
    else:
        return "32"

def getOSEnviron():
    l=os.environ.keys()
    for i in l:
        print i,os.environ[i]

        

def getmd5(filepath):
    import md5
    f = open(filepath,'rb')
    md5obj = md5.md5()
    md5obj.update(f.read())
    hash1 = md5obj.hexdigest()
    f.close()
    return str(hash1)

def helperzip():
    if(OS_Bit()=="64"):
        path="C:\\Program Files (x86)\\SogouMobileTool\\"
        
    else:
        path="C:\\Program Files (x86)\\SogouMobileTool\\"

    desktop=os.environ["HOME"]+"\\Desktop"
    savename="SMTHelperModule.zip"
    #压缩完毕默认保存在和该代码相同的目录
    f = zipfile.ZipFile(savename, 'w' ,zipfile.ZIP_DEFLATED)
    for dirpath, dirnames, filenames in os.walk(path, True):
        for filename in filenames:
            if filename=="PopupCond.dll" or filename=="SMTHelperModule.dll":
                direactory = os.path.join(dirpath,filename)
                print direactory
                f.write(direactory)        
    f.close()

    #将其移动到桌面
    desktopzip=desktop+"\\"+savename
    if os.path.exists(desktopzip):
        os.remove(desktopzip)
    zippath=os.getcwd()+"\\"+savename
    shutil.move(zippath,desktop)

    #计算md5和文件大小
    hpversion=raw_input('version:')
    hpversion="hpversion="+str(hpversion)
    hpfilesize="hpfilesize="+str(os.path.getsize(desktopzip))
    hpmd5="hpmd5="+str(getmd5(desktopzip))
    hpurl="hpurl=http://download.zhushou.sogou.com/SogouMobileTool/SMTHelperModule.zip"
    
    f=open(desktop+"\\update.ini",'w')
    f.write(hpversion+"\n")
    f.write(hpfilesize+"\n")
    f.write(hpmd5+"\n")
    f.write(hpurl+"\n")
    f.close()
helperzip()
