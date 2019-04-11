# -*- coding: utf-8 -*-
# **************************************************************************
# *                                                                        *
# *  Copyright (c) 20XX Joel Graff <monograff76@gmail.com>                         *
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
QAbstractTableModel class for Task QTableView
"""

import re
import operator

from PySide import QtCore

class TaskModel(QtCore.QAbstractTableModel):

    rex_station = re.compile('[0-9]+\+[0-9]{2}\.[0-9]{2,}')
    rex_near_station = re.compile('(?:[0-9]+\+?)?[0-9]{1,2}(?:\.[0-9]*)?')

    @staticmethod
    def validate_station(value):
        """
        Validate station data as correctly-formed
        """

        #test to see if input is correctly formed
        rex = TaskModel.rex_station.match(value)

        #if not, look for a nearly correct form
        if rex is None:

            rex = TaskModel.rex_near_station.match(value)

            #not a valid station.  Abort
            if rex is None:
                return None

            #value is nearly a valid station.  Fix it up.
            sta = float(rex.group().replace('+', ''))
            value = TaskModel.fixup_station(sta)

        return value

    @staticmethod
    def fixup_station(value):
        """
        Fix up a float value that is nearly a station
        Return as a string
        """

        station = '0'

        #split the station and offset, if the station exists
        if value >= 100.0:
            station = str(int(value / 100.0))
            offset = str(round(value - float(station) * 100.0, 2))

        else:
            offset = str(value)

        offset = offset.split('.')

        #no decimals entered
        if len(offset) == 1:
            offset.append('00')

        #offset is less than ten feet
        if len(offset[0]) == 1:
            offset[0] = '0' + offset[0]

        #only one decimal entered
        if len(offset[1]) == 1:
            offset[1] += '0'

        #truncate the offset to two decimal places
        offset[1] = offset[1][:2]

        return station + '+' + offset[0] + '.' + offset[1]

    def __init__(self, table_view, data, headers, parent=None):

        QtCore.QAbstractTableModel.__init__(self, parent)

        self.data_model = data
        self.headers = headers

        self.table_view = table_view

    def rowCount(self, parent=QtCore.QModelIndex()):
        """
        Number of rows currently in the model
        """

        if self.data_model:
            return len(self.data_model)

        #default
        return 0

    def columnCount(self, parent=QtCore.QModelIndex()):
        """
        Number of columns currently in the model
        """
        if self.data_model:
            return len(self.data_model[0])

        #default
        return 3

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

        return self.data_model[index.row()][index.column()]

    def setData(self, index, value, role):
        """
        Update existing model data
        """

        if role != QtCore.Qt.EditRole:
            return False

        if index.isValid() and 0 <= index.row() < len(self.data_model):

            raw_value = None

            #test for valid data types on a per-column basis
            if index.column() == 0:
                value = self.validate_station(value)

            else:

                try:
                    test = float(value)

                except:
                    return False

            #set the value
            self.data_model[index.row()][index.column()] = value

            #set the flaoting-point value of the station, if defined
            if raw_value:
                self.data_model[index.row()][2] = float(value.replace('+',''))

            #force a sort if not currently editing
            if not self.table_view.itemDelegate().isEditing():
                self.sort(2)

            self.dataChanged.emit(index, index)

            return True

        return False

    def headerData(self, col, orientation, role):
        """
        Headers to be displated
        """

        if col > 1:
            return None

        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self.headers[col]

        return None

    def insertRows(self, row, count, index=QtCore.QModelIndex()):
        """
        Insert row into model
        """

        self.beginInsertRows(QtCore.QModelIndex(), row, row + count - 1)

        for _x in range(count):
            self.data_model.insert(row + _x, ['0+00.00', 0, 0])

        self.endInsertRows()

        return True

    def removeRows(self, row, count, index=QtCore.QModelIndex()):
        """
        Remove row from model
        """

        self.beginRemoveRows(QtCore.QModelIndex(), row, row + count - 1)

        self.data_model = self.data_model[:row] + self.data_model[row + count:]

        self.endRemoveRows()

        return True

    def sort(self, col, order=QtCore.Qt.AscendingOrder):
        """
        Sort table by given column number.
        """

        self.emit(QtCore.SIGNAL('layoutAboutToBeChanged()'))
        self.data_model = sorted(self.data_model, key=operator.itemgetter(col))

        if order == QtCore.Qt.DescendingOrder:
            self.data_model.reverse()

        self.emit(QtCore.SIGNAL('layoutChanged()'))

    def flags(self, index):

        return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
