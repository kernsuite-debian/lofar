import unittest
from lofar.common.cache import cache


class TestCache(unittest.TestCase):

    @cache
    def cached_func(self, arg, kwarg=None):
        self.invocations += 1
        return arg, kwarg

    def setUp(self):
        self.invocations = 0

    def test_simple_function(self):
        """ Check whether the cache class works with simple functions. """

        @cache
        def cached_func(arg, kwarg=None):
            return arg, kwarg

        result = cached_func(1, 2)

        self.assertEqual(result, (1, 2))

    def test_class_member(self):
        """ Check whether the cache class works with class members. """

        class myclass:
            @cache
            def cached_func(self, arg, kwarg=None):
                return arg, kwarg

        obj = myclass()
        result = obj.cached_func(1, 2)

        self.assertEqual(result, (1, 2))

    def test_class_static_member(self):
        """ Check whether the cache class works with static class members. """

        class myclass:
            @staticmethod
            @cache
            def cached_func(arg, kwarg=None):
                return arg, kwarg

        obj = myclass()
        result = obj.cached_func(1, 2)

        self.assertEqual(result, (1, 2))

    def test_class_property(self):
        """ Check whether the cache class works with class properties. """

        class myclass:
            @property
            @cache
            def cached_func(self):
                return True

        obj = myclass()
        result = obj.cached_func

        self.assertEqual(result, True)

    def test_initial_call(self):
        """ Does the cache return the correct result? """

        result = self.cached_func(1, 2)

        self.assertEqual(result, (1, 2))
        self.assertEqual(self.invocations, 1)

    def test_cached_call(self):
        """ Does the cache cache results? """

        result = self.cached_func(1, 2)
        result = self.cached_func(1, 2)

        self.assertEqual(result, (1, 2))
        self.assertEqual(self.invocations, 1)

    def test_different_calls(self):
        """ Does the cache NOT cache results if new parameters are provided? """

        result = self.cached_func(1, 2)
        result = self.cached_func(1, 3)

        self.assertEqual(result, (1, 3))
        self.assertEqual(self.invocations, 2)

def main(argv):
    unittest.main()

if __name__ == "__main__":
    # run all tests
    import sys
    main(sys.argv[1:])

