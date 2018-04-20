import argparse
import ctypes
import datetime
import sys

import h5py
import numpy as np
import pyqtgraph as pg
from pyqtgraph.dockarea import Dock, DockArea
from pyqtgraph.Qt import QtCore, QtGui

from toon.input import MultiprocessInput as MpI
from toon.input.fake import FakeInput
from raw_hand import Hand
# from toon.input.hand import Hand


np.set_printoptions(precision=4, linewidth=150, suppress=True)

# base window, etc.
app = QtGui.QApplication([])
win = QtGui.QMainWindow()

area = DockArea()
win.setCentralWidget(area)
win.resize(1200, 400)
win.setWindowTitle('Calibration')

d0 = Dock('Voltages', size=(1000, 600))
d1 = Dock('Forces', size=(1000, 600))
d2 = Dock('Settings', size=(250, 600))
area.addDock(d0, 'left')
area.addDock(d1, 'left')
area.addDock(d2, 'right')

area.moveDock(d0, 'above', d1)

# "raw" voltages
raw_plotwidget = pg.GraphicsLayoutWidget()
raw_curves = list()

raw_plot = raw_plotwidget.addPlot()
raw_plot.setClipToView(True)
raw_plot.setRange(yRange=[0, 3.3])
data = np.random.normal(size=20)
for j in range(4):
    raw_curves.append(raw_plot.plot(data, pen=pg.mkPen(
                      color=pg.intColor(j, hues=5, alpha=255, width=3))))

d0.addWidget(raw_plotwidget)

# "forces"
force_plotwidget = pg.GraphicsLayoutWidget()
force_curves = list()

force_plot = force_plotwidget.addPlot()
force_plot.setClipToView(True)
force_plot.setRange(yRange=[-1.5, 1.5])
for j in range(3):
    force_curves.append(force_plot.plot(data, pen=pg.mkPen(
                        color=pg.intColor(j, hues=5, alpha=255, width=3))))

d1.addWidget(force_plotwidget)


logging = False
log_file_name = ''

def stop_logging():
    # write data to file, clean up
    global logging, log_file_name, log_settings
    global logged_force_data, logged_raw_data
    logging = False
    logging_toggler.setText('Log for N seconds')

    with h5py.File(log_file_name, 'a') as f:
        dt = log_settings['datetime']
        group = f.create_group(dt)
        group.attrs['datetime'] = dt
        group.attrs['finger'] = log_settings['finger']
        group.attrs['duration'] = log_settings['duration']
        group.attrs['angle1'] = log_settings['angle1']
        group.attrs['angle2'] = log_settings['angle2']
        group.attrs['weight'] = log_settings['weight']
        group.create_dataset('voltages', data=logged_raw_data)
        group.create_dataset('forces', data=logged_force_data)
    # reset things
    log_settings = dict.fromkeys(log_settings, None)
    logged_force_data = None
    logged_raw_data = None


timer = QtCore.QTimer()
log_duration = 2
def log_and_print():
    global logging, log_file_name, log_duration, log_settings
    # ignore if we're already logging
    if logging:
        print('already logging.')
        return
    # validate fields
    try:
        dur = record_dur.text()
        if dur == '':
            dur = '2'
        float(dur)
        float(record_angle1.text())
        float(record_angle2.text())
        float(record_weight.text())
    except:
        print('Something is wrong with one of the fields...')
        return
    logging = True
    log_file_name = filename_edit.text() + '.hdf5'
    log_duration = float(dur)
    logging_toggler.setText('Now logging for %s seconds' % dur)
    timer.singleShot(int(log_duration * 1000), stop_logging)


setwidget = pg.LayoutWidget()
d2.addWidget(setwidget)

# base filename setter
filename_info = QtGui.QLabel()
filename_info.setText('Base file:')
filename_edit = QtGui.QLineEdit()
filename_info2 = QtGui.QLabel()
filename_info2.setText('.hdf5')
setwidget.addWidget(filename_info, row=0, col=0)
setwidget.addWidget(filename_edit, row=0, col=1)
setwidget.addWidget(filename_info2, row=0, col=2)

# finger selection (sets an offset)
finger_select = QtGui.QComboBox()
finger_select.addItems(['thumb', 'index', 'middle', 'ring', 'pinky'])
finger_select.setCurrentIndex(0) # defines the offset
setwidget.addWidget(finger_select, row=5, col=3)
finger_info = QtGui.QLabel()
finger_info.setText('Finger:')
setwidget.addWidget(finger_info, row=5, col=2)

# set angles, weights
angle1_info = QtGui.QLabel()
angle1_info.setText('Angle1:')
record_angle1 = QtGui.QLineEdit()
angle2_info = QtGui.QLabel()
angle2_info.setText('Angle2:')
record_angle2 = QtGui.QLineEdit()
weight_info = QtGui.QLabel()
weight_info.setText('Weight:')
record_weight = QtGui.QLineEdit()

setwidget.addWidget(angle1_info, row=4, col=0)
setwidget.addWidget(record_angle1, row=4, col=1)
setwidget.addWidget(angle2_info, row=4, col=2)
setwidget.addWidget(record_angle2, row=4, col=3)
setwidget.addWidget(weight_info, row=5, col=0)
setwidget.addWidget(record_weight, row=5, col=1)


# toggle logging
logging_toggler = QtGui.QPushButton('Log for N seconds')
logging_toggler.clicked.connect(log_and_print)
setwidget.addWidget(logging_toggler, row=1, col=0)

# set the log duration
record_for_info = QtGui.QLabel()
record_for_info.setText('Duration of log (s):')
setwidget.addWidget(record_for_info, row=2, col=0)
record_dur = QtGui.QLineEdit()
setwidget.addWidget(record_dur, row=2, col=1)

current_raw_data_view = None
current_force_data_view = None
logged_raw_data = None
logged_force_data = None
log_settings = {'finger': None,
                'datetime': None,
                'duration': None,
                'angle1': None,
                'angle2': None,
                'weight': None}

def update():
    global current_raw_data_view, current_force_data_view
    global logged_raw_data, logged_force_data, logging, log_file_name, log_settings
    global log_duration
    ts, data = dev.read()
    if ts is None:
        return
    if current_raw_data_view is None:
        current_raw_data_view = data[1]
        current_force_data_view = data[0]
    elif current_raw_data_view.shape[0] < 1000:
        current_raw_data_view = np.vstack((current_raw_data_view, data[1]))
        current_force_data_view = np.vstack((current_force_data_view, data[0]))
    else:
        current_raw_data_view = np.roll(current_raw_data_view, -data[1].shape[0], axis=0)
        current_raw_data_view[-data[1].shape[0]:, :] = data[1]
        current_force_data_view = np.roll(current_force_data_view, -data[0].shape[0], axis=0)
        current_force_data_view[-data[0].shape[0]:, :] = data[0]
    current_index = finger_select.currentIndex()
    if logging: # update for hdf5
        if logged_raw_data is None:
            log_settings['finger'] = current_index
            log_settings['datetime'] = datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')
            log_settings['duration'] = log_duration
            log_settings['angle1'] = float(record_angle1.text())
            log_settings['angle2'] = float(record_angle2.text())
            log_settings['weight'] = float(record_weight.text())
            logged_raw_data = data[1][:, 4*current_index:4*current_index+4]
            logged_force_data = data[0][:, 3*current_index:3*current_index+3]
        else:
            logged_raw_data = np.vstack((logged_raw_data, data[1][:, 4*current_index:4*current_index+4]))
            logged_force_data = np.vstack((logged_force_data, data[0][:, 3*current_index:3*current_index+3]))
    for counter, c in enumerate(raw_curves):
        c.setData(y=current_raw_data_view[:, 4*current_index + counter]/65535.0 * 3.3)
    for counter, c in enumerate(force_curves):
        c.setData(y=current_force_data_view[:, 3*current_index + counter])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--demo', help='Demo mode or not', dest='demo', action='store_true')
    parser.set_defaults(demo=False)
    args = parser.parse_args()
    if args.demo:
        device = MpI(FakeInput, sampling_frequency=1000,
                     data_shape=[[15], [20]], 
                     data_type=[ctypes.c_double, ctypes.c_double])
    else:
        device = MpI(Hand)

    with device as dev:
        win.show()
        timer = pg.QtCore.QTimer()
        timer.timeout.connect(update)
        timer.start(17)
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()
