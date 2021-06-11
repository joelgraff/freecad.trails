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
"""get elevation data by srtm4 module"""


"""
SRTM data - some information
https://en.wikipedia.org/wiki/SRTM
according to englis wikipedia the resolution is
30 m for United States and 90 m outside United States

https://pypi.org/project/elevation/
another project I did not test so far

https://pypi.org/project/srtm4/
downloaded tiffs from area will be saved locally
download ca 35 MB, the half of switzerland
height not above sea level
https://github.com/cmla/srtm4/issues/10
important note ... method parameters are swapped
the longitude as first argument, the latitude as second argument

import srtm4
srtm4.srtm4(8.035, 46.503)  # Konkordiaplatz

from freecad.trails.geomatics.geoimport import get_elevation_srtm4
import importlib
importlib.reload(get_elevation_srtm4)
pts = [["620877237", "46.8076263", "8.0596176"], ["5067330264", "46.8010987", "8.0548266"]]
get_elevation_srtm4.get_height_list(pts)


{'46.8076263 8.0596176': 1300240.0, '46.8010987 8.0548266': 1727440.0}

"""

try:
    from srtm4 import srtm4
    nosrtm4 = False
except Exception:
    print("Module srtm4 not found. Install it to get heights.")
    nosrtm4 = True


def get_height_single(b, l):
    """
    get height of a single point with latitude b, longitude l
    """
    if nosrtm4 is True:
        return(0.0)

    elevation = srtm4(float(l), float(b))
    # print("lat: {}, long: {}, ele: {}".format(b, l, elevation))
    return round(elevation * 1000, 2)


def get_height_list(points):
    """
    uses get_height_single to get the height of each point
    """
    heights = {}
    for pt in points:
        # print(pt)
        key = "{:.7f} {:.7f}".format(float(pt[1]), float(pt[2]))
        # print(key)
        # swap will happen in other method
        heights[key] = get_height_single(pt[1], pt[2])
        # print(heights[key])
    return heights
