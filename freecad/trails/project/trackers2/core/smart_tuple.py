# -*- coding: utf-8 -*-
#**************************************************************************
#*                                                                     *
#* Copyright (c) 2019 Joel Graff <monograff76@gmail.com>               *
#*                                                                     *
#* This program is free software; you can redistribute it and/or modify*
#* it under the terms of the GNU Lesser General Public License (LGPL)  *
#* as published by the Free Software Foundation; either version 2 of   *
#* the License, or (at your option) any later version.                 *
#* for detail see the LICENCE text file.                               *
#*                                                                     *
#* This program is distributed in the hope that it will be useful,     *
#* but WITHOUT ANY WARRANTY; without even the implied warranty of      *
#* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the       *
#* GNU Library General Public License for more details.                *
#*                                                                     *
#* You should have received a copy of the GNU Library General Public   *
#* License along with this program; if not, write to the Free Software *
#* Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307*
#* USA                                                                 *
#*                                                                     *
#***********************************************************************
"""
A smart tuple object with built in type conversion and math functions
"""

from collections.abc import Iterable
from operator import sub as op_sub
from operator import add as op_add

class SmartTuple():

    _sub = lambda lhs, rhs: tuple(map(op_sub, lhs, rhs))
    _add = lambda lhs, rhs: tuple(map(op_add, lhs, rhs))

    def __init__(self, data: Iterable):

        assert(isinstance(data, Iterable)),\
            'Non-iterable data type passed.  Expected Iterable.'

        self._tuple = tuple(data)

    def from_values(self, *args):

        _type = None
        _vals = []

        for _v in args:

            if not _type:

                if isinstance(_v, (int, float)):
                    _type = type(_v)

                elif isinstance(_v, str):
                    _type = float

            if not isinstance(_v, _type):
                _vals.append(_type(_v))

        assert(len(_vals) != len(args)), 'Value type conversion mismatch.'

        self._tuple = tuple(_vals)

    def _validate(self, args):

        _tpl = ()

        if len(args) == 1:

            if isinstance(args[0], SmartTuple):
                _tpl = args[0]._tuple

            else:
                _tpl = SmartTuple(args)._tuple

        else:
            assert(len(args) == len(self._tuple)),\
                'Length mismatch. {} values expected.'.format(len(self._tuple))

            _tpl = SmartTuple.from_values(args)._tuple

        return _tpl

    def sub(self, *args):

        _tpl = self._validate(args)

        if _tpl:
            return self._sub(self._tuple, _tpl)

        return ()

    def add(self, *args):

        _tpl = self._validate(args)

        if _tpl:
            return self._add(self._tuple, _tpl)

        return ()

    def __add__(self, other):

        self.add(other)

    def __sub__(self, other):

        self.sub(other)

    def __str__(self):

        return str(self._tuple)

    def __repr__(self):

        return self._tuple
