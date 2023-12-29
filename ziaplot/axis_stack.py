''' Axis Stack '''

from __future__ import annotations
from typing import Union, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .axes import BasePlot
    from .series import Series
    from .layout import Layout
    from .drawable import Drawable

axis_stack: dict[Drawable, Optional[Drawable]] = {}
pause: bool = False


def push_axis(axis: Drawable) -> None:
    ''' Add a plot to the stack '''
    axis_stack[axis] = None

def pop_axis(axis: Drawable) -> None:
    ''' Remove the drawing from the stack '''
    axis_stack.pop(axis)

def push_series(series: Optional[Drawable]) -> None:
    if not pause and len(axis_stack) > 0:
        axis, prev_series = list(axis_stack.items())[-1]
        if prev_series is not None and prev_series not in axis:
            axis.add(prev_series)
        axis_stack[axis] = series

def current_axis() -> Optional[Drawable]:
    try:
        return list(axis_stack.keys())[-1]
    except IndexError:
        return None