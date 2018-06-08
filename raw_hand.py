import struct
import numpy as np
import hid
from toon.input.base_input import BaseInput
from ctypes import c_double, c_uint


class Hand(BaseInput):
    """Hand Articulation Neuro-Training Device (HAND)."""

    @staticmethod
    def samp_freq(**kwargs):
        return kwargs.get('sampling_frequency', 1000)

    @staticmethod
    def data_shapes(**kwargs):
        return [[15], [20], [15]]

    @staticmethod
    def data_types(**kwargs):
        return [c_double, c_uint, c_double]

    def __init__(self, **kwargs):
        super(Hand, self).__init__(**kwargs)
        self._sqrt2 = np.sqrt(2)
        self._device = None
        self._data_buffer = np.full(15, np.nan) # forces (~-1, 1??)
        self._raw_buffer = np.full(20, np.nan) # normalized "raw" voltage (0, 1)
        self._calib_buffer = np.full(15, np.nan) # 
        self.calib_matrix = np.eye(3) # np.array([[1., 2., 3.], [4, 5, 6], [7, 8, 9]])

    def __enter__(self):
        self._device = hid.device()
        dev_path = next((dev for dev in hid.enumerate() if dev['vendor_id'] == 0x16c0 and dev['interface_number'] == 0), None)['path']
        self._device.open_path(dev_path)
        return self

    def __exit__(self, *args):
        self._device.close()

    def read(self):
        data = self._device.read(46)
        time = self.clock()
        if data:
            data = struct.unpack('>Lh' + 'H'*20, bytearray(data)) # Timestamp, deviation, and 20 unsigned ints
            data = np.array(data, dtype='uint')
            np.copyto(self._raw_buffer, data[2:])
            data = data.astype(c_double)
            data[0] /= 1000.0
            data[2:] /= 65535.0
            self._data_buffer[0::3] = (data[2::4] - data[3::4])/self._sqrt2 # x
            self._data_buffer[1::3] = (data[2::4] + data[3::4])/self._sqrt2 # y
            self._data_buffer[2::3] = data[4::4] + data[5::4]  # z
            # apply calibration
            n = 0
            # for each finger, apply calibration
            for i in range(5):
                self._calib_buffer[0+n:3+n] = np.dot(self.calib_matrix, self._data_buffer[0+n:3+n])
                n += 3

            return time, [self._data_buffer, self._raw_buffer, self._calib_buffer]