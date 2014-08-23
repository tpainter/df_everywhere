try:
    import Image
    import ImageChops
except:
    from PIL import Image
    from PIL import ImageChops

import timeit
import numpy
import mmh3


a = numpy.random.rand(16,16,3) * 255
a_img = Image.fromarray(a.astype('uint8')).convert('RGB')

b = numpy.random.rand(16,16,3) * 255
b_img = Image.fromarray(a.astype('uint8')).convert('RGB')


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
import ImageChops
from __main__ import a_img, b_img
def equal(im1, im2):
    return ImageChops.difference(im1, im2).getbbox() is None 
'''
    
print("Hash compare: \t\t%f" % min(timeit.Timer('equal(a_img, b_img)', setup).repeat(7, 1000)))
print("mmh3 compare: \t\t%f" % min(timeit.Timer('equal(a_img, b_img)', setup1).repeat(7, 1000)))
print("Direct compare: \t%f" % min(timeit.Timer('equal(a_img, b_img)', setup2).repeat(7, 1000)))