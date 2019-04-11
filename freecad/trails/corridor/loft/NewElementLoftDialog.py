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

from PySide import QtCore, QtGui

class Dialog(QtGui.QDialog):

    def get_number(self, text):
        """
        Get the number, assuming it's float, int, or station
        """

        #assume the text is a float, int or valid station
        result = None

        try:
            result = float(text)
        except:
            try:
                result = float(int(text))
            except:
                if '+' in text:
                    result = self.get_number(text.replace('+', ''))

        return result

    def update_station(self, line_edit):
        """
        Validate the data entered in the station line edit
        """

        value = self.get_number(line_edit.text())

        if value is None:
            msg = QtGui.QMessageBox.critical(self, self.tr('Station Error'), self.tr('Invalid station entered'))
            msg.show()
            return

        station = int(value / 100.0)
        offset = value - float(station * 100.0)

        line_edit.setText(str(station) + '+' + str('{:04.2f}').format(offset))

    def accept(self):
        """
        Override accept function
        """

        self.update_cb(self.get_properties())
        self.done(QtGui.QDialog.DialogCode.Accepted)

    def reject(self):
        """
        Override reject function
        """

        self.update_cb(None)
        self.done(QtGui.QDialog.DialogCode.Rejected)

    def __init__(self, units, parent=None):

        super(Dialog, self).__init__(parent)

        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)

        self.setWindowTitle(self.tr('Generate New Element Loft'))
        self.setSizeGripEnabled(True)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        form_layout = QtGui.QFormLayout()
        pref_policy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        max_policy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)

        #self.setSizePolicy(max_policy)

        #loft name input
        self.loft_name = QtGui.QLineEdit('ElementLoft', self)
        self.loft_name.setSizePolicy(pref_policy)
        form_layout.addRow(self.tr('Name'), self.loft_name)

        #start and end stations
        station_layout = QtGui.QGridLayout()
        station_layout.addWidget(QtGui.QLabel(self.tr('from')),0,0)

        self.start_sta = QtGui.QLineEdit('', self)
        self.start_sta.setMinimumSize(self.start_sta.width() * 0.85, self.start_sta.height() * 0.65)        
        self.start_sta.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.start_sta.setSizePolicy(pref_policy)
        self.start_sta.setInputMethodHints(QtCore.Qt.ImhPreferNumbers)
        self.start_sta.editingFinished.connect( lambda: self.update_station(self.start_sta))
        self.start_sta.setText('0+00.00')

        station_layout.addWidget(self.start_sta, 0, 1)

        station_layout.addWidget(QtGui.QLabel(self.tr('to')), 0, 2)

        self.end_sta = QtGui.QLineEdit('', self)
        self.end_sta.setMinimumSize(self.end_sta.width() * 0.85, self.end_sta.height() * 0.65)
        self.end_sta.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.end_sta.setSizePolicy(pref_policy)
        self.end_sta.setInputMethodHints(QtCore.Qt.ImhPreferNumbers)
        self.end_sta.editingFinished.connect(lambda: self.update_station(self.end_sta))
        self.end_sta.setText('0+00.00')

        station_layout.addWidget(self.end_sta, 0, 3)

        form_layout.addRow(self.tr('Station'), station_layout)
        form_layout.setAlignment(station_layout, QtCore.Qt.AlignLeft)

        #sektch template dropdown
        sketch_layout = QtGui.QGridLayout()

        self.sketch_template = QtGui.QComboBox(self)
        self.sketch_template.setSizePolicy(pref_policy)

        sketch_layout.addWidget(self.sketch_template,0,0)

        self.sketch_local = QtGui.QCheckBox('Local Copy', self)
        self.sketch_local.setCheckState(QtCore.Qt.CheckState.Checked)

        sketch_layout.addWidget(self.sketch_local, 0, 1)

        form_layout.addRow(self.tr('Template'), sketch_layout)

        #alignment drop down
        self.alignment = QtGui.QComboBox(self)
        self.alignment.setSizePolicy(max_policy)

        form_layout.addRow(self.tr('Alignment'), self.alignment)

        #interval spinbox
        self.interval = QtGui.QSpinBox(self)
        self.interval.setRange(0, 100)
        self.interval.setValue(25)
        self.interval.setSizePolicy(max_policy)

        form_layout.addRow(self.tr('Interval (%s)' % units), self.interval)

        #material dropdown
        self.material = QtGui.QComboBox(self)
        self.material.addItems(['Default', 'Material 1', 'Material 2', 'Material 3'])
        self.material.setSizePolicy(max_policy)

        form_layout.addRow(self.tr('Material'), self.material)

        #buttons
        buttons_layout = QtGui.QDialogButtonBox(
            QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel,
            QtCore.Qt.Horizontal
        )
        buttons_layout.accepted.connect(self.accept)
        buttons_layout.rejected.connect(self.reject)

        #button_layout = QtGui.QHBoxLayout()
        #button_layout.addStretch(1)

        #self.ok_button = QtGui.QPushButton(self.tr('&Ok'), self)
        #button_layout.addWidget(self.ok_button)

        #self.cancel_button = QtGui.QPushButton(self.tr('&Cancel'), self)
        #button_layout.addWidget(self.cancel_button)

        #build dialog
        layout = QtGui.QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addStretch(1)
        layout.addWidget(buttons_layout)
        self.setLayout(layout)

        self.resize(self.minimumSizeHint())

    def set_update_cb(self, call_back):

        self.update_cb = call_back

    def get_properties(self):
        """
        Return the user-specified properties for the loft
        """

        return {
            'name' : self.get_name(),
            'stations' : self.get_stations(),
            'sketch' : self.get_template(),
            'is_local' : self.get_local_copy(),
            'material' : self.get_material(),
            'alignment' : self.get_alignment(),
            'interval' :self.get_interval()
        }

    def set_template_list(self, list_items):
        """
        Set the list of sketch templates
        """

        for item in list_items:
            self.sketch_template.addItem(item.Label, item)

    def set_alignment_list(self, list_items):
        """
        Set the list of alignments
        """

        for item in list_items:
            self.alignment.addItem(item.Label, item)

    def set_material_list(self, list_items):
        """
        Set the list of available materials
        """

        self.material.addItems(list_items)

    def get_alignment(self):
        """
        Return the user-selected alignment
        """

        return self.alignment.itemData(self.alignment.currentIndex())

    def get_template(self):
        """
        Return the user-selected template
        """

        return self.sketch_template.itemData(self.sketch_template.currentIndex())

    def get_material(self):
        """
        Return the user-selected material
        """

        return self.material.itemData(self.material.currentIndex())

    def get_interval(self):
        """
        Return the user-defined interval
        """

        return int(self.interval.cleanText())

    def get_stations(self):
        """
        Return the station range
        """

        return [self.get_number(self.start_sta.text()), self.get_number(self.end_sta.text())]

    def get_name(self):
        """
        Return the user-defined name for the loft
        """

        return self.loft_name.text()

    def get_local_copy(self):
        """
        Return whether the sketch template is to be a local copy
        """

        return self.sketch_local.isChecked()