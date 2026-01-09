"""MIDI service interface and factory."""

from abc import ABC, abstractmethod
from typing import Optional

from ..platform import is_raspberry_pi
from ..config import DEFAULT_VELOCITY, DEFAULT_CHANNEL, NOTE_NAMES


class MidiService(ABC):
    """Abstract base class for MIDI services."""

    def __init__(self, channel: int = DEFAULT_CHANNEL):
        self.channel = channel
        self._connected = False

    @abstractmethod
    def connect(self, port_name: Optional[str] = None) -> bool:
        """Connect to a MIDI output port."""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Disconnect from the MIDI port."""
        pass

    @abstractmethod
    def note_on(self, note: int, velocity: int = DEFAULT_VELOCITY) -> None:
        """Send a note on message."""
        pass

    @abstractmethod
    def note_off(self, note: int) -> None:
        """Send a note off message."""
        pass

    @abstractmethod
    def list_ports(self) -> list[str]:
        """List available MIDI output ports."""
        pass

    @property
    def connected(self) -> bool:
        """Return True if connected to a MIDI port."""
        return self._connected

    @staticmethod
    def note_name(note: int) -> str:
        """Convert MIDI note number to name (e.g., 60 -> 'C4')."""
        octave = (note // 12) - 1
        name = NOTE_NAMES[note % 12]
        return f"{name}{octave}"


def get_midi_service(use_mock: Optional[bool] = None) -> MidiService:
    """Factory function to get appropriate MIDI service.

    Args:
        use_mock: Force mock service if True, real service if False.
                  If None, auto-detect based on platform.
    """
    if use_mock is None:
        use_mock = not is_raspberry_pi()

    if use_mock:
        from .mock_midi_service import MockMidiService
        return MockMidiService()
    else:
        from .rtmidi_service import RtmidiService
        return RtmidiService()
