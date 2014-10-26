# DF Everywhere
# Copyright (C) 2014  Travis Painter

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

try:
    import Image
    import ImageChops
except:
    from PIL import Image
    from PIL import ImageChops

import sys
from cStringIO import StringIO
import mmh3
import numpy

import prettyConsole

class Tileset:
    """
    Holds details for the tileset.
    """
    
    def __init__(self, filename, tile_x, tile_y, array = False, debug = False):        
        
        self.tile_x = tile_x
        self.tile_y = tile_y
        self.screen_x = 0
        self.screen_y = 0
        
        self.fullMap = []
        self.prevDifMap = []
        
        if filename is None:
            #fake a filename
            self.filename = "%dx%d-%05d.png" % (self.tile_x, self.tile_y, 0)
            img = None
        else:
            self.filename = filename
            img = Image.open("./tilesets/%s" % filename)
            
        self.debug = debug        
        self.tileset = img      
        
        self.tileDict = {}
        self._parseFilename(self.filename)
        if img is not None:
            if array:
                self._loadSet(array = True)
            else:
                self._loadSet()
        
    def _parseFilename(self, filename):
        """
        Parses the filename to get tileset properties.
        Format is: NNxMM-00000.png
        Where:  NN = x-dimension pixels
                MM = y-dimension pixels
                00000 = number of tiles in tileset
        """
        
        file_x = int(filename[:2])
        file_y = int(filename[3:5])
        file_tiles = int(filename[6:11])
        file_extension = filename[11:]
        
        #Do checks to make sure that things make sense
        if (file_x == self.tile_x) and (file_y == self.tile_y):
            self.tileCount = file_tiles
            self.imgExtension = file_extension
        else:
            print("Error with tileset filename. Exiting.")
            sys.exit()
        
    def _loadSet(self, img = None, array = False, verbose = True):
        """
        Creates a dictionary from the tileset image.
        """
        
        if img is None:
            img = self.tileset
            
        if array:
            img_array = numpy.array(img)
        
        image_x, image_y = img.size
        
        tiles_x = image_x / self.tile_x
        tiles_y = image_y / self.tile_y
        
        #tile number i.e. "position"
        t = 0
        
        #reset tileDict
        self.tileDict.clear()
        
        for y_start in range(tiles_y):
            for x_start in range(tiles_x):
                #Once max tiles in tileset is reached, end the load process
                if t >= self.tileCount:
                    break
                if array:
                    tile = img_array[y_start * self.tile_y: y_start * self.tile_y + self.tile_y, x_start * self.tile_x: x_start * self.tile_x + self.tile_x]
                else:
                    tile = img.crop((x_start * self.tile_x, y_start * self.tile_y, x_start * self.tile_x + self.tile_x, y_start * self.tile_y + self.tile_y))       
                
                #Use the hash of the tile as a key to insure that it is unique
                tile_hash = self._imageHash(tile)
                
                if tile_hash in self.tileDict:
                    #It would be bad to find a duplicate in the tileset.
                    print("Error: Found duplicate tile in tileset. Exiting.")
                    print("t=%d" % t)
                    sys.exit()
                else:
                    self.tileDict[tile_hash] = t
                        
                t += 1
                        
        self.tileset = img
        if verbose:
            prettyConsole.console('log', "Tileset loaded: %s with %d tiles" % (self.filename, t))
            
    def _addTileToSet(self, img, array = False, verbose = True):
        """
        Adds new tile to tileset.
        """
        if array:
            img = Image.fromarray(img.astype('uint8')).convert('RGB')
        
        
        #Check that proposed tile matches the tile size of the set
        pTile_x, pTile_y = img.size
        if (pTile_x == self.tile_x) and (pTile_y == self.tile_y):
            pass
        else:
            prettyConsole.console('log', "Add tile error: tile dimensions do not match tileset")
            return
            
        if self.tileset is not None:
            image_x, image_y = self.tileset.size
        else:
            image_x = self.tile_x
            image_y = self.tile_y
        
        tiles_x = image_x / self.tile_x
        tiles_y = image_y / self.tile_y
        
        #Number of tiles to place across the width of the tileset image
        maxTiles_x = 32
        
        #Check if a new row needs to be created in the image
        if self.tileCount + 1 > maxTiles_x * tiles_y:
            #need to add another row to tileset image
            newTileSet = Image.new(self.tileset.mode, (maxTiles_x * self.tile_x, tiles_y * self.tile_y + self.tile_y), "white")
        else:
            #No need to add new row
            if self.tileset is not None:
                newTileSet = Image.new(self.tileset.mode, (maxTiles_x * self.tile_x, tiles_y * self.tile_y), "white")
            else:
                newTileSet = Image.new("RGB", (maxTiles_x * self.tile_x, tiles_y * self.tile_y), "white")
        
        #copy existing tileset image onto new blank image
        if self.tileset is not None:
            newTileSet.paste(self.tileset, (0, 0))
        
        #paste new tile into the proper location
        if self.tileset is not None:
            newTilePosition = self.tileCount
        else:
            #first tile goes in first spot
            newTilePosition = 0
            
        new_x = newTilePosition % maxTiles_x * self.tile_x
        new_y = newTilePosition / maxTiles_x * self.tile_y
        newTileSet.paste(img, (new_x, new_y))
        
        filename = "%dx%d-%05d.png" % (self.tile_x, self.tile_y, newTilePosition)
        
        #reload new tileset
        self.tileCount += 1
        self.filename = filename
        self._loadSet(newTileSet, array, verbose)
    
    def _saveSet(self):
        """
        Saves tileset image to disk
        """
        
        prettyConsole.console('log', "Saving new tileset image: %s" % self.filename)
        self.tileset.save("./tilesets/%s" % self.filename, optimize = True )
        
    def parseImage(self, img, returnFullMap = True):
        """
        Parses an image. Returns list of tile positions in map.
        """
        tileMap = []
        tileSetChanged = False
        image_x, image_y = img.size
        self.screen_x = image_x
        self.screen_y = image_y
           
        tiles_x = image_x / self.tile_x
        tiles_y = image_y / self.tile_y
        
        for y_start in range(tiles_y):
            row  = []
            for x_start in range(tiles_x):
                tile = img.crop((x_start * self.tile_x, y_start * self.tile_y, x_start * self.tile_x + self.tile_x, y_start * self.tile_y + self.tile_y))       
                
                #Use the hash of the tile as a key to ensure that it is unique
                tile_hash = self._imageHash(tile)
                
                if tile_hash in self.tileDict:
                    row.append(self.tileDict[tile_hash])
                else:
                    row.append(-1)
                    self._addTileToSet(tile)
                    tileSetChanged = True
                        
            tileMap.append(row)
                
        if tileSetChanged:
            #If new tiles were added, save the file to disk.
            #Do this here so that each new tile isn't saved.
            self._saveSet()
                    
        if returnFullMap:
            #Update fullMap
            self.fullMap[:] = []
            self.fullMap.extend(tileMap)
            return tileMap
        else:
            return self._tileMapDifference(tileMap)
        
    def _tileMapDifference(self, newMap):
        """
        Compares newMap to latest fullMap and prevDifMap. Returns newMap with '-2' in positions that didn't change.
        """
        
        #return newMap
        try:
            if len(newMap) != len(self.fullMap):
                #Map may have changed dimensions
                return newMap
            else:
                differenceMap = []
                for i in xrange(len(newMap)):
                    rowDif = []
                    for j in xrange(len(newMap[0])):
                        if newMap[i][j] == self.fullMap[i][j] and self.prevDifMap == -2:
                            rowDif.append(-2)
                        else:
                            rowDif.append(newMap[i][j])
                            #differenceMap.append(newMap[i])
                    differenceMap.append(rowDif)
                
                #Update the saved difMap
                self.prevDifMap[:] = []
                self.prevDifMap.extend(differenceMap)
                return differenceMap
        except:
            prettyConsole.console('log', "Difference map exception")
            return newMap
        

    def parseImageArray(self, img, returnFullMap = True):
        """
        Parses an image as an array. Returns list of tile positions in map.
        """
        #img_arr = numpy.ascontiguousarray(img)
        img_arr = numpy.array(img)
        tileMap = []
        addTilesDict = {}
        tileSetChanged = False        
        image_x, image_y = img.size
        self.screen_x = image_x
        self.screen_y = image_y
        
        tiles_x = image_x / self.tile_x
        tiles_y = image_y / self.tile_y
        
        # from: http://stackoverflow.com/questions/8070349/using-numpy-stride-tricks-to-get-non-overlapping-array-blocks
        sz = img_arr.itemsize
        h,w = image_y, image_x
        bh,bw = self.tile_y, self.tile_x
        #shape = numpy.array([h/bh, w/bw, bh, bw, 3])
        shape = numpy.array([h/bh, w/bw, bh, bw, 3])
        strides = sz*numpy.array([w*bh*3,bw*3,w*3,3,1])

        blocks=numpy.lib.stride_tricks.as_strided(img_arr, shape=shape, strides=strides)
        
        #prettyConsole.console('log', img_arr.shape)
        #prettyConsole.console('log', img_arr.itemsize)
        #img.save('strideTest.png')
        #prettyConsole.console('log', blocks.shape)
        
        row = []
        i = 0
        for b in blocks:
            for c in b:
                tile_hash = self._imageHash(c)
                
                if tile_hash in self.tileDict:
                    row.append(self.tileDict[tile_hash])
                else:
                    row.append(-1)
                    if tile_hash in addTilesDict:
                        pass
                    else:
                        addTilesDict[tile_hash] = c
                    tileSetChanged = True
                    
                i += 1
                if i == tiles_x:
                    tileMap.append(row)
                    row = []
                    i = 0        
                
        if tileSetChanged:
            #If new tiles were added, save the file to disk.
            #Do this here so that each new tile isn't saved.
            for k in addTilesDict.keys():
                self._addTileToSet(addTilesDict[k], array = True, verbose = False)
            self._saveSet()
                    
        if returnFullMap:
            #Update fullMap
            self.fullMap[:] = []
            self.fullMap.extend(tileMap)
            return tileMap
        else:
            return self._tileMapDifference(tileMap)
        
    def _imageHash(self, img):
        """
        Returns a hash of the image.
        """        
        #Hash is fast
        #return hash(img.tostring())
        
        #murmur3 is fastest but not a lot faster than Hash
        return mmh3.hash(img.tostring())
        
    def wampSend(self):
        """
        Converts tileset image to byte string so that it can be send via WAMP.
        """
        img_io = StringIO()
        self.tileset.save(img_io, 'png', optimize = True)
        img_io.seek(0)
        #return img_io
        #can't send binary data directly. Base64 encode first.
        return img_io.getvalue().encode("base64")
        