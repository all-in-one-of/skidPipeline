# ****************************************** S K I D     A N I M     U I ******************************************

import maya.cmds as cmds
from pymel.core import *


# ****************************************** I N T E R F A C E ******************************************

sectors = ['A','B','C','D','E','F','G','H','I','J','K','L']

def CreateUI(*args):
	# Load Renderman and check version
	cmds.evalDeferred("cmds.loadPlugin(\"RenderMan_for_Maya.py\")")
	from rfm2.config import cfg
	rmanversion = cfg().rfm_env['versions']['rfm']
	print rmanversion
	if rmanversion != "22.3" :
		commonTools.areeeeett()
		cmds.evalDeferred("cmds.warning('Wrong Renderman for Maya version (installed version is %s), should be 22.3')" % rmanversion)
		return
	
	# define template UI
	template = uiTemplate('ExampleTemplate', force=True)
	template.define(button, w=300, h=35, align='left')
	template.define(frameLayout, borderVisible=True, labelVisible=True)
	template.define(rowColumnLayout,numberOfColumns=2)
	template.define(optionMenu,w=200)
	template.define(optionMenu,h=35,w=300)

	try :
		cmds.deleteUI('setDressWindow')
	except RuntimeError :
		pass

	with window('setDressWindow', title='Set Dress Tools',menuBar=True,menuBarVisible=True) as win:
		with template:
			with columnLayout():

				with frameLayout('Prepare Scene'):
					with columnLayout():
						button(l='Import shot camera', \
							c='import renderTools; \
							reload(renderTools); \
							renderTools.importShotCamera()')
						button(l='Set Frame Range From Camera', \
							c='import previzTools;  \
							reload(previzTools); \
							previzTools.setShot()')
						button(l='Import Alembic as Reference', \
							c='import previzTools; \
							reload(previzTools); \
							previzTools.referenceAlembic()')


				with frameLayout('References'):
					with columnLayout():
						button(l='Load all references from selection',\
							c='import setDressTools; \
							reload(setDressTools); \
							setDressTools.loadAllReferences()',en=False)
						button(l='Unload references from selection',\
							c='import setDressTools; \
							reload(setDressTools); \
							setDressTools.unloadSelected()')
						button(l='Backup transforms to Atom file',\
							c='mel.eval("performExportAnim 1;")')

				with frameLayout('Sectors'):
					with columnLayout():
						for sector in sectors:
							button(l='Import sector %s'%sector, \
								h=25, \
								c='import setDressTools; \
								reload(setDressTools); \
								setDressTools.importSector("%s")'%sector)

				with frameLayout('Publish'):
					with columnLayout():
						button(l='Publish Set Dress', \
							c='import setDressTools; \
							reload(setDressTools); \
							setDressTools.publishSetDress()')
				
				with frameLayout('Nomenclatures'):
					button(l='Afficher nomenclatures', \
						c='import commonTools; \
						reload(commonTools); \
						commonTools.showNomenclatures()')


CreateUI()