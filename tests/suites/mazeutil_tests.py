from mazeweb.mazeutil.numeric import randuniq

from .. import test, assert_exception

@test
def numeric_randuniq0():
    """randuniq for negative length"""
    with assert_exception(ValueError):
        list(randuniq(-1))


@test
def numeric_randuniq1():
    """randuniq for zero length"""
    with assert_exception(ValueError):
        list(randuniq(0))


@test
def numeric_randuniq2():
    """randuniq for valid length"""
    seen = set()
    for i, n in enumerate(randuniq(5000)):
        assert not n in seen, \
            '%d was seen again at iteration %d' % (n, i)
        seen.add(n)


@test
def numeric_randuniq3():
    """randuniq for different seeds"""
    list1 = list(randuniq(500, seed = 456))
    list2 = list(randuniq(500, seed = 457))
    assert list1 != list2, \
        'ranuniq for different seeds less than length resulted in equal lists'


@test
def numeric_randuniq4():
    """randuniq for undefined length input yielding at least 10000 values"""
    seen = set()
    for i, n in enumerate(randuniq(10000)):
        assert not n in seen, \
            '%d was seen again at iteration %d' % (n, i)
        seen.add(n)
