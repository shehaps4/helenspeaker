"""
ALSHEHAB SOFT - Professional Mobile Maintenance & Diagnostics Suite
Author: Designed for Professional Mobile Technicians
Version: 1.0.0
"""

import os
import sys
import subprocess
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext


# Paths to bundled / system tools
DEFAULT_BIN_PATHS = [
    r"C:\UnlockTool\Binaries",
    r"C:\Program Files (x86)\BossV\Best Flash Tool",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "bin"),
]

def find_binary(name):
    # Check in PATH
    for folder in os.environ.get("PATH", "").split(os.pathsep):
        candidate = os.path.join(folder, name)
        if os.path.isfile(candidate):
            return candidate
    # Check default known directories
    for folder in DEFAULT_BIN_PATHS:
        candidate = os.path.join(folder, name)
        if os.path.isfile(candidate):
            return candidate
    return name


class DeviceEngine:
    def __init__(self, log_callback=None):
        self.log_callback = log_callback
        self.adb_path = find_binary("adb.exe")
        self.fastboot_path = find_binary("fastboot.exe")

    def log(self, message):
        if self.log_callback:
            timestamp = time.strftime("[%H:%M:%S] ")
            self.log_callback(timestamp + message + "\n")

    def run_cmd(self, executable, args):
        cmd = [executable] + args
        self.log(f"Executing: {' '.join(cmd)}")
        try:
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                startupinfo=startupinfo,
                encoding='utf-8',
                errors='replace'
            )
            stdout, stderr = proc.communicate()
            if stdout.strip():
                self.log(stdout.strip())
            if stderr.strip():
                self.log(f"[STDERR] {stderr.strip()}")
            return proc.returncode, stdout, stderr
        except Exception as e:
            self.log(f"[ERROR] {str(e)}")
            return -1, "", str(e)

    def adb_command(self, *args):
        return self.run_cmd(self.adb_path, list(args))

    def fastboot_command(self, *args):
        return self.run_cmd(self.fastboot_path, list(args))


class AlshehabSoftApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("ALSHEHAB SOFT - Professional Mobile Suite v1.0")
        self.geometry("980x680")
        self.minsize(850, 580)

        # Style & Themes
        self.engine = DeviceEngine(log_callback=self.append_log)
        self.setup_ui()
        self.start_device_monitor()

    def setup_ui(self):
        # Configure Colors
        self.bg_color = "#1e1e2e"
        self.card_color = "#282a36"
        self.accent_color = "#00adb5"
        self.fg_color = "#f8f8f2"
        self.text_dim = "#6272a4"

        self.configure(bg=self.bg_color)

        style = ttk.Style(self)
        style.theme_use("clam")

        # Custom Notebook Style
        style.configure("TNotebook", background=self.bg_color, borderwidth=0)
        style.configure("TNotebook.Tab", background="#383a59", foreground="#ffffff", padding=[16, 8], font=("Segoe UI", 10, "bold"))
        style.map("TNotebook.Tab", background=[("selected", self.accent_color)], foreground=[("selected", "#000000")])

        # Custom Buttons
        style.configure("TButton", font=("Segoe UI", 9, "bold"), padding=6)
        style.configure("Accent.TButton", background=self.accent_color, foreground="#000000", font=("Segoe UI", 9, "bold"))
        style.map("Accent.TButton", background=[("active", "#00d2dc")])

        # Top Header Banner
        header_frame = tk.Frame(self, bg="#11111b", height=75)
        header_frame.pack(fill=tk.X, side=tk.TOP)

        title_label = tk.Label(
            header_frame,
            text="ALSHEHAB SOFT",
            font=("Segoe UI", 20, "bold"),
            fg="#00adb5",
            bg="#11111b"
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=(10, 0))

        sub_label = tk.Label(
            header_frame,
            text="Advanced Mobile Servicing, Diagnostics & Flashing Framework",
            font=("Segoe UI", 9),
            fg="#a6adc8",
            bg="#11111b"
        )
        sub_label.pack(side=tk.LEFT, padx=20, pady=(38, 0))

        # Status badge on top right
        self.connection_badge = tk.Label(
            header_frame,
            text="● Searching Devices...",
            font=("Segoe UI", 10, "bold"),
            fg="#f38ba8",
            bg="#11111b"
        )
        self.connection_badge.pack(side=tk.RIGHT, padx=25, pady=20)

        # Main Workspace Container
        workspace_frame = tk.Frame(self, bg=self.bg_color)
        workspace_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)

        # Tabbed Notebook
        self.notebook = ttk.Notebook(workspace_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Tabs
        self.tab_adb = tk.Frame(self.notebook, bg=self.card_color)
        self.tab_fastboot = tk.Frame(self.notebook, bg=self.card_color)
        self.tab_tools = tk.Frame(self.notebook, bg=self.card_color)

        self.notebook.add(self.tab_adb, text="  ADB Diagnostics & Control  ")
        self.notebook.add(self.tab_fastboot, text="  Fastboot & Firmware Flasher  ")
        self.notebook.add(self.tab_tools, text="  System Utilities & Terminal  ")

        self.setup_adb_tab()
        self.setup_fastboot_tab()
        self.setup_tools_tab()

        # Bottom Live Terminal / Log Viewer
        log_frame = tk.Frame(self, bg="#11111b")
        log_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=12, pady=(0, 10))

        log_header = tk.Frame(log_frame, bg="#11111b")
        log_header.pack(fill=tk.X, padx=5, pady=3)

        tk.Label(log_header, text="Console Output & Activity Log", font=("Segoe UI", 9, "bold"), fg="#cdd6f4", bg="#11111b").pack(side=tk.LEFT)
        btn_clear = tk.Button(log_header, text="Clear Log", font=("Segoe UI", 8), bg="#313244", fg="#cdd6f4", bd=0, padx=8, command=self.clear_log)
        btn_clear.pack(side=tk.RIGHT)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=7, bg="#181825", fg="#a6e3a1", font=("Consolas", 9), insertbackground="white")
        self.log_text.pack(fill=tk.X, padx=5, pady=(0, 5))

    # ========================================================
    # ADB TAB
    # ========================================================
    def setup_adb_tab(self):
        container = tk.Frame(self.tab_adb, bg=self.card_color)
        container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Left Column: Device Information
        info_frame = tk.LabelFrame(container, text=" Device Information (ADB) ", bg=self.card_color, fg="#89b4fa", font=("Segoe UI", 10, "bold"), padx=10, pady=10)
        info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self.info_labels = {}
        fields = [
            ("Brand & Manufacturer:", "brand"),
            ("Model Name:", "model"),
            ("Android Version:", "android_ver"),
            ("Security Patch Level:", "sec_patch"),
            ("Build Number:", "build_id"),
            ("Serial Number / Hardware:", "serial"),
            ("Battery Level:", "battery"),
            ("CPU Architecture:", "cpu_abi"),
        ]

        for idx, (label_text, key) in enumerate(fields):
            lbl = tk.Label(info_frame, text=label_text, font=("Segoe UI", 9, "bold"), bg=self.card_color, fg="#cdd6f4")
            lbl.grid(row=idx, column=0, sticky="w", pady=4)
            val = tk.Label(info_frame, text="--", font=("Segoe UI", 9), bg=self.card_color, fg="#a6e3a1")
            val.grid(row=idx, column=1, sticky="w", padx=10, pady=4)
            self.info_labels[key] = val

        btn_read_info = tk.Button(info_frame, text="🔄 Read Full Device Info", bg="#00adb5", fg="#000000", font=("Segoe UI", 9, "bold"), bd=0, padx=12, pady=6, command=self.action_read_info)
        btn_read_info.grid(row=len(fields), column=0, columnspan=2, pady=15, sticky="ew")

        # Right Column: Power Controls & App Management
        right_frame = tk.Frame(container, bg=self.card_color)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Reboot Group
        reboot_frame = tk.LabelFrame(right_frame, text=" Power & Mode Transitions ", bg=self.card_color, fg="#89b4fa", font=("Segoe UI", 10, "bold"), padx=10, pady=10)
        reboot_frame.pack(fill=tk.X, pady=(0, 10))

        btn_reboot_sys = tk.Button(reboot_frame, text="Reboot System", bg="#313244", fg="#ffffff", bd=0, pady=5, command=lambda: self.run_async(self.engine.adb_command, "reboot"))
        btn_reboot_sys.grid(row=0, column=0, padx=5, pady=4, sticky="ew")

        btn_reboot_rec = tk.Button(reboot_frame, text="Reboot Recovery", bg="#313244", fg="#ffffff", bd=0, pady=5, command=lambda: self.run_async(self.engine.adb_command, "reboot", "recovery"))
        btn_reboot_rec.grid(row=0, column=1, padx=5, pady=4, sticky="ew")

        btn_reboot_bl = tk.Button(reboot_frame, text="Reboot Fastboot/Bootloader", bg="#313244", fg="#ffffff", bd=0, pady=5, command=lambda: self.run_async(self.engine.adb_command, "reboot", "bootloader"))
        btn_reboot_bl.grid(row=1, column=0, padx=5, pady=4, sticky="ew")

        btn_reboot_edl = tk.Button(reboot_frame, text="Reboot EDL (Qualcomm)", bg="#313244", fg="#ffffff", bd=0, pady=5, command=lambda: self.run_async(self.engine.adb_command, "reboot", "edl"))
        btn_reboot_edl.grid(row=1, column=1, padx=5, pady=4, sticky="ew")

        reboot_frame.columnconfigure(0, weight=1)
        reboot_frame.columnconfigure(1, weight=1)

        # App & APK Group
        app_frame = tk.LabelFrame(right_frame, text=" Application & APK Management ", bg=self.card_color, fg="#89b4fa", font=("Segoe UI", 10, "bold"), padx=10, pady=10)
        app_frame.pack(fill=tk.BOTH, expand=True)

        btn_install_apk = tk.Button(app_frame, text="📦 Select & Install APK", bg="#45475a", fg="#ffffff", bd=0, pady=6, command=self.action_install_apk)
        btn_install_apk.pack(fill=tk.X, pady=4)

        btn_take_screenshot = tk.Button(app_frame, text="📷 Take Screenshot to PC", bg="#45475a", fg="#ffffff", bd=0, pady=6, command=self.action_take_screenshot)
        btn_take_screenshot.pack(fill=tk.X, pady=4)

    # ========================================================
    # FASTBOOT TAB
    # ========================================================
    def setup_fastboot_tab(self):
        container = tk.Frame(self.tab_fastboot, bg=self.card_color)
        container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Controls & Diagnostics
        ctrl_frame = tk.LabelFrame(container, text=" Fastboot Diagnostics ", bg=self.card_color, fg="#89b4fa", font=("Segoe UI", 10, "bold"), padx=10, pady=10)
        ctrl_frame.pack(fill=tk.X, pady=(0, 10))

        btn_fb_devices = tk.Button(ctrl_frame, text="Check Fastboot Devices", bg="#313244", fg="#ffffff", bd=0, padx=10, pady=5, command=lambda: self.run_async(self.engine.fastboot_command, "devices"))
        btn_fb_devices.grid(row=0, column=0, padx=5, pady=4)

        btn_fb_getvar = tk.Button(ctrl_frame, text="Read All Variables (getvar all)", bg="#313244", fg="#ffffff", bd=0, padx=10, pady=5, command=lambda: self.run_async(self.engine.fastboot_command, "getvar", "all"))
        btn_fb_getvar.grid(row=0, column=1, padx=5, pady=4)

        btn_fb_reboot = tk.Button(ctrl_frame, text="Reboot to System", bg="#313244", fg="#ffffff", bd=0, padx=10, pady=5, command=lambda: self.run_async(self.engine.fastboot_command, "reboot"))
        btn_fb_reboot.grid(row=0, column=2, padx=5, pady=4)

        # Partition Flasher
        flash_frame = tk.LabelFrame(container, text=" Official Partition Flasher ", bg=self.card_color, fg="#89b4fa", font=("Segoe UI", 10, "bold"), padx=10, pady=10)
        flash_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(flash_frame, text="Select Target Partition:", bg=self.card_color, fg="#cdd6f4", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky="w", pady=5)
        self.combo_partition = ttk.Combobox(flash_frame, values=["boot", "recovery", "system", "vendor", "vbmeta", "dtbo", "userdata"], state="readonly", width=18)
        self.combo_partition.set("boot")
        self.combo_partition.grid(row=0, column=1, sticky="w", padx=10, pady=5)

        tk.Label(flash_frame, text="Select Image File (.img):", bg=self.card_color, fg="#cdd6f4", font=("Segoe UI", 9, "bold")).grid(row=1, column=0, sticky="w", pady=5)
        self.entry_img_path = tk.Entry(flash_frame, bg="#1e1e2e", fg="#ffffff", insertbackground="white", width=45)
        self.entry_img_path.grid(row=1, column=1, sticky="w", padx=10, pady=5)

        btn_browse_img = tk.Button(flash_frame, text="Browse...", bg="#45475a", fg="#ffffff", bd=0, padx=8, command=self.action_browse_img)
        btn_browse_img.grid(row=1, column=2, padx=5, pady=5)

        btn_flash = tk.Button(flash_frame, text="⚡ Flash Partition", bg="#a6e3a1", fg="#000000", font=("Segoe UI", 10, "bold"), bd=0, padx=15, pady=8, command=self.action_flash_partition)
        btn_flash.grid(row=2, column=0, columnspan=3, pady=15, sticky="ew")

    # ========================================================
    # TOOLS & TERMINAL TAB
    # ========================================================
    def setup_tools_tab(self):
        container = tk.Frame(self.tab_tools, bg=self.card_color)
        container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Quick System Tools
        sys_tools = tk.LabelFrame(container, text=" System & Driver Utilities ", bg=self.card_color, fg="#89b4fa", font=("Segoe UI", 10, "bold"), padx=10, pady=10)
        sys_tools.pack(fill=tk.X, pady=(0, 10))

        btn_devmgr = tk.Button(sys_tools, text="Open Device Manager", bg="#313244", fg="#ffffff", bd=0, padx=12, pady=6, command=lambda: os.system("start devmgmt.msc"))
        btn_devmgr.pack(side=tk.LEFT, padx=5)

        btn_restart_adb = tk.Button(sys_tools, text="Restart ADB Server", bg="#313244", fg="#ffffff", bd=0, padx=12, pady=6, command=self.action_restart_adb)
        btn_restart_adb.pack(side=tk.LEFT, padx=5)

        # Custom Command Runner
        cmd_frame = tk.LabelFrame(container, text=" Direct Command Terminal (ADB / Fastboot) ", bg=self.card_color, fg="#89b4fa", font=("Segoe UI", 10, "bold"), padx=10, pady=10)
        cmd_frame.pack(fill=tk.BOTH, expand=True)

        input_frame = tk.Frame(cmd_frame, bg=self.card_color)
        input_frame.pack(fill=tk.X, pady=5)

        self.combo_cmd_tool = ttk.Combobox(input_frame, values=["adb", "fastboot"], state="readonly", width=10)
        self.combo_cmd_tool.set("adb")
        self.combo_cmd_tool.pack(side=tk.LEFT, padx=(0, 10))

        self.entry_custom_cmd = tk.Entry(input_frame, bg="#1e1e2e", fg="#ffffff", insertbackground="white", font=("Consolas", 10))
        self.entry_custom_cmd.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.entry_custom_cmd.bind("<Return>", lambda e: self.action_run_custom_cmd())

        btn_run = tk.Button(input_frame, text="Run Command", bg="#00adb5", fg="#000000", font=("Segoe UI", 9, "bold"), bd=0, padx=12, command=self.action_run_custom_cmd)
        btn_run.pack(side=tk.RIGHT)

    # ========================================================
    # ACTIONS & LOGIC
    # ========================================================
    def append_log(self, text):
        self.log_text.insert(tk.END, text)
        self.log_text.see(tk.END)

    def clear_log(self):
        self.log_text.delete("1.0", tk.END)

    def run_async(self, func, *args):
        thread = threading.Thread(target=func, args=args, daemon=True)
        thread.start()

    def action_read_info(self):
        def worker():
            self.append_log("Reading full device hardware & build properties...\n")
            ret, brand, _ = self.engine.adb_command("shell", "getprop", "ro.product.manufacturer")
            _, model, _ = self.engine.adb_command("shell", "getprop", "ro.product.model")
            _, android_ver, _ = self.engine.adb_command("shell", "getprop", "ro.build.version.release")
            _, sec_patch, _ = self.engine.adb_command("shell", "getprop", "ro.build.version.security_patch")
            _, build_id, _ = self.engine.adb_command("shell", "getprop", "ro.build.display.id")
            _, serial, _ = self.engine.adb_command("get-serialno")
            _, battery, _ = self.engine.adb_command("shell", "dumpsys", "battery")
            _, cpu_abi, _ = self.engine.adb_command("shell", "getprop", "ro.product.cpu.abi")

            # Parse battery level
            bat_level = "Unknown"
            if "level:" in battery:
                for line in battery.splitlines():
                    if "level:" in line:
                        bat_level = line.split("level:")[1].strip() + "%"
                        break

            self.info_labels["brand"].config(text=brand.strip() or "N/A")
            self.info_labels["model"].config(text=model.strip() or "N/A")
            self.info_labels["android_ver"].config(text=f"Android {android_ver.strip()}" if android_ver.strip() else "N/A")
            self.info_labels["sec_patch"].config(text=sec_patch.strip() or "N/A")
            self.info_labels["build_id"].config(text=build_id.strip() or "N/A")
            self.info_labels["serial"].config(text=serial.strip() or "N/A")
            self.info_labels["battery"].config(text=bat_level)
            self.info_labels["cpu_abi"].config(text=cpu_abi.strip() or "N/A")

        self.run_async(worker)

    def action_install_apk(self):
        apk_path = filedialog.askopenfilename(filetypes=[("Android Package", "*.apk")])
        if apk_path:
            self.run_async(self.engine.adb_command, "install", "-r", apk_path)

    def action_take_screenshot(self):
        save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Image", "*.png")])
        if save_path:
            def worker():
                self.engine.adb_command("shell", "screencap", "-p", "/sdcard/screenshot_temp.png")
                self.engine.adb_command("pull", "/sdcard/screenshot_temp.png", save_path)
                self.engine.adb_command("shell", "rm", "/sdcard/screenshot_temp.png")
                self.append_log(f"Screenshot successfully saved to: {save_path}\n")
            self.run_async(worker)

    def action_browse_img(self):
        img_path = filedialog.askopenfilename(filetypes=[("Partition Image", "*.img")])
        if img_path:
            self.entry_img_path.delete(0, tk.END)
            self.entry_img_path.insert(0, img_path)

    def action_flash_partition(self):
        partition = self.combo_partition.get()
        img_path = self.entry_img_path.get().strip()
        if not img_path or not os.path.isfile(img_path):
            messagebox.showwarning("File Required", "Please select a valid .img file to flash.")
            return

        confirm = messagebox.askyesno("Confirm Flashing", f"Are you sure you want to flash '{partition}' with:\n{img_path}?")
        if confirm:
            self.run_async(self.engine.fastboot_command, "flash", partition, img_path)

    def action_restart_adb(self):
        def worker():
            self.engine.adb_command("kill-server")
            self.engine.adb_command("start-server")
        self.run_async(worker)

    def action_run_custom_cmd(self):
        tool = self.combo_cmd_tool.get()
        raw_cmd = self.entry_custom_cmd.get().strip()
        if not raw_cmd:
            return
        args = raw_cmd.split()
        if tool == "adb":
            self.run_async(self.engine.adb_command, *args)
        else:
            self.run_async(self.engine.fastboot_command, *args)
        self.entry_custom_cmd.delete(0, tk.END)

    def start_device_monitor(self):
        def monitor():
            while True:
                try:
                    # Check ADB
                    _, adb_out, _ = self.engine.adb_command("devices")
                    lines = [l for l in adb_out.strip().splitlines() if l and not l.startswith("List of")]
                    has_adb = any("device" in l for l in lines)

                    # Check Fastboot
                    _, fb_out, _ = self.engine.fastboot_command("devices")
                    has_fb = bool(fb_out.strip())

                    if has_adb:
                        self.connection_badge.config(text="● Connected (ADB Mode)", fg="#a6e3a1")
                    elif has_fb:
                        self.connection_badge.config(text="● Connected (Fastboot Mode)", fg="#fab387")
                    else:
                        self.connection_badge.config(text="● No Device Detected", fg="#f38ba8")
                except Exception:
                    pass
                time.sleep(4)

        threading.Thread(target=monitor, daemon=True).start()


if __name__ == "__main__":
    app = AlshehabSoftApp()
    app.mainloop()
