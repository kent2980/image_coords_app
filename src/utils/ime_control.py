import ctypes
from ctypes import wintypes

user32 = ctypes.WinDLL('user32', use_last_error=True)
imm32 = ctypes.WinDLL('imm32', use_last_error=True)

# 型定義
HWND = wintypes.HWND
HIMC = wintypes.HANDLE

# 関数定義
user32.GetForegroundWindow.restype = HWND
imm32.ImmGetContext.restype = HIMC
imm32.ImmGetDefaultIMEWnd.restype = HWND

# IME メッセージ定義
WM_IME_CONTROL = 0x283
IMC_SETOPENSTATUS = 0x0006
IMC_SETCOMPOSITIONFONT = 0x000A

def set_ime_off():
    """IMEを半角（英数入力OFF）に切り替える"""
    hwnd = user32.GetForegroundWindow()
    if not hwnd:
        print("Foreground window not found.")
        return
    ime_hwnd = imm32.ImmGetDefaultIMEWnd(hwnd)
    if not ime_hwnd:
        print("IME window not found.")
        return
    # 半角（IME OFF）に設定
    user32.SendMessageW(ime_hwnd, WM_IME_CONTROL, IMC_SETOPENSTATUS, 0)
    print("IMEを半角英数に切り替えました。")

def set_ime_on():
    """IMEを全角（日本語入力ON）に切り替える"""
    hwnd = user32.GetForegroundWindow()
    if not hwnd:
        print("Foreground window not found.")
        return
    ime_hwnd = imm32.ImmGetDefaultIMEWnd(hwnd)
    if not ime_hwnd:
        print("IME window not found.")
        return
    # 全角（IME ON）に設定
    user32.SendMessageW(ime_hwnd, WM_IME_CONTROL, IMC_SETOPENSTATUS, 1)
    print("IMEを全角（日本語入力）に切り替えました。")

if __name__ == "__main__":
    set_ime_on()
