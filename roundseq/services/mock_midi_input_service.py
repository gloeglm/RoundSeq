"""Mock MIDI input service for development.

Generates a synthetic MIDI clock stream so the clock-viz screen can be
developed on macOS without a hardware clock source.
"""
from __future__ import annotations

from typing import Optional

from kivy.clock import Clock

from .midi_input_service import MidiInputService


class _MockMessage:
    """Duck-typed stand-in for mido.Message — exposes .type (and .pos for songpos)."""

    def __init__(self, type_: str, pos: int = 0):
        self.type = type_
        self.pos = pos


class MockMidiInputService(MidiInputService):
    """Emits a synthetic 120 BPM clock at 24 PPQN."""

    DEFAULT_BPM = 120

    def __init__(self, bpm: float = DEFAULT_BPM):
        super().__init__()
        self._bpm = bpm
        self._tick_event = None
        self._port_name: Optional[str] = None

    def connect(self, port_name: Optional[str] = None) -> bool:
        self._port_name = port_name or "Mock MIDI Input"
        self._connected = True
        print(f"[MockMIDI-IN] Connected to: {self._port_name} ({self._bpm} BPM)")

        # Immediately emit a start, then begin ticking at 24 PPQN.
        Clock.schedule_once(lambda dt: self._dispatch(_MockMessage("start")), 0)
        interval = 60.0 / (self._bpm * 24)
        self._tick_event = Clock.schedule_interval(self._emit_tick, interval)
        return True

    def disconnect(self) -> None:
        if self._tick_event is not None:
            self._tick_event.cancel()
            self._tick_event = None
        if self._connected:
            print(f"[MockMIDI-IN] Disconnected from: {self._port_name}")
            self._connected = False
            self._port_name = None

    def list_ports(self) -> list[str]:
        return ["Mock MIDI Input"]

    def _emit_tick(self, _dt) -> None:
        self._dispatch(_MockMessage("clock"))
