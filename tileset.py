
try:
    import Image
except:
    from PIL import Image

from cStringIO import StringIO    
import hashlib

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
        
        if filename is None:
            #fake a filename
            self.filename = "%dx%d-%05d.png" % (self.tile_x, self.tile_y, 0)
            img = None
        else:
            self.filename = filename
            img = Image.open("./html/tilesets/%s" % filename)
            
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
        
        if self.debug:
            print("Tileset image dimensions: %dx%d" % (image_x, image_y))
            print("Tileset tiles: %dx%d" % (tiles_x, tiles_y))
            tileDictStats = {}
        
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
                    if self.debug:
                        tileDictStats[tile_hash] += 1
                    exit()
                else:
                    self.tileDict[tile_hash] = t
                    if self.debug:
                        tileDictStats[tile_hash] = 1
                        #filename = "aa_image%d.png" % t                        
                        #tile.save(filename)
                        
                t += 1
                        
        self.tileset = img
        print("Tileset loaded: %s with %d tiles" % (self.filename, t))
        
        if self.debug:            
            duplicates = 0
            nones = 0
            ones = 0
            others = 0
            for i in tileDictStats.keys():
                if tileDictStats[i] > 1:
                    duplicates += 1
                elif tileDictStats[i] == 0:
                    nones += 1
                elif tileDictStats[i] == 1:
                    ones += 1
                else:
                    others += 1    
        
            print("Tileset Load: duplicates: %d ones: %d nones: %d others: %d" % (duplicates, ones, nones, others))
            
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
        self.tileset.save("./html/tilesets/%s" % self.filename)
        
    def parseImage(self, img, returnFullMap = True):
        """
        Parses an image. Returns list of tile positions in map.
        """
        tileMap = []
        tileSetChanged = False
        image_x, image_y = img.size
        self.screen_x = image_x
        self.screen_y = image_y
        
        x = 0
        y = 0    
        tiles_x = image_x / self.tile_x
        tiles_y = image_y / self.tile_y
        
        if self.debug:
            print image_x, image_y
            print tiles_x, tiles_y
            tileDictStats = {}        
        
        for y_start in range(tiles_y):
            row  = []
            for x_start in range(tiles_x):
                tile = img.crop((x_start * self.tile_x, y_start * self.tile_y, x_start * self.tile_x + self.tile_x, y_start * self.tile_y + self.tile_y))       
                
                #Use the hash of the tile as a key to ensure that it is unique
                tile_hash = self._imageHash(tile)
                
                if tile_hash in self.tileDict:
                    row.append(self.tileDict[tile_hash])
                    if self.debug:
                        if tile_hash in tileDictStats:
                            tileDictStats[tile_hash] += 1
                        else:
                            tileDictStats[tile_hash] = 1
                else:
                    row.append(-1)
                    self._addTileToSet(tile)
                    tileSetChanged = True
                        
            tileMap.append(row)
        
        if self.debug:            
            duplicates = 0
            nones = 0
            ones = 0
            others = 0
            for i in tileDictStats.keys():
                if tileDictStats[i] > 1:
                    duplicates += 1
                elif tileDictStats[i] == 0:
                    nones += 1
                elif tileDictStats[i] == 1:
                    ones += 1
                else:
                    others += 1    
        
            print("Parse: duplicates: %d ones: %d nones: %d others: %d" % (duplicates, ones, nones, others))
        
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
        Compares newMap to latest fullMap. Returns newMap with '-2' in positions that didn't change.
        """
        
        if len(newMap) != len(self.fullMap):
            #Map may have changed dimensions
            return newMap
        else:
            differenceMap = []
            for i in xrange(len(newMap)):
                rowDif = []
                for j in xrange(len(newMap[0])):
                    if newMap[i][j] == self.fullMap[i][j]:
                        rowDif.append(-2)
                        #differenceMap.append(-2)
                    else:
                        rowDif.append(newMap[i][j])
                        #differenceMap.append(newMap[i])
                differenceMap.append(rowDif)
            
            return differenceMap
        
    def _imageHash(self, img):
        """
        Returns a hash of the image.
        """
        
        #Use md5 since this isn't a secure application and speed is helpful.
        #md5 is 32 characters, img.tostring() for 12x12 is 432 characters
        return hashlib.md5(img.tostring()).hexdigest()
        
    def wampSend(self):
        """
        Converts tileset image to byte string so that it can be send via WAMP.
        """
        img_io = StringIO()
        self.tileset.save(img_io, 'png')
        img_io.seek(0)
        #return img_io
        #can't send binary data directly. Base64 encode first.
        return img_io.getvalue().encode("base64")
        