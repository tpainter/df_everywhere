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

from cStringIO import StringIO
import mmh3
import numpy

class Tileset:
    """
    Holds details for the tileset.
    """
    
    def __init__(self, filename, tile_x, tile_y, debug = False):        
        
        self.tile_x = tile_x
        self.tile_y = tile_y
        self.screen_x = 0
        self.screen_y = 0
        
        self.fullMap = []
        self.prevDifMap = []
        self.prevImage = None
        self.prevArray = None
        
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
            exit()
        
    def _loadSet(self, img = None):
        """
        Creates a dictionary from the tileset image.
        """
        
        if img is None:
            img = self.tileset
        
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
                    
                tile = img.crop((x_start * self.tile_x, y_start * self.tile_y, x_start * self.tile_x + self.tile_x, y_start * self.tile_y + self.tile_y))       
                
                #Use the hash of the tile as a key to insure that it is unique
                tile_hash = self._imageHash(tile)
                
                if tile_hash in self.tileDict:
                    #It would be bad to find a duplicate in the tileset.
                    print("Error: Found duplicate tile in tileset. Exiting.")
                    print("t=%d" % t)
                    exit()
                else:
                    self.tileDict[tile_hash] = t
                        
                t += 1
                        
        self.tileset = img
        print("Tileset loaded: %s with %d tiles" % (self.filename, t))
            
    def _addTileToSet(self, img):
        """
        Adds new tile to tileset.
        """
        
        #Check that proposed tile matches the tile size of the set
        pTile_x, pTile_y = img.size
        if (pTile_x == self.tile_x) and (pTile_y == self.tile_y):
            pass
        else:
            print("Add tile error: tile dimensions do not match tileset")
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
        self._loadSet(newTileSet)
    
    def _saveSet(self):
        """
        Saves tileset image to disk
        """
        
        print("Saving new tileset image: %s" % self.filename)
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
            print("Difference map exception")
            return newMap
        
    def parseImageFast(self, new_img, returnFullMap = True):
        """
        Compares two images pixel by pixel.
        Doesn't end up being faster. 
        """
        tileMap = []
        tileSetChanged = False
        new_x, new_y = new_img.size
        numTilesSame = 0
        
        if self.prevImage is None:
            #Handle initial case
            returnFullMap = True
        else:
            old_x, old_y = self.prevImage.size        
        
            #Make sure that image sizes match
            if (old_x != new_x) or (old_y != new_y):
                returnFullMap = True
        
        tiles_x = new_x / self.tile_x
        tiles_y = new_y / self.tile_y
        
        for y_start in range(tiles_y):
            row  = []
            for x_start in range(tiles_x):
                tile = new_img.crop((x_start * self.tile_x, y_start * self.tile_y, x_start * self.tile_x + self.tile_x, y_start * self.tile_y + self.tile_y))
                
                if returnFullMap:
                    #Use the hash of the tile as a key to ensure that it is unique
                    tile_hash = self._imageHash(tile)
                
                    if tile_hash in self.tileDict:
                        row.append(self.tileDict[tile_hash])
                    else:
                        row.append(-1)
                        self._addTileToSet(tile)
                        tileSetChanged = True
                else:
                    tile_prev = self.prevImage.crop((x_start * self.tile_x, y_start * self.tile_y, x_start * self.tile_x + self.tile_x, y_start * self.tile_y + self.tile_y))
                    
                    tilesSame = self._imgEqual(tile, tile_prev, False)
                    
                    if tilesSame:
                        numTilesSame += 1
                        row.append(-2)
                    else:
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
        
        #Update the stored image with the current one
        self.prevImage = new_img
        #print numTilesSame
        
        return tileMap

    def parseImageArray(self, new_img, returnFullMap = True):
        """
        Compares two images.
        """
        tileMap = []
        tileSetChanged = False
        new_x, new_y = new_img.size
        numSame = 0
        
        new_imgArray = numpy.array(new_img)
        
        if self.prevArray is None:
            #Handle initial case
            returnFullMap = True
        else:
            #print self.prevArray.shape
            old_y, old_x, old_depth = self.prevArray.shape
            prev_imgArray = self.prevArray            
        
            #Make sure that image sizes match
            if (old_x != new_x) or (old_y != new_y):
                returnFullMap = True
        
        tiles_x = new_x / self.tile_x
        tiles_y = new_y / self.tile_y
        
        for y_start in range(tiles_y):
            row  = []
            for x_start in range(tiles_x):
                tile_arr = new_imgArray[y_start * self.tile_y: y_start * self.tile_y + self.tile_y, x_start * self.tile_x: x_start * self.tile_x + self.tile_x]
                tile_img = new_img.crop((x_start * self.tile_x, y_start * self.tile_y, x_start * self.tile_x + self.tile_x, y_start * self.tile_y + self.tile_y))
                
                if returnFullMap:
                    #Use the hash of the tile as a key to ensure that it is unique
                    tile_hash = self._imageHash(tile_img)
                
                    if tile_hash in self.tileDict:
                        row.append(self.tileDict[tile_hash])
                    else:
                        row.append(-1)
                        self._addTileToSet(tile_img)
                        tileSetChanged = True
                else:
                    #tile_prevImg = self.prevImage.crop((x_start * self.tile_x, y_start * self.tile_y, x_start * self.tile_x + self.tile_x, y_start * self.tile_y + self.tile_y))
                    tile_prevArr = prev_imgArray[y_start * self.tile_y: y_start * self.tile_y + self.tile_y, x_start * self.tile_x: x_start * self.tile_x + self.tile_x]
                    
                    #tilesSame = (tile_prevArr == tile_arr).all()
                    tilesSame = numpy.array_equal(tile_prevArr, tile_arr)
                    
                    if tilesSame:
                        row.append(-2)
                        numSame += 1
                    else:
                        tile_hash = self._imageHash(tile_img)
                        if tile_hash in self.tileDict:
                            row.append(self.tileDict[tile_hash])
                        else:
                            row.append(-1)
                            self._addTileToSet(tile_img)
                            tileSetChanged = True
            tileMap.append(row)
        
        if tileSetChanged:
            #If new tiles were added, save the file to disk.
            #Do this here so that each new tile isn't saved.
            self._saveSet()
        
        #Update the stored image with the current one
        self.prevArray = new_imgArray
        
        #print numSame
        return tileMap
            
    def _imgEqual(self, img1, img2, brute = False):
        """
        Returns 'True' if the two images are exactly equal.
        Compares pixel by pixel.
        """
        if not brute:
            return ImageChops.difference(img1, img2).getbbox() is None
        else:
            pixels1 = img1.load()
            pixels2 = img2.load()
            img_x, img_y = img1.size
            for x in range(img_x):
                for y in range(img_y):
                    if pixels1[x,y] == pixels2[x,y]:
                        pass
                    else:
                        return False
            return True
        
        
        
    def _imageHash(self, img):
        """
        Returns a hash of the image.
        """
        
        #Try to speed up hashing by using string hash
        #return str.__hash__(img.tostring())
        
        #Hash is faster
        #return hash(img.tostring())
        
        #murmur3 is fastest but not a lot faster than Hash
        return mmh3.hash(img.tostring())
        
        #just a long string?
        #return img.tostring()
        
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
        