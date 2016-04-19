#include "json2.js"

var DATABASE_FOLDER = "Y:\\Workspace\\SCRIPTS\\pipeline\\database\\";

function getItem(item_name, class_){
    /* Gets an item from the project window by name.  Looks for CompItem by default,
       but can be passed other objects (from the project window) to search for as well. */
    var comp;
    // Handling custom object parameter
    class_ = typeof class_ !== 'undefined' ? class_ : CompItem;
    // Search for the item by name
    for (var i=1; i<=app.project.numItems; i++){ 
        var item = app.project.item(i);
        // Check object type and name
        if ((item instanceof class_) && (item.name === item_name)){
            if (comp){
                alert('More than one item found with name ' + item_name + '.');
            }
            comp = item;
            break;
        }
    }
    return comp;
}

function getLayer(comp, layer_name){
    // Searches a comp for a given layer (by name)
    var layer;
    for (var i=1; i<=comp.numLayers; i++){
        lay = comp.layer(i);
        if (lay.name === layer_name){
            if (layer){
                alert('More than one layer found with name ' + layer_name + '.');
            }
            layer = lay;
            break;
        }
    }
    return layer;
}

function getProduction(){
    // Searches the scene for a production tag and returns the name of the production.
    var const_tkn = "!PRODUCTION:";
    var tkn_length = const_tkn.length;
    var production;
    for (i=1; i<=app.project.numItems; i++){
        item = app.project.item(i)
        if (item.name.indexOf(const_tkn) === 0){
            production = item.name;
            production = production.slice(tkn_length, item.name.length);
            break;
        }
    }
    return production;
}

function getProductionDatabase(production_){
    // Searches the production database for a given production
    var database = File(DATABASE_FOLDER + "\\productions_db.json");
    database.open('r');
    var stream = database.read();
    stream = JSON.parse(stream);
    // A default production database is always loaded
    default_db = stream['DEFAULT']
    // .. and any production database found appends / merges with the default
    try {
        var prod_db = stream[production_];
        for (var key in default_db) prod_db[key] = default_db[key];
        prod_db['is_default'] = false;
    // .. cleanup if no specific production database is found
    } catch(err) {
        prod_db = default_db;
        prod_db['is_default'] = true;
    }
    //alert(prod_db.toSource());
    database.close();
    return prod_db;
}

function getTeamDatabase(production_){
    // Gets the team database for a given production
    var prod_db = getProductionDatabase(production_);
    // if no team database is found
    if (prod_db['is_default'] === true){
        alert('Could not find team database for ' + production_ + '.')
        return false;
    }
    // parse the JSON
    var database = File(DATABASE_FOLDER + prod_db['team_db'] + ".json");
    database.open('r');
    var stream = database.read();
    stream = JSON.parse(stream);
    //alert(stream.toSource());
    database.close();
    return stream;
}

function getTeam(production_, tricode){
    // Searches a team DB for a given tricode
    var team_db = getTeamDatabase(production_);
    var team = null;
    for (var key in team_db){
        if (key === tricode){
            team = team_db[key];
        }
    }
    //alert(team.toSource());
    return team;
}

function createTeamSwatches(){
    // Creates team swatches for an entire production's worth of teams
    var prod_ = getProduction();
    var teams = getTeamDatabase(prod_);
    var colors = ['primary', 'secondary', 'tertiary'];
    var all = '';
    // Comp defaults 
    var name  = "{0}_COLORS".format(tricode);
    var xres  = 1920;
    var yres  = 1080;
    var par   = 1.0; // pixel aspect ratio
    var dur   = 60; // duration
    var frate = 59.94; // frame rate

    // Check for an existing TEAM_COLORS folder in the project window
    var team_folder = getItem('TEAM_COLORS', ItemCollection);
    if (team_folder === undefined){
        team_folder = app.project.items.addFolder('TEAM_COLORS');
    }
    // Iterate over all teams
    for (var key in teams){
        var tricode   = key;
        var team_data = getTeam(getProduction(), tricode);
        var team_comp = app.project.items.addComp("{0}_COLORS".format(tricode), xres, yres, par, dur, frate);
        var team_null = team_comp.layers.addNull();

        //team_comp.name = "{0}_COLORS".format(tricode);
        //team_comp.source.name = "{0}_COLORS".format(tricode);
        team_null.name = "{0}_COLORS".format(tricode);
        team_null.source.name = "{0}_COLORS".format(tricode);

        for (var color in colors){
            color_ctrl = team_null.property("Effects").addProperty("Color Control");
            color_ctrl.name = colors[color];
            color_ctrl.property("Color").setValue(convertColor(team_data[colors[color]]));
        }

        team_comp.parentFolder = team_folder;
    }
}

function setTeamColors(team_){
    // Sets team colors on 3 solids in a comp, all of which are named with a team tricode
    // container variables
    var comp;

    var primary;
    var secondary;
    var tertiary;

    var primary_solid;
    var secondary_solid;
    var tertiary_solid;
    // Get team comp & team data
    comp = getItem('{0}_COLORS'.format(team_));
    team = getTeam(getProduction(), team_);

    primary   = team['primary'];
    secondary = team['secondary'];
    tertiary  = team['tertiary'];
    // Get color solids from comp
    primary_solid   = getLayer(comp, '{0}_PRIMARY'.format(team_))
    secondary_solid = getLayer(comp, '{0}_SECONDARY'.format(team_))
    tertiary_solid  = getLayer(comp, '{0}_TERTIARY'.format(team_))
    // Change colors on solids
    primary_solid.source.mainSource.color = convertColor(primary);
    secondary_solid.source.mainSource.color = convertColor(secondary);
    tertiary_solid.source.mainSource.color = convertColor(tertiary);
}

function convertColor(color){
    // Converts color arrays from integer to float
    var r = color[0];
    var g = color[1];
    var b = color[2];

    r = (1.0/255) * r;
    g = (1.0/255) * g;
    b = (1.0/255) * b;
    return [r, g, b];
}

function nullTeam(){
    var team_data;
    team_data['primary'] = [0,0,0];
    team_data['secondary'] = [0,0,0];
    team_data['tertiary'] = [0,0,0];
    team_data['tricode'] = 'NULL';
    return team_data;
}

String.prototype.format = function() {
    // Adds a .format() method to the String prototype, similar to python
    var formatted = this;
    for (var i = 0; i < arguments.length; i++) {
        var regexp = new RegExp('\\{'+i+'\\}', 'gi');
        formatted = formatted.replace(regexp, arguments[i]);
    }
    return formatted;
};

createTeamSwatches();