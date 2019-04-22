'''This will export an animated alembic for the selected geometries using Mayapy'''

import os,sys,shutil,ctypes
import maya.standalone
import maya.cmds as cmds
# import maya.mel as mel

# Launch maya standalone

# Fetch arguments
sceneFile = sys.argv[1] # the sceneFile to open
asset = sys.argv[2] # working rig or camera
selectionSets = sys.argv[3:] # selection sets to export

# Print informations
print('\n')
print('Publishing animation with arguments :')
print('Scene file : %s' %sceneFile)
print('Asset : %s'%asset)
print('Sets : ')
for i in selectionSets :
	print(i)
print('\n')

# Launch maya standalone
maya.standalone.initialize()

# Load plugin
cmds.loadPlugin( 'AbcExport.mll' )

# 1. Open scene
cmds.file(sceneFile,open=True,force=True,ignoreVersion=True)

# 2. Set variables
scenePath = os.path.abspath(cmds.workspace(sn=True,q=True))
scenePath = scenePath.replace(os.sep, '/')
abcFile = scenePath + '/abc/' + asset + '.abc'
tempAbcFile = scenePath + '/abc/temp_' + asset + '.abc'
backupAbcFile = scenePath + '/abc/backup/' + asset + '.abc'
frameRange = str(cmds.playbackOptions(q=True,ast=True)) + ' ' + str(cmds.playbackOptions(q=True,aet=True))

# 3. Select geometries and create roots
cmds.select(selectionSets,r=True)
root = ''
for i in cmds.ls(selection=True,l=True):
	root = root + ' -root ' + i

# 4. Switch to DG
cmds.evaluationManager(mode="off")

# set export substep depending on asset
cars = ['propsBrevell','propsWerner']
for i in range(0,20):
	cars.append('propsOpponentsCar'+str(i))

if asset in cars :
	step = '0.05'
else :
	step = '1'

# 5. export alembic
print('\nExporting alembic...\n')
resolvedCmd = '-frameRange %s -step %s -stripNamespaces -uvWrite -worldSpace -writeVisibility -eulerFilter -dataFormat ogawa%s -file %s' \
 %(frameRange,step,root,tempAbcFile)
cmds.AbcExport(j=resolvedCmd)

# 6. Exit maya
cmds.quit(abort=True)
print('\n')

# 7. verify export was successfull and backup
if os.path.getsize(tempAbcFile) < 100000 :
	print('// Warning : Alembic export failed')
	os.remove(tempAbcFile)

else :
	print('Alembic export was successfull.\n')

	if not os.path.exists(scenePath + '/abc/backup'):
		os.makedirs(scenePath + '/abc/backup')

	if os.path.isfile(abcFile) :
		# remove old backup
		if os.path.isfile(backupAbcFile):
			os.remove(backupAbcFile)
		# backup published file
		print('Backing up previously published animation to ' + backupAbcFile)
		try :
			os.rename(abcFile,backupAbcFile)
		except WindowsError, e :
			print('Error : Could not backup file')
			os.system('pause')


	try :
		# replace old publish by our temp file
		os.rename(tempAbcFile,abcFile)
		os.system('cls')
		print('   _____')
		print('  / ____|')
		print(' | (___  _   _  ___ ___ ___  ___ ___ ')
		print('  \\___ \\| | | |/ __/ __/ _ \\/ __/ __|')
		print('  ____) | |_| | (_| (_|  __/\\__ \\__ \\')
		print(' |_____/ \\__,_|\\___\\___\\___||___/___/')
		print('\n')
		print('// Result : ' + abcFile)
	except WindowsError, e :
		# if replacement did not work, show message
		os.system('cls')
		print('   \\    /\\')
		print('    )  ( \')          ARREEEETT')
		print('   (  /  )')
		print('    \\(__)|')
		print('\n')
		print('// Error : Could not replace published alembic :')
		print(abcFile)
		print('File is already open in another application and cant be replaced. Replace manually after close.')
		print('// Result : ' + tempAbcFile)

os.system('pause')