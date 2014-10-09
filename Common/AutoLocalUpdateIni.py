#coding=utf-8
import os
import getpass
import shutil


class Update:
    version=""
    date=""
    filesize=""
    md5=""
    upfilesize=""
    upmd5=""
    url=""
    upurl=""
    hpversion=""
    hpfilesize=""
    hpmd5=""
    hpurl=""
    upcontrol=""
    changlog=""

def WriteForceSlientUpdate(path,update):
    '''
    ����Ŀ�ģ�дǿ�ƾ�Ĭ���������ļ�
    ����:����update.ini·��

    '''
    f=open(path,'w')
    f.write("[General]")
    f.write("\n")
    f.write(update.version)
    f.write(update.date)
    f.write(update.upfilesize)
    f.write(update.upmd5)
    f.write(update.upurl)
    f.write("upcontrol=2")
    f.write("\n")
    f.write("[Change]")
    f.write("\n")
    f.write(update.changlog)
    f.close()
    
def WriteForceUpdate(path,update):
    '''
    ����Ŀ�ģ�ǿ�ư�װ������
    ����:����update.ini·��

    '''
    f=open(path,'w')
    f.write("[General]")
    f.write("\n")
    f.write(update.version)
    f.write(update.date)
    f.write(update.filesize)
    f.write(update.md5)
    f.write(update.url)
    f.write("upcontrol=1")
    f.write("\n")
    f.write("[Change]")
    f.write("\n")
    f.write(update.changlog)
    f.close()

def WriteHelperUpdate(path,update):
    '''
    ����Ŀ�ģ�дhelper���������ļ�
    ����:����update.ini·��

    '''
    f=open(path,'w')
    f.write("[General]")
    f.write("\n")
    f.write(update.date)
    f.write(update.hpversion)
    f.write(update.hpfilesize)
    f.write(update.hpmd5)
    f.write(update.hpurl)
    f.close()

def WriteManualVersion(path,update):
    '''
    ����Ŀ�ģ�д�ֶ����������ļ�
    ����:����update.ini·��

    '''
    f=open(path,'w')
    f.write("[General]")
    f.write("\n")
    f.write(update.version)
    f.write(update.date)
    f.write(update.filesize)
    f.write(update.md5)
    f.write(update.url)
    f.write("[Change]")
    f.write("\n")
    f.write(update.changlog)
    f.close()

def WriteSlientUpdate(path,update):
    '''
    ����Ŀ�ģ���Ĭ���������ļ�
    ����:����update.ini·��

    '''
    f=open(path,'w')
    print path
    f.write("[General]")
    f.write("\n")
    f.write(update.version)
    f.write(update.date)
    f.write(update.upfilesize)
    f.write(update.upmd5)
    f.write(update.upurl)
    
    f.write("[Change]")
    f.write("\n")
    f.write(update.changlog)
    f.close()


    
def localupdateini(updatepath,update):
    '''
    ����Ŀ�ģ�����������������ļ�
    ����:����update.ini·��
    
    '''
    
    f=open(updatepath,'r')
    lines=f.readlines()
    for line in lines:
        if str(line).find('version')!=-1 and str(line).find('hpversion')==-1:
            update.version=line
            print update.version
        elif str(line).find('date')!=-1:
            update.date=line
            print update.date
        elif str(line).find('filesize')!=-1 and  str(line).find('upfilesize')==-1 and str(line).find('hpfilesize')==-1:
            update.filesize=line
        elif str(line).find('md5')!=-1 and str(line).find('upmd5')==-1 and str(line).find('hpmd5')==-1:
            update.md5=line
        elif str(line).find('upfilesize')!=-1:
            update.upfilesize=line
        elif str(line).find('upmd5')!=-1:
            update.upmd5=line
        elif str(line).find('url')!=-1 and str(line).find('hpurl')==-1 and str(line).find('upurl')==-1:
            update.url=line
        elif str(line).find('upurl')!=-1:
            update.upurl=line
        elif str(line).find('hpversion')!=-1:
            update.hpversion=line
        elif str(line).find('hpfilesize')!=-1:
            update.hpfilesize=line
        elif str(line).find('hpmd5')!=-1:
            update.hpmd5=line
        elif str(line).find('hpurl')!=-1:
            update.hpurl=line
        elif str(line).find('upcontrol')!=-1:
            update.upcontrol=line
        elif str(line).find('changelog')!=-1 or str(line).find('content')!=-1:
            update.changlog=line
            #if(update.changlog.find('changelog')==-1):
            update.changlog=update.changlog.replace('changelog','content')
            print update.changlog

    f.close()
    
    #һ��ʮ�������ļ�
    #���е�update�ļ�·��
    existIniPath="c:\\Users\\"+getpass.getuser()+"\\Desktop\\AutoToolsAndFiles\\ini\\"
    newIni="c:\\Users\\"+getpass.getuser()+"\\Desktop\\ini"
    if not os.path.isdir(newIni):
        os.makedirs(newIni)
    #���Ʋ���Ҫ�޸ĵ��ļ�
    CopyHighUpdate(existIniPath,newIni)
    #3--force_silent_update
    WriteForceSlientUpdate(newIni+"\\force_silent_update.txt",update)
    
    #5--force_update
    WriteForceUpdate(newIni+"\\force_update.txt",update)
    
    #7--helper_update
    WriteHelperUpdate(newIni+"\\helper_update.txt",update)
    
    
    #10--Manual_Version
    WriteManualVersion(newIni+"\\Manual_Version.txt",update)
    
    #12--silent_update
    WriteSlientUpdate(newIni+"\\silent_update.txt",update)
    
    if not os.path.isdir(newIni+"\\ini"):
        os.makedirs(newIni+"\\ini")
        
def CopyHighUpdate(path,dist):

    '''
    os,walk����˵��������Ԫtupple(dirpath, dirnames, filenames),���Ʋ���Ҫ�޸ĵ��ļ�
    ���е�һ��Ϊ��ʼ·����
    �ڶ���Ϊ��ʼ·���µ��ļ���,
    ����������ʼ·���µ��ļ�.
    һ����os.path.join(dirpath, name)ʹ��
    '''
    for root,dirs,filenames in os.walk(path):
        for name in filenames:
            if name.find('high')!=-1 or name.find('Response')!=-1 or name.find("Latest")!=-1:
                filepath=os.path.join(root,name)
                print filepath,os.path.exists(filepath)
                shutil.copy(filepath,dist)
                

path="c:\\Users\\"+getpass.getuser()+"\\Desktop\\update.ini"

update=Update()

localupdateini(path,update)
##existIniPath="c:\\Users\\"+getpass.getuser()+"\\Desktop\\AutoToolsAndFiles\\ini\\"
##newIni="c:\\Users\\"+getpass.getuser()+"\\Desktop\\ini"
##CopyHighUpdate(existIniPath,newIni)

##rc="d:\\Desktop.txt"
##dis="d:\\python"
##shutil.copy(src,dis)
    
    
raw_input("press Enter to finish")
