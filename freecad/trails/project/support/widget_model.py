# -*- coding: utf-8 -*-
#***********************************************************************
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
QAbstractTableModel class for Task QTableView
"""

import PySide.QtCore as QtCore

def create(data, headers=None, parent=None):
    """
    Creation method for widget models.

    Model is a dictionary or nested list providing the data set in a
    tabular format
    """

    model = WidgetModel(parent)

    model.data_model = data
    model.headers = headers

    return model


class WidgetModel(QtCore.QAbstractTableModel):
    """
    Widget model base class
    """

    def __init__(self, parent=None):

        QtCore.QAbstractTableModel.__init__(self)

        self.data_model = None
        self.headers = None

        self.default_flags = QtCore.Qt.ItemIsEditable \
                             | QtCore.Qt.ItemIsEnabled \
                             | QtCore.Qt.ItemIsSelectable

        self.data_roles = [QtCore.Qt.DisplayRole, QtCore.Qt.EditRole]

    def rowCount(self, parent=QtCore.QModelIndex()):
        """
        Number of rows currently in the model
        """

        if self.data_model:
            return len(self.data_model)

        return 0

    def columnCount(self, parent=QtCore.QModelIndex()):
        """
        Number of columns currently in the model
        """
        if self.data_model:
            if isinstance(self.data_model[0], list):
                return len(self.data_model[0])

            return 1

        return 0

    def data(self, index, role):
        """
        Return data for valid indices and display role
        """

        if not index.isValid():
            return None

        if not role in [QtCore.Qt.DisplayRole, QtCore.Qt.EditRole]:
            return None

        if not 0 <= index.row() < len(self.data_model):
            return None

        if self.columnCount(index) == 1:
            return self.data_model[index.row()]

        return self.data_model[index.row()][index.column()]

    def setData(self, index, value, role):
        """
        Update existing model data
        """

        if role != QtCore.Qt.EditRole:
            return False

        self.data_model[index.row()][index.column()] = value
        self.dataChanged.emit(index, index)

        return True

    def headerData(self, col, orientation, role):
        """
        Headers to be displated
        """

        if not self.headers:
            return None

        if orientation == QtCore.Qt.Horizontal \
            and role == QtCore.Qt.DisplayRole:

            return self.headers[col]

        return None

    def flags(self, index):
        """
        Model flags to control editing and viewing
        """
        if index.row() > 0:
            return self.default_flags & ~QtCore.Qt.ItemIsEditable

        return self.default_flags
