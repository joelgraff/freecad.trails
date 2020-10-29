# ***************************************************************************
# *   Copyright (c) 2020 Bernd Hahnebach <bernd@bimstatik.org>              *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************
"""get elevation data"""


"""
https://en.wikipedia.org/wiki/SRTM
resolution is 30 m
in english it says 30 m for United States and 90 m outside United States
downloaded tiffs from area locally
download von ca 35 MB, aber halbe Schweiz dann lokal gespeichert
https://pypi.org/project/elevation/
https://pypi.org/project/srtm4/
https://github.com/cmla/srtm4/issues/10

the longitude as first argument, and the latitude as second argument
thus method parameters are swaped


import srtm4
srtm4.srtm4(8.035, 46.503)  # Konkordiaplatz


from freecad.trails.geomatics.geoimport import get_elevation
import importlib
importlib.reload(get_elevation)
pts = [["620877237", "46.8076263", "8.0596176"], ["5067330264", "46.8010987", "8.0548266"]]
get_elevation.get_heights_srtm4(pts)


{'46.8076263 8.0596176': 1300240.0, '46.8010987 8.0548266': 1727440.0}

"""

def get_height_srtm4(b, l):
    """
    get height of a single point with latitude b, longitude l
    """

    try:
        from srtm4 import srtm4
        nosrtm4 = False
    except:
        print("Module srtm4 not found")
        nosrtm4 = True

    if nosrtm4 is True:
        return(0.0)


    elevation = srtm4(float(l), float(b))
    # print("lat: {}, long: {}, ele: {}".format(b, l, elevation))
    return round(elevation * 1000, 2)



def get_heights_srtm4(points):
    """
    uses get_height_srtm4 to get the height of each point
    """

    heights = {}
    for pt in points:
        # print(pt)
        key = "{:.7f} {:.7f}".format(float(pt[1]), float(pt[2]))
        # print(key)
        # swap will happen in other method
        heights[key] = get_height_srtm4(pt[1], pt[2])
        # print(heights[key])
    return heights
