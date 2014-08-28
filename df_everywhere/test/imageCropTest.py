try:
    import Image
except:
    from PIL import Image

import timeit
import numpy

a = numpy.random.rand(160,160,3) * 255
a_img = Image.fromarray(a.astype('uint8')).convert('RGB')
a_array = numpy.array(a_img)

setup = '''
from __main__ import a_img
try:
    import Image
except:
    from PIL import Image
'''

setup1 = '''
from __main__ import a_array

import numpy 
'''

setup2 = '''
from __main__ import a_img
try:
    import Image
except:
    from PIL import Image
import numpy 
'''

setup3 = '''
from __main__ import a_array
try:
    import Image
except:
    from PIL import Image
import numpy 
'''
#image.crop(l,t,r,b)
#array[t,b,l,r)

print("Image crop: \t\t%f" % min(timeit.Timer('a = a_img.crop((32, 80, 48, 96))', setup).repeat(7, 1000)))
print("Array crop: \t\t%f" % min(timeit.Timer('a = a_array[80:96, 32:48]', setup1).repeat(7, 1000)))
print("Image to array: \t%f" % min(timeit.Timer("a_array = numpy.array(a_img)", setup2).repeat(7, 1000)))
print("Array to image: \t%f" % min(timeit.Timer("a_img = Image.fromarray(a_array.astype('uint8')).convert('RGB')", setup3).repeat(7, 1000)))