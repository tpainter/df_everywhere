try:
    import Image
except:
    from PIL import Image

import timeit
import numpy
import mmh3


a = numpy.random.rand(32,32,3) * 255
a_img = Image.fromarray(a.astype('uint8')).convert('RGB')

b = numpy.random.rand(32,32,3) * 255
b_img = Image.fromarray(b.astype('uint8')).convert('RGB')


setup = '''
from __main__ import a_img, b_img
def equal(im1, im2):
    return hash(im1.tostring()) == hash(im2.tostring()) 
'''

setup1 = '''
import mmh3
from __main__ import a_img, b_img
def equal(im1, im2):
    return mmh3.hash(im1.tostring()) == mmh3.hash(im2.tostring()) 
'''

setup2 = '''
try:
    import ImageChops
except:
    from PIL import ImageChops
from __main__ import a_img, b_img
def equal(im1, im2):
    return ImageChops.difference(im1, im2).getbbox() is None 
'''

setup3 = '''
import numpy
from __main__ import a_img, b_img
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

print("Different images...")
print("Hash compare: \t\t%f" % min(timeit.Timer('equal(a_img, b_img)', setup).repeat(7, 1000)))
print("mmh3 compare: \t\t%f" % min(timeit.Timer('equal(a_img, b_img)', setup1).repeat(7, 1000)))
print("Difference compare: \t%f" % min(timeit.Timer('equal(a_img, b_img)', setup2).repeat(7, 1000)))
print("Numpy compare: \t\t%f" % min(timeit.Timer('equal(a_img, b_img)', setup3).repeat(7, 1000)))
print("Pixel compare: \t\t%f" % min(timeit.Timer('equal(a_img, b_img)', setup4).repeat(7, 1000)))
print("\nSame images...")
print("Hash compare: \t\t%f" % min(timeit.Timer('equal(a_img, a_img)', setup).repeat(7, 1000)))
print("mmh3 compare: \t\t%f" % min(timeit.Timer('equal(a_img, a_img)', setup1).repeat(7, 1000)))
print("Difference compare: \t%f" % min(timeit.Timer('equal(a_img, a_img)', setup2).repeat(7, 1000)))
print("Numpy compare: \t\t%f" % min(timeit.Timer('equal(a_img, a_img)', setup3).repeat(7, 1000)))
print("Pixel compare: \t\t%f" % min(timeit.Timer('equal(a_img, a_img)', setup4).repeat(7, 1000)))

'''RESULTS

'''