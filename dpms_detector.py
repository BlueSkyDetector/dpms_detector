#!/usr/bin/env python

import ctypes
import struct
from logging import getLogger, StreamHandler, Formatter, WARN, INFO, DEBUG

logger = getLogger(__name__)
formatter = Formatter('%(asctime)s - %(levelname)s: %(message)s',
                      '%Y/%m/%d %H:%M:%S')
handler = StreamHandler()
handler.setFormatter(formatter)
handler.setLevel(INFO)
logger.setLevel(INFO)
logger.addHandler(handler)
logger.propagate = False

ctypes.cdll.LoadLibrary('libXext.so')
libXext = ctypes.CDLL('libXext.so')

DPMSNONE = -2
DPMSFAIL = -1
DPMSModeOn = 0
DPMSModeStandby = 1
DPMSModeSuspend = 2
DPMSModeOff = 3


def get_DPMS_state(display_name_in_byte_string=b':0'):
    state = DPMSFAIL
    if not isinstance(display_name_in_byte_string, bytes):
        raise TypeError
    display_name = ctypes.c_char_p()
    display_name.value = display_name_in_byte_string
    libXext.XOpenDisplay.restype = ctypes.c_void_p
    display = ctypes.c_void_p(libXext.XOpenDisplay(display_name))
    dummy1_i_p = ctypes.create_string_buffer(8)
    dummy2_i_p = ctypes.create_string_buffer(8)
    if display.value:
        if libXext.DPMSQueryExtension(display, dummy1_i_p, dummy2_i_p)\
           and libXext.DPMSCapable(display):
            onoff_p = ctypes.create_string_buffer(1)
            state_p = ctypes.create_string_buffer(2)
            if libXext.DPMSInfo(display, state_p, onoff_p):
                onoff = struct.unpack('B', onoff_p.raw)[0]
                if onoff:
                    state = struct.unpack('H', state_p.raw)[0]
        libXext.XCloseDisplay(display)
    return state


def main():
    import time
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--display',
                        action='store',
                        required=True,
                        help='Specify display name in format \':0.0\'')
    args = parser.parse_args()
    logger.info('\'%s\' started' % __file__)
    display_name_in_byte_string = args.display.encode('ascii')
    dpms_state = DPMSNONE
    while True:
        new_dpms_state = get_DPMS_state(display_name_in_byte_string)
        if dpms_state != new_dpms_state:
            dpms_state = new_dpms_state
            if dpms_state == DPMSFAIL:
                logger.info('DPMS state is detected as [DPMSFAIL]')
            elif dpms_state == DPMSModeOn:
                logger.info('DPMS state is detected as [DPMSModeOn]')
            elif dpms_state == DPMSModeStandby:
                logger.info('DPMS state is detected as [DPMSModeStandby]')
            elif dpms_state == DPMSModeSuspend:
                logger.info('DPMS state is detected as [DPMSModeSuspend]')
            elif dpms_state == DPMSModeOff:
                logger.info('DPMS state is detected as [DPMSModeOff]')
        time.sleep(1)


if __name__ == '__main__':
    main()
