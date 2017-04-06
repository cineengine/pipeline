#include "core.jsx"
#include "json2.js"
{
	function pickleLogoSheet()
	{
		var output    = {};
		var selection = app.project.selection;

		for (i in selection)
		{
			siz = [selection[i].width, selection[i].height];
			pos = selection[i].layers[1].position.value;
			anx = selection[i].layers[1].anchorPoint.value;
			scl = selection[i].layers[1].scale.value;

			output[selection[i].name] = {
				"Size": siz,
				"Pos": pos,
				"Anx": anx,
				"Scl": scl
			}
		}
    	output = JSON.stringify(output);

		var out_json = new File("/v/cbb_logosheet.json");
    	out_json.open('w');
    	out_json.write(output);
	}

	function buildToolkittedPrecomps()
	{
		var temp = new File("/v/cbb_logosheet.json");
		temp.open('r');
		var layout = temp.read();
		layout = JSON.parse(layout);

		logo_sheet = getItem("Team Logosheet Master Switch");
		if (logo_sheet === undefined){
			return false;
		}

		for (c in layout)
		{
			comp  = app.project.items.addComp(c, layout[c]["Size"][0], layout[c]["Size"][1], 1.0, 60, 30);
			layer = comp.layers.add(logo_sheet);
			layer.position.setValue(layout[c]["Pos"]);
			layer.anchorPoint.setValue(layout[c]["Anx"]);
			layer.scale.setValue(layout[c]["Scl"]);
			layer.collapseTransformation = true;
		}
	}

	function buildMasterControl(prod)
	{
		teams = getTeamList(prod);
		if (!teams){ return false; }

		try{
			var c_tag      = app.project.items.addComp("!PRODUCTION:{0}".format(prod), 1, 1, 1.0, 1, 59.94);
			var c_switcher = app.project.items.addComp("0. Toolkit Master Control", 1920, 1080, 1.0, 1, 59.94);
			c_switcher.hideShyLayers = true;
			// create switch layer
			var l_switcher = c_switcher.layers.addNull();
			l_switcher.name = "Switch Team Here";
			l_switcher.source.name = "Switch Team Here";
			// add layer control effects on switch layer	
			// home team switcher
			e_switcher_home = l_switcher.property("Effects").addProperty("Layer Control");
			e_switcher_home.name = "Home Team";
			// away team switcher			
			e_switcher_away = l_switcher.property("Effects").addProperty("Layer Control");
			e_switcher_away.name = "Away Team";

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

	function run()
	{
		buildFolders();
		buildMasterControl();
		loadLogoSheets();
		buildToolkittedPrecomps();
	}

	/*
	function buildTeamSwatches()
	{
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
		var ims_folder = prod["IMS"];
		for (t in teams){
			var team     = teams[t];
			var swatch   = app.project.importFile(new ImportOptions(File(ims_loc)));
		}
		//} catch(e) { return false; }
	}*/

	//pickleLogoSheet();
	buildLayout();

}
