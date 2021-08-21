from datetime import date
from unittest import TestCase, skip

from daterange import DateRange


class TestDateRange(TestCase):
    def setUp(self) -> None:
        nov30 = date(2021, 11, 30)
        nov1 = date(2021, 11, 1)
        oct31 = date(2021, 10, 31)
        oct1 = date(2021, 10, 1)
        sep30 = date(2021, 9, 30)
        sep1 = date(2021, 9, 1)
        aug31 = date(2021, 8, 31)
        self.aug15 = date(2021, 8, 15)
        aug1 = date(2021, 8, 1)
        jul31 = date(2021, 7, 31)
        jul1 = date(2021, 7, 1)
        jun30 = date(2021, 6, 30)
        jun1 = date(2021, 6, 1)
        may31 = date(2021, 5, 31)
        may1 = date(2021, 5, 1)
        apr30 = date(2021, 4, 30)
        apr1 = date(2021, 4, 1)
        mar31 = date(2021, 3, 31)
        mar1 = date(2021, 3, 1)
        self.all_time = DateRange.all_time()
        self.year = DateRange(date(2021, 1, 1), date(2021, 12, 31))
        self.nov = DateRange(nov1, nov30)
        self.oct = DateRange(oct1, oct31)
        self.sep = DateRange(sep1, sep30)
        self.aug = DateRange(aug1, aug31)
        self.jul = DateRange(jul1, jul31)
        self.jun = DateRange(jun1, jun30)
        self.may = DateRange(may1, may31)
        self.apr = DateRange(apr1, apr30)
        self.mar = DateRange(mar1, mar31)
        self.oct_nov = DateRange(oct1, nov30)
        self.sep_oct = DateRange(sep1, oct31)
        self.aug_sep = DateRange(aug1, sep30)
        self.jul_aug = DateRange(jul1, aug31)
        self.jun_jul = DateRange(jun1, jul31)
        self.may_jun = DateRange(may1, jun30)
        self.apr_may = DateRange(apr1, may31)
        self.mar_apr = DateRange(mar1, apr30)
        self.sep_oct_nov = DateRange(sep1, nov30)
        self.aug_sep_oct = DateRange(aug1, oct31)
        self.jul_aug_sep = DateRange(jul1, sep30)
        self.jun_jul_aug = DateRange(jun1, aug31)
        self.may_jun_jul = DateRange(may1, jul31)
        self.apr_may_jun = DateRange(apr1, jun30)
        self.mar_apr_may = DateRange(mar1, may31)
        self.mar_thru_nov = DateRange(mar1, nov30)

        self.i_nov = DateRange.Interval(nov1, nov30)
        self.i_oct = DateRange.Interval(oct1, oct31)
        self.i_sep = DateRange.Interval(sep1, sep30)
        self.i_aug = DateRange.Interval(aug1, aug31)
        self.i_jul = DateRange.Interval(jul1, jul31)
        self.i_jun = DateRange.Interval(jun1, jun30)
        self.i_may = DateRange.Interval(may1, may31)
        self.i_oct_nov = DateRange.Interval(oct1, nov30)
        self.i_sep_oct = DateRange.Interval(sep1, oct31)
        self.i_aug_sep = DateRange.Interval(aug1, sep30)
        self.i_jul_aug = DateRange.Interval(jul1, aug31)
        self.i_jun_jul = DateRange.Interval(jun1, jul31)
        self.i_may_jun = DateRange.Interval(may1, jun30)
        self.i_may_jun_jul = DateRange.Interval(may1, jul31)
        self.i_aug_sep_oct = DateRange.Interval(aug1, oct31)

        self.not_aug = DateRange()
        self.not_aug._intervals.append(DateRange.Interval(None, jul31))
        self.not_aug._intervals.append(DateRange.Interval(sep1, None))

        self.not_aug_oct = DateRange()
        self.not_aug_oct._intervals.append(DateRange.Interval(None, jul31))
        self.not_aug_oct._intervals.append(DateRange.Interval(sep1, sep30))
        self.not_aug_oct._intervals.append(DateRange.Interval(nov1, None))

        self.to_aug = DateRange()
        self.to_aug._intervals.append(DateRange.Interval(None, jul31))

        self.from_aug = DateRange()
        self.from_aug._intervals.append(DateRange.Interval(aug1, None))

        self.no_time = DateRange()

        self.every_other_day_jun = DateRange()
        for day in range(1, 30 + 1, 2):
            interval = DateRange.Interval(date(2021, 6, day), date(2021, 6, day))
            self.every_other_day_jun._intervals.append(interval)

        self.every_other_day_jul = DateRange()
        for day in range(1, 31 + 1, 2):
            interval = DateRange.Interval(date(2021, 7, day), date(2021, 7, day))
            self.every_other_day_jul._intervals.append(interval)

        self.every_other_day_jun_jul = DateRange()
        for day in range(1, 30 + 1, 2):
            interval = DateRange.Interval(date(2021, 6, day), date(2021, 6, day))
            self.every_other_day_jun_jul._intervals.append(interval)
        for day in range(1, 31 + 1, 2):
            interval = DateRange.Interval(date(2021, 7, day), date(2021, 7, day))
            self.every_other_day_jun_jul._intervals.append(interval)

    def test_interval_subtract(self):
        # The bracket subtracts from the parenthesis
        # (..)  [..]
        self.assertEqual([self.i_may_jun, ], self.i_may_jun - self.i_jul_aug)
        # [..]  (..)
        self.assertEqual([self.i_aug_sep, ], self.i_aug_sep - self.i_may_jun)

        # (..[::)..]
        self.assertEqual([self.i_may, ], self.i_may_jun - self.i_jun_jul)
        # [..(::]..)
        self.assertEqual([self.i_aug, ], self.i_jul_aug - self.i_jun_jul)

        # ([::::::)]  the same
        self.assertEqual([], self.i_may_jun - self.i_may_jun)

        # [(:::)...]  the same start
        self.assertEqual([], self.i_may - self.i_may_jun)
        # ([:::]...)  the same start
        self.assertEqual([self.i_jun, ], self.i_may_jun - self.i_may)
        # (...[:::])  the same end
        self.assertEqual([self.i_may, ], self.i_may_jun - self.i_jun)
        # [...(:::)]  the same end
        self.assertEqual([], self.i_jun - self.i_may_jun)

        # (..[::]..)
        self.assertEqual([self.i_may, self.i_jul], self.i_may_jun_jul - self.i_jun)
        # [..(::)..]
        self.assertEqual([], self.i_jun - self.i_may_jun_jul)

        # (...)[...] touching
        self.assertEqual([self.i_jul], self.i_jul - self.i_aug)
        # [...](...) touching
        self.assertEqual([self.i_jul], self.i_jul - self.i_jun)

    def test_subtract(self):
        with self.subTest("a range with same start or end"):
            self.assertEqual(self.no_time, self.aug - self.aug)
            self.assertEqual(self.no_time, self.aug - self.aug_sep)
            self.assertEqual(self.no_time, self.aug - self.jul_aug)

        with self.subTest("from a larger ranges with same start or end"):
            self.assertEqual(self.aug, self.aug_sep - self.sep)
            self.assertEqual(self.sep, self.aug_sep - self.aug)

        with self.subTest("from range overlapping on one side"):
            self.assertEqual(self.aug, self.aug_sep - self.sep_oct)
            self.assertEqual(self.sep, self.aug_sep - self.jul_aug)

        with self.subTest("an entirely contained range"):
            self.assertEqual(self.jul + self.sep, self.jul_aug_sep - self.aug)

        # april to october but skip July
        apr_nojul_oct = self.apr_may_jun + self.aug_sep_oct

        with self.subTest("from a range with a gap in the middle"):
            self.assertEqual(self.apr_may + self.sep_oct, apr_nojul_oct - self.jun_jul_aug)
            self.assertEqual(self.may + self.sep_oct, apr_nojul_oct - (self.jun_jul_aug + self.apr))
            self.assertEqual(self.apr_may + self.sep, apr_nojul_oct - (self.jun_jul_aug + self.oct))
            self.assertEqual(self.may + self.sep, apr_nojul_oct - (self.jun_jul_aug + self.apr + self.oct))
            self.assertEqual(self.may + self.sep_oct, apr_nojul_oct - (self.jun_jul_aug + self.mar_apr))
            self.assertEqual(self.apr_may + self.sep, apr_nojul_oct - (self.jun_jul_aug + self.oct_nov))
            self.assertEqual(self.may + self.sep, apr_nojul_oct - (self.jun_jul_aug + self.mar_apr + self.oct_nov))

        with self.subTest("a range with a gap in the middle"):
            self.assertEqual(self.jul, (self.jun_jul_aug + self.apr) - apr_nojul_oct)
            self.assertEqual(self.jul, (self.jun_jul_aug + self.oct) - apr_nojul_oct)
            self.assertEqual(self.jul, self.jun_jul_aug - apr_nojul_oct)

        with self.subTest("a range with a gap from a range with multiple gaps"):
            self.assertEqual(self.jul, (self.jun_jul_aug + self.apr + self.oct) - apr_nojul_oct)
            self.assertEqual(self.mar + self.jul + self.nov,
                             (self.mar_apr + self.jun_jul_aug + self.oct_nov) - apr_nojul_oct)

        with self.subTest("a range with multiple intervals from within a continuous range"):
            self.assertEqual(self.mar + self.may + self.jul + self.sep_oct,
                             self.mar_thru_nov - self.apr - self.jun - self.aug - self.nov)
            self.assertEqual(self.mar + self.may + self.jul + self.sep_oct,
                             self.mar_thru_nov - (self.apr + self.jun + self.aug + self.nov))

        with self.subTest("from a range with multiple intervals a continuous range that is within"):
            self.assertEqual(self.mar + self.may + self.sep + self.nov,
                             (self.mar + self.may + self.jul + self.sep + self.nov) - self.jul_aug)
            self.assertEqual(self.mar + self.may + self.sep + self.nov,
                             (self.mar + self.may + self.jul + self.sep + self.nov) - self.jun_jul)

        with self.subTest("from a continuous range within a range with multiple intervals"):
            self.assertEqual(self.aug, self.jul_aug - (self.mar + self.may + self.jul + self.sep + self.nov))
            self.assertEqual(self.jun, self.jun_jul - (self.mar + self.may + self.jul + self.sep + self.nov))

        with self.subTest("a datetime.date from a range and vice versa"):
            no_aug_15 = DateRange(date(2021, 8, 1), date(2021, 8, 14)) + DateRange(date(2021, 8, 16), date(2021, 8, 31))
            self.assertEqual(no_aug_15, self.aug - self.aug15)
            self.assertEqual(self.no_time, self.aug15 - self.aug)

        with self.subTest("many consecutive datetime.date objects"):
            only_the_15th = self.aug.copy()
            for day in range(1, 14 + 1):
                only_the_15th -= date(2021, 8, day)
            for day in range(16, 31 + 1):
                only_the_15th -= date(2021, 8, day)
            self.assertEqual(self.aug15, only_the_15th)

            only_the_15th_2 = self.aug.copy()
            for day in range(14, 1 - 1, -1):
                only_the_15th_2 -= date(2021, 8, day)
            for day in range(31, 16 - 1, -1):
                only_the_15th_2 -= date(2021, 8, day)
            self.assertEqual(self.aug15, only_the_15th)

        with self.subTest("many nonconsecutive datetime.date objects"):
            every_other = self.every_other_day_jun.copy()
            for day in range(30, 2 - 1, -1):
                every_other -= date(2021, 6, day)
            self.assertEqual(DateRange(date(2021, 6, 1), date(2021, 6, 1)), every_other)

    def test_add(self):
        with self.subTest("self"):
            self.assertEqual(self.aug, self.aug + self.aug)
        with self.subTest("butted intervals"):
            self.assertEqual(self.aug_sep, self.aug + self.sep)
            self.assertEqual(self.aug_sep_oct, self.aug + self.sep + self.oct)

        with self.subTest("disjoint intervals"):
            self.assertIn(self.may, self.may + self.jul + self.sep)
            self.assertNotIn(self.jun, self.may + self.jul + self.sep)
            self.assertIn(self.jul, self.may + self.jul + self.sep)
            self.assertNotIn(self.aug, self.may + self.jul + self.sep)
            self.assertIn(self.sep, self.may + self.jul + self.sep)
            self.assertNotIn(self.oct, self.may + self.jul + self.sep)

        with self.subTest("add a datetime.date object"):
            self.assertEqual(DateRange(date(2021, 8, 1), date(2021, 9, 1)), self.aug + date(2021, 9, 1))
            self.assertEqual(DateRange(date(2021, 8, 1), date(2021, 9, 1)), date(2021, 9, 1) + self.aug)

        with self.subTest("many consecutive datetime.date objects"):
            many_days = DateRange()
            for day in range(1, 31 + 1):
                many_days += date(2021, 8, day)
            self.assertEqual(self.aug, many_days)
            self.assertEqual(1, len(many_days))

            many_days_backward = DateRange()
            for day in range(31, 1 - 1, -1):
                many_days_backward += date(2021, 8, day)
            self.assertEqual(self.aug, many_days_backward)
            self.assertEqual(1, len(many_days_backward))

        with self.subTest("many disjoint datetime.date objects"):
            every_other_day = DateRange()
            for day in range(1, 30 + 1, 2):
                every_other_day += date(2021, 6, day)
            self.assertEqual(15, len(every_other_day))

            every_other_day_backward = DateRange()
            for day in range(30, 1 - 1, -2):
                every_other_day_backward += date(2021, 6, day)
            self.assertEqual(15, len(every_other_day_backward))
            self.assertEqual(sorted(every_other_day_backward._intervals), every_other_day_backward.intervals)

        with self.subTest("disjoint intervals"):
            may_jun_jul = self.may + self.jun + self.jul
            may_jul_sep = self.may + self.jul + self.sep
            self.assertIn(may_jul_sep, may_jul_sep + may_jun_jul)
            self.assertNotIn(self.oct, may_jul_sep + may_jun_jul)
            self.assertEqual(1, len(may_jun_jul))
            self.assertEqual(3, len(may_jul_sep))

        with self.subTest("using or operator"):
            self.assertEqual(self.aug, self.aug | self.aug)
            self.assertEqual(self.aug_sep, self.aug | self.sep)
            self.assertEqual(self.aug_sep_oct, self.aug | self.sep + self.oct)

    def test_intersect(self):
        self.assertEqual(self.aug, self.aug & self.aug)

        self.assertEqual(self.aug15, self.aug & self.aug15)
        self.assertEqual(self.aug15, self.aug15 & self.aug)

        self.assertEqual(self.no_time, self.aug & self.sep)
        self.assertEqual(self.no_time, self.sep & self.aug)
        self.assertEqual(self.no_time, self.aug & self.oct)
        self.assertEqual(self.no_time, self.oct & self.aug)
        self.assertEqual(self.sep, self.aug_sep & self.sep_oct)
        self.assertEqual(self.sep, self.sep_oct & self.aug_sep)

        may_jul_sep = self.may + self.jul + self.sep
        self.assertEqual(may_jul_sep, may_jul_sep & self.year)
        self.assertEqual(may_jul_sep, self.year & may_jul_sep)

        self.assertEqual(self.sep, may_jul_sep & self.sep)
        self.assertEqual(self.sep, self.sep & may_jul_sep)

        jun_aug_oct = self.jun + self.aug + self.oct
        self.assertEqual(self.no_time, may_jul_sep & jun_aug_oct)
        self.assertEqual(self.no_time, jun_aug_oct & may_jul_sep)

        self.assertEqual(self.aug, self.aug & self.aug_sep)
        self.assertEqual(self.aug, self.aug_sep & self.aug)
        self.assertEqual(self.sep, self.aug_sep & self.sep)
        self.assertEqual(self.sep, self.sep & self.aug_sep)

        self.assertEqual(self.jun + self.aug, (self.apr_may_jun + self.aug_sep_oct) & self.jun_jul_aug)
        self.assertEqual(self.may + self.sep, (self.apr_may_jun + self.aug_sep_oct) & (self.may + self.sep))
        self.assertEqual(self.jun + self.aug, self.jun_jul_aug & (self.apr_may_jun + self.aug_sep_oct))
        self.assertEqual(self.may + self.sep, (self.may + self.sep) & (self.apr_may_jun + self.aug_sep_oct))

        test_range = self.mar_thru_nov.copy()
        test_range &= self.may_jun_jul
        self.assertEqual(self.may_jun_jul, test_range)
        test_range &= self.jun_jul
        self.assertEqual(self.jun_jul, test_range)
        test_range &= self.jul
        self.assertEqual(self.jul, test_range)

    def test_copy(self):
        self.assertIsNot(self.aug, self.aug.copy())
        self.assertIsNot(self.aug._intervals[0], self.aug.copy()._intervals[0])

    @skip
    def test_from_list(self):
        raise AssertionError("TODO")

    def test_in(self):
        self.assertIn(self.aug15, self.aug)
        self.assertNotIn(self.aug15, self.sep)
        self.assertIn(self.aug, self.year)
        self.assertNotIn(self.aug, self.sep)
        self.assertNotIn(self.sep, self.aug)
        self.assertNotIn(self.jul_aug, self.aug_sep)

        may_jul_sep = self.may + self.jul + self.sep
        self.assertIn(may_jul_sep, self.year)
        self.assertNotIn(may_jul_sep, self.may_jun_jul)
        self.assertNotIn(self.may_jun_jul, may_jul_sep)

        self.assertIn(self.no_time, self.no_time)
        self.assertNotIn(self.aug, self.no_time)
        self.assertNotIn(self.aug15, self.no_time)
        self.assertIn(self.no_time, self.aug)

        self.assertIn(self.every_other_day_jun, self.jun)
        self.assertIn(self.every_other_day_jun, self.every_other_day_jun_jul)
        self.assertIn(self.every_other_day_jul, self.every_other_day_jun_jul)

    def test_equal(self):
        self.assertEqual(self.aug, self.aug)
        self.assertEqual(DateRange(date(2021, 8, 1), date(2021, 8, 31)), self.aug)

        may_jun_jul = self.may + self.jun + self.jul
        self.assertEqual(self.may_jun_jul, may_jun_jul)

        self.assertNotEqual(self.sep, self.aug)
        may_jul_sep = self.may + self.jul + self.sep
        self.assertNotEqual(may_jul_sep, self.aug)
        self.assertNotEqual(may_jun_jul, may_jul_sep)

        self.assertEqual(DateRange(self.aug15, self.aug15), self.aug15)
        self.assertEqual(self.aug15, DateRange(self.aug15, self.aug15))

    def test_less_than(self):
        self.assertLess(self.jul, self.sep)
        self.assertLess(self.jul, self.aug)

        self.assertFalse(self.aug < self.jul)

        self.assertFalse(self.aug15 < self.jul)
        self.assertTrue(self.aug15 < self.sep)

        self.assertFalse(self.aug15 < self.aug)

    def test_greater_than(self):
        self.assertGreater(self.sep, self.jul)
        self.assertGreater(self.aug, self.jul)

        self.assertFalse(self.jul > self.aug)

        self.assertFalse(self.aug15 > self.sep)
        self.assertTrue(self.aug15 > self.jul)

        self.assertFalse(self.aug15 > self.aug)
