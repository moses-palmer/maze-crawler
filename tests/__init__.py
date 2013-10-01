"""
The current indentation.
"""
_indent = 0

def printf(format, *args):
    global _indent
    print('\t' * _indent + format % args)


class assert_exception(object):
    def __init__(self, *exceptions):
        self.exceptions = exceptions

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        assert exc_type in self.exceptions, \
            'None of exceptions [%s] were thrown' % (', '.join(
                e.__name__ for e in self.exceptions))
        return True


class Suite(object):
    """
    The test suites to run when test.run is called.

    Use the decorator test to populate this list.
    """
    __suites__ = {}

    def __init__(self, name):
        """
        Initialises this test suite from a module instance.

        No tests are added automatically: when using the @test decorator, a test
        suite will be instantiated for the first decorated function, and all
        following decorated functions will be added to this object.

        @param name
            The name of this test suite.
        """
        super(Suite, self).__init__()
        self.tests = []
        self._name = name
        self._setup = lambda: True
        self._teardown = lambda: True

    @property
    def name(self):
        """The name of this test suite"""
        return self._name

    def run(self):
        """
        Runs this test suite.

        @return the failed tests, or None if the suite was cancelled by setup
        """
        printf('Running test suite %s with %d tests...',
            self.name, len(self.tests))
        if not self._setup():
            return None
        global _indent
        _indent += 1
        failures = [test for test in self.tests if not test()]
        self._teardown()
        _indent -= 1
        return failures

    @classmethod
    def _get_test_suite(self, test):
        """
        Returns the test suite for a test.

        If the suite does not already exist, it is created.

        @param test
            The test instance.
        @return the suite instance
        """
        # Get the global scope for the function to retrieve the name of the
        # defining module
        suite = test.suite \
            if 'suite' in test.__dict__ \
            else test.__globals__['__name__']

        # If the test suite does not yet exist, create it
        if not suite in self.__suites__:
            self.__suites__[suite] = Suite(suite)

        return self.__suites__[suite]


def test(func):
    """
    Use this decorator to mark a callable as a test.

    The description of the test is determined as follows:
        * If func.description exists, it is used.
        * If the test function has a docstring, it is used.
        * Otherwise the function name is split on '_' and then joined with '.'
          before any part that begins with a capital letter followed by a lower
          case letter and '_' for any other case.
    """
    test_name = func.name \
        if hasattr(func, 'name') \
        else func.__name__
    if hasattr(func, 'description'):
        test_description = func.description
    elif func.__doc__:
        test_description = ' '.join(func.__doc__.split())
    else:
        test_description = ''
        was_namespace = False
        for s in test_name.split('_'):
            test_description += \
                '.' + s if was_namespace else \
                '_' + s if test_description else \
                s
            was_namespace = len(s) >= 2 and (
                s[0].isupper() and s[1].islower())

    def inner():
        global _indent
        test_before = getattr(func, 'test_before', lambda: True)
        test_after  = getattr(func, 'test_after', lambda: None)
        try:
            printf('%s - %s', test_name, test_description)
            try:
                _indent += 1
                if not test_before() is False:
                    try:
                        func()
                    finally:
                        test_after()
                return True
            finally:
                _indent -= 1
        except AssertionError as e:
            printf('Test %s did not pass: %s', test_name, str(e))
            inner.message = str(e)
            return False
        except SystemExit:
            raise
        except Exception as e:
            import traceback
            printf('Test %s did not pass: %s', test_name, str(e))
            traceback.print_exc()
            inner.message = str(e)
            return False

    # Add the function to the test suite for the defining module
    suite = Suite._get_test_suite(func)
    suite.tests.append(inner)

    inner.name = test_name
    inner.description = test_description
    inner.suite = suite.name
    inner.message = None
    return inner


def suite(func):
    """
    Use this decorator to mark a callable as a full test suite.

    The decorated function must return a list of tuples on the format (name,
    message). Each tuple represents a failed test with the name name and the
    message message.

    To signal that the suite was cancelled, return None.
    """
    class InnerTestResult(object):
        def __init__(self, name, message):
            self.name = name
            self.message = message

    class InnerSuite(Suite):
        def __init__(self, name):
            self._name = name

        def run(self):
            """
            @see Suite.run
            """
            printf('Running test suite %s...',
                func.__name__)
            if not getattr(func, 'setup', lambda: True)():
                return None
            global _indent
            _indent += 1
            result = func()
            if result is None:
                return None
            failures = [InnerTestResult(*t) for t in result]
            _indent -= 1
            return failures

    # Add the function as a suite
    wrapped = InnerSuite(func.__name__)
    Suite.__suites__[wrapped.name] = wrapped

    return wrapped


def _before(func):
    """
    Sets a callable to call before the test is run.

    If this function returns False, the test and the after function if set are
    not run.

    @param func
        The function to call before the test is run. This is called with no
        parameters.
    """
    def decorator(test):
        test.test_before = func
        return test
    return decorator
test.before = _before

def _after(func):
    """
    Sets a callable to call after the test is run. The callable is always
    called if the before function did not raise an exception or return False.

    @param func
        The function to call after the test is run. This is called with no
        parameters.
    """
    def decorator(test):
        test.test_after = func
        return test
    return decorator
test.after = _after


def _setup(func):
    """
    Use this decorator to mark a callable as a test suite setup function.
    """
    Suite._get_test_suite(func)._setup = func

    return func
test.setup = _setup

def _teardown(func):
    """
    Use this decorator to mark a callable as a test suite teardown function.
    """
    Suite._get_test_suite(func)._teardown = func

    return func
test.teardown = _teardown


def run(suite_names):
    import importlib
    import suites

    global _indent
    total_failures = []

    for suite_name in suite_names or suites.__all__:
        try:
            importlib.import_module('.' + suite_name, 'tests.suites')
        except ImportError as e:
            print('Failed to import test suite %s: %s' % (suite_name, str(e)))

    for suite in Suite.__suites__.values():
        _indent += 1
        failures = suite.run()
        _indent -= 1
        if failures is None:
            printf('Test suite %s was cancelled by setup.', suite.name)
            continue
        printf('Test suite %s completed with %d failed test(s).',
            suite.name, len(failures))
        total_failures += failures

    return total_failures
