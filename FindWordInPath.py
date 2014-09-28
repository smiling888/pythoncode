#coding=gbk
import os

def findStrInPath(path,word):
    if not os.path.exists(path):
        print 'path not exits'
        
    for dirpath,dirnames,filenames in os.walk(path):
        for filename in filenames:
            if filename.find(".txt")!=-1:
                filepath=os.path.join(dirpath,filename)
                f=open(filepath,'r')
                lines=f.readlines()
                for line in lines:
                    if line.find(word)!=-1:
                        print filepath
                        break

        
findStrInPath("C:\\Program Files (x86)\\Desktop_CheckList_TestingTools\\case","wall")
