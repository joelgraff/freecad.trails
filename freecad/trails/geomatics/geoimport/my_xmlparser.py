fn='/home/thomas/Dokumente/freecad_buch/D006_landxml/FreeCAD_Document.xml'

# demo files 
# http://www.landxml.org/webapps/LandXMLSamples.aspx
# http://landxml.org/schema/LandXML-2.0/samples/Carlson Software/corridor from CD3-2.0.xml

import re
from .say import say
from PySide import QtGui
import FreeCAD

class node():

	def __init__(self,typ):
#		print("create node,type ",typ)
		self.typ=typ
		self.params={}
		self.content=[]

	def getParam(self,param):
		return self.params[param]

	def getNodes(self,typ):
		ns=[]
		for c in self.content:
			if c.typ==typ:
				ns += [c]
		return ns
	
	def addContent(self,c):
		self.content += [c]

	def __str__(self):
		return self.typ


	def getiterator(self,typ):
		rc=[]
		for obj in self.content:
			if obj.typ==typ:
				rc += [obj]
			rc += obj.getiterator(typ)
		return rc


def parseParams(string):
	params={}
	s=string
	while s!="":
		res = re.search(r"(\S+)=\"([^\"]*)\"\s+(\S.*)", s)
		if res != None:
			assert len(res.groups())==3
			k,v,s=res.group(1),res.group(2),res.group(3)
			params[k]=v
			continue

		res = re.search(r"(\S+)=\"(.*)\"", s)
		if res != None:
			assert len(res.groups())==2
			k,v,s=res.group(1),res.group(2),""
			params[k]=v
			continue

		else:
			raise Exception("parse Params Error:"+ s)
	return params




def getData(fn,pb=None):
	
	if pb is None:
		pb=QtGui.QProgressBar()
		pb.show()


	stack=[0,0]*4
	stackpointer=-1

	objs=[]

	say("Parse xml data from local cached file ...")
	say(fn)
	f=open(fn,"r", encoding="utf8")
	content=f.readlines()
	c2=[]
	
	# FreeCAD File hack
	if content[2].startswith(" FreeCAD Document, see http://www.freecadweb.org"):
		content=content[4:]

	cl=len(content)
	say(cl)

	i=-1
	pb.setMaximum(cl)
	while i<cl-1:
		pb.setValue(i)
		i += 1

		line=content[i].strip()
		j=0
		while re.search(r">\s*$", line) is None and j<60:
			i += 1
			j += 1
			line += content[i] 

		c2 +=[line]
		line=''


	content=c2
	pb.setMaximum(len(content))

	for lc,line in enumerate(content):

		if "<TextureHexString>" in line:
			say ("break A")
			continue

		pb.setValue(lc)

#		if lc%100 == 0:
#			say(lc)
#			Gui.updateGui()

#		if stackpointer != -1:
#			print (res.groups())
#			print (stackpointer)

#		print ("\n-------------NEXT:")
#		print(line)
#		print ("--- PARSE IT------------------------")

		if re.search(r"^\s*$",line):
			continue

		# ein satz
		res = re.search(r"^\s*<(\S+)\s+([^<]*)/>\s*$", line)
		if res != None:
#			print ("complete! ",res.groups())
			assert len(res.groups())==2
			typ=res.group(1)
			obj=node(typ)
			paramstring=res.group(2)
			obj.params=parseParams(paramstring)
			objs += [obj]
			if stackpointer != -1:
				stack[stackpointer].content += [obj]
	#			print stack[stackpointer]
	#			for c in stack[stackpointer].content:
	#				print c,",",
	#			print 
			continue

		res = re.search(r"^\s*<(\S+)\s+([^<]*)>\s*$", line)
		if res != None:
#			print ("!start! ",res.groups())
			assert len(res.groups())==2
			typ=res.group(1)
			obj=node(typ)
			paramstring=res.group(2)
			obj.params=parseParams(paramstring)
			objs += [obj]
			
			if stackpointer != -1:
				stack[stackpointer].content += [obj]
	#			for c in stack[stackpointer].content:
	#				print c,
			stackpointer += 1
			stack[stackpointer]=obj
			continue


		res = re.search(r"^\s*</([^<]*)>\s*$", line)
		if res != None:
#			print ("!ende---------STACKPOINTER down! ",res.groups())
			assert len(res.groups())==1
			stackpointer -= 1
			continue

		res = re.search(r"^\s*<([^<\s]*)>\s*$", line)
		if res != None:
#			print ("!simple start! ",res.groups())
			assert len(res.groups())==1
			typ=res.group(1)
			obj=node(typ)


			if stackpointer != -1:
				stack[stackpointer].content += [obj]


			stackpointer += 1
			stack[stackpointer] = obj

			continue


		#auf und zu
		res = re.search(r"^\s*<(\S+)\s*([^<]*)>(.*)</([^<]+)>\s*$", line)
		if res != None:
#			print ("!alles! ",res.groups())
			assert len(res.groups())==4
			typ=res.group(1)
			obj=node(typ)
			paramstring=res.group(2)
			obj.params=parseParams(paramstring)
			obj.text=res.group(3)
			objs += [obj]
			
			if stackpointer != -1:
				stack[stackpointer].content += [obj]
	#			for c in stack[stackpointer].content:
	#				print c,
	#		stackpointer += 1
	#		stack[stackpointer]=obj


			continue


		raise Exception("unerwartet :" +line +":")
	#	x = re.findall('<([^<]*)>', line)
	#	for xl in x: 
	#		print(xl)

#	say("done getit--------")


	FreeCAD.stackpointer=stackpointer
	FreeCAD.stack=stack
	FreeCAD.objs=objs

	return stack[0]