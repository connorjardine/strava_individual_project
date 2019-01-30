import unittest

from frontend.application.services import *


class TestServices(unittest.TestCase):

    def test_hash(self):
        result = hash_md5("hello1234")
        self.assertEqual(result, "9a1996efc97181f0aee18321aa3b3b12")

    def test_convert_seconds(self):
        result = convert_seconds("9:59:59")
        self.assertEqual(result, 35999)
        self.assertNotEqual(result, "35999")

    def test_distance_between_start(self):
        result = dist_between_start([55.832429, -4.539433], [55.832394, -4.539464], 10)
        result1 = dist_between_start([55.832429, -4.539433], [55.832394, -4.539464], 100)
        self.assertTrue(result, True)
        self.assertTrue(result1, False)


if __name__ == '__main__':
    unittest.main()
