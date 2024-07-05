# Release notes

### 0.6 - In progress

Includes several breaking changes:

- Added `Point` and `Line`
- The old `Line` has become `PolyLine`, with alias `Plot`. The new `Line` represents a true Euclidean line rather than a set of (x, y) coordinates connected by line segments.
- Added `GridLayout` for placing axes in a grid. `Hlayout` and `Vlayout` now inherit from `GridLayout`, and no longer support nested layouts.
- Added more legend location options
- Code restructured into submodules


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
