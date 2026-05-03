from dataclasses import dataclass
from typing import Optional, Union

@dataclass
class KeyEvent:
    key: str
    ctrl: bool = False
    shift: bool = False
    alt: bool = False

@dataclass
class MouseEvent:
    type: str # 'CLICK', 'MOVE', 'SCROLL'
    x: int
    y: int
    button: Optional[int] = None
    delta: int = 0 # For scroll

Event = Union[KeyEvent, MouseEvent]
