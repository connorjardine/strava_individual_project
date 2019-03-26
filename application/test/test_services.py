import unittest

from application.func.services import *


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

    def test_convert_hours(self):
        result = convert_hours('1:20:00')
        self.assertEqual(result, 1.3333333333333333)

    def test_return_all_routes(self):
        result = return_all_routes()
        self.assertTrue(type(result) == list)

    def test_strava_auth(self):
        result = strava_auth()
        self.assertEqual(result, "https://www.strava.com/oauth/authorize?client_id=29157&redirect_uri=http%3A%2F%2F127.0.0.1%3A5000%2Flogin&approval_prompt=auto&response_type=code")


if __name__ == '__main__':
    unittest.main()
