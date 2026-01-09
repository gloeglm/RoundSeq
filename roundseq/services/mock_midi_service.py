"""Mock MIDI service for development."""
from __future__ import annotations

from typing import Optional

from .midi_service import MidiService
from ..config import DEFAULT_VELOCITY, DEFAULT_CHANNEL


class MockMidiService(MidiService):
    """Mock MIDI service that logs to console."""

    def __init__(self, channel: int = DEFAULT_CHANNEL):
        super().__init__(channel)
        self._port_name = None

    def connect(self, port_name: Optional[str] = None) -> bool:
        """Simulate connecting to a MIDI port."""
        self._port_name = port_name or "Mock MIDI Output"
        self._connected = True
        print(f"[MockMIDI] Connected to: {self._port_name}")
        return True

    def disconnect(self) -> None:
        """Simulate disconnecting."""
        if self._connected:
            print(f"[MockMIDI] Disconnected from: {self._port_name}")
            self._connected = False
            self._port_name = None

    def note_on(self, note: int, velocity: int = DEFAULT_VELOCITY) -> None:
        """Log note on message."""
        name = self.note_name(note)
        print(f"[MockMIDI] Note ON:  {name} (note={note}, vel={velocity}, ch={self.channel})")

    def note_off(self, note: int) -> None:
        """Log note off message."""
        name = self.note_name(note)
        print(f"[MockMIDI] Note OFF: {name} (note={note}, ch={self.channel})")

    def list_ports(self) -> list[str]:
        """Return fake port list."""
        return ["Mock MIDI Output", "Mock MIDI Output 2"]
