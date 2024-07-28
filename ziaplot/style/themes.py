''' Style themes '''
from __future__ import annotations
from .css import CssStyle, parse_css, merge
from .style import Style, AppliedStyle


# All themes stacked on top of this default one
THEME_BASE = ''' * {
        color: black;
        edge_color: black;
        stroke: solid;
        stroke_width: 2;
        shape: none;
        radius: 8;          /* Marker size */
        edge_width: 1;      /* Border around markers, bars, etc. */
        font: sans-serif;
        font_size: 14;
        num_format: g;
        height: 0;
        width: 0;
        margin: 0;
        pad: 0;
        colorcycle: black;
    }
    Canvas {
        color: none;
        width: 600;
        height: 400;
    }
    Graph {
        color: #F6F6F6;
        edge_width: 2;
        font_size: 16;
    }
    Graph.GridX {
        color: lightgray;
        stroke: dashed;
        stroke_width: 1;
    }
    Graph.GridY {
        color: lightgray;
        stroke: dashed;
        stroke_width: 1;
    }
    Graph.Title {
        font_size: 18;
    }
    Graph.XName {
        font_size: 14;
    }
    Graph.YName {
        font_size: 14;
    }
    Graph.Legend {
        color: none;
        stroke_width: 1;
        radius: 40;
        margin: 8;     /* Between legend and axis */
        pad: 4;        /* Between legend frame and contents */
    }
    Graph.LegendText {
        font_size: 14;
        margin: 4;
    }
    Graph.TickX {
        font_size: 13;
        height: 9;
        stroke_width: 2;
        margin: 4;
        pad: .2;        /* Stretch the x range by this fraction of a tick */
        num_format: g;
    }
    Graph.TickXMinor {
        height: 5;
        stroke_width: 1;
    }
    Graph.TickY {
        font_size: 13;
        height: 9;
        stroke_width: 2;
        margin: 4;
        pad: .2;        /* Stretch the y range by this fraction of a tick */
        num_format: g;
    }
    Graph.TickYMinor {
        height: 5;
        stroke_width: 1;
    }
    Text {
    }
    GraphPolar {
        color: #F6F6F6;
        pad: 10;      /* frame to canvas border */
        margin: 4;   /* theta labels to frame */
    }
    Smith.Grid {
        color: #dddddd;
        stroke_width: 1.2;
    }
    Smith.GridMinor {
        color: #e8e8e8;
        stroke_width: 1
    }
    BarChart {
        margin: 0.1;       /* Space between bars */
    }
    BarChartGrouped {
        margin: 0.5;      /* Space between bar groups */
    }
    BarChart.TickX {
        font_size: 13;
        height: 9;
        stroke_width: 2;
        margin: 4;
        num_format: g;
        pad: 0;  /* Let bars sit at exact bottom of axis */
    }
    BarChartHoriz.TickY {
        font_size: 13;
        height: 9;
        stroke_width: 2;
        margin: 4;
        num_format: g;
        pad: 0;  /* Let bars sit at exact left of axis */
    }
    BarChart.GridX {
        color: none;
        stroke: dashed;
        stroke_width: 1;
    }
    BarChart.GridY {
        color: lightgray;
        stroke: dashed;
        stroke_width: 1;
    }
    BarChartHoriz.GridX {
        color: lightgray;
        stroke: dashed;
        stroke_width: 1;
    }
    BarChartHoriz.GridY {
        color: none;
        stroke: dashed;
        stroke_width: 1;
    }
    Pie {
        margin: 10;  /* Canvas to Pie */
    }
    PieSlice {
        color: auto;
        stroke_width: 1;
    }
    PieSlice.Text {
        font_size: 14;
        margin: 4;    
    }
    Element {
        color: auto;
        stroke_width: 2;
        colorcycle: #ba0c2f, #ffc600, #007a86, #ed8b00,
                    #8a387c, #a8aa19, #63666a, #c05131,
                    #d6a461, #a7a8aa;
    }
    Scatter {
        shape: round;
        stroke: none;
        edge_width: 1;
    }
    ErrorBar.MarkerXError {
        color: auto;
        shape: |;
        radius: 7;
    }
    ErrorBar.MarkerYError {
        color: auto;
        shape: -;
        radius: 7;
    }
    LineFill {
        color: blue 30%;
    }
    Arrow {
        radius: 6;
        margin: 8;  /* to text */
    }
    Contour {
      /* Contours fade between these two colors, or step 
        if more than 2 colors are defined */
        colorcycle: #007a86, #ba0c2f;
    }
    Contour.ColorBar {
        stroke_width: 1;
        width: 20;
        margin: 8;
        num_format: .3g;
    }
    Point {
        shape: round;
        color: #007a86;
        stroke_width: 1;
        radius: 4;
    }
    Point.Text {
        font_size: 12;
        margin: 8;
    }
    Point.GuideX {
        stroke: dotted;
        stroke_width: 1.5;
    }
    Point.GuideY {
        stroke: dotted;
        stroke_width: 1.5;
    }
    IntegralFill {
        color: blue 30%;
    }
    Line.Text {
        font_size: 12;
        margin: 8;
    }
    Angle {
        stroke_width: 1.5;
        radius: 20;
        margin: 4;  /* between successive arcs */
    }
    Angle.Text {
        font_size: 14;
        margin: 5;
    }
    Shape {
        color: none;
        edge_color: black;
        stroke: solid;
    } 
'''


THEME_LOBO = THEME_BASE
THEME_TAFFY = '''
    Element {
        colorcycle: #00a4bd, #ff7a59, #00bda5,
                    #f2547d, #6a78d1, #f5C26b,
                    #516f90, #99acc2, #cc3399,
                    #99cc00;
    }
    '''

THEME_DARK = '''
    * {
        color: #cccccc;
        edge_color: #777777;
    }
    Canvas {
        color: black;
    }
    Graph {
        color: black;
        edge_color: #cccccc;
    }
    Graph.GridX {
        color: #555555;
    }
    Graph.GridY {
        color: #555555;
    }
    BarChart.GridX {
        color: #555555;
    }
    BarChart.GridY {
        color: #555555;
    }
    BarChartHoriz.GridX {
        color: #555555;
    }
    BarChartHoriz.GridY {
        color: #555555;
    }
'''


THEME_PASTEL = '''
    * {
         color: #444444;
         edge_color: #555555;
    }
    Element {
        colorcycle: #c6579A, #ffbe9f, #f1e6b2,
                    #b6cfae, #a7e6d7, #9AdBe8,
                    #decde7, #ffa1cb, #9a98b5,
                    #7589bf;
    }
    Graph {
        color: #fafafa;
    }            
    Point {
        color: #7589bf;
    }
'''


THEME_BOLD = '''
    Element {
        colorcycle: red, orange, yellow, #338833,
                    #00bb00, blue, #00eeee,
                    violet, purple, silver;
    }
    Point {
        color: #00aa00;
    }
'''


THEME_DARKTAFFY = THEME_DARK + THEME_TAFFY
THEME_DARKBOLD = THEME_DARK + THEME_BOLD

CSS_BLACKWHITE = '''
    Graph {
        color: none;
    }
    Element {
        colorcycle: black;
    }
    Point {
        color: black;
    }
    '''

CSS_NOBACKGROUND = 'Graph { color: none; }'
CSS_NOGRID = '''
    Graph.GridX {
        color: none;
    }
    Graph.GridY {
        color: none;
    }
'''


class Theme:
    ''' Store global Ziaplot themes '''
    THEMES = {
        'default': THEME_LOBO,
        'lobo': THEME_LOBO,
        'taffy': THEME_TAFFY,
        'pastel': THEME_PASTEL,
        'bold': THEME_BOLD,
        'dark': THEME_DARK,
        'darktaffy': THEME_DARKTAFFY,
        'darkbold': THEME_DARKBOLD
    }

    def __init__(self):
        self.theme = parse_css(THEME_BASE)
        self.usercss = CssStyle()

    def use(self, name: str) -> None:
        ''' Enable a theme by name. Use `list_themes` to see list of available
            theme names.
        '''
        if name not in self.THEMES:
            raise ValueError(f'No theme named {name}. Use zp.list_themes() to see available theme names')
        self.theme = parse_css(
            THEME_BASE + self.THEMES.get(name, '')
        )

    def list_themes(self) -> list[str]:
        ''' Get a list of available themes '''
        return list(self.THEMES.keys())

    def css(self, css: str) -> None:
        ''' Apply CSS on top of the actiive theme '''
        self.usercss = parse_css(css)

    def style(self,
              *classes: str,
              cssid: str|None = None,
              cssclass: str|None = None,
              container: CssStyle|None = None,
              instance: Style|None = None,
              ) -> AppliedStyle:
        '''
            Args:
                classes: List of class names to apply, from higest
                    to lowest preference
                cssid: The id of the drawable, located with # in css
                cssclass: The classid of the drawable, located with . in css
                container: Styles applied to the container (Diagram)
                instance: Styles applied to the instance Element
        '''
        # Start with base theme to fill everything in
        style = self.theme.extract('*')
        
        classes = tuple(reversed(classes))

        # Merge in the theme
        if len(classes):
            style = merge(
                style,
                self.theme.extract(classes, cssclass=cssclass, cssid=cssid))

        # Merge in the container
        if container:
            style = merge(
                style,
                container.extract(classes, cssclass=cssclass, cssid=cssid))

        # user css
        if self.usercss:
            style = merge(
                style,
                self.usercss.extract(classes, cssclass=cssclass, cssid=cssid))

        # Finish with instance overrides
        if instance:
            style = merge(style, instance)
        return AppliedStyle(**style.values())


zptheme = Theme()



def css(css: str) -> None:
    ''' Set global CSS styling '''
    zptheme.css(css)


def theme(name: str) -> None:
    ''' Activate a theme by name. Use `list_themes` to see list of available
        theme names.
    '''
    zptheme.use(name)

def theme_list() -> list[str]:
    ''' Get a list of available themes '''
    return list(zptheme.THEMES.keys())
