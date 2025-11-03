''' CSS Context Manager '''
from .. import diagram_stack


class Css:
    ''' Context Manager for applying a CSS style to a group of Elements '''
    def __init__(self, css: str):
        self.css = css

    def __enter__(self):
        diagram_stack.push_component(None)
        diagram_stack.apply_style.append(self.css)

    def __exit__(self, exc_type, exc_val, exc_tb):
        diagram_stack.push_component(None)
        diagram_stack.apply_style.pop()
