import unittest

from frontend.application.services import hash_md5


class TestServices(unittest.TestCase):

    def test_hash(self):
        result = hash_md5("hello_1234")
        self.assertEqual(result, "9a1996efc97181f0aee18321aa3b3b12")


if __name__ == '__main__':
    unittest.main()
