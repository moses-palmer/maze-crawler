# coding: utf-8
# mazeweb
# Copyright (C) 2012-2014 Moses Palmér
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.




def randuniq(length, seed = 1):
    """
    Generates length unique, pseudo-random numbers.

    @param length
        The number of numbers to generate. If this is None, an infinite number
        of numbers will be generated, but they are not necessarily unique.
    @param seed
        A seed to use to initialise the pseudo-random generator. Given the same
        length and same seed, the sequence of the numbers will always be the
        same. For the same length and different seeds, the sequence will be
        different as long as seed is smaller than length
    @return a generator that yields ints
    @raise ValueError if seed is zero or less, length is negative, zero or
        greater than 2**31
    """
    if seed <= 0:
        raise ValueError('seed is invalid')
    if not length is None:
        if length <= 0:
            raise ValueError('length is too small')
        elif length > 2**31:
            raise ValueError('length is too great')

    mask = 0xD0000001
    data = seed & (2**32 - 1)

    if not length is None:
        iterator = range(length)
    else:
        def iterator():
            i = 0
            while True:
                yield i
                i += 1
        iterator = iterator()

    for index in iterator:
        data = (data >> 1) ^ (-(data & 1) & mask)

        yield data
