import Part

def AreasBetweenPolylines(wireA, wireB, create=False):
    '''calculate the areas above wireA and below wireB'''
    shapeA = wireA
    shapeB = wireB

    boxA = shapeA.BoundBox
    boxB = shapeB.BoundBox

    # Find the coords for the 'limits' box:
    limMinX = max(boxA.XMin, boxB.XMin)
    limMaxX = min(boxA.XMax, boxB.XMax)
    limMinY = min(boxA.YMin, boxB.YMin) - 1.0
    limMaxY = max(boxA.YMax, boxB.YMax) + 1.0

    print(wireA.Vertexes[0].Point.x)
    print(boxA.XMin)

    if wireA.Vertexes[0].Point.x == boxA.XMin:
        staA = wireA.Vertexes[0].Point
        endA = wireA.Vertexes[-1].Point
    else:
        staA = wireA.Vertexes[-1].Point
        endA = wireA.Vertexes[0].Point

    if wireB.Vertexes[0].Point.x == boxB.XMin:
        staB = wireB.Vertexes[0].Point
        endB = wireB.Vertexes[-1].Point
    else:
        staB = wireB.Vertexes[-1].Point
        endB = wireB.Vertexes[0].Point

    ## Add 3 edges to A to get a closed boundary:
    edgesA = shapeA.Edges + [Part.makeLine(staA, (staA[0], limMaxY, 0.0)),
                             Part.makeLine((staA[0], limMaxY, 0.0), (endA[0], limMaxY, 0.0)),
                             Part.makeLine((endA[0], limMaxY, 0.0), endA)]

    ## Add 3 edges to B to get a closed boundary:
    edgesB = shapeB.Edges + [Part.makeLine(staB, (staB[0], limMinY, 0.0)),
                             Part.makeLine((staB[0], limMinY, 0.0), (endB[0], limMinY, 0.0)),
                             Part.makeLine((endB[0], limMinY, 0.0), endB)]

    ## Determine 4 edges for the 'limits' box:
    edgesLim = [Part.makeLine((limMinX, limMinY, 0.0), (limMaxX, limMinY, 0.0)),
                Part.makeLine((limMaxX, limMinY, 0.0), (limMaxX, limMaxY, 0.0)),
                Part.makeLine((limMaxX, limMaxY, 0.0), (limMinX, limMaxY, 0.0)),
                Part.makeLine((limMinX, limMaxY, 0.0), (limMinX, limMinY, 0.0))]

    faceA   = Part.Face(Part.Wire(edgesA))
    faceB   = Part.Face(Part.Wire(edgesB))
    faceLim = Part.Face(Part.Wire(edgesLim))

    faceA = faceA.common(faceLim)
    faceB = faceB.common(faceLim)
    faceResult = faceA.common(faceB)

    if create and faceResult.Area != 0.0:
      Part.show(faceResult)

    return faceResult.Area
"""
project = App.getDocument("Ba__lant__").getObject("CrossSection")
ground = App.getDocument("Ba__lant__").getObject("CrossSection001")

prj = project.Shape.Wires[1]
grd = ground.Shape.Wires[1]

AreasBetweenPolylines(prj, grd, create=True)
"""
