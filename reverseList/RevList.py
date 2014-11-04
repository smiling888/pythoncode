#coding=utf-8
import win32api
import win32con
import win32com.client


class Node:
    data=-1
    next=None
    


def reList(node):
    pre=None
    cur=node

    while cur!=None:
        temp=cur.next
        cur.next=pre
        pre=cur
        cur=temp
    return pre
   
def printList(node):
    while node!=None:
        print node.data
        node=node.next

n1=Node()
n1.data=1
n2=Node()
n2.data=2
n2.next=n1
n3=Node()
n3.data=3
n3.next=n2
printList(n3)
n4=reList(n3)
printList(n4)



