# ****************************************** S K I D     F O R E S T     U I ******************************************

import maya.cmds as cmds
from pymel.core import *
import os,glob

# ****************************************** G L O B A L S ******************************************

forestWindow = "forestWindow"
forestDir = '//Merlin/3d4/skid/04_asset/set/setForest/'

# ****************************************** F U N C T I O N S ******************************************

def call_fireHoudini(*_):
	VfocalLength = floatSliderGrp(focalLength,q=True,v=True)
	Vtop = floatSliderGrp(mtop,q=True,v=True)
	Vright = floatSliderGrp(mright, q=True, v=True)
	Vbot = floatSliderGrp(mbot,q=True,v=True)
 	Vleft= floatSliderGrp(mleft,q=True,v=True)
 	Vdepth = floatSliderGrp(depth,q=True,v=True)
 	import forestTools
 	reload(forestTools)
 	forestTools.fireHoudini(VfocalLength,Vtop,Vright,Vbot,Vleft,Vdepth)

# ****************************************** I N T E R F A C E ******************************************

def CreateUI(*args):
	cmds.evalDeferred("cmds.loadPlugin(\"RenderMan_for_Maya.py\")")
	from rfm2.config import cfg
	rmanversion = cfg().rfm_env['versions']['rfm']
	print rmanversion
	if rmanversion != "22.4" :
		commonTools.areeeeett()
		cmds.evalDeferred("cmds.warning('Wrong Renderman for Maya version (installed version is %s), should be 22.4')" % rmanversion)
		return

	template = uiTemplate('ExampleTemplate', force=True)
	template.define(button, w=300, h=35, align='left')
	template.define(frameLayout, borderVisible=True, labelVisible=True)
	template.define(rowColumnLayout,numberOfColumns=1)
	template.define(optionMenu,w=200)
	template.define(floatSliderGrp,w=300,h=25,f=True,min=0.0,max=1.0,s=0.1,v=0.1,cl3=('left','left','left'),cw3=(80,80,140))

	try :
		cmds.deleteUI(forestWindow)
	except RuntimeError :
		pass

	with window(forestWindow, title='Create forest archive',menuBar=True,menuBarVisible=True) as win:
		with template:
			with columnLayout():
				
				# with frameLayout('Camera setup'):
				# 	with rowColumnLayout():
				# 		button(l='Import shot camera', \
				# 			c='import renderTools; \
				# 			reload(renderTools); \
				# 			renderTools.importShotCamera()')
				# 		button(l='Set Frame Range From Camera', \
				# 			c='import previzTools;  \
				# 			reload(previzTools); \
				# 			previzTools.setShot()')

				# with frameLayout('Create point cloud'):
				# 	with rowColumnLayout():
				# 		focalLength = floatSliderGrp(l='Focal Length',min=5,max=300,s=1,v=50)
				# 		mtop = floatSliderGrp(l='Margin top')
				# 		mright = floatSliderGrp(l='Margin right')
				# 		mbot = floatSliderGrp(l='Margin bottom')
				# 		mleft = floatSliderGrp(l='Margin left')
				# 		depth = floatSliderGrp(l='Depth (m)',min=100,max=2000,s=10,v=200)
				# 		b = cmds.button('Compute point cloud')
				# 		button(b, e=True, c=call_fireHoudini)
				
				with frameLayout('Convert bgeo to maya point cloud'):
					with rowColumnLayout():
						# button(l='Load Houdini Engine for Maya', \
						# 	c='import forestTools; \
						# 	reload(forestTools); \
						# 	forestTools.loadHoudiniEngine()')
						bgeos = glob.glob(forestDir + r'geo/pointCloud_sector?.bgeo.sc')
						for bgeo in bgeos:
							sector = bgeo.split('_sector')[1]
							sector = sector.split('.')[0]
							# print sector
							button(l='Convert bgeo sector %s'%sector, \
								h=25, \
								c='import forestTools; \
								reload(forestTools); \
								forestTools.loadShotPoints("%s")'%sector)
				with frameLayout('Instancing'):
					with rowColumnLayout():
						button(l='Import assets to instance', \
							c='import forestTools; \
							reload(forestTools); \
							forestTools.createInstancer()')

				# with frameLayout('Forest rib archive import'):
				# 	with rowColumnLayout():
				# 		ribs = glob.glob(forestDir + r'setForest_sector?.rib')
				# 		for rib in ribs:
				# 			sector = rib.split('_sector')[1]
				# 			sector = sector.split('.')[0]
							# print sector
							# button(l='Import forest sector %s'%sector, \
							# 	h=25, \
							# 	c='import forestTools; \
							# 	reload(forestTools); \
							# 	forestTools.importForest("%s")'%sector)

CreateUI()