#!/usr/bin/env python3

# Jari Torniainen <jari.torniainen@ttl.fi>,
# Finnish Institute of Occupational Health
# Copyright 2015
#
# This code is released under the MIT license
# http://opensource.org/licenses/mit-license.php
#
# Please see the file LICENSE for details

import pylsl
import time
import colorama


def scan_ui():
    streams, status_connection = scan()
    header = '{}{}{}{}{}{}{}{}'.format('Name'.ljust(10),
                                       'Type'.ljust(10),
                                       'Hostname'.ljust(10),
                                       'Channels'.ljust(10),
                                       'Fs'.ljust(10),
                                       'Status'.ljust(10),
                                       'Source'.ljust(10),
                                       'UID'.ljust(10))

    print(colorama.Fore.CYAN + header + colorama.Style.RESET_ALL)

    for stream, status in zip(streams, status_connection):
        stream_name = stream.name()
        stream_type = stream.type()
        stream_host = stream.hostname()
        stream_srate = str(stream.nominal_srate()) + 'Hz'
        stream_channels = str(stream.channel_count())
        stream_source_id = stream.source_id()
        stream_uid = stream.uid()

        if status:
            stream_status = 'OK'
        else:
            stream_status = 'FAIL'

        print('{}{}{}{}{}{}{}{}'.format(stream_name.ljust(10),
                                        stream_type.ljust(10),
                                        stream_host.ljust(10),
                                        stream_channels.ljust(10),
                                        stream_srate.ljust(10),
                                        stream_status.ljust(10),
                                        stream_source_id.ljust(10),
                                        stream_uid.ljust(10)))


def get_stream_info_string(stream):
    """ Returns (compact) string with stream information. """
    name = stream.name()
    hostname = stream.hostname()
    source_id = stream.source_id()
    uid = stream.uid()
    return '{}@{}[{}][{}]'.format(name, hostname, source_id, uid)


def peek(stream_name):
    """ Connects to the specified stream and checks if it outputs samples """
    # TODO This functionality does not work yet
    stream = pylsl.resolve_byprop('name', stream_name)[0]
    if stream:
        inlet = pylsl.StreamInlet(stream)
        time.sleep(3)
        try:
            while True:
                sample, time_stamp = inlet.pull_sample(timeout=0)
                print('[%d] %s' % (time_stamp, sample))
        except KeyboardInterrupt:
            print('Terminating peek')


def scan():
    """ Scan through all visible streams and check if they can be connected to
    """
    colorama.init()

    streams = pylsl.resolve_streams()

    connection_ok = []
    for stream in streams:
        # Check if stream can be connected to
        inlet = pylsl.StreamInlet(stream)
        if inlet:
            connection_ok.append(True)
        else:
            connection_ok.append(False)
    return streams, connection_ok

if __name__ == '__main__':
    scan_ui()
