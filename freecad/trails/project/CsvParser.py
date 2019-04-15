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
Importer for CSV files
"""

import csv

from Corridor.Alignment import HorizontalAlignment

def create():

    return CsvParser()

class CsvParser:
    """
    Class to parse CSV alignment files
    """

    def __init__(self):
        self.data = []

    @staticmethod
    def is_empty_dict(dct):
        """
        Returns true if all key values are empty
        """

        for key, value in dct.items():
            if value:
                return False

        return True

    def _generate_indices(self, headers):
        """
        Generate index values for named data for the imported CSV
        """
        #dictionary keys for the dictionary data that is used for alignment construction
        meta_keys = HorizontalAlignment.meta_fields
        data_keys = HorizontalAlignment.data_fields
        station_keys = HorizontalAlignment.station_fields

        #get headers imported from file
        #headers = self.form.header_matcher.model().data_model[0]

        self.id_index = headers.index('ID')

        #find those headers in the pre-defined header lists, preserving blanks for unused columns
        meta_headers = [_v if _v in meta_keys else '' for _v in headers]
        data_headers = [_v if _v in data_keys else '' for _v in headers]
        station_headers = [_v if _v in station_keys else '' for _v in headers]

        #generate indexed lists of the headers
        meta_indices = [(_i, _v) for _i, _v in enumerate(meta_headers) if _v in headers]
        data_indices = [(_i, _v) for _i, _v in enumerate(data_headers) if _v in headers]
        station_indices = [(_i, _v) for _i, _v in enumerate(station_headers) if _v in headers]

        #reduce lists by removing empty columns, preserving original index values of the headers
        self.meta_indices = [_x for _x in meta_indices if _x[1]]
        self.data_indices = [_x for _x in data_indices if _x[1]]
        self.station_indices = [_x for _x in station_indices if _x[1]]

    def _scrape_meta(self, row):
        """
        Scrape metadata from a row being imported
        """
        dct = {}

        for tpl in self.meta_indices:

            key = tpl[1]
            value = row[tpl[0]]

            if key == 'ID':
                value = value.replace(' ', '_')

            dct[key] = value

        if dct['ID']:
            self.meta_dict = dct

    def _scrape_stations(self, row):
        """
        Scrape stationing from the row being imported
        """

        stations = [0.0, 0.0]
        parent_id = ''
        back_value = ''

        for tpl in self.station_indices:

            key = tpl[1]
            value = row[tpl[0]]

            if not value:
                continue

            if key == 'Back':
                stations[0] = value

            elif key == 'Forward':
                stations[1] = value

            elif key == 'Parent_ID':
                parent_id = value.replace(' ', '_')

        if stations != [0.0, 0.0]:

            #Parent_ID means it's an intersection equation
            if parent_id:
                self.station_dict[parent_id] = stations

            else:
                self.station_dict['equations'].append(stations)

    def _scrape_data(self, row):
        """
        Scrape PI data from the row being imported
        """

        #build the PI dictionary to capture data from the row
        pi_dict = dict.fromkeys(HorizontalAlignment.data_fields, '')

        for tpl in self.data_indices:

            key = tpl[1]
            value = row[tpl[0]]

            if value:
                pi_dict[key] = value

        #(northing / easting) or (bearing / distance) must be specified, along with
        #either radius or degree of curve
        valid_ne = all([pi_dict['Northing'], pi_dict['Easting']])
        valid_db = all([pi_dict['Bearing'], pi_dict['Distance']])
        valid_rd = pi_dict['Radius'] or pi_dict['Degree']

        valid_pos = valid_ne or valid_db

        if valid_pos and valid_rd:
            self.alignment_dict['data'].append(pi_dict)

    def _build_dictionaries(self):
        """
        Build the self object dictionaries that are used in data scraping
        """

        self.meta_dict = dict.fromkeys(HorizontalAlignment.meta_fields)
        self.station_dict = {'equations':[]}
        self.alignment_dict = {'meta': [], 'station': [], 'data': []}

    def _save_alignment(self):
        """
        Save the current alignment data to the alignment dicitonary
        and reset the collecting dictionaries
        """

        if self.is_empty_dict(self.alignment_dict):
            return

        self.alignment_dict['meta'] = self.meta_dict
        self.alignment_dict['station'] = self.station_dict
        self.data.append(self.alignment_dict)

        self._build_dictionaries()

    def import_file(self, filepath, headers, dialect):
        """
        Import the CSV data
        """

        skip_header = headers

        self._build_dictionaries()
        self._generate_indices(headers)

        #build the data set as a list
        with open(filepath, encoding="utf-8-sig") as stream:

            #each row represents a PI, a station equation, or metadata for the alignment
            for row in csv.reader(stream, dialect):

                if skip_header:

                    skip_header = False
                    continue

                #if the ID field has a value, a new alignment has begun
                #save the current alignment and clear the dictionary
                if row[self.id_index]:
                    self._save_alignment()

                #meta data is defined only where the ID value is defined
                self._scrape_meta(row)

                #station equations are appended, 
                #intersection equations are added as items using the parent id
                self._scrape_stations(row)

                #scrae PI data from the row
                self._scrape_data(row)

        #final write of the data
        self._save_alignment()
