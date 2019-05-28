# -*- coding: utf-8 -*-

import unittest

from . import double


class TestSuite(unittest.TestCase):
    def test_foo(self) -> None:
        self.assertEqual(double(2), 4)


if __name__ == "__main__":
    unittest.main()
