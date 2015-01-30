# THIS MODULE IS UNIQUE TO THE WONKY COLLEGE FOOTBALL '14 PLAYOFFS.  TOTAL HACK JOB.

import pymel.core as pm

import pipeline.cfb as cfb
from pipeline.maya.sort import addSortgroupToLayer

def replaceTeamLogo(namespace, tricode):
    for ref in pm.listReferences():
        if ref.namespace == namespace:

	    try:
	        ref.replaceWith(cfb.TEAMS_ASSET_DIR + tricode + "\\" + tricode + ".mb")
	        return True
	    except: 
	        pm.warning('Failed to reference ' + tricode + '!!')
	        return False


def nysTeamTrans(tricode, *a):
    #team        = cfb.db.Team(tricode)
    file_prefix = pm.PyNode('vraySettings').fileNamePrefix

    # Find the reference node of the team logo
    #for ref in pm.listReferences():
    #    if ref.namespace == 'TEAM':
    #        break

    # Swap the reference node 
    #ref.replaceWith(cfb.TEAMS_ASSET_DIR + tricode + "\\" + tricode + ".mb")

    replaceTeamLogo('TEAM', tricode)

    # Sort TEAM:sg_sign into btyTeamLogo
    addSortgroupToLayer( 'TEAM:sg_sign', 'btyTeamLogo' )
    # Sort TEAM:sg_sign into matteTeamLogo
    addSortgroupToLayer( 'TEAM:sg_sign', 'matteTeamLogo' )
    # Sort TEAM:sg_sign into utilTeamLogo
    addSortgroupToLayer( 'TEAM:sg_sign', 'utilTeamLogo' )
    # Sort TEAM:lg_night into btyTeamLogo
    addSortgroupToLayer( 'TEAM:lg_night', 'btyTeamLogo' )

    # Change render file name prefix
    file_prefix.set( "LOGOS/" + tricode + "/<Layer>/<Layer>")

    # Save off a new version of the scene file
    # ... maybe later ...

    # Submit to the farm
    # ... maybe later ...


def nysTeamEndstamp(tricode, *a):
    #team        = cfb.db.Team(tricode)
    file_prefix = pm.PyNode('vraySettings').fileNamePrefix

    # Find the reference node of the team logo
    #for ref in pm.listReferences():
    #    if ref.namespace == 'HOMELOGO':
    #        break

    # Swap the reference node 
    #ref.replaceWith(cfb.TEAMS_ASSET_DIR + tricode + "\\" + tricode + ".mb")

    replaceTeamLogo('HOMELOGO', tricode)

    # Sort TEAM:sg_sign into btyTeamLogo
    addSortgroupToLayer( 'HOMELOGO:sg_sign', 'btyHomeLogo' )
    # Sort TEAM:sg_sign into matteTeamLogo
    addSortgroupToLayer( 'HOMELOGO:sg_sign', 'matteHomeLogo' )
    # Sort TEAM:sg_sign into utilTeamLogo
    addSortgroupToLayer( 'HOMELOGO:sg_sign', 'utilHomeLogo' )
    # Sort TEAM:lg_night into btyTeamLogo
    addSortgroupToLayer( 'HOMELOGO:lg_night', 'btyHomeLogo' )

    # Change render file name prefix
    file_prefix.set( "LOGOS/" + tricode + "/<Layer>/<Layer>.#")

    # Save off a new version of the scene file
    # ... maybe later ...

    # Submit to the farm
    # ... maybe later ...


def nysTeamMatchupTransition(away_tri, home_tri, *a):
    file_prefix = pm.PyNode('vraySettings').fileNamePrefix

    #for ref in pm.listReferences():
    #    if ref.namespace == 'HOMELOGO':
    #        break
    #ref.replaceWith(cfb.TEAMS_ASSET_DIR + home_tri + "\\" + home_tri + ".mb")

    #for ref in pm.listReferences():
    #    if ref.namespace == 'AWAYLOGO':
    #        break
    #ref.replaceWith(cfb.TEAMS_ASSET_DIR + away_tri + "\\" + away_tri + ".mb")

    replaceTeamLogo('HOMELOGO', home_tri)
    replaceTeamLogo('AWAYLOGO', away_tri)

    # HOME TEAM
    # Sort TEAM:sg_sign into btyTeamLogo
    addSortgroupToLayer( 'HOMELOGO:sg_sign', 'btyHomeLogo' )
    # Sort TEAM:sg_sign into matteTeamLogo
    addSortgroupToLayer( 'HOMELOGO:sg_sign', 'matteHomeLogo' )
    # Sort TEAM:sg_sign into utilTeamLogo
    addSortgroupToLayer( 'HOMELOGO:sg_sign', 'utilHomeLogo' )
    # Sort TEAM:lg_night into btyTeamLogo
    addSortgroupToLayer( 'HOMELOGO:lg_night', 'btyHomeLogo' )

    # AWAY TEAM
    # Sort TEAM:sg_sign into btyTeamLogo
    addSortgroupToLayer( 'AWAYLOGO:sg_sign', 'btyAwayLogo' )
    # Sort TEAM:sg_sign into matteTeamLogo
    addSortgroupToLayer( 'AWAYLOGO:sg_sign', 'matteAwayLogo' )
    # Sort TEAM:sg_sign into utilTeamLogo
    addSortgroupToLayer( 'AWAYLOGO:sg_sign', 'utilAwayLogo' )
    # Sort TEAM:lg_night into btyTeamLogo
    addSortgroupToLayer( 'AWAYLOGO:lg_night', 'btyAwayLogo' )

    # Change render file name prefix
    file_prefix.set( "LOGOS/" + away_tri + "_" + home_tri + "/<Layer>/<Layer>.#")