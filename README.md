# Skid Pipeline

This is a collection of scripts I wrote during production of our graduation movie 'Skid' (ESMA 2019). These pipeline scripts are intended to work with Maya 2018 and Renderman 22. They are presented here solely as a showcase of my work and should not be used in a production environment.

## Departments
Scripts are separated depending on departments you would normaly have in a studio :

### Assets

#### Assets tools
* Asset checker : topology, UVs, normals, duplicate names, nomenclatures... etc.
* Fix duplicate names / shape names
* Fix normals
* Select objects with no UVs
* Create basic rig (for set dress)
* Assign material ID
* Export

#### Lookdev tools
* Load Renderman, check version
* List of HDRI to choose from
* Create a complete Renderman shading network
* Convert PxrSurface to PxrLayer
* Geometry / lighting turn

### Shots

#### Previz tools (deprecated)
* Load rig
* Playblast / publish for previz editing
* Publish previz animations

#### Animation tools
* Load animation plugins
* Auto import character and vehicle rig
* Animation constraints, start pose...
* Playblast with backup / publish for editing
* Publish animation with backup

#### Set Dress tools
* Reference alembic
* Unload references from selection
* ATOM export

#### Forest tools
* Compute forest instancing point cloud
* Load point cloud
* Instance tress, grass, rocks... etc.

#### Render tools
* Auto import shot animations
* Auto import shaders for animations
* Auto assign shaders for animations
* Auto import shot forest
* Auto import lighting rig, list of HDR to choose from
* Override geometry attributes for render (Subdiv, trace bias, motion samples)

### Common tools
* Increment and save (with versioning)
* Compact Renamer from [Erik Lehmann](https://gumroad.com/eriklehmann)
* Viewport debug
* Auto import shot camera
* Set frame range from camera
* Attach Renderman Subdiv scheme
* Load render settings presets (lookdev, shot)
* Nomenclatures cheat sheet
