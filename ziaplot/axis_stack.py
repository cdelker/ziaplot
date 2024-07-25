''' Axis Stack '''

from __future__ import annotations
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .drawable import Drawable

axis_stack: dict[Drawable, Optional[Drawable]] = {}
pause: bool = False


def push_axis(axis: Drawable) -> None:
    ''' Add a plot to the stack '''
    axis_stack[axis] = None

def pop_axis(axis: Drawable) -> None:
    ''' Remove the drawing from the stack '''
    axis_stack.pop(axis)

def push_figure(figure: Optional[Drawable]) -> None:
    if not pause and len(axis_stack) > 0:
        axis, prev_figure = list(axis_stack.items())[-1]
        if prev_figure is not None and prev_figure not in axis:
            axis.add(prev_figure)
        axis_stack[axis] = figure

def current_axis() -> Optional[Drawable]:
    try:
        return list(axis_stack.keys())[-1]
    except IndexError:
        return None
