# mysetup.py
from distutils.core import setup
import py2exe

setup(
    windows=[{"script":"UI.py"}],
    options={"py2exe":
       {"dll_excludes":["COMCTL32.dll","comdlg32.dll","RPCRT4.dll","ADVAPI32.dll","KERNEL32.dll","GDI32.dll","WSOCK32.dll","GDIplus.dll","MSVCP90.dll","msvcp71.dll","msvcm90.dll","OLE32.dll","WINMM.dll","OLEAUT32.dll","USER32.dll","SHELL32.dll"]}
       }
)
