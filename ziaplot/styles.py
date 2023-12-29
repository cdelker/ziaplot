''' Predefined plotting Styles/Themes '''

from typing import Type
from copy import deepcopy

from . import styletypes
from .colors import ColorCycle

_default = styletypes.Style  # User-selected default style
Style = styletypes.Style     # Base style


def setdefault(style: Type[styletypes.Style]) -> None:
    ''' Set the default plotting style to use for all plots '''
    if style == Default:
        style = Lobo  # type: ignore
    global _default
    _default = style


def settextcolor(st: styletypes.Style, color: str):
    ''' Change all text colors in the style '''
    st.axis.xname.color = color
    st.axis.yname.color = color
    st.tick.text.color = color
    st.series.text.color = color
    st.series.colorbar.text.color = color
    st.legend.text.color = color
    st.polar.title.color = color
    st.pie.title.color = color
    st.pie.label.color = color


def setaxiscolor(st: styletypes.Style, color: str = 'black'):
    ''' Change color of all axes, ticks, and labels '''
    settextcolor(st, color)
    st.axis.color = color
    st.legend.border = color
    st.series.colorbar.bordercolor = color


def Default() -> styletypes.Style:
    ''' Get the default style as configured by setdefault. '''
    if callable(_default):
        return _default()
    else:
        return deepcopy(_default)


def Lobo() -> styletypes.Style:
    ''' Lobo style (default) '''
    return styletypes.Style()


def Taffy() -> styletypes.Style:
    ''' Taffy theme '''
    s = styletypes.Style()
    s.colorcycle = ColorCycle('#00a4bd', '#ff7a59', '#00bda5',
                              '#f2547d', '#6a78d1', '#f5C26b',
                              '#516f90', '#99acc2', '#cc3399',
                              '#99cc00')
    return s


def Pastel() -> styletypes.Style:
    ''' Pastel colors '''
    s = styletypes.Style()
    s.axis.bgcolor = '#fafafa'
    setaxiscolor(s, '#555555')
    s.series.marker.strokecolor = '#555555'
    s.series.border.color = '#555555'
    s.colorcycle = ColorCycle('#c6579A', '#ffbe9f', '#f1e6b2',
                              '#b6cfae', '#a7e6d7', '#9AdBe8',
                              '#decde7', '#ffa1cb', '#9a98b5',
                              '#7589bf')
    return s


def Bold() -> styletypes.Style:
    ''' Bold colors '''
    s = styletypes.Style()
    s.colorcycle = ColorCycle('red', 'orange', 'yellow', 'lime',
                              '#00aa00', 'blue', '#00eeee',
                              'violet', 'purple', 'silver')
    return s


def Dark() -> styletypes.Style:
    ''' Dark background theme - white on black, but same
        colors as Lobo theme.
    '''
    s = styletypes.Style()
    setaxiscolor(s, '#cccccc')
    s.bgcolor = 'black'
    s.axis.gridcolor = '#555555'
    s.axis.bgcolor = 'black'
    s.series.border.color = 'none'
    s.series.border.width = 0
    return s


def DarkBold() -> styletypes.Style:
    ''' Bold colors on dark background '''
    s = Dark()
    setaxiscolor(s, '#bbbbbb')
    s.colorcycle = ColorCycle('red',
                              'orange',
                              'yellow',
                              'lime',
                              '#00aa00',
                              'blue',
                              '#00eeee',
                              'violet',
                              'purple',
                              'silver')
    return s    


def DarkTaffy() -> styletypes.Style:
    ''' Dark Taffy Style '''
    s = Dark()
    s.colorcycle = ColorCycle('#00a4bd', '#ff7a59', '#00bda5',
                              '#f2547d', '#6a78d1', '#f5C26b',
                              '#516f90', '#99acc2', '#cc3399',
                              '#99cc00')
    return s


def DocStyle() -> styletypes.Style:
    ''' Style for ziaplot documentation '''
    s = Style()
    s.canvasw = 400
    s.canvash = 300
    return s
