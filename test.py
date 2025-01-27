import unittest
from fortest import divide

class Testdivide(unittest.TestCase):
    def test_divide_success(self):
        self.assertEqual(divide(50,2), 0)
        self.assertEqual(divide(1, 2), 1)
        self.assertEqual(divide(0, 4), 0)

    def test_divide_zero(self):
        self.assertRaises(ValueError, divide, 35, 0)

if __name__ == '__main__':
    unittest.main()