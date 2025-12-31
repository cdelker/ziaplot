# Release notes

### 0.9 - In progress

Contains breaking changes:

- zp.calcs module was removed and merged with zp.geometry module.
- Removed `index` parameter from intersection functions, replaced with smarter `which` parameter.
- Changed Point, Circle, and Ellipse to take PointType (tuple) instead of separate x and y values.
- Renamed `cssclass` method to `cls`.
- Renamed `svg()` method to `tosvg()` to avoid naming clash.
- Merged `BezierQuad` and `BezierCubic` into single `Bezier` class.

Enhancements:

- Added rudimentary animation via SVG SMIL animation tags
- Ability to set SVG attributes and subelements on drawing components
- Added `Arc` and `ArcCompass` geometric figures
- Added `Css` context manager for temporarily applying a style
- Apply stroke style to ellipses, rectangles, and arcs
- Added `fill_color` css attribute for fill of geometric shapes
- Added methods to bisect two points, and image and reflect points over lines


### 0.8 - 2025-03-02

- Fix zorder of legends
- Added BezierSpline and Hobby Curves
- Add Polygon
- Fix rectangles with negative width or height
- Fix histogram with only one bin
- Fix rectangle fill transparency
- Added colorblind-friendly themes


### 0.7 - 2024-08-24

- Added `NumberLine` graph type
- Added a zorder parameter for layering drawing elements
- Allow named font sizes, such as "large" and "small", in CSS
- Change arrowhead marker to point at its data coordinate rather than be centered over it


### 0.6 - 2024-07-27

This release includes major BREAKING CHANGES. The API was reworked to focus more on
graphing of geometric primitives (Lines, Circles, Points, etc.) in addition to empirical data.
It also adds a CSS styling system.

- Added geometric objects and shapes, including `Line`, `Point`, `Circle`, `BezierQuad`, `Function`, etc., in the `geo` submodule.
- The old `Line` has become `PolyLine`, with alias `Plot`.
- The new `Line` represents a true Euclidean line rather than a set of (x, y) coordinates connected by line segments.
- Added `LayoutGrid` for placing axes in a grid. `LayoutH` and `LayoutV` now inherit from `LayoutGrid`, and no longer support nested layouts.
- Added `HistogramHoriz` for horizontal histograms
- Added `Implicit` to plot implicit functions
- Renamed axes to `Graph`, `GraphQuad`, `GraphPolar`, `GraphSmith`. `Diagram` added as an empty surface for geometric diagrams.
- Added tangent and normal lines.
- Added point placemenet at intersections and extrema.
- Added `ticker` for easy forming of tick locations
- Added `equal_aspect` method to equalize x and y scales
- Changed to use a CSS-like styling system for applying styles and themes.
- Added more legend location options


### 0.5 - 2023-12-20

- Updated Pie and Bar interfaces
- Fixed legend text spacing
- Added context manager for axes and layouts
- Allow more than 2 colors in colorfade
- Added contour plots
- Added LayoutGap for leaving space in a Layout


### 0.4 - 2022-06-20

- Implement ziamath's Text object for plot labels
- Added size property to plot style, combining canvas width and canvas height
- Added global configuration object


### 0.3

- Added an option to use SVG1.x format for compatibility since SVG2.0 is not fully supported in all browsers/renderers yet.


### 0.2

- Use ziamath library to draw math text.


### 0.1

Initial Release
