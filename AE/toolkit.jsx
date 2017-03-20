#include "core.jsx"
{
	DB_ALTID_REDIRECT = {
		"ims_swatch": ["ims_swatch", "ims_swatch2"],
		"Pb": ["Pb", "Pb2"],
		"Pr": ["Pr", "Pr2"],
		"Pg": ["Pg", "Pg2"],
		"Sb": ["Sb", "Sb2"],
		"Sr": ["Sr", "Sr2"],
		"Sg": ["Sg", "Sg2"],
		"ims_name": ["IMS", "IMS2"],
		"tricode": ["TRICODE", "TRICODE2"]
	};

	function buildTeamSwitcher(){
		prod = getProduction();
		if (!prod){	return false; }

		teams = getTeamList(prod);
		if (!teams){ return false; }

		try{
			// 
			var c_switcher = app.project.items.addComp("TEAM_SWITCHER", 1920, 1080, 1.0, 1, 59.94);
			c_switcher.hideShyLayers = true;
			// create switch layer
			var l_switcher = c_switcher.layers.addNull();
			l_switcher.name = "Select Team(s)";
			l_switcher.source.name = "Select Team(s)";
			// add layer control effects on switch layer	
			// home team switcher
			e_switcher_home = l_switcher.property("Effects").addProperty("Layer Control");
			e_switcher_home.name = "Home Team";
			// home team alternate identity checkbox
			e_alternate_home= l_switcher.property("Effects").addProperty("Checkbox Control");
			e_alternate_home.name = "Use Alternate Identity (Home)";
			// away team switcher			
			e_switcher_away = l_switcher.property("Effects").addProperty("Layer Control");
			e_switcher_away.name = "Away Team";
			// away team alternate identity checkbox
			e_alternate_away= l_switcher.property("Effects").addProperty("Checkbox Control");
			e_alternate_away.name = "Use Alternate Identity (Away)";

			for (i=0; i<teams.length; i++){
				l_team = c_switcher.layers.addNull();
				l_team.name = teams[i];
				l_team.source.name = teams[i];
				l_team.moveToEnd();
				l_team.shy = true;
			}
	
		} catch(e) { return false; }

		return true;
	}

	function buildTeamSwatches(alt_map){
		if (alt_map === undefined || alt_map === 0) alt_map = 0;

		prod_name = getProduction();
		if (!prod_name){ return false };

		prod = getProductionDatabase(prod_name);
		if (!prod){ return false };

		teams = getTeamDatabase(prod_name);
		if (!teams){ return false };

		//try{
		var c_swatches = app.project.items.addComp("TEAM_SWATCHES", 1920, 1080, 1.0, 1, 59.94);
		c_swatches.hideShyLayers = true;
		var ims_folder = prod[DB_ALTID_REDIRECT["ims_swatch"][alt_map]];
		for (t in teams){
			var team     = teams[t];
			var ims_name = team["IMS"];//DB_ALTID_REDIRECT["ims_name"][alt_map]];
			var ims_loc  = "{0}\\{1}.png".format(ims_folder, ims_name);
			var swatch   = app.project.importFile(new ImportOptions(File(ims_loc)));
		}
		//} catch(e) { return false; }
	}

	buildTeamSwatches(1);
}
