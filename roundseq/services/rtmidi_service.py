"""Real MIDI service using python-rtmidi via mido."""
from __future__ import annotations

from typing import Optional

import mido

from .midi_service import MidiService
from ..config import DEFAULT_VELOCITY, DEFAULT_CHANNEL


class RtmidiService(MidiService):
    """MIDI service using mido/rtmidi for real MIDI output."""

    def __init__(self, channel: int = DEFAULT_CHANNEL):
        super().__init__(channel)
        self._port: Optional[mido.ports.BaseOutput] = None

    def connect(self, port_name: Optional[str] = None) -> bool:
        """Connect to a MIDI output port.

        Args:
            port_name: Name of port to connect to. If None, uses first available.
        """
        try:
            if port_name:
                self._port = mido.open_output(port_name)
            else:
                ports = self.list_ports()
                if ports:
                    self._port = mido.open_output(ports[0])
                else:
                    print("[MIDI] No output ports available")
                    return False

            self._connected = True
            print(f"[MIDI] Connected to: {self._port.name}")
            return True
        except Exception as e:
            print(f"[MIDI] Connection failed: {e}")
            return False

    def disconnect(self) -> None:
        """Disconnect from the MIDI port."""
        if self._port:
            self._port.close()
            print(f"[MIDI] Disconnected")
            self._port = None
            self._connected = False

    def note_on(self, note: int, velocity: int = DEFAULT_VELOCITY) -> None:
        """Send a note on message."""
        if not self._port:
            return
        msg = mido.Message("note_on", note=note, velocity=velocity, channel=self.channel)
        self._port.send(msg)
        name = self.note_name(note)
        print(f"[MIDI] Note ON:  {name} (note={note}, vel={velocity})")

    def note_off(self, note: int) -> None:
        """Send a note off message."""
        if not self._port:
            return
        msg = mido.Message("note_off", note=note, velocity=0, channel=self.channel)
        self._port.send(msg)
        name = self.note_name(note)
        print(f"[MIDI] Note OFF: {name} (note={note})")

    def list_ports(self) -> list[str]:
        """List available MIDI output ports."""
        return mido.get_output_names()
