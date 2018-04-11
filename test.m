
hinfo = h5info('test.hdf5');

dset = h5read(hinfo.Groups.Name.Datasets.Name(0));

h5disp('test.hdf5', hinfo.Groups.Name)

data = h5read('test.hdf5', strcat(hinfo.Groups.Name, '/forces'));

plot(data')

data2 = h5read('test.hdf5', strcat(hinfo.Groups.Name, '/voltages'));
