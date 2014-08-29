try:
    import Image
except:
    from PIL import Image

import timeit
import numpy
import mmh3


a = numpy.random.rand(32,32,3) * 255
a_img = Image.fromarray(a.astype('uint8')).convert('RGB')
a_array = numpy.array(a_img)

b = numpy.random.rand(32,32,3) * 255
b_img = Image.fromarray(b.astype('uint8')).convert('RGB')
b_array = numpy.array(b_img)

c = numpy.random.rand(1000,1000,3) * 255
c_img = Image.fromarray(c.astype('uint8')).convert('RGB')
c_array = numpy.array(c_img)

setup = '''
from __main__ import a_img, b_img, c_img
def equal(im1, im2):
    return hash(im1.tostring()) == hash(im2.tostring()) 
'''

setup1 = '''
import mmh3
from __main__ import a_img, b_img, c_img
def equal(im1, im2):
    return mmh3.hash(im1.tostring()) == mmh3.hash(im2.tostring()) 
'''

setup2 = '''
try:
    import ImageChops
except:
    from PIL import ImageChops
from __main__ import a_img, b_img, c_img
def equal(im1, im2):
    return ImageChops.difference(im1, im2).getbbox() is None 
'''

setup3 = '''
import numpy
from __main__ import a_img, b_img, c_img
def equal(im1, im2):
    arr1 = numpy.array(im1)
    arr2 = numpy.array(im2)
    return (arr1 == arr2).all 
'''

setup4 = '''
try:
    import Image
except:
    from PIL import Image
from __main__ import a_img, b_img
def equal(im1, im2):
    pixels1 = im1.load()
    pixels2 = im2.load()
    img_x, img_y = im1.size
    for x in range(img_x):
        for y in range(img_y):
            if pixels1[x,y] == pixels2[x,y]:
                pass
            else:
                return False
    return True 
'''

setup5 = '''
try:
    import Image
except:
    from PIL import Image
from __main__ import a_array, b_array, c_array
def equal(im1, im2):
    return (im1 == im2).all() 
'''

setup6 = '''
try:
    import Image
except:
    from PIL import Image
import numpy
from __main__ import a_array, b_array, c_array
def equal(im1, im2):
    return numpy.array_equal(im1, im2) 
'''

setup7 = '''
try:
    import Image
except:
    from PIL import Image
import numpy
from __main__ import a_array, b_array, c_array
import mmh3
def equal(im1, im2):
    return mmh3.hash(im1.tostring()) == mmh3.hash(im2.tostring()) 
'''

print("Different images...")
print("Hash compare: \t\t%f" % min(timeit.Timer('equal(a_img, b_img)', setup).repeat(7, 1000)))
print("mmh3 compare: \t\t%f" % min(timeit.Timer('equal(a_img, b_img)', setup1).repeat(7, 1000)))
print("Difference compare: \t%f" % min(timeit.Timer('equal(a_img, b_img)', setup2).repeat(7, 1000)))
print("Numpy compare: \t\t%f" % min(timeit.Timer('equal(a_img, b_img)', setup3).repeat(7, 1000)))
print("Pixel compare: \t\t%f" % min(timeit.Timer('equal(a_img, b_img)', setup4).repeat(7, 1000)))
print("Numpy array: \t\t%f" % min(timeit.Timer('equal(a_array, b_array)', setup5).repeat(7, 1000)))
print("Numpy array2: \t\t%f" % min(timeit.Timer('equal(a_array, b_array)', setup6).repeat(7, 1000)))
print("Numpy array hash: \t%f" % min(timeit.Timer('equal(a_array, b_array)', setup7).repeat(7, 1000)))
print("\nSame images...")
print("Hash compare: \t\t%f" % min(timeit.Timer('equal(a_img, a_img)', setup).repeat(7, 1000)))
print("mmh3 compare: \t\t%f" % min(timeit.Timer('equal(a_img, a_img)', setup1).repeat(7, 1000)))
print("Difference compare: \t%f" % min(timeit.Timer('equal(a_img, a_img)', setup2).repeat(7, 1000)))
print("Numpy compare: \t\t%f" % min(timeit.Timer('equal(a_img, a_img)', setup3).repeat(7, 1000)))
print("Pixel compare: \t\t%f" % min(timeit.Timer('equal(a_img, a_img)', setup4).repeat(7, 1000)))
print("Numpy array: \t\t%f" % min(timeit.Timer('equal(a_array, a_array)', setup5).repeat(7, 1000)))
print("Numpy array2: \t\t%f" % min(timeit.Timer('equal(a_array, a_array)', setup6).repeat(7, 1000)))
print("Numpy array hash: \t%f" % min(timeit.Timer('equal(a_array, a_array)', setup7).repeat(7, 1000)))
print("\nLarge image...")
print("Hash compare: \t\t%f" % min(timeit.Timer('equal(c_img, c_img)', setup).repeat(3, 100)))
print("mmh3 compare: \t\t%f" % min(timeit.Timer('equal(c_img, c_img)', setup1).repeat(3, 100)))
print("Difference compare: \t%f" % min(timeit.Timer('equal(c_img, c_img)', setup2).repeat(3, 100)))
print("Numpy compare: \t\t%f" % min(timeit.Timer('equal(c_img, c_img)', setup3).repeat(3, 100)))
print("Numpy array: \t\t%f" % min(timeit.Timer('equal(c_array, c_array)', setup5).repeat(3, 100)))
print("Numpy array2: \t\t%f" % min(timeit.Timer('equal(c_array, c_array)', setup6).repeat(3, 100)))
print("Numpy array hash: \t%f" % min(timeit.Timer('equal(c_array, c_array)', setup7).repeat(3, 100)))

'''RESULTS-Desktop
Different images...
Hash compare: 		0.035704
mmh3 compare: 		0.030296
Difference compare: 0.023359
Numpy compare: 		0.046932
Pixel compare: 		0.004296
Numpy array: 		0.012363
Numpy array2: 		0.017940
Numpy array hash: 	0.005040

Same images...
Hash compare: 		0.035535
mmh3 compare: 		0.030228
Difference compare: 0.021173
Numpy compare: 		0.046807
Pixel compare: 		0.456738
Numpy array: 		0.012392
Numpy array2: 		0.017782
Numpy array hash: 	0.004989

Large image...
Hash compare: 		1.959854
mmh3 compare: 		1.428058
Difference compare: 1.566704
Numpy compare: 		3.441948
Numpy array: 		0.599959
Numpy array2: 		0.602276
Numpy array hash: 	0.738304

RESULTS-netbook
Different images...
Hash compare: 		0.151597
mmh3 compare: 		0.135760
Difference compare: 0.099016
Numpy compare: 		0.257428
Pixel compare: 		0.021328
Numpy array: 		0.069450
Numpy array2: 		0.096126
Numpy array hash: 	0.030749

Same images...
Hash compare: 		0.151313
mmh3 compare: 		0.136140
Difference compare: 0.092382
Numpy compare: 		0.258598
Pixel compare: 		2.395519
Numpy array: 		0.072579
Numpy array2: 		0.099269
Numpy array hash: 	0.030374

Large image...
Hash compare: 		7.479523
mmh3 compare: 		5.561126
Difference compare: 4.889773
Numpy compare: 		8.210509
Numpy array: 		3.528336
Numpy array2: 		3.563061
Numpy array hash: 	3.357889

'''