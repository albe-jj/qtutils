# -*- coding: utf-8 -*-
# @Author: atosato
# @Date:   2021-04-10 11:23:37
# @Last Modified by:   atosato
# @Last Modified time: 2021-04-10 11:24:20

import matplotlib.pyplot as plt
import io
import win32clipboard
from PIL import Image

def __init__():
    # plt.rcParams['figure.dpi'] = 100
    plt.rcParams['xtick.major.size'] = 7
    plt.rcParams['xtick.major.width'] = 1.5
    plt.rcParams['ytick.major.size'] = 7
    plt.rcParams['ytick.major.width'] = 1.5
    plt.rcParams['xtick.minor.size'] = 4
    plt.rcParams['xtick.minor.width'] = 1.5
    plt.rcParams['ytick.minor.size'] = 4
    plt.rcParams['ytick.minor.width'] = 1.5
    plt.rcParams['font.family'] = 'Arial'
    plt.rcParams['text.usetex'] = False
    # plt.rc('pdf', fonttype = 42)
    plt.rcParams['axes.linewidth'] = 2.0
    plt.rcParams['lines.linewidth'] = 2.5
    # plt.rcParams["legend.numpoints"] = 1.0
    # plt.rcParams["legend.frameon"] = False
    plt.rcParams['font.size'] = 17
    plt.rcParams['mathtext.rm'] = 'Arial'
    plt.rcParams['savefig.format'] = 'svg'

__init__()

def two_axis(figsize=[13,4]):
    fig,(ax1,ax2) = plt.subplots(1,2,figsize=figsize)
    plt.subplots_adjust(left=0.1,
                    bottom=0.1, 
                    right=0.9, 
                    top=0.9, 
                    wspace=0.4, 
                    hspace=0.4)
    return ax1, ax2


def to_clipboard(fig=None, format='png'):
    def _send_to_clipboard(clip_type, data):
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(clip_type, data)
        win32clipboard.CloseClipboard()
    if not fig:
        fig = plt.gcf()

    fig.tight_layout()
    buf = io.BytesIO()
    fig.savefig(buf, format=format)

    format_map = {'png': 'PNG',
                  'svg': 'image/svg+xml',
                  'jpg': 'JFIF',
                  'jpeg': 'JFIF',
                  }

    data = buf.getvalue()
    format_id = win32clipboard.RegisterClipboardFormat(format_map[format])
    
    if format in ['jpeg', 'jpg']: #to allow pasting outside powerpoint
        image = Image.open(buf)
        buf = io.BytesIO()
        image.convert("RGB").save(buf, "BMP")
        data = buf.getvalue()[14:]
        format_id = win32clipboard.CF_DIB

    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(format_id, data)
    win32clipboard.CloseClipboard()

    # from PIL import ImageGrab
    # im = ImageGrab.grabclipboard()


