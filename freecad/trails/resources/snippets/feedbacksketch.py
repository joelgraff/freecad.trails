# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- feedbacksketch
#--
#-- microelly 2017 v 0.3
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------


# from say import *
# import nurbswb.pyob
#------------------------------
import FreeCAD,FreeCADGui,Sketcher,Part

App = FreeCAD
Gui = FreeCADGui

from PySide import QtCore


import numpy as np
import time


class FeaturePython:
    """ basic defs"""

    def __init__(self, obj):
        obj.Proxy = self
        self.Object = obj

    def attach(self, vobj):
        self.Object = vobj.Object

    def claimChildren(self):
        return self.Object.Group

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None


class ViewProvider:
    """ basic defs """

    def __init__(self, obj):
        obj.Proxy = self
        self.Object = obj

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None

    def setupContextMenu(self, obj, menu):
        pass
        #menu.clear()
        #action = menu.addAction("MyMethod #1")
        #action.triggered.connect(lambda:self.methodA(obj.Object))
       # action = menu.addAction("MyMethod #2")
       # action.triggered.connect(lambda:self.methodB(obj.Object))

    def methodA(self,obj):
        print ("my Method A Finisher")
        FreeCAD.activeDocument().recompute()

    def methodB(self,obj):
        print ("my method 2 Starter")
        FreeCAD.activeDocument().recompute()

    def editA(self):
        print ("EDIT A")

    def setEdit(self,vobj,mode=0):
        print ("IN EDIT MODE")

    def unsetEdit(self,vobj,mode=0):
        print ("unset edit "),mode
        self.methodA(None)
        return False


    def doubleClicked(self,vobj):
        print ("double clicked")
        self.methodB(None)
        vobj.Visibility=True
        self.setEdit(vobj,1)
        return True

#-------------------------------


def createGeometryS(obj=None):
    """create a testcase sketch"""

    if obj==None:
        sk=App.ActiveDocument.addObject('Sketcher::SketchObject','Sketch')
    else:
        sk=obj

    sk.addGeometry(Part.ArcOfCircle(Part.Circle(App.Vector(96.450951,236.065002,0),App.Vector(0,0,1),267.931216),-2.497296,-1.226827),False)
    App.ActiveDocument.recompute()

    sk.addGeometry(Part.ArcOfCircle(Part.Circle(App.Vector(-223.275940,-184.908691,0),App.Vector(0,0,1),280.634057),-0.171680,1.185353),False)
    sk.addConstraint(Sketcher.Constraint('Coincident',0,1,1,1))
    App.ActiveDocument.recompute()

    sk.addConstraint(Sketcher.Constraint('Tangent',0,1))
    App.ActiveDocument.recompute()

    sk.addConstraint(Sketcher.Constraint('Radius',0,1500.))
    App.ActiveDocument.recompute()

    # punkt A bewegen
    sk.movePoint(0,1,App.Vector(-228.741898,243.874924,0),0)

    consAX=sk.addConstraint(Sketcher.Constraint('DistanceX',0,2,-284.619380))
    sk.setDatum(consAX,-300)
    sk.renameConstraint(consAX, u'AX')
    consAY=sk.addConstraint(Sketcher.Constraint('DistanceY',0,2,162.125989))
    sk.setDatum(consAY,200)
    sk.renameConstraint(consAY, u'AY')
    App.ActiveDocument.recompute()

    # punkt B bewegen
    consBX=sk.addConstraint(Sketcher.Constraint('DistanceX',1,2,-284.619380))
    sk.setDatum(consBX,200)
    sk.renameConstraint(consBX, u'BX')
    consBY=sk.addConstraint(Sketcher.Constraint('DistanceY',1,2,162.125989))
    sk.setDatum(consBY,-75)
    sk.renameConstraint(consBY, u'BY')
    App.ActiveDocument.recompute()

    sk.addConstraint(Sketcher.Constraint('Radius',1,3000.))

    return



def getNamedConstraint(sketch,name):
    """get the index of a constraint name"""
    for i,c in enumerate (sketch.Constraints):
        if c.Name==name: return i
    print ('Constraint name "'+name+'" not in ' +sketch.Label)
    raise Exception ('Constraint name "'+name+'" not in ' + sketch.Label)



def clearReportView(name):
    from PySide import QtGui
    mw=Gui.getMainWindow()
    r=mw.findChild(QtGui.QTextEdit, "Report view")
    r.clear()
    import time
    now = time.ctime(int(time.time()))
    App.Console.PrintWarning("Cleared Report view " +str(now)+" by " + name+"\n")



class FeedbackSketch(FeaturePython):
    """Sketch Object with Python"""

    ##\cond
    def __init__(self, obj, icon='/home/thomas/.FreeCAD/Mod/freecad-nurbs/icons/draw.svg'):
        obj.Proxy = self
        self.Type = self.__class__.__name__
        self.obj2 = obj
        self.aa = None
        obj.addProperty("App::PropertyBool",'clearReportview', 'Base',"clear window for every execute")
        obj.addProperty("App::PropertyBool",'error', 'Base',"error solving sketch")
        obj.addProperty("App::PropertyBool",'autoupdate', 'Base',"auto recompute")

        obj.addProperty("App::PropertyString",'shapeBuilder', 'Base',"method to build the shape")
        ViewProvider(obj.ViewObject)
    ##\endcond

#   def onChanged(proxy,obj,prop):
#       print ("onChanged:",obj.Label,prop)
#       print "Sketch",App.ActiveDocument.Sketch.State
#       print "Sketch001",App.ActiveDocument.Sketch001.State

#       """run myExecute for property prop: relativePosition and vertexNumber"""
#
#       if prop in ["parent"]:
#           proxy.myExecute(obj)


    def myExecute(proxy,obj):

        debug=False
        debug=True

        if obj.clearReportview:
            clearReportView(obj.Label)





        if debug: print (obj.Label,"execute vor try")
        try:
            if proxy.exflag: pass
        except: proxy.exflag=True

        if  not proxy.exflag:
            proxy.exflag=True
            if debug: print ("no execute")
            return

        proxy.exflag=False
        if debug: print ("execute ",obj.Label)

        changed={}

        for subs in obj.bases:
            if debug: print ("Section ",subs)
            g=getattr(obj,"base"+subs)
            if g == None: continue
            if debug: print (g.Label)
            if getattr(obj,"active"+subs):
                for sof in getattr(obj,"setoff"+subs):
                    ci=getNamedConstraint(g,sof)
                    g.setDriving(ci,False)

                for gets in getattr(obj,"get"+subs):
                    cgi=getNamedConstraint(g,gets)
                    val_cgi=g.Constraints[cgi].Value
                    if debug: print ("got ",gets,val_cgi)
                    # set the own geometry
                    ci=getNamedConstraint(obj,gets)
                    valwar=obj.Constraints[ci].Value
                    if debug: print ("old value was",gets,valwar)
                    if valwar == val_cgi:
                        if debug: print ("nix zu aendern")
                        continue
                    try:
                        changed[gets]
                        #if valwar == val_cgi:
                        if debug: print ("stop change")
                        changed[gets]=2
                    except:
                        changed[gets]=0
                        if valwar != val_cgi:
                            changed[gets]=1

                    if changed[gets]==2:
                        if debug: print ("already changed",gets)
                        continue
                    else:
                        try:
                            obj.setDatum(ci,val_cgi)
                        except:
                            FreeCAD.Console.PrintError("cannot set datum\n")
                            if debug: print ("old value ",valwar)
                            obj.setDriving(ci,False)
                            rc=obj.solve()
                            valneu=obj.Constraints[ci].Value
                            if debug:
                                print ("possible value",valneu)
                                print(obj.Label, "solved with possible value",rc)
                            obj.setDriving(ci,True)
                            #hier abbrechen
                            # wert zurück schreiben
                            g.setDatum(cgi,valneu)
                            rc=g.solve()
                            if debug: print(obj.Label, "solve after rollback ",rc)
                            obj.error=True


                            raise Exception("Problem on Constraints no feedback data")


                # solve the tasks

                rc=obj.solve()
                if debug: print(obj.Label, "solve after get",rc)

                for sets in getattr(obj,"set"+subs):
                    cgi=getNamedConstraint(obj,sets)
                    val_cgi=obj.Constraints[cgi].Value
                    if debug: print ("BB set ",sets,val_cgi)
                    # set the data back
                    ci=getNamedConstraint(g,sets)
                    if debug: print ("ci BB",ci,sets,g.Label)

                    isdriving=g.getDriving(ci)
                    g.setDriving(ci,True)

                    if debug:
                        print ("try to set ",ci ,val_cgi)
                        print (g.Label)

                    try:
                        g.setDatum(ci,val_cgi)
                    except:
                        print ("debug --- ")
                        for cii,c in enumerate(g.Constraints):
                            print (cii,c,  g.Constraints[cii].Value)

                        print ("try to set ",ci,g.Constraints[ci].Value)

                        g.setDatum(ci,App.Units.Quantity(str(g.Constraints[ci].Value) +' mm'))
                        print ("still okay?")
                        g.setDatum(ci,g.Constraints[ci].Value)
                        print ("!!",g.Constraints[ci].Value)
                        g.setDatum(ci,App.Units.Quantity(str(val_cgi) +' mm'))

                    rc=g.solve()

                    if debug: print(obj.Label, "solve after set",rc)

                    if not isdriving:
                        g.setDriving(ci,False)
                        rc=g.solve()
                        if debug: print(obj.Label, "solve after set and switch back to blue",rc)

                for sof in getattr(obj,"seton"+subs):
                    ci=getNamedConstraint(g,sof)
                    g.setDriving(ci,True)


            rc=g.solve()
            if debug: print(obj.Label, "AA final solve",rc)

        for subs in obj.bases:
            if debug: print ("Section ",subs)
            g=getattr(obj,"base"+subs)
            if g == None: continue

            if getattr(obj,"active"+subs):

                for sets in getattr(obj,"set"+subs):
                    cgi=getNamedConstraint(obj,sets)
                    val_cgi=obj.Constraints[cgi].Value
                    if debug: print ("AB set ",sets,val_cgi)
                    # set the data back
                    try:
                        ci=getNamedConstraint(g,sets)
                    except:
                        print ("getNamedConstraint ERROR")
                        ci=9999
                        raise Exception("getNamedConstraint")

                    isdriving=g.getDriving(ci)
                    g.setDriving(ci,True)

                    g.setDatum(ci,val_cgi)

                    rc=g.solve()
                    if debug: print(obj.Label, "solve after set",rc)

                    if not isdriving:
                        g.setDriving(ci,False)
                        rc=g.solve()
                        print(obj.Label, "solve after set and switch back to blue",rc)

                for sof in getattr(obj,"seton"+subs):
                    ci=getNamedConstraint(g,sof)
                    g.setDriving(ci,True)


        return

    def onChanged(self, obj, prop):
#       print ("onChange", prop)
        if prop=='bases':
            for b in obj.bases: addgrp(obj,b)

        if prop=="autoupdate":
            if obj.autoupdate:
                self.runTimer(obj)
            else:
                if hasattr(obj.Proxy,"myTimer"):
                    obj.Proxy.myTimer.stop()


    def someOtherFunction(self):
        try: self.Object.Label
        except:
            print ("someOtherFunction not ready")
            if hasattr(self,"myTimer"):
                self.myTimer.stop()
            return

        print ("run auto update")
        FreeCAD.ActiveDocument.recompute()


    def runTimer(self,obj):
        self.Object=obj
        self.myTimer = QtCore.QTimer()
        self.myTimer.setInterval(1000)
        self.myTimer.timeout.connect(self.someOtherFunction)
        self.myTimer.start()




    def execute(self,obj):

#       if obj.error:
#               obj.error=False
#               raise Exception("Obj -- Error")




        obj.recompute()
        try: self.Lock
        except: self.Lock=False
        if not self.Lock:
            self.Lock=True
            dats=[]
            for subs in obj.bases:
#               print ("erstelle Sicherung ",subs)
                g=getattr(obj,"base"+subs)
                if g is not None:
                    gs,cs,cons=storeSketch(g)
                else: gs,cs,cons=[],[],[]
                dats.append((gs,cs,cons))

            try:
                #print ("run myexecute")
                self.myExecute(obj)
                FreeCAD.Console.PrintMessage("myexecute success\n")
                #print ("myexecute done")
            except Exception as ex:
                print(ex)
                print('myExecute error')
#               sayexc("myExecute Error")
                print ("RESTORE ...")
                FreeCAD.Console.PrintWarning("RESTORE after sketch solve failure\n")
                if hasattr(self,'dats'):
#                   print ("vereende self sicherung daten ")
                    dats=self.dats
                for i,subs in enumerate(obj.bases):
#                   print ("hole Section ",i,subs)
                    g=getattr(obj,"base"+subs)
                    if g is not None:
                        gs,cs,cons=dats[i]
                        resetSketch(g)
                        fillSketch(g,gs,cs,cons)

                self.Lock=False
                #raise Exception("myExecute Error AA")
                print ("ReSTORED")

            self.Lock=False

#           print )"ERSTELLE SICHERUNG-------------# sichern")
            dats=[]
            for subs in obj.bases:
#               print ("Section ",subs
                g=getattr(obj,"base"+subs)
                if g is not None:
                    gs,cs,cons=storeSketch(g)
                else: gs,cs,cons=[],[],[]
                dats.append((gs,cs,cons))
            self.dats=dats



        # eigene Figur berechnen
        import sketcher.demoshapes
        reload(sketcher.demoshapes)

        sh=sketcher.demoshapes.myShape(obj,obj.shapeBuilder)
        if sh is not None: obj.Shape=sh


##\cond
    def yexecute(self, obj):
        """ recompute sketch and than run postprocess: myExecute"""
        obj.recompute()
        self.myExecute(obj)
##\endcond




def createFeedbackSketch(name="MyFeedbackSketch"):
    """runS(name="MyFeedbackSketch"):
        creates a Demo Feedbacksketch
    """

    obj = FreeCAD.ActiveDocument.addObject("Sketcher::SketchObjectPython",name)
    FeedbackSketch(obj)
    return obj

def copySketch(source,target):
    """Sketch uebernehmen"""
    for g in source.Geometry:
        target.addGeometry(g)
    for c in source.Constraints:
        target.addConstraint(c)



# Sketch kopieren
def fillSketch(target,gs,cs,cons):
    print ("Restore ",target.Label,len(gs),len(cs))
    for i,g in enumerate(gs):
        target.addGeometry(g)
        target.setConstruction(i,cons[i])
    for c in cs:
        target.addConstraint(c)


def resetSketch(target):
    gc=target.GeometryCount
    print ("Loesche Geometry",target.Label,gc)
    for i in range(gc):
        target.delGeometry(gc-i-1)
    target.solve()


def storeSketch(sketch):
    gs=sketch.Geometry
    cs=sketch.Constraints
    cons=[g.Construction for g in gs]
    return gs,cs,cons





## \cond
if __name__=='__main__':
    fbs=createFeedbackSketch()
    fbs.parent=App.ActiveDocument.Sketch
    fbs.addProperty("App::PropertyLink", "grand", "Parent", )
    fbs.grand=App.ActiveDocument.Sketch001
    copySketch(App.ActiveDocument.Sketch002,fbs)
    App.activeDocument().recompute()
#\endcond



#----------------------



def addgrp(fbs,grpname):
    """add a parameter group to a fbs"""

    if hasattr(fbs,'active'+grpname): return

    fbs.addProperty("App::PropertyBool",'active'+grpname, grpname, )
    fbs.addProperty("App::PropertyLink",'base'+grpname, grpname, )
    fbs.addProperty("App::PropertyStringList",'get'+grpname, grpname, )
    fbs.addProperty("App::PropertyStringList",'set'+grpname, grpname, )
    fbs.addProperty("App::PropertyStringList",'seton'+grpname, grpname, )
    fbs.addProperty("App::PropertyStringList",'setoff'+grpname, grpname, )

def run_test_two_clients():
    """example with two sketches both 1 in and 1 out parameter"""

    try: App.closeDocument("beuger")
    except: pass

    FreeCAD.open(u"/home/thomas/freecad_buch/b248_stassenbau/beuger.fcstd")
    App.setActiveDocument("beuger")
    App.ActiveDocument=App.getDocument("beuger")
    Gui.ActiveDocument=Gui.getDocument("beuger")

    fbs=createFeedbackSketch(name="MultiFB")
    fbs.clearReportview=True
    copySketch(App.ActiveDocument.Sketch002,fbs)

    fbs.addProperty("App::PropertyBool",'active', 'Base', )
    fbs.addProperty("App::PropertyStringList",'bases', 'Base', )
    fbs.active=True
    fbs.bases=['TAA','TBB']

    addgrp(fbs,"TAA")
    fbs.baseTAA=App.ActiveDocument.Sketch
    fbs.getTAA=['in_p']
    fbs.setTAA=['result_p']
    fbs.activeTAA=True

    addgrp(fbs,"TBB")
    fbs.activeTBB=True
    fbs.baseTBB=App.ActiveDocument.Sketch001
    fbs.getTBB=['in_g']
    fbs.setTBB=['result_g']


def run_test_reverse_Constraints():
    """testcase reorder the constraints"""
    targ=App.ActiveDocument.Sketch002
    csts=targ.Constraints
    yy=targ.ConstraintCount
    for i in range(targ.ConstraintCount):
        targ.delConstraint(yy-1-i)

    copySketch(App.ActiveDocument.Sketch,App.ActiveDocument.Sketch002)
    csts=targ.Constraints
    cx=[]
    cxi=[]
    for i,c in  enumerate(csts):
        print ("!",c.Name,"!")
        if c.Name is not '':
            cx.append(c)
            cxi.append(i)
    cxi.reverse()
    for i in cxi:
        targ.delConstraint(i)
    cx.reverse()
    for c in cx:
        targ.addConstraint(c)



def runB():
    # testcase example

    fbs=createFeedbackSketch(name="MultiFB")
    copySketch(App.ActiveDocument.Sketch,fbs)


    fbs.addProperty("App::PropertyBool",'active', 'Base', )
    fbs.addProperty("App::PropertyStringList",'bases', 'Base', )
    fbs.active=True
    fbs.bases=['ClientA','ClientB']
    for b in fbs.bases: addgrp(fbs,b)
    fbs.baseClientA=App.ActiveDocument.Sketch001
    fbs.getClientA=['a','b']
    fbs.setClientA=['c','bm']
    fbs.activeClientA=True



def run_copySketch():
    """copy Sketch"""
    ss=Gui.Selection.getSelection()
    if len(ss) != 2:
        print ("select source and target sketch!")
        return
    copySketch(ss[0],ss[1])


def run_createFBS_with_one_Client():
    """feedbacksketch with one client"""
    fbs=createFeedbackSketch(name="SingleClientFeedback")
    fbs.addProperty("App::PropertyBool",'active', 'Base', )
    fbs.addProperty("App::PropertyStringList",'bases', 'Base', )
    fbs.active=True
    fbs.bases=['Client']
    for b in fbs.bases: addgrp(fbs,b)
    fbs.activeClient=True


def run_createFBS_with_two_Clients():
    """feedbacksketch with 2 clients"""
    fbs=createFeedbackSketch(name="TwoClientsFeedback")
    fbs.addProperty("App::PropertyBool",'active', 'Base', )
    fbs.addProperty("App::PropertyStringList",'bases', 'Base', )
    fbs.active=True
    fbs.bases=['ClientA','ClientB']
    for b in fbs.bases: addgrp(fbs,b)
    fbs.activeClientA=True
    fbs.activeClientB=True

def run_createFBS_with_three_Clients():
    """feedbacksketch with 3 clients"""
    fbs=createFeedbackSketch(name="ThreeClientsFeedback")
    fbs.addProperty("App::PropertyBool",'active', 'Base', )
    fbs.addProperty("App::PropertyStringList",'bases', 'Base', )
    fbs.active=True
    fbs.bases=['ClientA','ClientB','ClientC']
    for b in fbs.bases: addgrp(fbs,b)
    fbs.activeClientA=True
    fbs.activeClientB=True
    fbs.activeClientC=True
