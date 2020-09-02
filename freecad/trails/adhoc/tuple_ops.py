import math

from collections.abc import Iterable

from operator import sub as op_sub
from operator import add as op_add
from operator import mul as op_mul
from operator import truediv as op_div

def _operation(op, op1, op2, fail_on_empty=False):

    #default tests for failed operations
    if op1 is None or op2 is None:

        if fail_on_empty or op1 is None:
            return None

    _op1 = op1
    _op2 = op2

    if not isinstance(_op1, Iterable):
        _op1 = (_op1,)

    #recurse against the list of items in op1 if op2 is undefined
    if op2 is None:

        _op2 = _op1[1:]

        #if op1 is a scalar, return op1
        if not _op2:
            return _op1

        #otherwise, recurse, operating all subsequent elements
        #against the first
        _op1 = (_op1[0],)*len(_op1)

        return tuple(map(op, _op1, _op2))

    elif not isinstance(op2, Iterable):
        _op2 = (_op2,)

    #op1 and op2 are both defined.
    _nests = [isinstance(_op1[0], Iterable), isinstance(_op2[0], Iterable)]

    #if both operands are not nested iterables, ensure they are
    #equal length, or pad accordingly and return the operation
    #if not any(_nests):

    _lens = [len(_op1), len(_op2)]
    _delta = abs(_lens[0] - _lens[1])

    _op1 = _op1
    _op2 = _op2

    if _delta:

        print(_delta)

        if _lens[0] < _lens[1]:
            print('truncate')
            _op2 = _op2[:_lens[0]]

        else:

            print('pad')
            _pad = 0

            if op == op_mul or op == op_div:
                _pad = 1

            if any(_nests):
                _pad = (_pad,)

            _pad = (_pad,)*_delta

            if _lens[0] > _lens[1]:
                _op2 = _op2 + _pad

        print(_lens, _pad, _op1, _op2)

    return tuple(map(op, _op1, _op2))

def add(op1, op2=None, fail_on_empty=False):
    """
    Add two operands as tuples, lists of tuples, or accumulate
    a single list of tuples (op1)
    """

    return _operation(op_add, op1, op2, fail_on_empty)

def subtract(op1, op2=None, fail_on_empty=False):
    """
    Subtract two operands as tuples, lists of tuples, or accumulate
    a single list of tuples (op1)
    """

    return _operation(op_sub, op1, op2, fail_on_empty)

def multiply(op1, op2=None, fail_on_empty=False):
    """
    Multiply two operands as tuples, lists of tuples, or accumulate
    a single list of tuples (op1)
    """

    return _operation(op_mul, op1, op2, fail_on_empty)

def divide(op1, op2=None, fail_on_empty=False):
    """
    Divide two operands as tuples, lists of tuples, or accumulate
    a single list of tuples (op1)
    """

    return _operation(op_div, op1, op2, fail_on_empty)