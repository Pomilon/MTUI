import sys
import os
from .events import KeyEvent, MouseEvent, Event
from typing import Optional, List

# Platform-specific imports
def _get_platform():
    return sys.platform

class InputManager:
    def __init__(self):
        self.platform = _get_platform()
        self.key_map = {
            '\x1b[A': 'UP',
            '\x1b[B': 'DOWN',
            '\x1b[C': 'RIGHT',
            '\x1b[D': 'LEFT',
            '\x1b[H': 'HOME',
            '\x1b[F': 'END',
            '\x1b[3~': 'DELETE',
            '\x1b[5~': 'PAGE_UP',
            '\x1b[6~': 'PAGE_DOWN',
            '\r': 'ENTER',
            '\n': 'ENTER',
            '\x7f': 'BACKSPACE',
            '\x08': 'BACKSPACE', # Windows backspace
            '\x03': 'CTRL_C',
            '\t': 'TAB',
            '\x1b': 'ESC',
            '\x1b[24~': 'F12',
        }
        self._buffer = ""

    def get_events(self) -> List[Event]:
        try:
            if self.platform == "win32":
                import msvcrt
                # Windows implementation using msvcrt
                while msvcrt.kbhit():
                    char = msvcrt.getwch()
                    # msvcrt.getwch() returns some special keys as '\x00' or '\xe0' followed by another char
                    if char in ('\x00', '\xe0'):
                        if msvcrt.kbhit():
                            next_char = msvcrt.getwch()
                            # Map Windows scan codes to ANSI-like sequences or names
                            scan_map = {
                                'H': '\x1b[A', # UP
                                'P': '\x1b[B', # DOWN
                                'M': '\x1b[C', # RIGHT
                                'K': '\x1b[D', # LEFT
                                'G': '\x1b[H', # HOME
                                'O': '\x1b[F', # END
                                'S': '\x1b[3~', # DELETE
                                'I': '\x1b[5~', # PAGE_UP
                                'Q': '\x1b[6~', # PAGE_DOWN
                                '\x87': '\x1b[24~', # F12 (Approximate)
                            }
                            if next_char in scan_map:
                                self._buffer += scan_map[next_char]
                            continue
                    
                    if char == '\r': # Windows uses \r for Enter
                        char = '\n'
                    self._buffer += char
            else:
                import select
                # Unix implementation using select
                r, _, _ = select.select([sys.stdin], [], [], 0.001)
                if r:
                    raw_data = os.read(sys.stdin.fileno(), 4096)
                    if raw_data:
                        self._buffer += raw_data.decode('utf-8', errors='ignore')
        except (IOError, AttributeError, ImportError):
            # Known issues in some environments (e.g. non-TTY stdin in tests)
            pass

        events = []
        while self._buffer:
            event, consumed = self._parse_event(self._buffer)
            if consumed == 0:
                break
            if event:
                events.append(event)
            self._buffer = self._buffer[consumed:]
        return events

    def _parse_event(self, data: str) -> (Optional[Event], int):
        if not data:
            return None, 0

        # Non-escape character
        if data[0] != '\x1b':
            char = data[0]
            return KeyEvent(self.key_map.get(char, char)), 1

        # Single ESC (might be start of a sequence)
        if len(data) == 1:
            return None, 0

        # Not a CSI sequence (e.g., Alt+key)
        if data[1] != '[':
            return KeyEvent(data[:2]), 2

        # CSI sequence: look for the terminator
        for i in range(2, len(data)):
            c = data[i]
            if 'a' <= c <= 'z' or 'A' <= c <= 'Z' or c == '~':
                seq = data[:i+1]
                
                # Mouse SGR Mode: \x1b[<button;x;y;M/m
                if seq.startswith('\x1b[<'):
                    try:
                        terminator = seq[-1]
                        parts = seq[3:-1].split(';')
                        if len(parts) == 3:
                            b = int(parts[0])
                            x = int(parts[1]) - 1
                            y = int(parts[2]) - 1
                            if terminator == 'M': # Button Press / Scroll / Motion
                                if b == 0: return MouseEvent('CLICK', x, y, button=1), len(seq)
                                if b == 1: return MouseEvent('CLICK', x, y, button=2), len(seq)
                                if b == 2: return MouseEvent('CLICK', x, y, button=3), len(seq)
                                if b == 35: return MouseEvent('MOVE', x, y, button=0), len(seq)
                                if b == 64: return MouseEvent('SCROLL', x, y, delta=-1), len(seq)
                                if b == 65: return MouseEvent('SCROLL', x, y, delta=1), len(seq)
                                if b & 32: return MouseEvent('MOVE', x, y, button=(b & 3)), len(seq)
                            elif terminator == 'm': # Release
                                return MouseEvent('RELEASE', x, y, button=(b & 3)), len(seq)
                        return None, len(seq)
                    except Exception:
                        return None, len(seq)
                
                return KeyEvent(self.key_map.get(seq, seq)), len(seq)
        
        # Buffer incomplete sequence for a bit, then discard if too long
        if len(data) > 32:
            return None, 1
        return None, 0
