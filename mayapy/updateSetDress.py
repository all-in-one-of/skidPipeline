'''This will update the published setDress using Mayapy'''

import os,sys,glob
import maya.standalone
import maya.cmds as cmds
# import maya.mel as mel

# Launch maya standalone

# Fetch arguments
shot = sys.argv[1] # the shot to open

# Print informations
print('\n')
print('Updating setDress for shot ' + shot)

# Deduce scenefile
skidShots = '//Merlin/3d4/skid/05_shot/'
sceneFile = glob.glob(skidShots+shot+r'/mayaScenes/setDress/'+shot+r'_*_v*.ma')[-1]
sceneFile = sceneFile.replace(os.sep, '/')
maPublish = '%s%s/geo/%s_setDress.ma'%(skidShots,shot,shot)

if not sceneFile :
	print('Error : no setDress scene found')
	os.system('pause')
	os.system('exit')


# Launch maya standalone
maya.standalone.initialize()

# Load plugin
cmds.loadPlugin( 'AbcExport.mll' )

# 1. Open scene
cmds.file(sceneFile,open=True,force=True,ignoreVersion=True)

# 2. verifiy if group exists and select
if not cmds.objExists('setDress_grp'):
	print('Error : no setDress scene found')
	os.system('pause')
	os.system('exit')

cmds.select('setDress_grp',r=True)

# 3. publish
print('\n\n\nExporting %s...\n'%maPublish)

cmds.file(maPublish, \
		type='mayaAscii', \
		exportSelected=True, \
		force=True, \
		preserveReferences=False)

# 4. Exit maya
cmds.quit(abort=True)
print('\n')

os.system('cls')
print('   _____')
print('  / ____|')
print(' | (___  _   _  ___ ___ ___  ___ ___ ')
print('  \\___ \\| | | |/ __/ __/ _ \\/ __/ __|')
print('  ____) | |_| | (_| (_|  __/\\__ \\__ \\')
print(' |_____/ \\__,_|\\___\\___\\___||___/___/')
print('\n')
print('(probably)')
print('\n')
print('// Result : ' + maPublish)

os.system('pause')