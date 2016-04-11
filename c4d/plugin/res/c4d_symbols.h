//*********************************************************************\
// File name        : c4d_symbols.h
// Description      : symbol definition file for the plugin 
//*********************************************************************/
// WARNING : Only edit this file, if you exactly know what you are doing.

// Weird things happen when you let the enum automatically increment the ID numbers
// So to keep things simple(and working). The items listed in this file Exactly match the items listed at the top of the pyp file

enum
{
ID_STATIC            = 99999,
ESPNPipelineMenu     = 10000,
ESPNHelpMenu         = 99998,
MAIN_DIALOG          = 10001,
FIRST_TAB            = 10002,
LBL_PROD_NAME        = 10004,
DRP_PROD_NAME        = 10005,
LBL_PROJ_NAME        = 10006,
CHK_EXISTING         = 10007,
DRP_PROJ_NAME        = 10008,
TXT_PROJ_NAME        = 10009,
LBL_SCENE_NAME       = 10010,
TXT_SCENE_NAME       = 10011,
LBL_FRAMERATE        = 10012,
RDO_FRAMERATE        = 10013,
RDO_FRAMERATE_30     = 10030,
RDO_FRAMERATE_60     = 10060,
FIRST_TAB_SEP_01     = 10017,
LBL_PREVIEW          = 10018,
LBL_PREVIEW_NULL     = 10118,
LBL_PREVIEW_PROJ     = 10019,
TXT_PREVIEW_PROJ     = 10020,
LBL_PREVIEW_FILE     = 10021,
TXT_PREVIEW_FILE     = 10022,
BTN_NEWPROJ_EXEC     = 10023,
BTN_HELP_EXEC        = 10024,
//BTN_RENAME_EXEC      = 10025,
//LBL_NEWPROJ_EXEC     = 10026,
//LBL_MIGPROJ_EXEC     = 10027,
//LBL_RENAME_EXEC      = 10028,
TAB1_HELP_IMAGE      = 10029,
SECOND_TAB           = 20000,
SECOND_TAB_TEXT      = 20001,
SECOND_TAB_TEXTBOX   = 20002,
THIRD_TAB            = 30000,
THIRD_TAB_TEXT       = 30001,
THIRD_TAB_TEXTBOX    = 30002,
FOURTH_TAB           = 40000,
FOURTH_TAB_TEXT      = 40001,
FOURTH_TAB_TEXTBOX   = 40002,
DRP_PROJ_NAME_START_ID = 80000,
DRP_PROD_NAME_START_ID = 90000,
}


