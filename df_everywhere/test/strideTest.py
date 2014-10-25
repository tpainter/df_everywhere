try:
    import Image
except:
    from PIL import Image

import numpy

tile_x = 2
tile_y = 2
image_x = 4
image_y = 4

#a = numpy.random.rand(image_x,image_y,3) * 255
#a_img = Image.fromarray(a.astype('uint8')).convert('RGB')
#a_img.save('strideTest.png')
a_img = Image.open('strideTest.png')
a_array = numpy.array(a_img)

sz = a_array.itemsize
h,w = image_y, image_x
bh,bw = tile_y, tile_x
shape = numpy.array([h/bh, w/bw, bh, bw, 3])
strides = sz*numpy.array([w*bh*3,bw*3,w*3,3,1])

blocks=numpy.lib.stride_tricks.as_strided(a_array, shape=shape, strides=strides)

print(a_array)
print('----------------------------------')
print(blocks)
print('----------------------------------')