"""MIDI input service interface and factory."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Callable, Optional

from ..platform import is_raspberry_pi


MidiCallback = Callable[[object], None]


class MidiInputService(ABC):
    """Abstract base class for MIDI input services.

    Subscribers receive mido-style messages (must expose a `.type` attribute
    and any type-specific fields like `.pos` for songpos).
    """

    def __init__(self):
        self._connected = False
        self._subscribers: list[MidiCallback] = []

    @abstractmethod
    def connect(self, port_name: Optional[str] = None) -> bool:
        """Connect to a MIDI input port."""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from the MIDI port."""
        pass

    @abstractmethod
    def list_ports(self) -> list[str]:
        """List available MIDI input ports."""
        pass

    def subscribe(self, callback: MidiCallback) -> None:
        """Register a callback to receive MIDI messages on the Kivy main thread."""
        self._subscribers.append(callback)

    def unsubscribe(self, callback: MidiCallback) -> None:
        if callback in self._subscribers:
            self._subscribers.remove(callback)

    def _dispatch(self, message) -> None:
        """Deliver a message to all subscribers. Must be called on the Kivy main thread."""
        for cb in self._subscribers:
            cb(message)

    @property
    def connected(self) -> bool:
        return self._connected


def get_midi_input_service(use_mock: Optional[bool] = None) -> MidiInputService:
    """Factory for the MIDI input service.

    Args:
        use_mock: Force mock if True, real if False. None auto-detects.
    """
    if use_mock is True:
        from .mock_midi_input_service import MockMidiInputService
        return MockMidiInputService()

    if use_mock is False or is_raspberry_pi():
        try:
            from .rtmidi_input_service import RtmidiInputService
            import mido
            mido.get_input_names()
            return RtmidiInputService()
        except (ImportError, Exception) as e:
            print(f"[MIDI-IN] rtmidi not available, falling back to mock: {e}")

    from .mock_midi_input_service import MockMidiInputService
    return MockMidiInputService()
