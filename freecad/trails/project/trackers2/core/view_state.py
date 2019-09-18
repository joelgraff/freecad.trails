# -*- coding: utf-8 -*-
#***********************************************************************
#*                                                                     *
#* Copyright (c) 2018 Joel Graff <monograff76@gmail.com>               *
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
View state class
"""

from pivy import coin
from PySide import QtGui

from FreeCAD import Vector

import FreeCADGui as Gui

from . import utils

from .singleton import Singleton

class ViewState(metaclass=Singleton):
    """
    Class to track the current state of the active or specified view
    """

    def __init__(self, view=None):
        """
        ViewState constructor
        """

        if not view:
            view = Gui.ActiveDocument.ActiveView

        self.view = view
        self.viewport = \
            view.getViewer().getSoRenderManager().getViewportRegion()

        self.sg_root = self.view.getSceneGraph()

        self.active_task_panel = None
        self._matrix = None

    def get_matrix(self, node, parent=None, refresh=True):
        """
        Return the matrix for transfomations applied to the passed node

        node - the Coin3D SoNode with the desired transformation
        parent - optional - sg root default
        refresh - if false, retrieves last matrix
        """

        if not parent:
            parent = self.sg_root

        if not refresh:
            if self._matrix:
                return self._matrix

        #define the search path
        _search = coin.SoSearchAction()
        _search.setNode(node)
        _search.apply(parent)

        #get the matrix for the transformation
        _matrix = coin.SoGetMatrixAction(ViewState().viewport)
        _matrix.apply(_search.getPath())

        self._matrix = coin.SbMatrix(_matrix.getMatrix().getValue())

        return self._matrix

    def get_active_task_panel(self, refresh=False):
        """
        Return a reference to the task panel form currently displayed
        and save a reference to it in the active_task property
        """

        if self.active_task_panel and not refresh:
            return self.active_task_panel

        _form = utils.getMainWindow().findChild(QtGui.QWidget, 'TaskPanel')

        self.active_task_panel = _form

        return _form

    def valid_matrix(self):
        """
        Returns whether or not the matrix has been updated by the
        scenegraph by testing for the bottom-right value == 1.0
        """

        if not self._matrix:
            return False

        return self._matrix.getValue()[3][3] == 1.0

    def transform_points(self, points, node=None, refresh=True):
        """
        Transform selected points by the transformation matrix
        """

        #store the view state matrix if a valid node is passed.
        #subsequent calls with null node will re-use the last valid node matrix
        refresh = refresh and node is not None

        _matrix = self.get_matrix(node, refresh=refresh)

        if not _matrix:
            return []

        #list of coin vectors requires conversion to tuples
        if isinstance(points[0], coin.SbVec3f):
            points = [_v.getValue() for _v in points]

        elif isinstance(points[0], Vector):
            points = [tuple(_v) for _v in points]

        #append fourth point to each coordinate
        _pts = [_v + (1.0,) for _v in points]

        _s = 0
        _result = []

        #iterate the list, processing it in sets of four coordinates at a time
        while _s < len(_pts):

            _mat_pts = _pts[_s:_s + 4]

            _last_point = len(_mat_pts)

            #pad the list if less than four points
            for _i in range(len(_mat_pts), 4):
                _mat_pts.append((0.0, 0.0, 0.0, 1.0))

            #convert and transform
            _mat = coin.SbMatrix(_mat_pts)

            for _v in _mat.multRight(_matrix).getValue()[:_last_point]:
                _result.append(tuple(_v))

            _s += 4

        return _result

    def getPointOnScreen(self, point):
        """
        Convenience function for view.getPointOnScreen()
        """

        return Vector(self.view.getPointOnScreen(Vector(point)) + (0.0,))
