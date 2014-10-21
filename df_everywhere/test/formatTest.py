import sys

for i in xrange(2):
    sys.stdout.write("A{0:<{1}}\r".format('text', 50))
    sys.stdout.write('11111111112222222222333333333344444444445555555555666666666677777777778888888888')
    sys.stdout.write("A{0:<{1}}\n".format('text', 50))