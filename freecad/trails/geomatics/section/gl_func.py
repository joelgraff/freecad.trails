
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

class GLFunc:
    """
    This class is contain Surface Object functions.
    """
    def __init__(self):
        pass

    def GetOrthoVector(self, line, distance, side=''):
        """
        Return the orthogonal vector pointing toward the indicated side at the
        provided position.  Defaults to left-hand side
        """

        _dir = 1.0

        _side = side.lower()

        if _side in ['r', 'rt', 'right']:
            _dir = -1.0

        start = line.Start
        end = line.End

        if (start is None) or (end is None):
            return None, None

        _delta = end.sub(start).normalize()
        _left = FreeCAD.Vector(-_delta.y, _delta.x, 0.0)

        _coord = start.add(_delta.multiply(distance*1000))

        return _coord, _left.multiply(_dir)

    def CreateGuideLines(self, alignment, increments, ofsets, region):
        """
        Generates guidelines along a selected alignment
        """
        # Get left and right offsets from centerline
        l = ofsets[0]
        r = ofsets[1]

        # Gegion limits
        FirstStation = region[0]
        LastStation = region[1]

        cluster = self

        # Guideline intervals
        TangentIncrement = increments[0]
        CurveSpiralIncrement = increments[1]

        #retrieve alignment data
        if hasattr(alignment.Proxy, 'model'):
            Start = alignment.Proxy.model.data['meta']['StartStation']
            Length = alignment.Proxy.model.data['meta']['Length']
            End = Start + Length/1000
        else:
            Start = 0.0
            Length = alignment.Length.Value
            End = Start + Length/1000

        #get 3D coordinate dataset and placement
        Stations = []
        if hasattr(Alignment.Proxy, 'model'):
            AlgPl = Alignment.Placement.Base
            Geometry = Alignment.Proxy.model.data['geometry']

            for Geo in Geometry:
                #compute starting and ending stations based on alignment
                StartStation = Geo.get('StartStation')
                EndStation = Geo.get('StartStation')+Geo.get('Length')/1000

                if StartStation != 0:
                    if self.IPFui.HorGeoPointsChB.isChecked():
                        Stations.append(StartStation)

                #generate line intervals
                if Geo.get('Type') == 'Line':

                    #Iterate the station range, rounding to the nearest whole
                    for i in range(
                        round(float(StartStation)), round(float(EndStation))):

                        #add stations which land on increments exactly
                        if i % int(TangentIncrement) == 0:
                            Stations.append(i)

                #generate curve intervals
                elif Geo.get('Type') == 'Curve' or Geo["Type"] == 'Spiral':

                    for i in range(round(float(StartStation)), round(float(EndStation))):
                        if i % int(CurveSpiralIncrement) == 0:
                            Stations.append(i)

        else:
            StartStation = Start
            EndStation = End
            AlgPl = FreeCAD.Vector(0, 0, 0)
            if StartStation != 0:
                if self.IPFui.HorGeoPointsChB.isChecked():
                    Stations.append(StartStation)

            for i in range(int(float(StartStation)), int(float(EndStation))):
                if i % int(TangentIncrement) == 0:
                    Stations.append(i)

        #add the end station, rounded to the nearest three decimals
        Stations.append(round(End,3))

        Result = []

        #iterate the stations, appending what falls in the specified limits
        for Station in Stations:

            if float(FirstStation) <= Station <= float(LastStation):
                Result.append(Station)

        Result.sort()

        #iterate the final list of stations,
        #computing coordinates and orthoginals for guidelines
        for Station in Result:
            if hasattr(Alignment.Proxy, 'model'):
                Coord, vec = Alignment.Proxy.model.get_orthogonal( Station, "Left")
            else:
                Coord, vec = self.GetOrthoVector(Alignment, Station, "Left")

            LeftEnd = Coord.add(FreeCAD.Vector(vec).multiply(int(l)*1000))
            RightEnd = Coord.add(vec.negative().multiply(int(r)*1000))

            #generate guide line object and add to document
            GuideLine = Draft.makeWire([LeftEnd, Coord, RightEnd])
            GuideLine.Placement.Base = AlgPl
            GuideLine.Label = str(round(Station, 3))

            cluster.addObject(GuideLine)
            FreeCAD.ActiveDocument.recompute()
