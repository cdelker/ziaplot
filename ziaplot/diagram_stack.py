''' Diagram Stack for recording Diagrams added inside context managers '''

from __future__ import annotations
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .drawable import Drawable

diagram_stack: dict[Drawable, Optional[Drawable]] = {}
pause: bool = False


def push_diagram(diagram: Drawable) -> None:
    ''' Add a plot to the stack '''
    diagram_stack[diagram] = None

def pop_diagram(diagram: Drawable) -> None:
    ''' Remove the drawing from the stack '''
    diagram_stack.pop(diagram)

def push_component(comp: Optional[Drawable]) -> None:
    if not pause and len(diagram_stack) > 0:
        diagram, prev_comp = list(diagram_stack.items())[-1]
        if prev_comp is not None and prev_comp not in diagram:
            diagram.add(prev_comp)  # type: ignore
        diagram_stack[diagram] = comp

def current_diagram() -> Optional[Drawable]:
    try:
        return list(diagram_stack.keys())[-1]
    except IndexError:
        return None
