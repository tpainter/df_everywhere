"""
When run directly, it finds Dwarf Fortress window
"""  

def get_windows_bytitle(title_text, exact = False):    
    """
    Gets details of window position by title text. [Windows Only]
    """
    #Windows only - get screenshot of window instead of whole screen
    # from: https://stackoverflow.com/questions/3260559/how-to-get-a-window-or-fullscreen-screenshot-in-python-3k-without-pil
    
    import win32gui
    
    def _window_callback(hwnd, all_windows):
        all_windows.append((hwnd, win32gui.GetWindowText(hwnd)))
    windows = []
    win32gui.EnumWindows(_window_callback, windows)
    if exact:
        return [hwnd for hwnd, title in windows if title_text == title]
    else:
        return [hwnd for hwnd, title in windows if title_text in title]
        
def screenshot(hwnd = None, debug = False):
    """
    Takes a screenshot of only the area given by the window.
    """
    import ImageGrab
    import win32gui
    from time import sleep
    
    if not hwnd:
        print("Unable to get window. Exiting.")
        exit()
    
    win32gui.SetForegroundWindow(hwnd)
    bbox_total = win32gui.GetWindowRect(hwnd)
    bbox_client = win32gui.GetClientRect(hwnd) #window without the title bar, but in 'local' window coordinates
    #bbox points are [start_x, start_y, stop_x, stop_y]
    #added extra number to make it work on my system... need to look into this - seems to be a 4px border
    diff_x = (bbox_total[2] - bbox_total[0]) - bbox_client[2] - 4
    diff_y = (bbox_total[3] - bbox_total[1]) - bbox_client[3] - 4
    bbox = [bbox_total[0] + diff_x, bbox_total[1] + diff_y, bbox_total[0] + diff_x + bbox_client[2], bbox_total[1] + diff_y + bbox_client[3]] 
    sleep(.2) #wait for window to be brought to front
    img = ImageGrab.grab(bbox)
    
    if debug:
        print("Whole window:")
        print(bbox_total)
        print("Client area:")
        print(bbox_client)
        print("Modified box:")
        print(bbox)
    
        filename = "aa_image.png"
        img.save(filename)
        #import webbrowser
        #webbrowser.open(filename)
    
    return img
    
class Tileset:
    """
    Holds details for the tileset.
    """
    
    def __init__(self, filename, tile_x, tile_y, debug = False):
        import Image
        
        self.tile_x = tile_x
        self.tile_y = tile_y
        if filename is None:
            #fake a filename
            self.filename = "%dx%d-%05d.png" % (self.tile_x, self.tile_y, 0)
            img = None
        else:
            self.filename = filename
            img = Image.open(filename)
            
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
        import hashlib
        
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
        import Image
        
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
                
        maxTiles_x = 32
        
        #Find if a new row needs to be created in the image
        if self.tileCount + 1 > maxTiles_x * tiles_y:
            #need to add another row to tileset image
            newTileSet = Image.new(self.tileset.mode, (maxTiles_x * self.tile_x, tiles_y * self.tile_y + tile_y), "white")
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
        
        #write new image file to disk
        filename = "%dx%d-%05d.png" % (self.tile_x, self.tile_y, newTilePosition)
        print("Saving new tileset image: %s" % filename)
        newTileSet.save(filename)
        
        #reload new tileset
        self.tileCount += 1
        self.filename = filename
        self._loadSet(newTileSet)
        
    def parseImage(self, img):
        """
        Parses an image. Returns list of tile positions in map.
        """
        tileMap = []
        image_x, image_y = img.size
        
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
                
                #Use the hash of the tile as a key to insure that it is unique
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
            
        return tileMap
        
    def _imageHash(self, img):
        """
        Returns a hash of the image.
        """
        import hashlib
        
        #Use md5 since this isn't a secure application and speed is helpful.
        #md5 is 32 characters, img.tostring() for 12x12 is 432 characters
        return hashlib.md5(img.tostring()).hexdigest()
        

def trim(im, debug = False):
    """ 
    Automatically crops a solid color border off of the image.
    """
    import Image
    import ImageChops
        
    bg = Image.new(im.mode, im.size, "black")
    diff = ImageChops.difference(im, bg)
    bbox = diff.getbbox()
    if debug:
        print("Original size:")
        print(im.size)
        print("bbox:")
        print(bbox)
    if bbox:
        return im.crop(bbox)

def findTileSize(img):
    """
    Tries to automatically find the tile size
    """
    
    #start with 16x16 tile
    initial_guess = 16
    
    tile_x = initial_guess
    tile_y = initial_guess
    px, py = img.size
    
    #The tiles should be square
    for x in range(initial_guess, 0, -1):
        if (px % x == 0) and (py % x == 0):
            tile_x = x
            tile_y = x
            break
        else:
            continue
    
    print("Tile size found: %dx%d" % (tile_x, tile_y))
    if tile_x < 7:
        print("Error: Tile size too small")
        exit()
    
    return tile_x, tile_y
    
def findLocalImg(x, y):
    """
    Try to find the best local tileset based on tile dimensions
    """
    import os
    
    fileList = []
    filePrefix = "%02dx%02d-" % (x, y)
    
    for file in os.listdir("."):
        if file.endswith(".png"):
            if file.startswith(filePrefix):
                fileList.append((int(file[6:11]), file))
    
    #sort by number of tiles in tileset
    fileList_sorted = sorted(fileList, key=lambda tup: tup[0], reverse = True)
    
    if fileList == []:
        print("Didn't find appropriate tileset image. Continuing")
        return None
    else:
        print("Found tileset image: %s" % fileList_sorted[0][1])
        return fileList_sorted[0][1]
    
    
if __name__ == "__main__":
    from time import sleep
    
    from twisted.internet import reactor
    from twisted.internet.endpoints import serverFromString
    
    ## create a WAMP router factory
    from autobahn.wamp.router import RouterFactory
    router_factory = RouterFactory()

    ## create a WAMP router session factory
    from autobahn.twisted.wamp import RouterSessionFactory
    session_factory = RouterSessionFactory(router_factory)

    ## create a WAMP-over-WebSocket transport server factory
    from autobahn.twisted.websocket import WampWebSocketServerFactory
    transport_factory = WampWebSocketServerFactory(session_factory, "ws://localhost:7081/ws", debug = False)
    transport_factory.setProtocolOptions(failByDrop = False)

    ## Start websocket server
    server = serverFromString(reactor, "tcp:7081")
    server.listen(transport_factory)
    
    #Change screenshot method based on operating system
    from sys import platform as _platform
    if _platform == "linux" or _platform == "linux2":
        print("Linux unsuported at this time. Exiting..."
        exit()
    elif _platform == "darwin":
        print("OS X unsuported at this time. Exiting..."
        exit()
    elif _platform == "win32":
        # Windows..
        window_handle = get_windows_bytitle("Dwarf Fortress")
        shot = screenshot(window_handle[0], debug = False)
    else:
        print("Unsuported platform detected. Exiting..."
        exit()
    
    shot = trim(shot, debug = False)
    tile_x, tile_y = findTileSize(shot)
    local_file = findLocalImg(tile_x, tile_y)
    tset = Tileset(local_file, tile_x, tile_y, debug = False)
        
    tickMax = 40
    
    def keepGoing(tick):
        shot = screenshot(window_handle[0], debug = False)
        shot = trim(shot, debug = False)
        tileMap = tset.parseImage(shot)
        print("tileMap created.")
        
        if (tick < tickMax):
            reactor.callLater(.2, keepGoing, tick + 1)
        else:
            reactor.stop()
        
    reactor.callWhenRunning(keepGoing, 0)
    reactor.run()
    