from __future__ import annotations

import json
import sys
import tkinter as tk
from pathlib import Path
from tkinter import messagebox

import customtkinter as ctk
from PIL import Image

from audio_engine import AudioEngine, SessionInfo
from preview_sound import play_preview

APP_NAME = "AutoAudio"
APP_VERSION = "1.0.0"


def _app_dir() -> Path:

    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent


def _resource_path(name: str) -> Path:
   
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS) / name
    return Path(__file__).resolve().parent / name


LOGO_PATH = _resource_path("logoW.png")
CONFIG_PATH = _app_dir() / "config.json"

MIT_LICENSE = """MIT License

Copyright (c) 2026 ErkinKraft

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""


BG = "#0B0B0B"
PANEL = "#121212"
PANEL_2 = "#181818"
BORDER = "#2A2A2A"
RED = "#E10600"
RED_DIM = "#8B0400"
RED_GLOW = "#FF1A1A"
TEXT = "#F2F2F2"
MUTED = "#8A8A8A"
OK = "#E10600"


def load_config() -> dict:
    if CONFIG_PATH.exists():
        try:
            return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "target": 0.45,
        "mode": "comfort",
        "whitelist": ["discord.exe", "voicechat.exe"],
    }


def save_config(data: dict) -> None:
    CONFIG_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


class GlowFrame(ctk.CTkFrame):
 

    def __init__(self, master, **kwargs):
        kwargs.setdefault("fg_color", PANEL)
        kwargs.setdefault("corner_radius", 10)
        kwargs.setdefault("border_width", 1)
        kwargs.setdefault("border_color", BORDER)
        super().__init__(master, **kwargs)


class AboutWindow(ctk.CTkToplevel):
  

    def __init__(self, parent: ctk.CTk) -> None:
        super().__init__(parent)
        self.title("О программе")
        self.configure(fg_color=BG)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        width, height = 440, 560
        self.update_idletasks()
        x = parent.winfo_x() + max(0, (parent.winfo_width() - width) // 2)
        y = parent.winfo_y() + max(0, (parent.winfo_height() - height) // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

        self._build()
        self.protocol("WM_DELETE_WINDOW", self._close)

    def _build(self) -> None:
        pad = ctk.CTkFrame(self, fg_color=BG)
        pad.pack(fill="both", expand=True, padx=22, pady=18)

        ctk.CTkLabel(
            pad,
            text="О ПРОГРАММЕ",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=RED,
        ).pack(anchor="w")

        ctk.CTkFrame(pad, fg_color=RED, height=2, corner_radius=0).pack(fill="x", pady=(10, 18))

        panel = GlowFrame(pad)
        panel.pack(fill="both", expand=True)

        inner = ctk.CTkFrame(panel, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=20, pady=20)

        if LOGO_PATH.exists():
            img = Image.open(LOGO_PATH)
            logo_w = 140
            ratio = logo_w / img.width
            logo_h = max(1, int(img.height * ratio))
            self._logo_img = ctk.CTkImage(
                light_image=img,
                dark_image=img,
                size=(logo_w, logo_h),
            )
            ctk.CTkLabel(inner, image=self._logo_img, text="").pack(pady=(4, 10))
        else:
            ctk.CTkLabel(
                inner,
                text="EK",
                font=ctk.CTkFont(family="Segoe UI", size=48, weight="bold"),
                text_color=TEXT,
            ).pack(pady=(8, 10))

        ctk.CTkLabel(
            inner,
            text="ErkinKraft",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=TEXT,
        ).pack(pady=(0, 14))

        ctk.CTkLabel(
            inner,
            text=f"{APP_NAME}  v{APP_VERSION}",
            font=ctk.CTkFont(family="Consolas", size=14, weight="bold"),
            text_color=RED,
        ).pack(pady=(0, 12))

        ctk.CTkLabel(
            inner,
            text="Автоматическая выравнивание громкости приложений Windows",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=MUTED,
            wraplength=340,
            justify="center",
        ).pack(pady=(0, 14))

        license_box = ctk.CTkScrollableFrame(
            inner,
            fg_color=PANEL_2,
            corner_radius=8,
            border_width=1,
            border_color=BORDER,
            height=200,
        )
        license_box.pack(fill="both", expand=True)

        ctk.CTkLabel(
            license_box,
            text=MIT_LICENSE,
            font=ctk.CTkFont(family="Consolas", size=10),
            text_color="#AAAAAA",
            justify="left",
            anchor="nw",
            wraplength=330,
        ).pack(fill="x", padx=10, pady=10)

        ctk.CTkButton(
            pad,
            text="ЗАКРЫТЬ",
            height=40,
            corner_radius=6,
            fg_color=RED,
            hover_color=RED_GLOW,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            command=self._close,
        ).pack(fill="x", pady=(14, 0))

    def _close(self) -> None:
        self.grab_release()
        self.destroy()


class AutoAudioApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title("AutoAudio")
        self.geometry("920x640")
        self.minsize(820, 800)
        self.configure(fg_color=BG)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.cfg = load_config()
        mode = self.cfg.get("mode", "comfort")
        if mode not in ("comfort", "aggressive"):
            mode = "comfort"
        self.engine = AudioEngine(
            target=float(self.cfg.get("target", 0.45)),
            mode=mode,
            whitelist=set(self.cfg.get("whitelist", [])),
        )
        self.engine.on_sessions_update(self._on_sessions)
        self._session_cache: list[SessionInfo] = []
        self._pulse = False
        self._about_window: AboutWindow | None = None

        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.after(400, self._refresh_sessions_idle)
        self.after(80, self._animate_status)

    def _build_ui(self) -> None:
   
        header = ctk.CTkFrame(self, fg_color=BG, height=78)
        header.pack(fill="x", padx=22, pady=(18, 8))
        header.pack_propagate(False)

        brand = ctk.CTkLabel(
            header,
            text="AUTOAUDIO",
            font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold"),
            text_color=RED,
        )
        brand.pack(side="left", pady=16)

        subtitle = ctk.CTkLabel(
            header,
            text="  // volume intelligence",
            font=ctk.CTkFont(family="Consolas", size=14),
            text_color=MUTED,
        )
        subtitle.pack(side="left", pady=22)

        about_btn = ctk.CTkButton(
            header,
            text="О программе",
            width=110,
            height=32,
            corner_radius=6,
            fg_color=PANEL_2,
            hover_color=RED_DIM,
            border_width=1,
            border_color=BORDER,
            text_color=TEXT,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            command=self._open_about,
        )
        about_btn.pack(side="right", padx=(0, 14), pady=20)

        self.status_dot = ctk.CTkLabel(
            header,
            text="●",
            font=ctk.CTkFont(size=16),
            text_color=MUTED,
        )
        self.status_dot.pack(side="right", padx=(0, 6), pady=16)

        self.status_label = ctk.CTkLabel(
            header,
            text="STANDBY",
            font=ctk.CTkFont(family="Consolas", size=13, weight="bold"),
            text_color=MUTED,
        )
        self.status_label.pack(side="right", pady=16)


        ctk.CTkFrame(self, fg_color=RED, height=2, corner_radius=0).pack(
            fill="x", padx=22, pady=(0, 14)
        )

        body = ctk.CTkFrame(self, fg_color=BG)
        body.pack(fill="both", expand=True, padx=22, pady=(0, 18))
        body.grid_columnconfigure(0, weight=3)
        body.grid_columnconfigure(1, weight=2)
        body.grid_rowconfigure(0, weight=1)

        left = GlowFrame(body)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        right = GlowFrame(body)
        right.grid(row=0, column=1, sticky="nsew")

        self._build_left(left)
        self._build_right(right)

    def _build_left(self, parent: ctk.CTkFrame) -> None:
        pad = ctk.CTkFrame(parent, fg_color="transparent")
        pad.pack(fill="both", expand=True, padx=22, pady=20)

        ctk.CTkLabel(
            pad,
            text="ЦЕЛЕВОЙ УРОВЕНЬ",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=MUTED,
        ).pack(anchor="w")

        level_row = ctk.CTkFrame(pad, fg_color="transparent")
        level_row.pack(fill="x", pady=(10, 6))

        self.level_value = ctk.CTkLabel(
            level_row,
            text=f"{int(self.engine.target * 100)}%",
            font=ctk.CTkFont(family="Segoe UI", size=42, weight="bold"),
            text_color=TEXT,
        )
        self.level_value.pack(side="left")

        self.preview_btn = ctk.CTkButton(
            level_row,
            text="▶  ПРОИГРАТЬ",
            width=150,
            height=40,
            corner_radius=6,
            fg_color=PANEL_2,
            hover_color=RED_DIM,
            border_width=1,
            border_color=RED,
            text_color=TEXT,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            command=self._play_preview,
        )
        self.preview_btn.pack(side="right", pady=8)

        self.slider = ctk.CTkSlider(
            pad,
            from_=0.05,
            to=1.0,
            number_of_steps=95,
            height=18,
            button_color=RED,
            button_hover_color=RED_GLOW,
            progress_color=RED,
            fg_color="#2A2A2A",
            command=self._on_slider,
        )
        self.slider.set(self.engine.target)
        self.slider.pack(fill="x", pady=(4, 8))

        hint = ctk.CTkLabel(
            pad,
            text="При запуске системная громкость → 100%. Затем громкость каждого приложения подгоняется под цель.",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=MUTED,
            wraplength=480,
            justify="left",
        )
        hint.pack(anchor="w", pady=(0, 6))

        self.master_label = ctk.CTkLabel(
            pad,
            text=f"Системная громкость: {int(self.engine.master_volume * 100)}%",
            font=ctk.CTkFont(family="Consolas", size=12),
            text_color="#666666",
        )
        self.master_label.pack(anchor="w", pady=(0, 10))

        ctk.CTkLabel(
            pad,
            text="РЕЖИМ",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=MUTED,
        ).pack(anchor="w", pady=(4, 8))

        mode_row = ctk.CTkFrame(pad, fg_color="transparent")
        mode_row.pack(fill="x", pady=(0, 6))

        self.mode_switch = ctk.CTkSegmentedButton(
            mode_row,
            values=["Комфорт", "Агрессивный"],
            command=self._on_mode,
            height=36,
            corner_radius=6,
            fg_color=PANEL_2,
            selected_color=RED,
            selected_hover_color=RED_GLOW,
            unselected_color=PANEL_2,
            unselected_hover_color="#252525",
            text_color=TEXT,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
        )
        self.mode_switch.set("Агрессивный" if self.engine.mode == "aggressive" else "Комфорт")
        self.mode_switch.pack(fill="x")

        self.mode_hint = ctk.CTkLabel(
            pad,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#666666",
            wraplength=480,
            justify="left",
        )
        self.mode_hint.pack(anchor="w", pady=(6, 14))
        self._update_mode_hint()

   
        controls = ctk.CTkFrame(pad, fg_color="transparent")
        controls.pack(fill="x", pady=(4, 16))

        self.start_btn = ctk.CTkButton(
            controls,
            text="ЗАПУСТИТЬ",
            height=48,
            corner_radius=6,
            fg_color=RED,
            hover_color=RED_GLOW,
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            command=self._toggle_engine,
        )
        self.start_btn.pack(side="left", fill="x", expand=True, padx=(0, 8))

        refresh_btn = ctk.CTkButton(
            controls,
            text="ОБНОВИТЬ",
            width=120,
            height=48,
            corner_radius=6,
            fg_color=PANEL_2,
            hover_color="#252525",
            border_width=1,
            border_color=BORDER,
            text_color=TEXT,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            command=self._refresh_sessions_idle,
        )
        refresh_btn.pack(side="right")

        ctk.CTkLabel(
            pad,
            text="АКТИВНЫЕ СЕССИИ",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=MUTED,
        ).pack(anchor="w", pady=(8, 8))

        self.sessions_box = ctk.CTkScrollableFrame(
            pad,
            fg_color=PANEL_2,
            corner_radius=8,
            border_width=1,
            border_color=BORDER,
        )
        self.sessions_box.pack(fill="both", expand=True)

    def _build_right(self, parent: ctk.CTkFrame) -> None:
        pad = ctk.CTkFrame(parent, fg_color="transparent")
        pad.pack(fill="both", expand=True, padx=18, pady=20)

        ctk.CTkLabel(
            pad,
            text="БЕЛЫЙ СПИСОК",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=MUTED,
        ).pack(anchor="w")

        ctk.CTkLabel(
            pad,
            text="Эти приложения не затрагиваются регулировкой.",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=MUTED,
            wraplength=280,
            justify="left",
        ).pack(anchor="w", pady=(6, 12))

        add_row = ctk.CTkFrame(pad, fg_color="transparent")
        add_row.pack(fill="x", pady=(0, 10))

        self.whitelist_entry = ctk.CTkEntry(
            add_row,
            placeholder_text="например: spotify.exe",
            height=38,
            corner_radius=6,
            fg_color=PANEL_2,
            border_color=BORDER,
            text_color=TEXT,
            placeholder_text_color="#555555",
        )
        self.whitelist_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        add_btn = ctk.CTkButton(
            add_row,
            text="+",
            width=42,
            height=38,
            corner_radius=6,
            fg_color=RED,
            hover_color=RED_GLOW,
            font=ctk.CTkFont(size=18, weight="bold"),
            command=self._add_whitelist_from_entry,
        )
        add_btn.pack(side="right")

        self.whitelist_box = ctk.CTkScrollableFrame(
            pad,
            fg_color=PANEL_2,
            corner_radius=8,
            border_width=1,
            border_color=BORDER,
        )
        self.whitelist_box.pack(fill="both", expand=True, pady=(4, 10))

        tip = ctk.CTkLabel(
            pad,
            text="Подсказка: нажмите «В список» у сессии слева\nили введите имя процесса вручную.",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color="#666666",
            justify="left",
        )
        tip.pack(anchor="w")

        self._render_whitelist()


    def _on_slider(self, value: float) -> None:
        self.engine.set_target(value)
        self.level_value.configure(text=f"{int(value * 100)}%")
        self._persist()

    def _on_mode(self, value: str) -> None:
        mode = "aggressive" if value == "Агрессивный" else "comfort"
        self.engine.set_mode(mode)
        self._update_mode_hint()
        self._persist()

    def _update_mode_hint(self) -> None:
        if self.engine.mode == "aggressive":
            text = "Агрессивный: приложения сразу получают нужную громкость (без плавности)."
        else:
            text = "Комфорт: громкость приложений плавно поднимается и опускается."
        self.mode_hint.configure(text=text)

    def _update_master_label(self) -> None:
        mv = int(self.engine.master_volume * 100)
        if self.engine.running:
            text = f"Системная громкость: {mv}%  →  100% (авто)"
            color = RED
        else:
            text = f"Системная громкость: {mv}%"
            color = "#666666"
        self.master_label.configure(text=text, text_color=color)

    def _play_preview(self) -> None:
        play_preview(self.slider.get())

    def _open_about(self) -> None:
        if self._about_window is not None and self._about_window.winfo_exists():
            self._about_window.focus()
            self._about_window.lift()
            return
        self._about_window = AboutWindow(self)

    def _toggle_engine(self) -> None:
        if self.engine.running:
            self.engine.stop()
            self.start_btn.configure(text="ЗАПУСТИТЬ", fg_color=RED, hover_color=RED_GLOW)
            self.status_label.configure(text="STANDBY", text_color=MUTED)
            self.status_dot.configure(text_color=MUTED)
        else:
            self.engine.start()
            self.start_btn.configure(text="ОСТАНОВИТЬ", fg_color=RED_DIM, hover_color="#5A0200")
            self.status_label.configure(text="ACTIVE", text_color=RED)
            self.status_dot.configure(text_color=RED)
        self._update_master_label()

    def _persist(self) -> None:
        save_config(
            {
                "target": round(float(self.slider.get()), 3),
                "mode": self.engine.mode,
                "whitelist": sorted(self.engine.whitelist),
            }
        )

    def _add_whitelist_from_entry(self) -> None:
        name = self.whitelist_entry.get().strip()
        if not name:
            return
        if not name.lower().endswith(".exe"):
            name = f"{name}.exe"
        self.engine.add_to_whitelist(name)
        self.whitelist_entry.delete(0, "end")
        self._render_whitelist()
        self._persist()

    def _add_whitelist(self, name: str) -> None:
        self.engine.add_to_whitelist(name)
        self._render_whitelist()
        self._persist()

    def _remove_whitelist(self, name: str) -> None:
        self.engine.remove_from_whitelist(name)
        self._render_whitelist()
        self._persist()

    def _render_whitelist(self) -> None:
        for child in self.whitelist_box.winfo_children():
            child.destroy()

        items = sorted(self.engine.whitelist)
        if not items:
            ctk.CTkLabel(
                self.whitelist_box,
                text="Список пуст",
                text_color="#555555",
                font=ctk.CTkFont(size=12),
            ).pack(pady=16)
            return

        for name in items:
            row = ctk.CTkFrame(self.whitelist_box, fg_color="transparent")
            row.pack(fill="x", padx=8, pady=4)

            ctk.CTkLabel(
                row,
                text=name,
                anchor="w",
                text_color=TEXT,
                font=ctk.CTkFont(family="Consolas", size=12),
            ).pack(side="left", fill="x", expand=True)

            ctk.CTkButton(
                row,
                text="×",
                width=30,
                height=26,
                corner_radius=4,
                fg_color="#2A1515",
                hover_color=RED_DIM,
                text_color=RED,
                command=lambda n=name: self._remove_whitelist(n),
            ).pack(side="right")

    def _refresh_sessions_idle(self) -> None:
        try:
            sessions = self.engine.list_sessions()
            self._paint_sessions(sessions)
            self._update_master_label()
        except Exception as exc:
            messagebox.showerror("AutoAudio", f"Не удалось получить сессии:\n{exc}")

    def _on_sessions(self, sessions: list[SessionInfo]) -> None:
        self.after(0, lambda: (self._paint_sessions(sessions), self._update_master_label()))

    def _paint_sessions(self, sessions: list[SessionInfo]) -> None:
        self._session_cache = sessions
        for child in self.sessions_box.winfo_children():
            child.destroy()

        if not sessions:
            ctk.CTkLabel(
                self.sessions_box,
                text="Нет активных приложений со звуком",
                text_color="#555555",
                font=ctk.CTkFont(size=12),
            ).pack(pady=20)
            return

 
        best: dict[str, SessionInfo] = {}
        for s in sessions:
            key = s.name.lower()
            if key not in best or s.peak > best[key].peak:
                best[key] = s

        for s in sorted(best.values(), key=lambda x: x.name.lower()):
            protected = self.engine.is_protected(s.name, s.pid)
            row = ctk.CTkFrame(self.sessions_box, fg_color="#151515", corner_radius=6)
            row.pack(fill="x", padx=6, pady=4)

            left = ctk.CTkFrame(row, fg_color="transparent")
            left.pack(side="left", fill="x", expand=True, padx=10, pady=8)

            name_color = MUTED if protected else TEXT
            ctk.CTkLabel(
                left,
                text=s.name,
                anchor="w",
                text_color=name_color,
                font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
            ).pack(anchor="w")

            meta = f"громкость {int(s.volume * 100)}%  ·  пик {int(s.peak * 100)}%"
            if protected:
                meta += "  ·  whitelist"
            ctk.CTkLabel(
                left,
                text=meta,
                anchor="w",
                text_color="#666666",
                font=ctk.CTkFont(size=11),
            ).pack(anchor="w")

    
            bar_bg = ctk.CTkFrame(left, fg_color="#222222", height=4, corner_radius=2)
            bar_bg.pack(fill="x", pady=(6, 0))
            fill_w = max(2, int(220 * min(1.0, s.peak)))
            bar = ctk.CTkFrame(
                bar_bg,
                fg_color=RED if s.peak > 0.02 else "#333333",
                height=4,
                width=fill_w,
                corner_radius=2,
            )
            bar.place(x=0, y=0)

            if not protected:
                ctk.CTkButton(
                    row,
                    text="В список",
                    width=88,
                    height=30,
                    corner_radius=5,
                    fg_color=PANEL,
                    hover_color=RED_DIM,
                    border_width=1,
                    border_color=BORDER,
                    text_color=TEXT,
                    font=ctk.CTkFont(size=11),
                    command=lambda n=s.name: self._add_whitelist(n),
                ).pack(side="right", padx=10, pady=10)

    def _animate_status(self) -> None:
        if self.engine.running:
            self._pulse = not self._pulse
            self.status_dot.configure(text_color=RED if self._pulse else RED_DIM)
        self.after(450, self._animate_status)

    def _on_close(self) -> None:
        self._persist()
        if self.engine.running:
            self.engine.stop()
        self.destroy()


def main() -> None:
    app = AutoAudioApp()
    app.mainloop()


if __name__ == "__main__":
    main()
