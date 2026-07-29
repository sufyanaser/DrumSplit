from __future__ import annotations

import os
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from .engine import SUPPORTED_EXTENSIONS, detect_device, separate
from .setup_model import download_model

APP_NAME = "DrumSplit"
WINDOW_SIZE = "760x520"


def app_data_dir() -> Path:
    base = os.environ.get("LOCALAPPDATA") or str(Path.home())
    return Path(base) / APP_NAME


class DrumSplitApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_NAME)
        self.geometry(WINDOW_SIZE)
        self.minsize(700, 480)

        self.input_var = tk.StringVar()
        self.output_var = tk.StringVar(value=str(Path.home() / "DrumSplit Output"))
        self.device_var = tk.StringVar(value="auto")
        self.status_var = tk.StringVar(value="Ready")

        self._configure_style()
        self._build_ui()

    def _configure_style(self) -> None:
        style = ttk.Style(self)
        if "vista" in style.theme_names():
            style.theme_use("vista")
        style.configure("Title.TLabel", font=("Segoe UI", 22, "bold"))
        style.configure("Sub.TLabel", font=("Segoe UI", 10))
        style.configure("Primary.TButton", font=("Segoe UI", 11, "bold"), padding=10)

    def _build_ui(self) -> None:
        root = ttk.Frame(self, padding=24)
        root.pack(fill="both", expand=True)

        ttk.Label(root, text="DrumSplit", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            root,
            text="Local drum-component separation: Kick, Snare, Cymbals and Toms",
            style="Sub.TLabel",
        ).pack(anchor="w", pady=(2, 22))

        source_box = ttk.LabelFrame(root, text="Source drum track", padding=14)
        source_box.pack(fill="x")
        ttk.Entry(source_box, textvariable=self.input_var).pack(
            side="left", fill="x", expand=True
        )
        ttk.Button(source_box, text="Browse", command=self._select_input).pack(
            side="left", padx=(10, 0)
        )

        output_box = ttk.LabelFrame(root, text="Output folder", padding=14)
        output_box.pack(fill="x", pady=(14, 0))
        ttk.Entry(output_box, textvariable=self.output_var).pack(
            side="left", fill="x", expand=True
        )
        ttk.Button(output_box, text="Browse", command=self._select_output).pack(
            side="left", padx=(10, 0)
        )

        options = ttk.Frame(root)
        options.pack(fill="x", pady=(16, 0))
        ttk.Label(options, text="Processing device:").pack(side="left")
        ttk.Combobox(
            options,
            textvariable=self.device_var,
            values=("auto", "cuda", "cpu"),
            state="readonly",
            width=10,
        ).pack(side="left", padx=(8, 0))
        detected = detect_device("auto")
        ttk.Label(options, text=f"Detected: {detected.upper()}").pack(
            side="left", padx=(14, 0)
        )

        self.progress = ttk.Progressbar(root, mode="indeterminate")
        self.progress.pack(fill="x", pady=(24, 8))
        ttk.Label(root, textvariable=self.status_var).pack(anchor="w")

        self.run_button = ttk.Button(
            root,
            text="Separate Drums",
            style="Primary.TButton",
            command=self._start,
        )
        self.run_button.pack(fill="x", pady=(18, 0))

        note = (
            "Input must be a drum-only track. The verified Inagoy model exports "
            "four synchronized WAV stems."
        )
        ttk.Label(root, text=note, wraplength=690).pack(anchor="w", pady=(18, 0))

    def _select_input(self) -> None:
        formats = " ".join(f"*{suffix}" for suffix in sorted(SUPPORTED_EXTENSIONS))
        path = filedialog.askopenfilename(
            title="Select drum-only audio",
            filetypes=(("Supported audio", formats), ("All files", "*.*")),
        )
        if path:
            self.input_var.set(path)

    def _select_output(self) -> None:
        path = filedialog.askdirectory(title="Select output folder")
        if path:
            self.output_var.set(path)

    def _start(self) -> None:
        input_path = Path(self.input_var.get().strip())
        output_dir = Path(self.output_var.get().strip())
        if not input_path.is_file():
            messagebox.showerror(APP_NAME, "Select a valid drum-only audio file.")
            return
        if input_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            messagebox.showerror(APP_NAME, "Unsupported audio format.")
            return

        self.run_button.configure(state="disabled")
        self.progress.start(12)
        self.status_var.set("Preparing model and processing audio...")
        thread = threading.Thread(
            target=self._process,
            args=(input_path, output_dir),
            daemon=True,
        )
        thread.start()

    def _process(self, input_path: Path, output_dir: Path) -> None:
        try:
            model_dir = app_data_dir() / "model"
            self.after(0, self.status_var.set, "Checking DrumSep model...")
            download_model(model_dir)
            self.after(0, self.status_var.set, "Separating drum components...")
            separate(input_path, output_dir, model_dir, self.device_var.get())
        except Exception as exc:  # noqa: BLE001
            self.after(0, self._finish_error, str(exc))
            return
        self.after(0, self._finish_success, output_dir / input_path.stem)

    def _finish_success(self, result_dir: Path) -> None:
        self.progress.stop()
        self.run_button.configure(state="normal")
        self.status_var.set("Completed")
        messagebox.showinfo(
            APP_NAME,
            "Separation completed.\n\n"
            f"Output: {result_dir}\n\n"
            "Generated: kick.wav, snare.wav, cymbals.wav, toms.wav",
        )

    def _finish_error(self, error: str) -> None:
        self.progress.stop()
        self.run_button.configure(state="normal")
        self.status_var.set("Failed")
        messagebox.showerror(APP_NAME, error)


def main() -> int:
    app = DrumSplitApp()
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
