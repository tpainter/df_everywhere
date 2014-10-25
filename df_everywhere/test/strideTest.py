try:
    import Image
except:
    from PIL import Image

import numpy

tile_x = 12
tile_y = 12
image_x = tile_x * 1
image_y = tile_y * 1

a = numpy.random.rand(image_x,image_y,3) * 255
a_img = Image.fromarray(a.astype('uint8')).convert('RGB')
a_img.save('strideTest.png')
a_img = Image.open('strideTest.png')
a_array = numpy.array(a_img)

sz = a_array.itemsize
h,w = image_y, image_x
bh,bw = tile_y, tile_x
shape = numpy.array([h/bh, w/bw, bh, bw, 3])
strides = sz*numpy.array([w*bh*3,bw*3,w*3,3,1])

blocks=numpy.lib.stride_tricks.as_strided(a_array, shape=shape, strides=strides)

i=0
for block in blocks:
    for lock in block:
        img = Image.fromarray(lock.astype('uint8')).convert('RGB')
        img.save('%d.png' % i)
        i += 1