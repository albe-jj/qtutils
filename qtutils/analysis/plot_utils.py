# -*- coding: utf-8 -*-
# @Author: atosato
# @Date:   2021-04-10 11:23:37
# @Last Modified by:   Alberto Tosato
# @Last Modified time: 2021-07-01 08:50:00

import matplotlib.pyplot as plt
import io
import win32clipboard
from PIL import Image
import matplotlib as mpl

def __init__():
    # mpl.rcParams['figure.dpi'] = 100
    mpl.rcParams['xtick.major.size'] = 7
    mpl.rcParams['xtick.major.width'] = 1.5
    mpl.rcParams['ytick.major.size'] = 7
    mpl.rcParams['ytick.major.width'] = 1.5
    mpl.rcParams['xtick.minor.size'] = 4
    mpl.rcParams['xtick.minor.width'] = 1.5
    mpl.rcParams['ytick.minor.size'] = 4
    mpl.rcParams['ytick.minor.width'] = 1.5
    mpl.rcParams['font.family'] = 'Arial'
    mpl.rcParams['text.usetex'] = False
    # mpl.rc('pdf', fonttype = 42)
    mpl.rcParams['axes.linewidth'] = 2.0
    mpl.rcParams['lines.linewidth'] = 2.5
    # mpl.rcParams["legend.numpoints"] = 1.0
    # mpl.rcParams["legend.frameon"] = False
    mpl.rcParams['font.size'] = 17
    # mpl.rcParams['mathtext.rm'] = 'Arial'
    mpl.rcParams['savefig.format'] = 'svg'

    mpl.rcParams['pdf.fonttype'] = 42 #for illustrator to get editable text (Type 2/TrueType fonts)
    mpl.rcParams['ps.fonttype'] = 42
    # mpl.rcParams['svg.fonttype']='none' #'path'

    mpl.rcParams['savefig.bbox'] = 'tight' #to avoid clipping mask cropping the axis label
    # mpl.rcParams['mathtext.fontset'] = 'cm' #this gives you nice font But! non compatible with illustrator

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


def to_clipboard(fig=None, format='jpeg'):
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


