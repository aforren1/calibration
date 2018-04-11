
import h5py
import matplotlib.pyplot as plt

f = h5py.File('demo.hdf5', 'r')

for i in f: print(i)

dset = f[list(f.keys())[0]]
for i in dset: print(i)

for i in dset.attrs: print(i)

plt.plot(dset['voltages'])
plt.show()

plt.plot(dset['forces'])
plt.show()

f.close()
