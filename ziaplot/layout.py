''' Layouts for creating multi-axis plots '''

import xml.etree.ElementTree as ET

from .axes import XyPlot
from .series import Series
from .canvas import Canvas, ViewBox
from .drawable import Drawable
from . import axis_stack
from typing import Optional


class LayoutGap(Drawable):
    ''' Empty placeholder for layout '''
    def __init__(self):
        axis_stack.push_series(self)
        super().__init__()


class Layout(Drawable):
    ''' Base class for multi-axis plots.

        Args:
            axes: The axes, or other layouts, to include
            width: Width of the figure/layout
            height: Height of the figure/layout
            sep: Distance between subplots

        Note:
            height and width are ignored if the layout is
            added to another layout.
    '''
    def __init__(self, *axes: Drawable, width: float = 600, height: float = 400, sep: float = 10):
        self.axes = list(axes)
        self.sep: float = sep
        self.width: float = width
        self.height: float = height
        self.x: float = 0
        self.y: float = 0

    def __contains__(self, axis: Drawable):
        return axis in self.axes

    def __enter__(self):
        axis_stack.push_series(self)
        axis_stack.push_axis(self)
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        ''' Exit context manager - save to file and display '''
        axis_stack.push_series(None)
        axis_stack.pop_axis(self)
        if axis_stack.current_axis() is None:
            # Display if not inside another layout
            try:
                display(self)
            except NameError:  # Not in Jupyter/IPython
                pass
    
    def add(self, axis: Drawable) -> None:
        self.axes.append(axis)
    
    def svgxml(self, border: bool = False) -> ET.Element:
        ''' XML for standalone SVG '''
        canvas = Canvas(self.width, self.height)
        self._xml(canvas)
        if border:
            attrib = {'x': '0', 'y': '0',
                      'width': '100%', 'height': '100%',
                      'fill': 'none', 'stroke': 'black'}
            ET.SubElement(canvas.group, 'rect', attrib=attrib)
        return canvas.xml()


class Hlayout(Layout):
    ''' Horizontal Plot Layout

        Args:
            axes: The axes and/or VLayouts to draw, evenly spaced horizontally
            width: Width of the figure/layout
            height: Height of the figure/layout
            sep: Distance between subplots

        Note:
            height and width are ignored if the layout is
            added to another layout.
    '''
    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None) -> ET.Element:
        ''' Add XML elements to the canvas '''
        N = len(self.axes)
        axwidth = (self.width - self.sep*(N-1)) / N

        # Calculate viewbox for each axis
        vboxes = []
        for i, ax in enumerate(self.axes):
            x = i * (axwidth+self.sep)

            if isinstance(ax, Vlayout):
                ax.width = axwidth
                ax.height = self.height
                ax.x = x
            vboxes.append(ViewBox(x, self.y, axwidth, self.height))

        # Draw all backgrounds first in case of overlap
        for i, ax in enumerate(self.axes):
            if hasattr(ax, 'style') and hasattr(ax.style, 'bgcolor'):  # type: ignore

                canvas.setviewbox(vboxes[i], clippad=self.sep)
                canvas.rect(vboxes[i].x, vboxes[i].y,
                            axwidth+self.sep,
                            self.height+self.sep,
                            fill=ax.style.bgcolor,   # type: ignore
                            strokecolor=ax.style.bgcolor)   # type: ignore

        # Now draw the axes
        for i, ax in enumerate(self.axes):
            canvas.setviewbox(vboxes[i])
            if isinstance(ax, Series):
                a = XyPlot()
                a.add(ax)
                a._xml(canvas)
            else:
                ax._xml(canvas)
            canvas.resetviewbox()
        return canvas.xml()


class Vlayout(Layout):
    ''' Vertical Plot Layout

        Args:
            axes: The axes and/or HLayouts to draw, evenly spaced vertically
            width: Width of the figure/layout
            height: Height of the figure/layout
            sep: Distance between subplots

        Note:
            height and width are ignored if the layout is
            added to another layout.
    '''
    def _xml(self, canvas: Canvas, databox: Optional[ViewBox] = None) -> ET.Element:
        ''' Add XML elements to the canvas '''
        N = len(self.axes)
        axheight = (self.height - self.sep*(N-1)) / N

        # Calculate viewbox for each axis
        vboxes = []
        for i, ax in enumerate(self.axes):
            y = ((N-1)-i) * (axheight+self.sep)
            if isinstance(ax, Hlayout):
                ax.width = self.width
                ax.height = axheight
                ax.y = y

            vboxes.append(ViewBox(self.x, y, self.width, axheight))

        # Draw all backgrounds first in case of overlap
        for i, ax in enumerate(self.axes):
            canvas.setviewbox(vboxes[i], clippad=self.sep)
            if hasattr(ax, 'style') and hasattr(ax.style, 'bgcolor'):  # type: ignore
                canvas.rect(vboxes[i].x, vboxes[i].y,
                            self.width+self.sep,
                            axheight+self.sep,
                            fill=ax.style.bgcolor,  # type: ignore
                            strokecolor=ax.style.bgcolor)  # type: ignore

        # Now draw the axes
        for i, ax in enumerate(self.axes):
            canvas.setviewbox(vboxes[i])
            if isinstance(ax, Series):
                a = XyPlot()
                a.add(ax)
                a._xml(canvas)
            else:
                ax._xml(canvas)
            canvas.resetviewbox()

        return canvas.xml()
