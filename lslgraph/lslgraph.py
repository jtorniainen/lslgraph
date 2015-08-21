#!/usr/bin/env python3

# Jari Torniainen <jari.torniainen@ttl.fi>,
# Finnish Institute of Occupational Health
# Copyright 2015
#
# This code is released under the MIT license
# http://opensource.org/licenses/mit-license.php
#
# Please see the file LICENSE for details

import pyqtgraph as pg
from pyqtgraph import numpy as np
import pylsl
from PyQt4 import QtGui
import os
import sys


class Grapher():
    """ Grapher object for an LSL stream.

        Grapher object visualizes the input LSL stream using pyqtgraph.
        Graph title is derived from StreamInfo. Buffer size of the displayed
        data and color can be defined when initializing the grapher object.
    """
    def __init__(self, stream, buf_size, col="w", chnames=False, invert=False):
        """ Initializes the grapher.

        Args:
            stream: <pylsl.StreamInfo instance> pointer to a stream
            buf_size: <integer> visualization buffer length in samples
            col: <char> color of the line plot (b,r,g,c,m,y,k and w)
        """

        self.stream = stream
        self.inlet = pylsl.StreamInlet(stream)

        self.buf_size = buf_size
        self.channel_count = self.inlet.channel_count
        self.gbuffer = np.zeros(self.buf_size*self.channel_count)
        self.gtimes = np.zeros(self.buf_size) + pylsl.local_clock()
        self.col = col
        if chnames:
            if self.channel_count == len(chnames):
                self.chnames = chnames
            else:
                print("Channel names vs channel count mismatch, skipping")
        else:
            self.chnames = False

        if invert:
            pg.setConfigOption('background', 'w')
            pg.setConfigOption('foreground', 'k')
        self.fill_buffer()
        self.start_graph()

    def fill_buffer(self):
        """ Fill buffer before starting the grapher. """
        num_of_smp = 0
        while num_of_smp < self.buf_size:
            c, t = self.inlet.pull_chunk(timeout=0.0)
            new_c = []
            new_t = []
            while c:
                new_c += c
                new_t += t
                c, t = self.inlet.pull_chunk(timeout=0.0)

            # add samples to buffer
            if any(new_c):
                # add samples
                num_of_smp += len(new_c)
                data_v = [item for sublist in new_c for item in sublist]
                self.gbuffer = np.roll(self.gbuffer, -len(data_v))
                self.gbuffer[-len(data_v):] = data_v
                # add timestamps
                if new_t:
                    self.gtimes = np.roll(self.gtimes, -len(new_t))
                    self.gtimes[-len(new_t):] = new_t

    def update(self):
        """ Updates the buffer and plot if there are new chunks available. """
        # pull all available chunks
        c, t = self.inlet.pull_chunk(timeout=0.0)
        new_c = []
        new_t = []
        while c:
            new_c += c
            new_t += t
            c, t = self.inlet.pull_chunk(timeout=0.0)

        # add samples to buffer
        if any(new_c):
            # add samples
            data_v = [item for sublist in new_c for item in sublist]
            self.gbuffer = np.roll(self.gbuffer, -len(data_v))
            self.gbuffer[-len(data_v):] = data_v
            # add timestamps
            if new_t:
                self.gtimes = np.roll(self.gtimes, -len(new_t))
                self.gtimes[-len(new_t):] = new_t

        # update graph handles
        if self.gbuffer.any():
            for k in range(0, self.channel_count):
                self.handles[k].setData(self.gtimes,
                                        self.gbuffer[k::self.channel_count])

    def start_graph(self):
        """ Starts graphing. """
        # setup plot title and initialize plots+handles
        title_str = "%s(%s)" % (self.stream.name(), self.stream.type())
        self.win = pg.GraphicsWindow(title=title_str)
        self.plots = []
        self.handles = []

        # add each channel as a (vertical) subplot
        for k in range(0, self.channel_count):
            if self.chnames:
                self.plots.append(self.win.addPlot(title=self.chnames[k]))
            else:
                self.plots.append(self.win.addPlot(title="ch"+str(k)))

            self.handles.append(self.plots[k].plot(pen=self.col))
            if k < self.channel_count - 1:
                self.plots[k].showAxis('bottom', show=False)
                self.win.nextRow()

        # its go time
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(15)  # heuristically derived sleepytime

        # this stuff is for insuring a clean exit
        QtGui.QApplication.instance().exec_()
        os._exit(0)


class XYGrapher():
    """ XY-Grapher object for an LSL stream.

        Grapher object visualizes 2D LSL streams.
        Graph title is derived from StreamInfo. Buffer size of the displayed
        data and color can be defined when initializing the grapher object.
        All streams are presumed to contain X and Y coordinates in the first two
        channels.
    """
    def __init__(self, stream, buf_size, col="w"):
        """ Initializes the grapher.

        Args:
            stream: <pylsl.StreamInfo instance> pointer to a stream
            buf_size: <integer> visualization buffer length in samples
            col: <char> color of the line plot (b,r,g,c,m,y,k and w)
        """

        self.stream = stream
        self.inlet = pylsl.StreamInlet(stream)

        self.buf_size = buf_size

        self.xvals = np.zeros(self.buf_size)
        self.yvals = np.zeros(self.buf_size)

        self.col = col
        self.start_graph()

    def update(self):
        """ Updates the buffer and plot if there are new chunks available. """
        # pull all available chunks
        c, t = self.inlet.pull_chunk(timeout=0.0)
        new_c = []
        new_t = []
        while c:
            new_c += c
            new_t += t
            c, t = self.inlet.pull_chunk(timeout=0.0)

        # add samples to buffer
        if any(new_c):
            data_x = []
            data_y = []
            for smp in new_c:
                data_x.append(smp[0])
                data_y.append(smp[1])
            self.xvals = np.roll(self.xvals, -len(data_x))
            self.yvals = np.roll(self.yvals, -len(data_y))
            self.xvals[-len(data_x):] = data_x
            self.yvals[-len(data_y):] = data_y

        # update graph handles
        self.handle.setData(self.xvals, self.yvals)

    def start_graph(self):
        """ Starts graphing. """
        # setup plot title and initialize plots+handles
        title_str = "%s(%s)" % (self.stream.name(), self.stream.type())
        self.win = pg.GraphicsWindow(title=title_str)
        self.xyplot = self.win.addPlot(title="XY")
        self.handle = self.xyplot.plot(pen=self.col)

        # its go time
        self.timer = pg.QtCore.QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(15)  # heuristically derived sleepytime

        # this stuff is for insuring a clean exit (also kills everything, sorry)
        QtGui.QApplication.instance().exec_()
        os._exit(0)


def start_grapher(stream_name, buffer_size=512):
    streams = pylsl.resolve_byprop('name', stream_name, timeout=5)

    if streams:
        print('Connecting to stream: %s' % streams[0])
        g = Grapher(streams[0], buffer_size)
    else:
        print('No stream by name %s found...' % stream_name)
        list_streams()


def list_streams():
    streams = pylsl.resolve_streams()
    print('Available streams:')
    print('==================')
    for stream in streams:
        print(stream.name())


def run_from_cli(argv):
    if len(argv) == 1:
        list_streams()
    elif len(argv) == 2:
        start_grapher(stream_name=argv[1])
    elif len(argv) == 3:
        start_grapher(stream_name=argv[1], buffer_size=argv[2])
    else:
        print('lslgrapher takes max 2 arguments (stream_name and buffer_size)')

if __name__ == "__main__":
    run_from_cli(sys.argv)
