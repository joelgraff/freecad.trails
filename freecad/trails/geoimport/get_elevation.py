# -------------------------------------------------
# -- osm map importer
# --
# -- microelly 2016 v 0.4
# -- Bernd Hahnebach <bernd@bimstatik.org> 2020 v 0.5
# --
# -- GNU Lesser General Public License (LGPL)
# -------------------------------------------------
"""get elevation data"""

import json
import urllib
import time

# import FreeCAD
# import FreeCADGui


def getHeight(b, l):
    """
    Get height of a single point with latitude b, longitude l
    """

    anz = 0

    while anz < 4:
        source = "https://maps.googleapis.com/maps/api/elevation/json?locations="+str(b)+','+str(l)
        response = urllib.request.urlopen(source)
        ans = response.read()

        if ans.find("OVER_QUERY_LIMIT"):
            anz += 1
            time.sleep(5)

        else:
            anz = 10

    s = json.loads(ans)
    res = s['results']

    for r in res:
        return round(r['elevation'] * 1000, 2)


# Get the heights for a list of points
def getHeights(points):
    """
    Get heights for a list of points
    """

    i = 0
    size = len(points)

    while i < size:
        source = "https://maps.googleapis.com/maps/api/elevation/json?locations="
        ii = 0

        if i > 0:
            time.sleep(1)

        while ii < 20 and i < size:
            p = points[i]
            ss = p[1]+','+p[2] + '|'
            source += ss
            i += 1
            ii += 1

        source += "60.0,10.0"
        response = urllib.request.urlopen(source)
        ans = response.read()
        s = json.loads(ans)
        res = s['results']
        heights = {}

        for r in res:
            key = "%0.7f" % (r['location']['lat']) + " " + "%0.7f" % (r['location']['lng'])
            heights[key] = r['elevation']

    return heights
