from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import Callable, Literal

from pycaw.pycaw import (
    AudioUtilities,
    IAudioMeterInformation,
    ISimpleAudioVolume,
)

ModeName = Literal["comfort", "aggressive"]

MODES: dict[ModeName, dict[str, float]] = {
    "comfort": {
        "interval": 0.10,
        "boost_step": 0.07,
        "cut_step": 0.05,
        "peak_smooth": 0.40,
    },
    "aggressive": {
        "interval": 0.03,
        "boost_step": 1.0,
        "cut_step": 1.0,
        "peak_smooth": 1.0,
    },
}


@dataclass
class SessionInfo:
    name: str
    pid: int
    volume: float
    peak: float
    muted: bool


@dataclass
class _TrackState:
    source: float = 0.0
    last_active: float = 0.0


@dataclass
class AudioEngine:
    """
    1) Системная (главная) громкость → 100%
    2) Громкость каждого приложения подгоняется под целевой уровень
    """

    target: float = 0.45
    mode: ModeName = "comfort"
    whitelist: set[str] = field(default_factory=set)
    exclude_self: bool = True
    silence_gate: float = 0.006

    _running: bool = field(default=False, init=False, repr=False)
    _thread: threading.Thread | None = field(default=None, init=False, repr=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False, repr=False)
    _on_sessions: Callable[[list[SessionInfo]], None] | None = field(
        default=None, init=False, repr=False
    )
    _self_pid: int = field(default=0, init=False, repr=False)
    _tracks: dict[str, _TrackState] = field(default_factory=dict, init=False, repr=False)
    _saved_master: float | None = field(default=None, init=False, repr=False)
    _master_volume: float = field(default=1.0, init=False, repr=False)

    def __post_init__(self) -> None:
        import os

        self._self_pid = os.getpid()
        self.whitelist = {n.lower() for n in self.whitelist}
        if self.mode not in MODES:
            self.mode = "comfort"
        self._read_master()

    @property
    def master_volume(self) -> float:
        return self._master_volume

    def set_target(self, value: float) -> None:
        with self._lock:
            self.target = max(0.05, min(1.0, float(value)))

    def set_mode(self, mode: ModeName | str) -> None:
        with self._lock:
            if mode in MODES:
                self.mode = mode
                self._tracks.clear()

    def set_whitelist(self, names: set[str] | list[str]) -> None:
        with self._lock:
            self.whitelist = {n.strip().lower() for n in names if n.strip()}

    def add_to_whitelist(self, name: str) -> None:
        with self._lock:
            self.whitelist.add(name.strip().lower())

    def remove_from_whitelist(self, name: str) -> None:
        with self._lock:
            self.whitelist.discard(name.strip().lower())

    def on_sessions_update(self, callback: Callable[[list[SessionInfo]], None]) -> None:
        self._on_sessions = callback

    @property
    def running(self) -> bool:
        return self._running

    def _endpoint(self):
        return AudioUtilities.GetSpeakers().EndpointVolume

    def _read_master(self) -> float:
        try:
            self._master_volume = float(self._endpoint().GetMasterVolumeLevelScalar())
        except Exception:
            pass
        return self._master_volume

    def _set_master_full(self) -> None:
        try:
            ep = self._endpoint()
            if self._saved_master is None:
                self._saved_master = float(ep.GetMasterVolumeLevelScalar())
            ep.SetMasterVolumeLevelScalar(1.0, None)
            self._master_volume = 1.0
        except Exception:
            self._read_master()

    def _restore_master(self) -> None:
        if self._saved_master is None:
            return
        try:
            self._endpoint().SetMasterVolumeLevelScalar(self._saved_master, None)
            self._master_volume = self._saved_master
        except Exception:
            pass
        self._saved_master = None

    def start(self) -> None:
        if self._running:
            return
        with self._lock:
            self._tracks.clear()
        self._set_master_full()
        self._running = True
        self._thread = threading.Thread(target=self._loop, name="AudioEngine", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        self._thread = None
        self._restore_master()
        with self._lock:
            self._tracks.clear()

    def list_sessions(self) -> list[SessionInfo]:
        self._read_master()
        return self._collect(adjust=False)

    def _is_whitelisted(self, name: str, pid: int) -> bool:
        if self.exclude_self and pid == self._self_pid:
            return True
        key = name.lower()
        if key in self.whitelist:
            return True
        base = key[:-4] if key.endswith(".exe") else key
        for item in self.whitelist:
            item_base = item[:-4] if item.endswith(".exe") else item
            if base == item_base or key == item:
                return True
        return False

    def is_protected(self, name: str, pid: int) -> bool:
        with self._lock:
            return self._is_whitelisted(name, pid)

    def _key(self, name: str, pid: int) -> str:
        return f"{pid}:{name.lower()}"

    def _estimate_source(self, track: _TrackState, peak: float, vol: float, smooth: float) -> float:
        vol_safe = max(vol, 0.05)
        instant = peak / vol_safe
        instant = max(0.01, min(2.0, instant))

        if track.source <= 0 or smooth >= 0.999:
            track.source = instant
        elif instant < track.source:
            a = min(1.0, smooth * 1.5)
            track.source = track.source * (1.0 - a) + instant * a
        else:
            a = smooth * 0.5
            track.source = track.source * (1.0 - a) + instant * a

        return max(track.source, 0.01)

    def _desired_app_volume(self, source: float, target: float) -> float:

        desired = target / source
        return max(0.05, min(1.0, desired))

    def _apply_step(
        self,
        current: float,
        desired: float,
        mode: ModeName,
        cfg: dict[str, float],
    ) -> float:
        if mode == "aggressive":
            return desired

        delta = desired - current
        if delta > 0:
            step = min(delta, cfg["boost_step"])
        else:
            step = max(delta, -cfg["cut_step"])
        return max(0.05, min(1.0, current + step))

    def _collect(self, adjust: bool) -> list[SessionInfo]:
        with self._lock:
            target = self.target
            mode = self.mode
            cfg = MODES[mode]
            peak_smooth = cfg["peak_smooth"]

        if adjust:
            self._set_master_full()

        result: list[SessionInfo] = []
        seen: set[str] = set()
        now = time.monotonic()

        try:
            sessions = AudioUtilities.GetAllSessions()
        except Exception:
            return result

        for session in sessions:
            if session.Process is None:
                continue
            try:
                name = session.Process.name() or "unknown"
                pid = int(session.Process.pid)
            except Exception:
                continue

            try:
                volume_iface = session._ctl.QueryInterface(ISimpleAudioVolume)
                meter = session._ctl.QueryInterface(IAudioMeterInformation)
                peak = float(meter.GetPeakValue())
                vol = float(volume_iface.GetMasterVolume())
                muted = bool(volume_iface.GetMute())
            except Exception:
                continue

            result.append(SessionInfo(name=name, pid=pid, volume=vol, peak=peak, muted=muted))
            key = self._key(name, pid)
            seen.add(key)

            if not adjust or muted:
                continue
            if self.is_protected(name, pid):
                continue
            if peak < self.silence_gate:
                continue

            with self._lock:
                track = self._tracks.get(key)
                if track is None:
                    track = _TrackState()
                    self._tracks[key] = track

            source = self._estimate_source(track, peak, vol, peak_smooth)
            track.last_active = now

            desired = self._desired_app_volume(source, target)
            new_vol = self._apply_step(vol, desired, mode, cfg)
            new_vol = max(0.05, min(1.0, float(new_vol)))

            if abs(new_vol - vol) < 0.003:
                continue
            try:
                volume_iface.SetMasterVolume(new_vol, None)
            except Exception:
                pass

        with self._lock:
            for key in list(self._tracks):
                if key not in seen:
                    del self._tracks[key]

        return result

    def _loop(self) -> None:
        while self._running:
            with self._lock:
                interval = MODES[self.mode]["interval"]
            try:
                sessions = self._collect(adjust=True)
                if self._on_sessions:
                    self._on_sessions(sessions)
            except Exception:
                pass
            time.sleep(interval)
