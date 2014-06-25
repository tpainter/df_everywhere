
var ctx;

function Tileset(tile_x, tile_y){
    
    this.tileset_x;
    this.tileset_y;
    this.tiles_x;
    this.tiles_y;
    this.tile_x = tile_x;
    this.tile_y = tile_y;
    this.loaded = false;
    
    this.drawTile = function (tileNum, drawPos){
        //drawPos is [row, column]
        var t_row = Math.floor(tileNum / this.tiles_x);
        var t_column = tileNum % this.tiles_x;
                
        var sx = t_column * this.tile_x;
        var sy = t_row * this.tile_y;
        var swidth = this.tile_x;
        var sheight = this.tile_y;
        var x = drawPos[1] * this.tile_x;
        var y = drawPos[0] * this.tile_y;
        var width = this.tile_x;
        var height = this.tile_y;
        
        ctx.drawImage(this.img,sx,sy,swidth,sheight,x,y,width,height);        
    }
}

var tileset_image = new Image;               

var tileset = new Tileset(16, 16);

$(document).ready( function(){    
    var div = document.getElementById('compare');
    
    tileset_image.onload = function(){
        tileset.tileset_x = this.width;
        tileset.tileset_y = this.height;
        tileset.tiles_x = this.width / tileset.tile_x;
        tileset.tiles_y = this.height / tileset.tile_y;
        tileset.loaded = true;
        tileset.img = this;
    }   
        
    ctx = $('#gameboard')[0].getContext("2d");
    ctx.canvas.width = 80 * 16;
    ctx.canvas.height = 25 * 16;
    
});

function draw_image(tile_map){
    if (tileset.loaded){
        console.log("drawing map");
        var row = 0;
        var column = 0;
        tile_map = tile_map[0];
        for (elem in tile_map){
            for (elem2 in tile_map[elem]){
                tileset.drawTile(tile_map[elem][elem2], [row, column]);
                column++;
            }
            row++;
            column = 0;
        }
    } else {
        console.log("Waiting for tileset to load.");
    }
    
}

function update_tileset(fname){
    
    if (tileset_image.src.indexOf(fname[0]) > -1){
        console.log("Tileset name update not needed.");
    }
    else {
        console.log("Updating tileset name.");
        tileset_image.src = fname[0];
    }
}

function update_screensize(dims) {
    //dims is [x_pixels, y_pixels]
    screen_x = dims[0][0];
    screen_y = dims[0][1];
    
    if (screen_x != ctx.canvas.width || screen_y != ctx.canvas.height){
        console.log("Updating screen size.");
        ctx.canvas.width = screen_x[0];
        ctx.canvas.height = screen_y[0];
    }
    else {
        console.log("Screen size update not needed.");
    }
    
}

try {
   var autobahn = require('autobahn');
} catch (e) {
   // when running in browser, AutobahnJS will
   // be included without a module system
}

var connection = new autobahn.Connection({
   url: 'ws://127.0.0.1:7081/ws',
   //url: 'ws://192.168.0.20:7081/ws',
   realm: 'realm1'}
);

//Setup Autobahn for WAMP connection
connection.onopen = function (session) {
    console.log("WAMP connection open...");

   //subscribe to tilemap
   session.subscribe("df_anywhere.g1.map", draw_image);
   
   //subscribe to tileset updates
   session.subscribe("df_anywhere.g1.tileset", update_tileset);
   
   //subscribe to screensize updates
   session.subscribe("df_anywhere.g1.screensize", update_screensize);   
   
};

connection.open();


