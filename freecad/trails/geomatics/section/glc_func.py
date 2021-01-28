
# /**********************************************************************
# *                                                                     *
# * Copyright (c) 2021 Hakan Seven <hakanseven12@gmail.com>             *
# *                                                                     *
# * This program is free software; you can redistribute it and/or modify*
# * it under the terms of the GNU Lesser General Public License (LGPL)  *
# * as published by the Free Software Foundation; either version 2 of   *
# * the License, or (at your option) any later version.                 *
# * for detail see the LICENCE text file.                               *
# *                                                                     *
# * This program is distributed in the hope that it will be useful,     *
# * but WITHOUT ANY WARRANTY; without even the implied warranty of      *
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the       *
# * GNU Library General Public License for more details.                *
# *                                                                     *
# * You should have received a copy of the GNU Library General Public   *
# * License along with this program; if not, write to the Free Software *
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307*
# * USA                                                                 *
# *                                                                     *
# ***********************************************************************

'''
Define Surface Object functions.
'''

import FreeCAD
import Part
import copy
from . import guidelines

class GLCFunc:
    """
    This class is contain Surface Object functions.
    """
    def __init__(self):
        pass

    def guidelines(self, obj):
        """
        Find the existing Guide Line Clusters group object
        """
        # Return an existing instance of the same name, if found.
        for child in obj.Group:
            if child.Proxy.Type == 'Trails::Guidelines':
                return child
        gl = guidelines.create()
        obj.addObject(gl)
        return gl

    def get_alignment_infos(self, alignment):
        if hasattr(alignment.Proxy, 'model'):
            start = alignment.Proxy.model.data['meta']['StartStation']*1000
            length = alignment.Proxy.model.data['meta']['Length']
            end = start + length
        else:
            start = 0.0
            length = alignment.Length.Value
            end = start + length
        return start, end

    def generate(self, alignment, increments, region, horiz_pnts = True):
        """
        Generates guidelines along a selected alignment
        """
        # Guideline intervals
        tangent_increment = increments[0]/1000
        curve_increment = increments[1]/1000
        spiral_increment = increments[2]/1000

        # Region limits
        start_station = round(region[0]/1000, 3)
        end_station = round(region[1]/1000, 3)

        # Retrieve alignment data get geometry and placement
        stations = []
        if hasattr(alignment.Proxy, 'model'):
            start = alignment.Proxy.model.data['meta']['StartStation']
            length = alignment.Proxy.model.data['meta']['Length']
            end = start + length/1000

            geometry = alignment.Proxy.model.data['geometry']
            for element in geometry:
                # Get starting and ending stations based on alignment
                elem_start = element.get('StartStation')
                elem_end = element.get('StartStation')+element.get('Length')/1000

                if elem_start != 0 and horiz_pnts:
                        stations.append(elem_start)

                # Generate line intervals
                if element.get('Type') == 'Line':

                    # Iterate the station range
                    for sta in range(int(elem_start), int(elem_end)):

                        # Add stations which land on increments exactly
                        if sta % int(tangent_increment) == 0:
                            stations.append(sta)

                # Generate curve intervals
                elif element.get('Type') == 'Curve':
                    for sta in range(int(elem_start), int(elem_end)):
                        if sta % int(curve_increment) == 0:
                            stations.append(sta)

                #Generate spiral intervals
                elif element.get("Type") == 'Spiral':
                    for sta in range(int(elem_start), int(elem_end)):
                        if sta % int(spiral_increment) == 0:
                            stations.append(sta)
    
            # Add the end station
            stations.append(round(end,3))

        # Create guide lines from standart line object
        else:
            length = alignment.Length.Value
            for sta in range(0, int(length/1000)):
                if sta % int(tangent_increment) == 0:
                    stations.append(sta)

            # Add the end station
            stations.append(round(length/1000,3))

        # Iterate the stations, appending what falls in the specified limits
        region_stations = []
        for sta in stations:
            if start_station <= sta <= end_station:
                region_stations.append(sta)

        region_stations.sort()
        return region_stations
