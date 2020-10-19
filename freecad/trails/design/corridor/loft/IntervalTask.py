# -*- coding: utf-8 -*-
# **************************************************************************
# *                                                                        *
# *  Copyright (c) 2019 Joel Graff <monograff76@gmail.com>                         *
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
Task classes for manageing the ElementLoft interval schedule
"""

import sys
from PySide import QtGui, QtCore
import operator
import re

class IntervalTask:
    def __init__(self, update_callback):

        #hack to find the ui file... :/
        path = sys.path[0] + '/../freecad-transportation-wb/transportationwb/corridor/task_panel.ui'
        self.ui = path
        self.form = None
        self.update_callback = update_callback

    def accept(self):
        self.update_callback(self)
        return True

    def reject(self):
        return True

    def clicked(self, index):
        pass

    def open(self):
        pass

    def needsFullSpace(self):
        return False

    def isAllowedAlterSelection(self):
        return True

    def isAllowedAlterView(self):
        return True

    def isAllowedAlterDocument(self):
        return True

    def getStandardButtons(self):
        return int(QtGui.QDialogButtonBox.Ok)

    def helpRequested(self):
        pass

    def add_item(self):

        indices = self.form.table_view.selectionModel().selectedIndexes()
        index = 0

        if not indices:
            row = self.form.table_view.model().rowCount()
            self.form.table_view.model().insertRows(row, 1)
            index = self.form.table_view.model().index(row, 0)

        else:
            for index in indices:

                if not index.isValid():
                    continue

                self.form.table_view.model().insertRows(index.row(), 1)

            index = indices[0]

        self.form.table_view.setCurrentIndex(index)
        self.form.table_view.edit(index)

    def remove_item(self):

        indices = self.form.table_view.selectionModel().selectedIndexes()

        for index in indices:

            if not index.isValid():
                continue

            self.form.table_view.model().removeRows(index.row(), 1)

    def build_model(self, data):
        """
        Construct the table model from the loft object property data
        """
        model_data = []

        for _i in range(0, len(data), 3):
            model_data.append([TableModel.fixup_station(data[_i]), data[_i + 1], data[_i]])

        return model_data

    def setup(self, data):

        #convert the data to lists of lists

        _mw = self.getMainWindow()

        form = _mw.findChild(QtGui.QWidget, 'TaskPanel')

        form.add_button = form.findChild(QtGui.QPushButton, 'add_button')
        form.remove_button = form.findChild(QtGui.QPushButton, 'remove_button')
        form.table_view = form.findChild(QtGui.QTableView, 'table_view')

        model_data = self.build_model(data)

        form.table_view.setModel(TableModel(form.table_view, model_data))
        form.table_view.setColumnHidden(2, True)
        form.table_view.setItemDelegate(TableModelDelegate())
        form.table_view.clicked.connect(lambda: form.table_view.model().sort(2))

        self.form = form

        QtCore.QObject.connect(form.add_button, QtCore.SIGNAL('clicked()'), self.add_item)
        QtCore.QObject.connect(form.remove_button, QtCore.SIGNAL('clicked()'), self.remove_item)

    def getMainWindow(self):

        top = QtGui.QApplication.topLevelWidgets()

        for item in top:
            if item.metaObject().className() == 'Gui::MainWindow':
                return item

        raise RuntimeError('No main window found')

    def addItem(self):
        pass

    def get_model(self):
        """
        Returns the model data set with every element converted to string to external Loft object
        """

        data = self.form.table_view.model().dataset

        result = []

        #truncate the formatted station column
        #and store the reversed result so the float station is first
        for _i in data:
            trunc = [_x for _x in _i[1:]]
            result.extend(trunc[::-1])

        return result

class TableModelDelegate(QtGui.QItemDelegate):

    def __init__(self, parent=None):

        QtGui.QItemDelegate.__init__(self, parent)

        self._is_editing = False

    def createEditor(self, parent, option, index):

        return super(TableModelDelegate, self).createEditor(parent, option, index)

    def setEditorData(self, editor, index):

        self._is_editing = True

        value = index.data(QtCore.Qt.EditRole) or index.data(QtCore.Qt.DisplayRole)

        if editor.metaObject().className() in ['QSpinBox', 'QDoubleSpinBox']:
            editor.setValue(value)

        else:
            editor.setText(value)

    def setModelData(self, editor, model, index):

        super(TableModelDelegate, self).setModelData(editor, model, index)

        self._is_editing = False

        #force a sort if data is set on the second column
        #assumption:  User is done adding / edditing an interval, so now it's safe to re-sort
        if index.column() == 1:
            model.sort(2)

    def isEditing(self):

        return self._is_editing

class TableModel(QtCore.QAbstractTableModel):

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

        return station + '+' + offset[0] + '.' + offset[1], value

    def __init__(self, table_view, data, parent=None):
        """
        Args:
            datain: a list of lists\n
            headerdata: a list of strings
        """
        QtCore.QAbstractTableModel.__init__(self, parent)

        self.rex_station = re.compile('[0-9]+\+[0-9]{2}\.[0-9]{2,}')
        self.rex_near_station = re.compile('(?:[0-9]+\+?)?[0-9]{1,2}(?:\.[0-9]*)?')

        self.dataset = data
        self.headerdata = ['Station', 'Interval', 'Value']

        self.table_view = table_view

    def rowCount(self, parent=QtCore.QModelIndex()):
        """
        Number of rows currently in the model
        """

        if self.dataset:
            return len(self.dataset)

        return 0

    def columnCount(self, parent=QtCore.QModelIndex()):
        """
        Number of columns currently in the model
        """
        if self.dataset:
            return len(self.dataset[0])

        return 3

    def data(self, index, role):
        """
        Return data for valid indices and display role
        """
        if not index.isValid():
            return None

        if not role in [QtCore.Qt.DisplayRole, QtCore.Qt.EditRole]:
            return None

        if not 0 <= index.row() < len(self.dataset):
            return None

        return self.dataset[index.row()][index.column()]

    def setData(self, index, value, role):
        """
        Update existing model data
        """

        if role != QtCore.Qt.EditRole:
            return False

        if index.isValid() and 0 <= index.row() < len(self.dataset):

            raw_value = None

            if index.column() == 0:

                #test to see if input is correctly formed
                rex = self.rex_station.match(value)

                #if not, look for a nearly correct form
                if rex is None:

                    rex = self.rex_near_station.match(value)

                    #not a valid station.  Abort
                    if rex is None:
                        return False

                    #value is nearly a valid station.  Fix it up.
                    sta = float(rex.group().replace('+', ''))
                    value, raw_value = self.fixup_station(sta)

            else:

                try:
                    test = float(value)

                except:
                    return False

            #set the value
            self.dataset[index.row()][index.column()] = value

            #set the flaoting-point value of the station, if defined
            if raw_value:
                self.dataset[index.row()][2] = raw_value

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
            return self.headerdata[col]

        return None

    def insertRows(self, row, count, index=QtCore.QModelIndex()):
        """
        Insert row into model
        """

        self.beginInsertRows(QtCore.QModelIndex(), row, row + count - 1)

        for _x in range(count):
            self.dataset.insert(row + _x, ['0+00.00', 0, 0])

        self.endInsertRows()

        return True

    def removeRows(self, row, count, index=QtCore.QModelIndex()):
        """
        Remove row from model
        """

        self.beginRemoveRows(QtCore.QModelIndex(), row, row + count - 1)

        self.dataset = self.dataset[:row] + self.dataset[row + count:]

        self.endRemoveRows()

        return True

    def sort(self, col, order=QtCore.Qt.AscendingOrder):
        """
        Sort table by given column number.
        """

        self.emit(QtCore.SIGNAL('layoutAboutToBeChanged()'))
        self.dataset = sorted(self.dataset, key=operator.itemgetter(col))

        if order == QtCore.Qt.DescendingOrder:
            self.dataset.reverse()

        self.emit(QtCore.SIGNAL('layoutChanged()'))

    def flags(self, index):

        return QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
