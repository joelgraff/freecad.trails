# testfalle
from geodat.say import *

import sys
if sys.version_info[0] !=2:
	from importlib import reload

cleanup=False

def test_import_osm():

	import geodat.import_osm
	reload(geodat.import_osm) 
	b=50.340722 
	l=11.232647
	s=0.3
	progb=False
	status=False
	elevation=False
	rc= geodat.import_osm.import_osm2(float(b),float(l),float(s)/10,progb,status,elevation)
	print  (rc)
	assert len(App.ActiveDocument.GRP_highways.OutList)==1
	assert len(App.ActiveDocument.GRP_pathes.OutList)==4
	assert len(App.ActiveDocument.Objects)==13
	if cleanup:
		App.closeDocument("OSM_Map")


def test_import_csv():

	import geodat.import_csv
	reload(geodat.import_csv) 
	a=App.newDocument("CSV")
	App.setActiveDocument(a.Name)
	App.ActiveDocument=App.getDocument(a.Name)
	Gui.ActiveDocument=Gui.getDocument(a.Name)
	
	fn='UserAppData/Mod/geodat/testdata/csv_example.csv'
	
	if fn.startswith('UserAppData'):
		fn=fn.replace('UserAppData',FreeCAD.ConfigGet("UserAppData"))
	
	orig="50.3729107,11.1913920"
	geodat.import_csv.import_csv(fn,orig,datatext='')
	assert len(App.ActiveDocument.Objects)==1
	
	if cleanup:
		App.closeDocument(App.ActiveDocument.Name)


def test_import_gpx():

	import geodat.import_gpx
	reload(geodat.import_gpx) 

	fn='UserAppData/Mod/geodat/testdata/neufang.gpx'

	if fn.startswith('UserAppData'):
		fn=fn.replace('UserAppData',FreeCAD.ConfigGet("UserAppData"))


	orig="50.3729107,11.1913920"
	orig='auto'
	hi=100
	geodat.import_gpx.import_gpx(fn,orig,hi)


def test_A():
	''' dummy test'''

	say("dummy test A")
	say("huhwas")
	raise Exception ("huhu")




def test_import_srtm():

	import geodat.import_srtm
	reload(geodat.import_srtm) 

	dy=0.009
	dx=0.009
	my=47.4210641
	mx=10.9678556
	pts=geodat.import_srtm.run(mx,my,dx,dy)
	assert len(pts)==2386

def test_import_xyz():


	import geodat.import_xyz
	reload(geodat.import_xyz) 
	fn='UserAppData/Mod/geodat/testdata/xyz.txt'
	mode=0

	if fn.startswith('UserAppData'):
		fn=fn.replace('UserAppData',FreeCAD.ConfigGet("UserAppData"))

	pts=geodat.import_xyz.import_xyz(mode,filename=fn,label='',ku=20, kv=10,lu=0,lv=0)
	u=0
	v=0
	lu=3
	lv=3
	d=1
	geodat.import_xyz.suv(pts,u,v,d+1,lu,lv)
	geodat.import_xyz.muv(pts,u,v,d+1,lu,lv)


def test_B():

	say("all tests")
	test_import_osm()
	#test_import_csv()
	#test_import_srtm()
	#test_import_xyz()
