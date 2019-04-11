# -*- coding: utf-8 -*-
#***********************************************************************
#*                                                                     *
#* Copyright (c) 20XX Joel Graff <monograff76@gmail.com>               *
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
Subtask to populate the XML dialog when an XML file is chosen for import
"""

import csv

import PySide.QtGui as QtGui
import PySide.QtCore as QtCore

from freecad.trails.project import CsvParser
from freecad.trails.project.tasks.alignment.import_alignment_model \
    import ImportAlignmentModel as Model

from freecad.trails.project.tasks.alignment.import_alignment_view_delegate \
    import ImportAlignmentViewDelegate as Delegate

from freecad.trails.corridor.alignment import horizontal_alignment

def create(panel, filepath):

    return ImportCsvSubtask(panel, filepath)

class ImportCsvSubtask:

    def __init__(self, panel, filepath):

        self.errors = []
        self.panel = panel
        self.filepath = filepath

        self._setup_panel()

        self._populate_panel()

    def _setup_panel(self):

        self.table_view = self.panel.findChild(QtGui.QTableView, 'table_view')
        self.header_matcher = self.panel.findChild(QtGui.QTableView, 'header_matcher')

        self.headers = self.panel.findChild(QtGui.QCheckBox, 'headers')
        self.delimiter = self.panel.findChild(QtGui.QLineEdit, 'delimiter')

        self.headers.stateChanged.connect(self._open_file)
        self.delimiter.editingFinished.connect(self._open_file)

    def _populate_panel(self):

        sniffer = csv.Sniffer()

        with open(self.filepath, encoding="utf-8-sig") as stream:

            first_bytes = stream.read(1024)
            stream.seek(0)

            self.dialect = sniffer.sniff(first_bytes)
            self.panel.delimiter.setText(self.dialect.delimiter)

        check_state = QtCore.Qt.Checked

        if not sniffer.has_header(first_bytes):
            check_state = QtCore.Qt.Unchecked

        self.panel.headers.setCheckState(check_state)

        self._open_file()

    def _open_file(self):
        """
        Open the file for previewing
        """

        if self.dialect.delimiter != self.panel.delimiter.text():
            self.dialect.delimiter = self.panel.delimiter.text()

        with open(self.filepath, encoding="utf-8-sig") as stream:

            csv_reader = csv.reader(stream, self.dialect)

            #populate table view...
            data = [row for row in csv_reader]

        headers = data[0]

        if self.panel.headers.isChecked():
            data = data[1:]
        else:
            headers = ['Column ' + str(_i) for _i in range(0, len(data[0]))]

        table_model = Model('csv', headers[:], data)
        self.panel.table_view.setModel(table_model)

        self._populate_views(headers)

    def _populate_views(self, header):
        """
        Populate the table views with the data acquired from open_file
        """
        model = HorizontalAlignment.meta_fields + HorizontalAlignment.data_fields + HorizontalAlignment.station_fields

        lower_header = [_x.lower() for _x in header]
        lower_model = [_x.lower() for _x in model]
        
        #get indices in model that are exact matches in header
        model_indices = [_i for _i, _v in enumerate(lower_model) if _v in lower_header]
        header_indices = [_i for _i, _v in enumerate(lower_header) if _v in lower_model]

        pairs = []

        for _i in model_indices:

            for _j in header_indices:

                if lower_model[_i] == lower_header[_j]:
                    pairs.append([_i, _j])

        top_row = [''] * len(header)

        for tpl in pairs:
            top_row[tpl[1]] = model[tpl[0]]

        matcher_model = Model('matcher', [], [top_row])

        self.panel.header_matcher.setModel(matcher_model)
        self.panel.header_matcher.hideRow(1)
        self.panel.header_matcher.setMinimumHeight(self.panel.header_matcher.rowHeight(0))
        self.panel.header_matcher.setMaximumHeight(self.panel.header_matcher.rowHeight(0))
        self.panel.header_matcher.setItemDelegate(Delegate(model))

        self.panel.table_view.horizontalScrollBar().valueChanged.connect(self.panel.header_matcher.horizontalScrollBar().setValue)

    def _validate_headers(self, headers):
        """
        Returns an empty list if header selections are valid,
        list of conflicing header tuples otherwise
        Northing / Easting cannot be selected with Distance / Bearing
        Radius cannot be selected with Degree
        """

        #key headers to test for
        nedb = ['Northing', 'Easting', 'Distance', 'Bearing']

        #list of valid headers from the user input
        valid_items = [_i for _i in headers if _i in nedb]

        #boolean list of indices in nedb which are found in the headers
        bools = [_i in headers for _i in nedb]

        ne_bools = bools[:2]
        db_bools = bools[2:]

        #resulting message
        result = ''

        #------------
        #----TESTS---
        #------------

        #test for duplicates
        dupes = list(set([_i for _i in valid_items if valid_items.count(_i) > 1]))

        if dupes:

            result += 'Duplicates: ' + ','.join(dupes) + '\n'

        #test to seee if both northing / easting or distance / bearing are specified
        if not (all(_i for _i in ne_bools) or all(_i for _i in db_bools)):

            result += 'Incomplete Northing/Easting or Bearing/Distance\n'

        return result

    def import_model(self):
        """
        Import the model using the CsvParser module
        """

        #get the headers from the model
        headers = self.header_matcher.model().data_model[0]

        #returns a message string for notification
        result = self._validate_headers([_x for _x in headers if _x])

        if result:
            return None

        parser = CsvParser.create()

        parser.import_file(self.filepath, headers, self.dialect)
        return parser.data
