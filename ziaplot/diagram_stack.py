''' Diagram Stack for recording Diagrams added inside context managers '''

from __future__ import annotations
from typing import Optional, TYPE_CHECKING


if TYPE_CHECKING:
    from .drawable import Drawable
    from .container import Container


diagram_stack: dict[Container, Optional[Drawable]] = {}
pause: bool = False
apply_style: list[str] = []

# Globally track unused ID names for SVG element id= attributes
svg_element_id: int = -1


def push_diagram(diagram: Container) -> None:
    ''' Add a plot to the stack '''
    diagram_stack[diagram] = None


def pop_diagram(diagram: Container) -> None:
    ''' Remove the drawing from the stack '''
    diagram_stack.pop(diagram)


def push_component(comp: Optional[Drawable]) -> None:
    if not pause and len(diagram_stack) > 0:
        diagram, prev_comp = list(diagram_stack.items())[-1]
        if prev_comp is not None and prev_comp not in diagram:
            diagram.add(prev_comp)  # type: ignore
            for sty in apply_style:
                if hasattr(prev_comp, 'style'):
                    prev_comp.style(sty)
        diagram_stack[diagram] = comp


def current_diagram() -> Optional[Drawable]:
    try:
        return list(diagram_stack.keys())[-1]
    except IndexError:
        return None


def get_elmid():
    ''' Get unique ID for use in an SVG id= attribute '''
    global svg_element_id
    svg_element_id += 1
    return f'zp{svg_element_id}'
