# Iteration 1 tests: happy path only, the kind you get without the AI doing the thinking. They pass, but they do
# not test the tricky part (the remainder in a split), so the gate should catch that the tests are weak.
import unittest

import money


class TestMoneyHappy(unittest.TestCase):
    def test_add(self):
        self.assertEqual(money.add_cents(100, 50), 150)

    def test_percent(self):
        self.assertEqual(money.percent_cents(1000, 10), 100)

    def test_split_even(self):
        self.assertEqual(money.split_bill(100, 4), [25, 25, 25, 25])


if __name__ == '__main__':
    unittest.main()
