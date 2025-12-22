''' Geometric Element base classes

    Component: Anything that can be added to a Diagram
    Element: Geometric element made of points, lines, planes
'''
from __future__ import annotations
from xml.etree import ElementTree as ET

from . import diagram_stack
from .drawable import Drawable
from .canvas import DataRange
from .style.style import Style, AppliedStyle, DashTypes
from .style.css import merge_css, CssStyle
from .style.themes import zptheme


class Component(Drawable):
    ''' Base class for things added to a Diagram '''
    _step_color = False

    def __init__(self) -> None:
        super().__init__()
        self._style = Style()
        self._containerstyle: CssStyle | None = None
        self._name: str|None = None
        self._zorder: int = 2  # Components draw on top of containers
        self._erased: bool = False
        diagram_stack.push_component(self)

    def style(self, style: str) -> 'Component':
        ''' Add CSS key-name pairs to the style '''
        self._style = merge_css(self._style, style)
        return self

    def _build_style(self, name: str|None = None) -> AppliedStyle:
        ''' Build the style '''
        if name is None:
            classes = [p.__qualname__ for p in self.__class__.mro()]
        else:
            classes = [name, '*']

        return zptheme.style(
            *classes,
            cssid=self._cssid,
            cssclass=self._csscls,
            container=self._containerstyle,
            instance=self._style)

    def color(self, color: str) -> 'Component':
        ''' Sets the component's color '''
        self._style.color = color
        return self

    def stroke(self, stroke: DashTypes) -> 'Component':
        ''' Sets the component's stroke/linestyle '''
        self._style.stroke = stroke
        return self

    def strokewidth(self, width: float) -> 'Component':
        ''' Sets the component's strokewidth '''
        self._style.stroke_width = width
        return self

    def datarange(self) -> DataRange:
        ''' Get range of data '''
        return DataRange(None, None, None, None)

    def _logy(self) -> None:
        ''' Convert y coordinates to log(y) '''

    def _logx(self) -> None:
        ''' Convert x values to log(x) '''

    def animate_set(self, attribute: str, to: str,
                    begin: str = '', duration: str = '') -> 'Component':
        ''' Animate an attribute value of the element (using svg <set> tag) '''
        elm = ET.Element('set')
        elm.set('attributeName', attribute)
        elm.set('to', str(to))
        if begin:
            elm.set('begin', str(begin))
        if duration:
            elm.set('dur', str(duration))
        self._subelms.append(elm)
        return self

    def animate_move(self, path: 'Component', begin: str = '',
                     duration: str = '', repeat: str = 'indefinite',
                     rotate: str = 'auto',
                     ) -> 'Component':
        ''' Animate the object, moving it along path defined by the `path` component.
            Sets the <animateMotion> svg tag.
        '''
        if not (tag := path.get_attribute('id')):
            tag = diagram_stack.get_elmid()
            path.attribute('id', tag)

        elm = ET.Element('animateMotion')
        mpath = ET.SubElement(elm, 'mpath')
        mpath.set('href', f'#{tag}')
        if begin:
            elm.set('begin', str(begin))
        if duration:
            elm.set('dur', str(duration))
        if repeat:
            elm.set('repeatCount', str(repeat))
        if rotate:
            elm.set('rotate', rotate)
        self._subelms.append(elm)
        return self

    def animate_in(self, begin: str='', duration: str = '',
                   repeat: str = ''):
        ''' Animate the path as if it is being drawn '''
        tag = diagram_stack.get_elmid()

        elm = ET.Element('animate')
        elm.set('attributeName', 'stroke-dashoffset')
        elm.set('to', '0')
        elm.set('from', '$length')
        elm.set('id', tag)
        if begin:
            elm.set('begin', str(begin))
        if duration:
            elm.set('dur', str(duration))
        if repeat:
            elm.set('repeatCount', repeat)

        self._attrs['stroke-dasharray'] = '$length'
        self._attrs['stroke-dashoffset'] = '$length'
        self._subelms.append(elm)

        elm = ET.Element('set')
        elm.set('attributeName', 'stroke-dashoffset')
        elm.set('to', '0')
        elm.set('begin', f'{tag}.end')
        self._subelms.append(elm)
        return self

    def animate_out(self, begin: str='', duration: str = '',
                    repeat: str = ''):
        ''' Animate the path as if it is being erased '''
        tag = diagram_stack.get_elmid()
        elm = ET.Element('animate')
        elm.set('attributeName', 'stroke-dashoffset')
        elm.set('to', '$length')
        elm.set('from', '0')
        elm.set('id', tag)
        if begin:
            elm.set('begin', str(begin))
        if duration:
            elm.set('dur', str(duration))
        if repeat:
            elm.set('repeatCount', repeat)

        self._attrs['stroke-dasharray'] = '$length'
        self._subelms.append(elm)

        elm = ET.Element('set')
        elm.set('attributeName', 'stroke-dashoffset')
        elm.set('to', '$length')
        elm.set('begin', f'{tag}.end')
        self._subelms.append(elm)
        return self


class Element(Component):
    ''' Base class for elements, defining a single object in a plot '''
    _step_color = False  # Whether to increment the color cycle
    legend_square = False  # Draw legend item as a square

    def __init__(self) -> None:
        super().__init__()
        self._style = Style()
        self._name: str = ''
        self._containerstyle: CssStyle | None = None
        self._markername: str|None = None  # SVG ID of marker for legend

    def _set_cycle_index(self, index: int = 0):
        ''' Set the index of this element within the colorcycle '''
        self._style._set_cycle_index(index)

    def name(self, name: str) -> 'Element':
        ''' Sets the element name to include in the legend '''
        self._name = name
        return self
