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

import math

import FreeCAD as App
import FreeCADGui as Gui

from DraftTools import Modifier
from ..support.const import Const
from ...geometry import support
from ...geometry import arc

class Fresnel(Const):
    """
    Fresnel const support class
    """

    TERM_LIST = [_v for _v in range(0, 16)]

    POW_FN = lambda _p, _t=TERM_LIST: [4*_v + _p for _v in _t]

    TERM_FN = lambda _p, _c, _t=TERM_LIST[::-1]: [
        ((-1)**_v) / (math.factorial((2*_v)+_c) * _p[_v]) for _v in _t
    ]

    TERM_C = TERM_FN(POW_FN(1), 0)
    TERM_S = TERM_FN(POW_FN(3), 1)

    @staticmethod
    def _fresnel(value, base_power, terms):
        """
        Evaluate the fresnel integral
        """

        val_4 = value**4
        _result = 0.0

        for _v in terms[:-1]:
            _result = val_4 * (_v + _result)

        return (value**base_power) * (terms[-1]+_result)

    @staticmethod
    def fresnel_c(value):
        """
        Evaluate the fresnel integral of cos(t^2) dt
        """

        return Fresnel._fresnel(value, 1, Fresnel.TERM_C)

    @staticmethod
    def fresnel_s(value):
        """
        Evaluate the fresnel integral of sin(t^2) dt
        """

        return Fresnel._fresnel(value, 3, Fresnel.TERM_S)

class SpiralTest(Modifier):
    """
    Command Description
    """
    def __init__(self):

        pass

    def GetResources(self):

        return {'Pixmap'  : '',
                'Accel'   : '',
                'MenuText': '',
                'ToolTip' : '',
                'CmdType' : 'ForEdit'}

    def Activated(self):
        """
        Command activation method
        """

        #generate a spiral with two radii given the arcs on either side
        #and render it
        Modifier.Activated(self, 'SpiralTest')

        arc1 = {
            'BearingIn': math.pi / 2.0,
            'Radius': 2600.0,
            'Delta': math.radians(44.821592613698),
            'Start': App.Vector(),
            'Direction': -1
        }

        arc1 = arc.get_parameters(arc1)

        arc2 = {
            'BearingIn': 10.0,
            'Radius': 1750.0,
            'Delta': math.radians(16.074936823812),
            'Start': App.Vector(),
            'Direction': -1
        }

        arc2 = arc.get_parameters(arc2)


Gui.addCommand('SpiralTest', SpiralTest())
