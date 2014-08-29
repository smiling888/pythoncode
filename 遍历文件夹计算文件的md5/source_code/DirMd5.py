#coding:gbk
'''
计算文件夹下各个文件的md5

'''

import md5
import os
filterSuffix=[".dll",'.exe','.manifest','.sqlite3','.apk']
MD5_FILE_PATH="d:/SogouTool_md5"

def getmd5(filepath):
    '''
    函数名：返回文件的md5值
    返回值：
    '''
    import md5
    f = open(filepath,'rb')
    md5obj = md5.md5()
    md5obj.update(f.read())
    hash1 = md5obj.hexdigest()
    f.close()
    return str(hash1)

def CalDirMd5(root):
    MD5_FILE_PATH="d:/SogouTool_md5"
    while os.path.exists(MD5_FILE_PATH+'.ini'):
        MD5_FILE_PATH+="0"
    MD5_FILE_PATH+='.ini'
    f=open(MD5_FILE_PATH,"w")
    file_Num=0
    for dirpath1,dirnames1,filenames in os.walk(root):
        for filename in filenames:
            path=os.path.join(dirpath1,filename)

            if os.path.isfile(path):
                if FilterSuf(path):
                    line= filename+" = "+getmd5(path)+"     "+path
                    print line
                    f.write(line+"\n")
                    file_Num+=1
    f.write("File Number:"+str(file_Num))
    print "File Number:"+str(file_Num)
    f.close()
    print "文件保存在: "+MD5_FILE_PATH

def FilterSuf(path,suffix=filterSuffix):
    for sux in suffix:
        if path.find(sux)!=-1:
            return True
    return False

if __name__=="__main__":

    root=raw_input("Input SogouMoBileTool Directory(like:C:\\Users\\test\\AppData\\Local\\SogouMobileTool):"+"\n")
    #root=r"C:\Users\test\AppData\Local\SogouMobileTool"
    CalDirMd5(root)

