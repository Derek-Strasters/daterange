from datetime import timedelta, date
from typing import Optional, Union, List

_DAY = timedelta(days=1)


def type_check(func):
    def wrapper(*args, **kwargs):
        if not isinstance(args[1], DateRange):
            if isinstance(args[1], date):
                day_range = DateRange(args[1], args[1])
                args = (args[0], day_range, *args[2:]) if len(args) > 2 else (args[0], day_range)
            else:
                def not_implemented():
                    return NotImplemented

                return not_implemented()
        return func(*args, **kwargs)

    return wrapper


class DateRange:
    """
    Contains a range of dates that are not necessarily contiguous.
    Intervals can be constructed with dates and added with the familiar
    numerical operators.
    Adding:
    >>> my_range = DateRange(date(2021, 8, 1), date(2021, 8, 31))  # All of Aug
    >>> my_range += DateRange(date(2021, 10, 1), date(2021, 10, 31)) # All of Aug and Sep
    >>> print(my_range)
    from 2021-08-01 to 2021-08-31 and
    from 2021-10-01 to 2021-10-31
    >>> august = DateRange(date(2021, 8, 1), date(2021, 8, 31))
    >>> september = DateRange(date(2021, 9, 1), date(2021, 9, 30))
    >>> july = DateRange(date(2021, 7, 1), date(2021, 7, 31))
    >>> august + september + july == DateRange(date(2021, 7, 1), date(2021, 9, 30))
    True

    datetime.date object can also be checked if they fall within a DateRange:
    >>> date(2021, 8, 17) in august # Is Aug 17th in the range?
    True
    >>> date(2021, 9, 10) in august # Is Oct 10th in the range?
    False

    This works with DateRanges as well
    >>> august in  DateRange(date(2021, 7, 1), date(2021, 9, 30))
    True

    DateRanges can also be intersected with and subtracted from one another:
    >>> aug_2_sep = august + september + july
    >>> print(aug_2_sep - august)
    from 2021-07-01 to 2021-07-31 and
    from 2021-09-01 to 2021-09-30
    >>> jul_2_aug = july + august
    >>> print(jul_2_aug & aug_2_sep)
    from 2021-07-01 to 2021-08-31

    Taking inspiration from the way we refer to dates with language, DateRanges
    are treated inclusively as this is the most idiomatic approach.
    For example when we say "for the month of August" we mean every day
    within the month, or when we say "Monday through Friday" we mean the
    entirety of each day and not just the delta time.
    For example:
    >>> date(2021, 8, 31) in august
    True
    >>> date(2021, 8, 1) in august
    True
    >>> DateRange(date(2021, 8, 1), date(2021, 8, 31)).days
    31

    If the start day is before the end day, the range will include all time
    except for that between the start date and end date
    If the start day is exactly one day after the end day the range will be all
    time.
    """

    __slots__ = '_intervals'

    class Interval:
        __slots__ = 'start', 'end'

        max = date.max
        min = date.min

        def __init__(self,
                     start: Optional[date] = None,
                     end: Optional[date] = None):
            self.start = start if start else self.min
            self.end = end if end else self.max
            if self.start > self.end:
                raise ValueError(f"End cannot be before start: {start} > {end}")

        def __contains__(self, other: Union[date, 'DateRange.Interval']):
            """If a date or DateRange is entirely within this DateRange (Inclusive of end date)"""
            if isinstance(other, date):
                return self.date_in(other)
            return self.start <= other.start and self.end >= other.end

        def date_in(self, _date: date):
            return self.end >= _date >= self.start

        def __eq__(self, other):
            return self.start == other.start and self.end == other.end

        def __lt__(self, other: Union['DateRange.Interval', date]):
            """If this DateRange is entirely after another DateRange"""
            return self.end < other.start if isinstance(other, type(self)) else self.end < other

        def __gt__(self, other: Union['DateRange.Interval', date]):
            """If this DateRange is entirely after another DateRange"""
            return self.start > other.end if isinstance(other, type(self)) else self.start > other

        def __and__(self, other: 'DateRange.Interval') -> Union[None, 'DateRange.Interval']:
            """Intersection"""
            start = self.start if self.start >= other.start else other.start
            end = self.end if self.end <= other.end else other.end
            return type(self)(start, end) if start <= end else None

        def __sub__(self, other: 'DateRange.Interval') -> List['DateRange.Interval']:
            """Remove dates where another Interval intersects this one. Returns a list of Intervals"""
            if self.start < other.start:
                if self.end >= other.start:
                    if self.end > other.end:
                        return [type(self)(self.start, other.start - _DAY),
                                type(self)(other.end + _DAY, self.end)]  # (..[::]..)
                    return [type(self)(self.start, other.start - _DAY), ]  # (...[:::])  (..[::)..]
                return [self.copy(), ]  # (..) [..]
            if self.start > other.end:
                return [self.copy(), ]  # [..] (..)
            if self.end > other.end:
                return [type(self)(other.end + _DAY, self.end), ]  # [..(::]..)  ([:::]...)
            return []  # [(::::::)]  [..(::)..]  [(:::)...]  [...(:::)]

        def __repr__(self):
            return f"Interval({self.start}, {self.end})"

        __str__ = __repr__

        def intersects(self, other: 'DateRange.Interval') -> bool:
            return self.end >= other.start and self.start <= other.end

        def not_intersects(self, other: 'DateRange.Interval') -> bool:
            return self.end < other.start or self.start > other.end

        def r_butted(self, other: 'DateRange.Interval') -> bool:
            """Is the end of this date interval butted against another interval?"""
            return other.start - self.end == _DAY

        def l_butted(self, other: 'DateRange.Interval') -> bool:
            """Is the start of this date interval butted against another interval?"""
            return self.start - other.end == _DAY

        def delta(self) -> timedelta:
            return self.end - self.start

        def copy(self):
            return type(self)(self.start, self.end)

        @property
        def days(self) -> int:
            return self.delta().days + 1

    def __init__(self,
                 start: Optional[date] = None,
                 end: Optional[date] = None):
        self._intervals = []
        self._add_init_range(start, end)

    def _add_init_range(self, start, end):
        if not start and not end:
            return

        if start and end:
            # If the start is larger than the end we use two intervals
            # from the beginning of time to end date
            # from the start date to the end of time
            if start > end:
                if start - end <= _DAY:
                    # All of time
                    self._intervals.append(self.Interval(None, None))
                    return
                else:
                    self._intervals.append(self.Interval(None, end))
                    self._intervals.append(self.Interval(start, None))
                    return
        self._intervals.append(self.Interval(start, end))

    @classmethod
    def from_list(cls, ranges: List[Union['DateRange', 'DateRange.Interval', date]]) -> 'DateRange':
        new = cls()
        # TODO: use sorted for better performance
        for item in ranges:
            if isinstance(item, cls.Interval):
                new_new = cls()
                cls()._intervals = [item]
                new += new_new
            if isinstance(item, (DateRange, date)):
                new += item
                continue
            raise TypeError(f'Cannot create range from type: {type(item)}')
        return new

    def copy(self) -> 'DateRange':
        new: DateRange = type(self)(None, None)
        new._intervals = [interval.copy() for interval in self]
        return new

    @property
    def days(self) -> int:
        return sum(interval.days for interval in self)

    @property
    def intervals(self) -> List[Interval]:
        return self._intervals

    @property
    def earliest(self) -> date:
        return self.intervals[0].start if self.intervals else None

    @property
    def latest(self) -> date:
        return self.intervals[-1].end if self.intervals else None

    @classmethod
    def all_time(cls):
        return cls(date.min, date.max)

    def __iter__(self):
        """Iterate over the intervals"""
        for interval in self.intervals:
            yield interval

    def __len__(self):
        """Return the number of intervals"""
        return len(self.intervals)

    @type_check
    def __eq__(self, other: Union[date, 'DateRange']):
        if len(self) != len(other):
            return False
        return all(interval[0] == interval[1] for interval in zip(self, other))

    @type_check
    def __gt__(self, other):
        """All time intervals are entirely after all of another date range's time intervals"""
        return self.earliest > other.latest if self.earliest and other.latest else None

    @type_check
    def __lt__(self, other):
        """All time intervals are entirely before all of another date range's time intervals"""
        return self.latest < other.earliest if self.latest and other.earliest else None

    def __contains__(self, other: Union[date, 'DateRange']):
        """If another DateRange (or date) is entirely within this DateRange (Inclusive of end date)"""
        if not isinstance(other, DateRange):
            if isinstance(other, date):
                return any(other in _range for _range in self)
            return NotImplemented
        queries = iter(other.intervals)
        intervals = iter(self.intervals)

        total_hits = 0

        interval = next(intervals, None)
        query = next(queries, None)
        while interval and query:
            # Since queries should always be smaller or equal if true, they are advanced first
            if query < interval:
                query = next(queries, None)
                continue
            if query in interval:
                total_hits += 1
                query = next(queries, None)
                continue
            if interval < query:
                interval = next(intervals, None)
                continue
            # This accounts for queries that overlap intervals, and queries that are larger than the interval
            return False

        return total_hits == len(other.intervals)

    def _interval_intersect(self, other: 'DateRange') -> 'DateRange':
        if not isinstance(other, DateRange):
            if isinstance(other, date):
                if other in self:
                    return type(self)(other, other)
                self._intervals = []
                return self
            return NotImplemented
        intervals = self._sorted_interval_iter(self.intervals, other.intervals)
        new_intervals = []

        interval = next(intervals, None)
        next_interval = next(intervals, None)
        while interval and next_interval:
            intersection = interval & next_interval
            if intersection:
                new_intervals.append(intersection.copy())
            if next_interval.end > interval.end:
                interval = next_interval
            next_interval = next(intervals, None)

        self._intervals = new_intervals
        return self

    def __and__(self, other: Union[date, 'DateRange']) -> 'DateRange':
        """Return the intersection of date ranges or None if they do not intersect"""
        return self.copy()._interval_intersect(other)

    __rand__ = __and__

    def __iand__(self, other: Union[date, 'DateRange']) -> 'DateRange':
        return self._interval_intersect(other)

    def _interval_union(self, other: 'DateRange') -> 'DateRange':
        intervals = self._sorted_interval_iter(self.intervals, other.intervals)
        new_intervals = []

        interval = next(intervals, None)
        next_interval = next(intervals, None)
        while interval and next_interval:
            if interval < next_interval and not interval.r_butted(next_interval):
                new_intervals.append(interval.copy())
                interval = next_interval
                next_interval = next(intervals, None)
                continue

            if next_interval.end > interval.end:
                interval.end = next_interval.end
            next_interval = next(intervals, None)

        self._intervals = new_intervals + [interval] if interval else []
        return self

    @type_check
    def __or__(self, other: Union[date, 'DateRange']) -> 'DateRange':
        """Return the Union of date ranges"""
        return self.copy()._interval_union(other)

    __ror__ = __or__
    __add__ = __or__
    __radd__ = __or__

    @type_check
    def __ior__(self, other: Union[date, 'DateRange']) -> 'DateRange':
        return self._interval_union(other)

    __iadd__ = __ior__

    def _interval_subtract(self, other: 'DateRange') -> 'DateRange':
        # TODO: would it be easier to invert the subtrahend and intersect them?
        intervals = iter(self.intervals)
        subtrahends = iter(other.intervals)
        new_intervals = []
        temp_intervals = []

        interval = next(intervals, None)
        subtrahend = next(subtrahends, None)
        while interval and subtrahend:
            if subtrahend < interval:
                subtrahend = next(subtrahends, None)
                if subtrahend is None:
                    new_intervals.append(interval)
                continue
            if interval < subtrahend:
                new_intervals.append(interval)
                interval = next(intervals, None)
                continue

            # The subtrahend must be overlapping the interval at this point so we subtract
            temp_intervals += interval - subtrahend

            # If a portion of the interval extends past the subtrahend
            if subtrahend.end < interval.end:
                subtrahend = next(subtrahends, None)
                if subtrahend is not None:
                    interval = temp_intervals.pop()
            else:
                interval = next(intervals, None)
                new_intervals += temp_intervals
                temp_intervals.clear()
        self._intervals = new_intervals + temp_intervals + list(intervals)
        return self

    @type_check
    def __sub__(self, other: Union[date, 'DateRange']) -> 'DateRange':
        return self.copy()._interval_subtract(other)

    @type_check
    def __rsub__(self, other: Union[date, 'DateRange']) -> 'DateRange':
        # ORDER IS IMPORTANT HERE
        return other._interval_subtract(self)

    @type_check
    def __isub__(self, other: Union[date, 'DateRange']) -> 'DateRange':
        return self._interval_subtract(other)

    def __repr__(self):
        return f"DateRange[{len(self)}]({self.earliest}, {self.latest})"

    def __str__(self):
        return ' and\n'.join([f"from {inter.start} to {inter.end}" for inter in self])

    @staticmethod
    def _sorted_interval_iter(interval_list_1: List[Interval], interval_list_2: List[Interval]):
        # Assumes the individual intervals are already in ascending order
        intervals_1 = iter(interval_list_1)
        intervals_2 = iter(interval_list_2)

        interval_1 = next(intervals_1, None)
        interval_2 = next(intervals_2, None)
        while interval_1 or interval_2:
            if interval_1 and interval_2:
                if interval_1.start < interval_2.start:
                    yield interval_1.copy()
                    interval_1 = next(intervals_1, None)
                    continue
                if interval_1.start > interval_2.start:
                    yield interval_2.copy()
                    interval_2 = next(intervals_2, None)
                    continue
                if interval_1.end <= interval_2.end:
                    yield interval_1.copy()
                    interval_1 = next(intervals_1, None)
                    continue
                yield interval_2.copy()
                interval_2 = next(intervals_2, None)
                continue
            if interval_1:
                yield interval_1.copy()
                interval_1 = next(intervals_1, None)
                continue
            yield interval_2.copy()
            interval_2 = next(intervals_2, None)
