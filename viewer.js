
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
        var t_row = Math.floor(tileNum / this.tiles_x);
        var t_column = tileNum % this.tiles_x;
        
        var c_row = Math.floor(drawPos / this.tiles_x);
        var c_column = drawPos % this.tiles_x;
        
        var sx = t_column * this.tile_x;
        var sy = t_row * this.tile_y;
        var swidth = this.tile_x;
        var sheight = this.tile_y;
        var x = t_column * this.tile_x;
        var y = c_row * this.tile_y;
        var width = this.tile_x;
        var height = this.tile_y;
        
        ctx.drawImage(this.img,sx,sy,swidth,sheight,x,y,width,height);
        
    }
}

var tileset_image = new Image;
function update_tileset(fname){
    console.log("Updating tileset name");
    tileset_image.src = fname;
}

function update_screensize(screen_x, screen_y) {
    console.log("Updating screen size");
    ctx.canvas.width = screen_x;
    ctx.canvas.height = screen_y;
}

var test_array = [ 0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15,
                  16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 
                  32, 33, 34];
                  

var tileset = new Tileset(12, 12);

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
    
    tileset_image.src = "12x12-00913.png"
    
    ctx = $('#gameboard')[0].getContext("2d");
    ctx.canvas.width = 256;
    ctx.canvas.height = 256;
    
    //tileWait();
});

function tileWait(){
    if (tileset.loaded){
        ctx.clearRect(0,0,256,256);
        var i = 0;
        for (elem in test_array){
            tileset.drawTile(test_array[elem], i);
            i++;
        }
        setInterval(tileWait, .2 * 1000);
    } else {
        console.log("waiting");
        setTimeout(tileWait, .25 * 1000);
    }
}

function draw_image(tile_map){
    if (tileset.loaded){
        console.log("drawing map");
        ctx.canvas.width = ctx.canvas.width;
        var i = 0;
        for (elem in tile_map){
            tileset.drawTile(tile_map[elem], i);
            i++;
        }
        setInterval(tileWait, .2 * 1000);
    } else {
        console.log("waiting");
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
   session.subscribe("df_anywhere.1.map", draw_image);
   
   //subscribe to tileset updates
   session.subscribe("df_anywhere.1.tileset", update_tileset);
   
   //subscribe to screensize updates
   session.subscribe("df_anywhere.1.screensize", update_screensize);
   
};

connection.open();
