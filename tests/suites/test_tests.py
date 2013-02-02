from .. import test

before_was_called = False

def before_check(*args):
    global before_was_called
    before_was_called = True


after_was_called = False

def after_check():
    global after_was_called
    after_was_called = True


@test
@test.before(before_check)
@test.after(after_check)
def test_before_after0():
    """Asserts that the test.before function was called, and prepares for
    test_before_after0"""
    global before_was_called
    assert before_was_called, \
        'test.before did not cause the function to be called'


@test
def test_before_after1():
    """Asserts that the test.after function for test_before_after0 was called"""
    global after_was_called
    assert after_was_called, \
        'test.after did not cause the function to be called'


def after_raise():
    raise AssertionError('The test.after was run even when test.before '
        'returned False')

@test
@test.before(lambda: False)
@test.after(after_raise)
def test_before_cancelled0():
    """Asserts that returning False from test.before prevents the test and
    test.after from being run"""
    raise AssertionError('The test was run even when test.before returned '
        'False')
