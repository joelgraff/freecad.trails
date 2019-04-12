# -*- coding: utf-8 -*-
# **************************************************************************
# *                                                                        *
# *  Copyright (c) 2019 Joel Graff <monograff76@gmail.com>                 *
# *                                                                        *
# *  This program is free software; you can redistribute it and/or modify  *
# *  it under the terms of the GNU Lesser General Public License (LGPL)    *
# *  as published by the Free Software Foundation; either version 2 of     *
# *  the License, or (at your option) any later version.                   *
# *  for detail see the LICENCE text file.                                 *
# *                                                                        *
# *  This program is distributed in the hope that it will be useful,       *
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *  GNU Library General Public License for more details.                  *
# *                                                                        *
# *  You should have received a copy of the GNU Library General Public     *
# *  License along with this program; if not, write to the Free Software   *
# *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *  USA                                                                   *
# *                                                                        *
# **************************************************************************

"""
Line generation tools
"""

from Geometry import Support

def get_parameters(line):
    """
    Return a fully-defined line
    """

    _coord_truth = [not line.get('Start') is None, not line.get('End') is None]
    _param_truth = [not line.get('BearingIn') is None, not line.get('Length') is None]

    #both coordinates defined
    _case_one = all(_coord_truth)

    #only one coordinate defined, plus both length and bearing
    _case_two = any(_coord_truth) and not all(_coord_truth) and all(_param_truth)

    if _case_one:

        line_vec = line['End'].sub(line['Start'])
        _bearing = Support.get_bearing(line_vec)
        _length = line_vec.Length

        #test for missing parameters, preserving the existing ones
        if line.get('BearingIn'):
            if Support.within_tolerance(line['BearingIn'], _bearing):
                _bearing = line['BearingIn']

        line['BearingIn'] = line['BearingOut'] = _bearing

        if line.get('Length'):
            if Support.within_tolerance(line['Length'], _length):
                _length = line['Length']

        line['Length'] = _length

    elif _case_two:

        _vec = Support.vector_from_angle(line['BearingIn']).multiply(line['Length'])

        if line.get('Start'):
            line['End'] = line['Start'].add(_vec)
        else:
            line['Start'] = line['End'].add(_vec)

    else:
        print('Unable to calculate line parametters')

    result = None

    if _case_one or _case_two:
        result = {**{'Type': 'line'}, **line}

    return result
