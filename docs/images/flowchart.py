''' Create the inheritance flowchart '''
import schemdraw
from schemdraw import flow


flow.Box.defaults['anchor'] = 'N'
flow.Box.defaults['fill'] = 'azure'
with schemdraw.Drawing(file='inheritance.svg'):
    draw = flow.Box(h=1).label('Drawable')
    cont = flow.Box(h=1).at((-5.5, -2)).label('Container')
    layout = flow.Box(h=1).at((-7.5, -4)).label('Layout')
    layoutgrid = flow.Box(h=1).at((-7.5, -6)).label('LayoutGrid')
    layout_ex = flow.Box().at((-7.5, -8)).label('LayoutH\nLayoutV')
    diag = flow.Box(h=1).at((-3.5, -4)).label('Diagram')
    graph = flow.Box().at((-3.5, -8)).label('Graph\nGraphQuad\nGraphLog\nGraphPolar\nGraphSmith\nBarChart\nPie')

    comp = flow.Box(h=1).at((5.5, -2)).label('Component')
    elm = flow.Box(h=1).at((2.5, -4)).label('Element')
    discrete = flow.Box(h=1).at((.5, -6)).label('Discrete')
    discrete_ex = flow.Box().at((.5, -8)).label('PolyLine\nScatter\nErrorBar\nLineFill\nLinePolar\nHistogram\nContour')
    geo = flow.Box().at((4.5, -8)).label('Point\nFunction\nLine\nSegment\nCurve\nBezier\nIntegralFill\nCircle\nEllipse\nRectangle\nBars\nPieSlice')
    annot = flow.Box(h=1).at((8.5, -4)).label('Annotations')
    annot_ex = flow.Box().at((8.5, -8)).label('Text\nArrow\nAngle')

    flow.Arrow().at(draw.S).to(cont.N)
    flow.Arrow().at(draw.S).to(comp.N)
    flow.Arrow().at(cont.S).to(layout.N)
    flow.Arrow().at(cont.S).to(diag.N)
    flow.Arrow().at(layout.S).to(layoutgrid.N)
    flow.Arrow().at(layoutgrid.S).to(layout_ex.N)
    flow.Arrow().at(diag.S).to(graph.N)
    flow.Arrow().at(comp.S).to(elm.N)
    flow.Arrow().at(elm.S).to(discrete.N)
    flow.Arrow().at(discrete.S).to(discrete_ex.N)
    flow.Arrow().at(elm.S).to(geo.N)
    flow.Arrow().at(comp.S).to(annot.N)
    flow.Arrow().at(annot.S).to(annot_ex.N)