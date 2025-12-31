''' SVG Attributes and SubElements, including SMIL animations '''
from typing import Optional, TYPE_CHECKING
from xml.etree import ElementTree as ET

from . import diagram_stack
if TYPE_CHECKING:
    from .drawable import Drawable
    from .element import Component


class Attributes:
    ''' Access attributes and subelements of the SVG element '''
    def __init__(self) -> None:
        self._attrs: dict[str, str] = {}
        self._subelms: list[ET.Element] = []

    def __setattr__(self, name: str, value: 'Attributes') -> None:
        ''' For Typing  '''
        super().__setattr__(name, value)

    def __getattr__(self, name: str) -> 'Attributes':
        ''' For Typing '''
        raise AttributeError

    def set(self, name: str, value: str) -> 'Attributes':
        ''' Set an XML attribute to the SVG elemenet '''
        self._attrs[name] = value
        return self

    def get(self, name: str, default: Optional[str] = None) -> Optional[str]:
        ''' Get an SVG attribute from the element '''
        return self._attrs.get(name, default)

    def subelement(self, element: str|ET.Element) -> 'Attributes':
        ''' Add an XML/SVG sub element '''
        if isinstance(element, str):
            element = ET.fromstring(element)
        self._subelms.append(element)
        return self


class Animatable(Attributes):
    ''' SVG attributes and subelements, with functions for adding SMIL annimation elements '''
    def animate_set(self, attribute: str, to: str,
                    begin: str = '', duration: str = '') -> 'Animatable':
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
                     ) -> 'Animatable':
        ''' Animate the object, moving it along path defined by the `path` component.
            Sets the <animateMotion> svg tag.
        '''
        if not (tag := path.tree.get('id')):
            tag = diagram_stack.get_elmid()
            assert tag is not None
            path.tree.set('id', tag)

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
                   repeat: str = '') -> 'Animatable':
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
                    repeat: str = '') -> 'Animatable':
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

    def animate(self, attribute: str, to: str, frm: str,
                begin: str = '', duration: str = '',
                repeat: str = 'indefinite') -> 'Animatable':
        ''' Animate an attribute. (Note parameters are in SVG coordinates, not drawing
            coordinates)
        '''
        elm = ET.Element('animate')
        elm.set('attributeName', attribute)
        elm.set('to', to)
        elm.set('from', frm)
        if begin:
            elm.set('begin', str(begin))
        if duration:
            elm.set('dur', str(duration))
        if repeat:
            elm.set('repeatCount', repeat)
        self._subelms.append(elm)
        return self

    def animate_show(self, begin: str = '',
                     duration: str = '',
                     repeat: str = '') -> 'Animatable':
        ''' Animate the visibile attribute
        '''
        elm = ET.Element('set')
        elm.set('attributeName', 'visibility')
        elm.set('to', 'visible')
        if begin:
            elm.set('begin', str(begin))
        if duration:
            elm.set('dur', str(duration))
        self._subelms.append(elm)

        if 'visibility' not in self._attrs:
            self._attrs['visibility'] = 'hidden'
        return self
