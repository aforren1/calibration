% just noise, but example of extracting data
hinfo = h5info('demo.hdf5');

h5disp('demo.hdf5', hinfo.Groups(2).Name)

data = h5read('demo.hdf5', strcat(hinfo.Groups(2).Name, '/forces'));

plot(data')

data2 = h5read('demo.hdf5', strcat(hinfo.Groups(2).Name, '/voltages'));

plot(data2')
