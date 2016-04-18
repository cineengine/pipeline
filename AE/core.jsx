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
    var database = File(DATABASE_FOLDER + "\\productions_db.json");
    database.open('r');
    var stream = database.read();
    stream = JSON.parse(stream);

    default_db = stream['DEFAULT']

    try {
        var prod_db = stream[production_];
        for (var key in default_db) prod_db[key] = default_db[key];
        prod_db['is_default'] = false;
    } catch(err) {
        prod_db = default_db;
        prod_db['is_default'] = true;
    }
    //alert(prod_db.toSource());
    database.close();
    return prod_db;
}

function getTeamDatabase(production_){
    var prod_db = getProductionDatabase(production_);

    if (prod_db['is_default'] === true){
        alert('Could not find team database for ' + production_ + '.')
        return false;
    }

    var database = File(DATABASE_FOLDER + prod_db['team_db'] + ".json");
    database.open('r');
    var stream = database.read();
    stream = JSON.parse(stream);
    //alert(stream.toSource());
    database.close();
    return stream;
}

function getTeam(production_, tricode){
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
    var prod_ = getProduction();
    var teams = getTeamDatabase(prod_);
    var all = '';

    var team_folder = getItem('TEAM_COLORS', ItemCollection);
    if (team_folder === undefined){
        team_folder = app.project.items.addFolder('TEAM_COLORS');
    }

    for (var key in teams){
        tricode   = key;
        primary   = teams[key]['primary'];
        secondary = teams[key]['secondary'];
        tertiary  = teams[key]['tertiary'];

        name  = "{0}_COLORS".format(tricode);
        xres  = 1920;
        yres  = 1080;
        par   = 1.0;
        dur   = 60;
        frate = 59.94;
        team_comp = app.project.items.addComp(name, xres, yres, par, dur, frate);

        pri_solid = team_comp.layers.addSolid([0,0,0], "{0}_PRIMARY".format(tricode), xres/3, yres, par);
        sec_solid = team_comp.layers.addSolid([0,0,0], "{0}_SECONDARY".format(tricode), xres/3, yres, par);
        tri_solid = team_comp.layers.addSolid([0,0,0], "{0}_TERTIARY".format(tricode), xres/3, yres, par);

        pri_solid.property("Position").setValue([320, 540]);
        tri_solid.property("Position").setValue([1600, 540]);

        team_comp.parentFolder = team_folder;
        setTeamColors(tricode);
    }
    
}

function setTeamColors(team_){
    var comp;

    var primary;
    var secondary;
    var tertiary;

    var primary_solid;
    var secondary_solid;
    var tertiary_solid;

    comp = getItem('{0}_COLORS'.format(team_));
    team = getTeam(getProduction(), team_);

    primary   = team['primary'];
    secondary = team['secondary'];
    tertiary  = team['tertiary'];

    primary_solid   = getLayer(comp, '{0}_PRIMARY'.format(team_))
    secondary_solid = getLayer(comp, '{0}_SECONDARY'.format(team_))
    tertiary_solid  = getLayer(comp, '{0}_TERTIARY'.format(team_))

    primary_solid.source.mainSource.color = convertColor(primary);
    secondary_solid.source.mainSource.color = convertColor(secondary);
    tertiary_solid.source.mainSource.color = convertColor(tertiary);
}

function convertColor(color){
    var r = color[0];
    var g = color[1];
    var b = color[2];

    r = (1.0/255) * r;
    g = (1.0/255) * g;
    b = (1.0/255) * b;
    return [r, g, b];
}

String.prototype.format = function() {
    var formatted = this;
    for (var i = 0; i < arguments.length; i++) {
        var regexp = new RegExp('\\{'+i+'\\}', 'gi');
        formatted = formatted.replace(regexp, arguments[i]);
    }
    return formatted;
};

createTeamSwatches();