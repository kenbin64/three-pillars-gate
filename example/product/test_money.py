# Iteration 2 tests: the edges and the failure cases, the part the AI adds. These pin the exact shares, the exact
# sums, and the rounding, so a change to the code that breaks the behaviour is caught (the mutants die).
import unittest

import money


class TestMoney(unittest.TestCase):
    def test_add(self):
        self.assertEqual(money.add_cents(100, 50), 150)
        self.assertEqual(money.add_cents(0, 0), 0)

    def test_percent_exact(self):
        self.assertEqual(money.percent_cents(1000, 10), 100)
        self.assertEqual(money.percent_cents(1234, 10), 123)

    def test_percent_rounds_half_up(self):
        self.assertEqual(money.percent_cents(5, 10), 1)
        self.assertEqual(money.percent_cents(4, 10), 0)

    def test_split_even(self):
        self.assertEqual(money.split_bill(100, 4), [25, 25, 25, 25])

    def test_split_remainder_exact_shares(self):
        self.assertEqual(money.split_bill(101, 4), [26, 25, 25, 25])
        self.assertEqual(money.split_bill(100, 3), [34, 33, 33])

    def test_split_always_sums_to_total(self):
        for total in (0, 1, 7, 100, 101, 999, 1000):
            for people in (1, 2, 3, 4, 7):
                shares = money.split_bill(total, people)
                self.assertEqual(sum(shares), total)
                self.assertEqual(len(shares), people)
                self.assertLessEqual(max(shares) - min(shares), 1)


if __name__ == '__main__':
    unittest.main()
