from mazeweb.util.numeric import randuniq
from mazeweb.util.data import wrap, ConfigurationStore

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


@test
def wrap_cmp():
    """Tests comparison for standard types"""
    assert wrap(5) == 5, \
        'Comparison == with number failed'

    assert wrap(5) < 6, \
        'Comparison < with number failed'

    assert wrap(7) > 6, \
        'Comparison > with number failed'

    assert wrap(True) == True, \
        'Comparison with bool failed'

    assert wrap('Hello World!') == 'Hello World!', \
        'Comparison with string failed'

    assert wrap([1, 2, 3, 'four']) == [1, 2, 3, 'four'], \
        'Comparison with list failed'

    assert wrap({1: 'one', 2: 'two'}) == {1: 'one', 2: 'two'}, \
        'Comparison with dict failed'


@test
def wrap_hash():
    """Tests that using wrapped values as keys works as expected"""
    m = {}

    m[wrap(5)] = 5
    assert m.get(5, None) == 5, \
        'Hashing of number failed (keys: %s)' % m.keys()

    m[wrap(True)] = True
    assert m.get(True, None) == True, \
        'Hashing of boolean failed'

    m[wrap('A string')] = 'The string'
    assert m.get('A string', None) == 'The string', \
        'Hashing of string failed'


@test
def wrap_getattr():
    """Tests that wraps allows for easy attribute retrieval"""
    w = wrap(dict(
        a_boolean = True,
        a_number = 42,
        a_string = 'Some string',
        a_list = [
            True, 2, 'three',
            dict(
                key = 'next',
                value = 5)]))

    assert w.a_boolean == True, \
        'Access failed'
    assert w.a_number == 42, \
        'Access failed'
    assert w.a_string == 'Some string', \
        'Access failed'
    assert w.a_list[2] == 'three', \
        'Access failed'
    assert w.a_list[3].key == 'next', \
        'Access failed'


@test
def ConfigurationStore_call0():
    """Tests that calling a ConfigurationStore works"""
    w = ConfigurationStore(dict(
        a_boolean = True,
        a_number = 42,
        a_string = 'Some string',
        a_dict = dict(
            key = 'next',
            value = 5,
            another_dict = dict(
                the = 'end'))))

    assert w('a_boolean') == True, \
        'Access failed'
    assert w('a_number') == 42, \
        'Access failed'
    assert w('a_string') == 'Some string', \
        'Access failed'
    assert w('a_dict.key') == 'next', \
        'Access failed'
    assert w('a_dict.another_dict') == {'the': 'end'}, \
        'Access failed'


@test
def ConfigurationStore_call1():
    """Tests that calling a ConfigurationStore with default values works"""
    w = ConfigurationStore(dict(
        a_dict = dict(
            another_dict = dict(
                the = 'end'))))

    assert w('a_boolean', True) == True, \
        'Access failed'
    assert w('a_number', 42) == 42, \
        'Access failed'
    assert w('a_dict.key', 'next') == 'next', \
        'Access failed'
