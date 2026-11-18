"""A small Windows GUI using Python's bundled Tk: no runtime Python install needed."""
from __future__ import annotations

import ctypes
import json
import os
from pathlib import Path
import queue
import sys
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import webbrowser

from desktop import __version__
from desktop.core import Backend, DesktopError, RestartRequired, FASTA_SUFFIXES


class Application:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.messages = queue.Queue()
        self.backend = Backend(log=lambda line: self.messages.put(("log", line)),
                               event=lambda item: self.messages.put(("event", item)))
        logs = self.backend.data / "logs"
        logs.mkdir(exist_ok=True)
        self.log_path = logs / (time.strftime("desktop-%Y%m%d-%H%M%S-") + str(os.getpid()) + ".log")
        self.log_file = self.log_path.open("a", encoding="utf-8", buffering=1)
        self.inputs: list[str] = []
        self.result: Path | None = None
        self.ready = False
        self.busy: str | None = None
        self.run_status = None
        self.last_stage = ""
        self.output = tk.StringVar(value=str(Path.home() / "Documents" / "ChromoPlas-results"))
        self.threads = tk.StringVar(value=str(min(4, max(1, (os.cpu_count() or 2) // 2))))
        self.status = tk.StringVar(value="Checking analysis environment...")
        self.file_summary = tk.StringVar(value="No assemblies selected")
        self.elapsed = tk.StringVar(value="")
        self.started = None
        self._build()
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.after(100, self.poll)
        self.root.after(200, lambda: self.start("check", self.backend.probe))

    def _build(self):
        self.root.title(f"ChromoPlas Desktop {__version__} — Preview")
        self.root.geometry("980x790")
        self.root.minsize(820, 700)
        self.root.configure(background="#f4f6fa")
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#f4f6fa")
        style.configure("TLabel", background="#f4f6fa", foreground="#26354d", font=("Segoe UI", 10))
        style.configure("Card.TFrame", background="white")
        style.configure("Card.TLabel", background="white")
        style.configure("Title.TLabel", foreground="#102b50", font=("Segoe UI", 25, "bold"))
        style.configure("Heading.TLabel", background="white", font=("Segoe UI", 12, "bold"))
        style.configure("TButton", padding=(12, 8), font=("Segoe UI", 10))
        style.configure("Accent.TButton", background="#165acb", foreground="white")
        style.map("Accent.TButton", background=[("active", "#104aa8"), ("disabled", "#aabbd7")])
        style.configure("TEntry", padding=6)
        outer = ttk.Frame(self.root, padding=24)
        outer.pack(fill="both", expand=True)
        ttk.Label(outer, text="ChromoPlas", style="Title.TLabel").pack(anchor="w")
        ttk.Label(outer, text="From bacterial assemblies to chromosome–plasmid gene localization").pack(anchor="w", pady=(2, 16))

        setup = ttk.Frame(outer, style="Card.TFrame", padding=16)
        setup.pack(fill="x", pady=(0, 12))
        ttk.Label(setup, text="Analysis engine", style="Heading.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(setup, text="First setup downloads tools and reference databases. Internet and 25 GiB free space required.\n"
                  "Windows may request administrator approval and a restart. Later analyses run locally.",
                  style="Card.TLabel", wraplength=640).grid(row=1, column=0, sticky="w", pady=(6, 0))
        self.setup_button = ttk.Button(setup, text="Set up engine", command=lambda: self.start("setup", self.backend.setup))
        self.setup_button.grid(row=0, column=1, rowspan=2, padx=(12, 0))
        setup.columnconfigure(0, weight=1)

        card = ttk.Frame(outer, style="Card.TFrame", padding=16)
        card.pack(fill="x", pady=(0, 12))
        ttk.Label(card, text="1   Select assemblies", style="Heading.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(card, text="FASTA files (.fa, .fna, .fasta, optionally .gz).", style="Card.TLabel").grid(row=1, column=0, sticky="w", pady=(4, 8))
        self.choose_button = ttk.Button(card, text="Choose files", command=self.choose_files)
        self.choose_button.grid(row=0, column=1, sticky="e")
        self.folder_button = ttk.Button(card, text="Choose folder", command=self.choose_folder)
        self.folder_button.grid(row=1, column=1, sticky="e", pady=(4, 8))
        ttk.Label(card, textvariable=self.file_summary, style="Card.TLabel", wraplength=800).grid(row=2, column=0, columnspan=2, sticky="w")
        ttk.Separator(card).grid(row=3, column=0, columnspan=2, sticky="ew", pady=12)
        ttk.Label(card, text="2   Save results", style="Heading.TLabel").grid(row=4, column=0, sticky="w", pady=(0, 8))
        self.output_entry = ttk.Entry(card, textvariable=self.output)
        self.output_entry.grid(row=5, column=0, sticky="ew")
        self.browse_button = ttk.Button(card, text="Browse", command=self.choose_output)
        self.browse_button.grid(row=5, column=1, padx=(12, 0))
        settings = ttk.Frame(card, style="Card.TFrame")
        settings.grid(row=6, column=0, columnspan=2, sticky="w", pady=(12, 0))
        ttk.Label(settings, text="CPU threads", style="Card.TLabel").pack(side="left")
        self.thread_box = ttk.Spinbox(settings, from_=1, to=max(1, os.cpu_count() or 2), width=5, textvariable=self.threads)
        self.thread_box.pack(side="left", padx=(10, 18))
        ttk.Label(settings, text="A new result folder is created for each analysis.", style="Card.TLabel").pack(side="left")
        card.columnconfigure(0, weight=1)

        actions = ttk.Frame(outer)
        actions.pack(fill="x", pady=(0, 12))
        self.run_button = ttk.Button(actions, text="Run analysis", style="Accent.TButton", command=self.run)
        self.run_button.pack(side="left")
        self.stop_button = ttk.Button(actions, text="Stop", command=self.stop, state="disabled")
        self.stop_button.pack(side="left", padx=(8, 0))
        self.report_button = ttk.Button(actions, text="Open report", command=self.open_report, state="disabled")
        self.report_button.pack(side="right")
        self.results_button = ttk.Button(actions, text="Results folder", command=self.open_results, state="disabled")
        self.results_button.pack(side="right", padx=(0, 8))
        ttk.Label(outer, textvariable=self.status, wraplength=880).pack(anchor="w")
        ttk.Label(outer, textvariable=self.elapsed).pack(anchor="w", pady=(2, 4))
        self.progress = ttk.Progressbar(outer, mode="indeterminate")
        self.progress.pack(fill="x", pady=(0, 8))
        log_frame = ttk.Frame(outer)
        log_frame.pack(fill="both", expand=True)
        self.log_view = tk.Text(log_frame, height=8, background="#10243c", foreground="#dce8f5",
                                font=("Consolas", 9), wrap="word", relief="flat", padx=10, pady=10, state="disabled")
        scroll = ttk.Scrollbar(log_frame, command=self.log_view.yview)
        self.log_view.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.log_view.pack(side="left", fill="both", expand=True)
        footer = ttk.Frame(outer)
        footer.pack(fill="x", pady=(8, 0))
        ttk.Label(footer, text="Research preview · Computational predictions · Processing stays on this computer", font=("Segoe UI", 9)).pack(side="left")
        ttk.Button(footer, text="Open setup log", command=lambda: self.open_path(self.log_path)).pack(side="right")

    def select(self, values):
        self.inputs = list(values)
        names = [Path(p).name for p in self.inputs]
        self.file_summary.set((f"{len(names)} assembly file(s): " + ", ".join(names[:4]) + (" …" if len(names) > 4 else ""))
                              if names else "No assemblies selected")

    def choose_files(self):
        values = filedialog.askopenfilenames(title="Select assembled bacterial genomes", filetypes=[("FASTA assemblies", "*.fa *.fna *.fasta *.fa.gz *.fna.gz *.fasta.gz"), ("All files", "*.*")])
        if values:
            self.select(values)

    def choose_folder(self):
        directory = filedialog.askdirectory(title="Select a folder of assembled genomes")
        if directory:
            self.select(str(p) for p in sorted(Path(directory).iterdir()) if p.is_file() and p.name.lower().endswith(FASTA_SUFFIXES))

    def choose_output(self):
        directory = filedialog.askdirectory(title="Save results under this folder")
        if directory:
            self.output.set(directory)

    def set_busy(self, action=None):
        self.busy = action
        state = "disabled" if action else "normal"
        for widget in (self.setup_button, self.choose_button, self.folder_button, self.browse_button,
                       self.output_entry, self.thread_box):
            widget.configure(state=state)
        self.run_button.configure(state="normal" if self.ready and not action else "disabled")
        self.stop_button.configure(state="normal" if action == "analysis" else "disabled")
        if action:
            self.started = time.monotonic()
            self.progress.start(15)
        else:
            self.progress.stop()
            self.started = None

    def start(self, action, function):
        if self.busy:
            return
        self.run_status = None
        self.last_stage = ""
        self.set_busy(action)
        self.status.set({"check": "Checking analysis environment...", "setup": "Setting up analysis engine...",
                         "analysis": "Preparing analysis..."}[action])
        def work():
            try:
                result = function()
                self.messages.put(("done", (action, result)))
            except Exception as exc:
                self.messages.put(("failure", (action, exc)))
        threading.Thread(target=work, daemon=True).start()

    def run(self):
        try:
            threads = int(self.threads.get())
        except ValueError:
            messagebox.showerror("CPU threads", "Enter a whole number of CPU threads.")
            return
        values, output = self.inputs.copy(), self.output.get()
        if not output.strip():
            messagebox.showerror("Results folder", "Choose a folder for your results.")
            return
        self.result = None
        self.report_button.configure(state="disabled")
        self.results_button.configure(state="disabled")
        self.start("analysis", lambda: self.backend.analyze(values, output, threads))

    def stop(self):
        if self.busy != "analysis":
            return
        if messagebox.askyesno("Stop analysis", "Stop the current analysis? Its log and partial Linux working files will be kept."):
            self.stop_button.configure(state="disabled")
            def stop_worker():
                try:
                    self.backend.stop()
                except Exception as exc:
                    self.messages.put(("log", f"Stop failed: {exc}"))
            threading.Thread(target=stop_worker, daemon=True).start()

    def poll(self):
        for _ in range(250):
            try:
                kind, value = self.messages.get_nowait()
            except queue.Empty:
                break
            if kind == "log":
                self.log_file.write(value + "\n")
                self.log_view.configure(state="normal")
                self.log_view.insert("end", value + "\n")
                if int(self.log_view.index("end-1c").split(".")[0]) > 2500:
                    self.log_view.delete("1.0", "500.0")
                self.log_view.see("end")
                self.log_view.configure(state="disabled")
            elif kind == "event":
                if value.get("stage"):
                    self.last_stage = value["stage"]
                    self.status.set(self.last_stage)
                if value.get("status") in ("complete", "qc_failed", "failed"):
                    self.run_status = value["status"]
            elif kind == "done":
                action, result = value
                if action in ("setup", "check"):
                    self.ready = True
                    self.setup_button.configure(text="Repair engine")
                    self.status.set("Analysis engine ready. Select assemblies to begin.")
                else:
                    self.result = result
                    self.status.set(self.last_stage or "Analysis complete")
                    self.results_button.configure(state="normal")
                    self.report_button.configure(state="normal")
                self.set_busy()
            elif kind == "failure":
                action, error = value
                if action in ("setup", "check"):
                    self.ready = False
                self.set_busy()
                self.status.set("Set up the engine to begin." if action == "check" else str(error).splitlines()[0])
                self.messages.put(("log", str(error)))
                if action != "check":
                    title = "Restart or setup needs attention" if isinstance(error, RestartRequired) else "ChromoPlas needs attention"
                    messagebox.showerror(title, str(error)[:2500] + f"\n\nFull log: {self.log_path}")
        if self.started:
            seconds = int(time.monotonic() - self.started)
            self.elapsed.set(f"Elapsed: {seconds // 60:02d}:{seconds % 60:02d}")
        self.root.after(100, self.poll)

    @staticmethod
    def open_path(path):
        if sys.platform == "win32":
            os.startfile(str(path))
        else:
            webbrowser.open(Path(path).resolve().as_uri())

    def open_report(self):
        if self.result:
            webbrowser.open((self.result / "07_reports/report.html").resolve().as_uri())

    def open_results(self):
        if self.result:
            self.open_path(self.result)

    def close(self):
        if self.busy:
            messagebox.showinfo("Work in progress", "Wait for setup to finish, or use Stop for a running analysis, before closing.")
            return
        self.log_file.close()
        self.root.destroy()


def main():
    root = tk.Tk()
    if "--smoke-test" in sys.argv:
        root.withdraw()
        app = Application(root)
        manifest = json.loads((app.backend.assets / "payload.json").read_text())
        assert len(manifest["sha256"]) == 64
        root.update_idletasks()
        app.log_file.close()
        root.destroy()
        return
    handle = None
    if sys.platform == "win32":
        kernel = ctypes.WinDLL("kernel32", use_last_error=True)
        kernel.CreateMutexW.restype = ctypes.c_void_p
        kernel.CreateMutexW.argtypes = [ctypes.c_void_p, ctypes.c_bool, ctypes.c_wchar_p]
        handle = kernel.CreateMutexW(None, False, "Local\\ChromoPlasDesktop-v1")
        if not handle or ctypes.get_last_error() == 183:
            messagebox.showinfo("ChromoPlas", "ChromoPlas is already open in this Windows session.")
            root.destroy()
            return
    Application(root)
    root.mainloop()
    if handle:
        kernel.CloseHandle.argtypes = [ctypes.c_void_p]
        kernel.CloseHandle(handle)


if __name__ == "__main__":
    main()
