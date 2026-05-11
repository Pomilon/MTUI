import sys
import unittest
from unittest.mock import MagicMock, patch
import os

# PRE-MOCK msvcrt
mock_msvcrt = MagicMock()
sys.modules['msvcrt'] = mock_msvcrt

# Mock APPDATA for pyfiglet
os.environ['APPDATA'] = '/tmp'

from rc_tui.input import InputManager
from rc_tui.events import KeyEvent

class TestCrossPlatformInput(unittest.TestCase):
    def test_windows_arrow_keys(self):
        """Test that Windows scan codes are correctly mapped to ANSI sequences."""
        with patch('rc_tui.input._get_platform', return_value='win32'):
            input_manager = InputManager()
            # Simulate pressing UP arrow on Windows: '\xe0' followed by 'H'
            mock_msvcrt.kbhit.side_effect = [True, True, False]
            mock_msvcrt.getwch.side_effect = ['\xe0', 'H']
            
            events = input_manager.get_events()
            self.assertEqual(len(events), 1)
            self.assertEqual(events[0].key, 'UP')

    def test_windows_enter_key(self):
        """Test that Windows \r is mapped to \n."""
        with patch('rc_tui.input._get_platform', return_value='win32'):
            input_manager = InputManager()
            mock_msvcrt.kbhit.side_effect = [True, False]
            mock_msvcrt.getwch.side_effect = ['\r']
            
            events = input_manager.get_events()
            self.assertEqual(len(events), 1)
            self.assertEqual(events[0].key, 'ENTER')

    def test_linux_ansi_parsing(self):
        """Test that Linux/Unix ANSI parsing remains intact."""
        with patch('rc_tui.input._get_platform', return_value='linux'):
            input_manager = InputManager()
            # Simulate ANSI escape for LEFT arrow
            with patch('os.read') as mock_read:
                with patch('select.select') as mock_select:
                    with patch('sys.stdin') as mock_stdin:
                        mock_stdin.fileno.return_value = 0
                        mock_select.return_value = ([mock_stdin], [], [])
                        mock_read.return_value = b'\x1b[D'
                        
                        events = input_manager.get_events()
                        self.assertEqual(len(events), 1)
                        self.assertEqual(events[0].key, 'LEFT')

if __name__ == '__main__':
    unittest.main()
