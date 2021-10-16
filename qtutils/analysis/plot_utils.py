# -*- coding: utf-8 -*-
# @Author: atosato
# @Date:   2021-04-10 11:23:37
# @Last Modified by:   Alberto Tosato
# @Last Modified time: 2021-07-16 14:04:55

import matplotlib.pyplot as plt
import io
import win32clipboard
from PIL import Image
import matplotlib as mpl
from matplotlib.gridspec import GridSpec
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)
from mpl_toolkits.axes_grid1.axes_divider import make_axes_locatable
from .mpl_styles import article_style, quick_style
from matplotlib.colors import LinearSegmentedColormap

import numpy as np

quick_style()
inch = 1/2.54 # inch/cm

def two_axis(figsize=[13,4]):
    fig,(ax1,ax2) = plt.subplots(1,2,figsize=figsize)
    plt.subplots_adjust(left=0.1,
                    bottom=0.1, 
                    right=0.9, 
                    top=0.9, 
                    wspace=0.4, 
                    hspace=0.4)
    return ax1, ax2


def to_clipboard(fig=None, format='jpeg', tight=True):
    def _send_to_clipboard(clip_type, data):
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(clip_type, data)
        win32clipboard.CloseClipboard()
    if not fig:
        fig = plt.gcf()
    if tight:
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

def display_cmap(cmap):
    plt.imshow(np.linspace(0, 100, 256)[None, :],  aspect=25,    interpolation='nearest', cmap=cmap) 
    plt.axis('off')


def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=-1):
    """
    Usage example:
    cmap_t = truncate_colormap(plt.get_cmap(cmap_str), minval=0.1, maxval=0.9)
    """
    if n == -1:
        n = cmap.N
    new_cmap = LinearSegmentedColormap.from_list(
         'trunc({name},{a:.2f},{b:.2f})'.format(name=cmap.name, a=minval, b=maxval),
         cmap(np.linspace(minval, maxval, n)))
    return new_cmap