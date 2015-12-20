# -*- coding: cp1251 -*-
__author__ = 'whoami'

from cx_Freeze import setup, Executable

if __name__ == "__main__":
    setup(
        name="PasswordWizard",
        version="1.2.2",
        description="It stores and encrypts passwords",
        executables=[Executable("PasswordWizard.py", base="Win32GUI", icon="main.ico")]
    )
