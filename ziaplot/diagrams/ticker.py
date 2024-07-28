''' Generate tick positions using slice notation '''
from .. import util


class _Ticker:
    ''' Use to generate ticks using slice notation:

        Examples:
            ticker[0:10:1]  # Generate ticks from 0 to 10
            ticker[0:10:2]  # Step from 0-10 by 2's
    '''
    def __getitem__(self, item):
        start, stop, step = item.start, item.stop, item.step
        if start is None:
            start = 0
        if stop is None:
            raise ValueError('stop value is required')
        if step is None:
            step = (stop - start) / 9
        return util.zrange(start, stop, step)


ticker = _Ticker()
