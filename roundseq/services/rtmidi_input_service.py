"""Real MIDI input service using python-rtmidi via mido."""
from __future__ import annotations

from typing import Optional

import mido
from kivy.clock import Clock

from .midi_input_service import MidiInputService


class RtmidiInputService(MidiInputService):
    """MIDI input service using mido/rtmidi.

    rtmidi delivers callbacks on its own thread; we marshal each message
    onto the Kivy main thread before dispatching to subscribers.
    """

    def __init__(self):
        super().__init__()
        self._port: Optional[mido.ports.BaseInput] = None

    def connect(self, port_name: Optional[str] = None) -> bool:
        try:
            if port_name:
                self._port = mido.open_input(port_name, callback=self._on_message)
            else:
                ports = self.list_ports()
                if not ports:
                    print("[MIDI-IN] No input ports available")
                    return False

                selected = ports[0]
                for port in ports:
                    if "pisound" in port.lower():
                        selected = port
                        break
                print(f"[MIDI-IN] Available input ports: {ports}")
                self._port = mido.open_input(selected, callback=self._on_message)

            self._connected = True
            print(f"[MIDI-IN] Connected to: {self._port.name}")
            return True
        except Exception as e:
            print(f"[MIDI-IN] Connection failed: {e}")
            return False

    def disconnect(self) -> None:
        if self._port:
            self._port.close()
            print(f"[MIDI-IN] Disconnected")
            self._port = None
            self._connected = False

    def list_ports(self) -> list[str]:
        return mido.get_input_names()

    def _on_message(self, message) -> None:
        # Runs on rtmidi's thread — hop to Kivy main thread before dispatch.
        Clock.schedule_once(lambda dt, m=message: self._dispatch(m), 0)
