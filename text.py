import os

print(__file__)
print(os.path.basename(__file__))
print(os.path.splitext(__file__))
print('.'.join([os.path.splitext(__file__)[0], 'txt']))