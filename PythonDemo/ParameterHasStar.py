#!/usr/bin/env python
#coding=utf-8
'''
函数参数带星号的时候
'''
def ParamHasStarTest(a,*b):
    """
    if ParamHasStarTest(1) then
    1
    0 ()
    if ParamHasStarTest(1,2) then
    1
    1 (2,)
    """
    print a
    print len(b),b
    
def ArrayInLine(test,b):
    for i in b:
        if test.find(i)==-1:
            return False
    return True    


    
def ParamHasStar(a,*b):
    test="a,b,c,das,da,f,sdf,sdfas"
    if(test.find(a)!=1) and (ArrayInLine(test,b)):
        return True
    return False
assert ParamHasStar('a')==True
print ParamHasStar('a','b')    
print ParamHasStar('a','b','c')
print ParamHasStar('a','b','aaad')
