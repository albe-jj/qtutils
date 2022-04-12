import matplotlib as mpl

inch = 1/2.54 #inch/cm


def article_style():
    mpl.rcdefaults()
    mpl.rcParams['figure.dpi'] = 200 
    mpl.rcParams['figure.figsize'] = (3.5*inch,2.5*inch) 

    mpl.rcParams['axes.linewidth'] = 0.5
    mpl.rcParams['lines.linewidth'] = 1
    mpl.rcParams["legend.numpoints"] = 1
    mpl.rcParams["legend.frameon"] = False
    #mpl.rcParams['figure.figsize'] = (4, 3)
    mpl.rcParams['font.size'] = 8
    mpl.rcParams['font.family'] = 'Arial'

    # #Setting finally the Text characters to regular instead of italics.
    mpl.rcParams['mathtext.rm'] = 'Arial'                 #'custom''Arial' #custom make mu italic, Arial straight
    mpl.rcParams['mathtext.it'] = 'Arial: italic'         #make latex italics unless use \mathrm{}
    mpl.rcParams['mathtext.default'] = 'it'#'regular'
    mpl.rcParams['xtick.direction'] = 'out'
    mpl.rcParams['ytick.direction'] = 'out'
    mpl.rcParams['xtick.major.width'] = 0.5
    mpl.rcParams['ytick.major.width'] = 0.5
    mpl.rcParams['xtick.major.size'] = 3 #default 3.5
    mpl.rcParams['xtick.minor.size'] = 1.7 #default 2.0
    mpl.rcParams['ytick.major.size'] = 3 #default 3.5
    mpl.rcParams['ytick.minor.size'] = 1.7 #default 2.0

    mpl.rcParams["errorbar.capsize"]= 3
    mpl.rcParams['savefig.bbox'] = 'tight' #to avoid clipping mask cropping the axis label

def quick_style():
    mpl.rcdefaults()
    mpl.rcParams['figure.dpi'] = 79
    mpl.rcParams['figure.figsize'] = (13*inch,9*inch) 
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
    mpl.rcParams['font.size'] = 16
    mpl.rcParams['mathtext.rm'] = 'Arial'
    mpl.rcParams['savefig.format'] = 'svg'
    mpl.rcParams['mathtext.default'] = 'it'


    mpl.rcParams['pdf.fonttype'] = 42 #for illustrator to get editable text (Type 2/TrueType fonts)
    mpl.rcParams['ps.fonttype'] = 42
    # mpl.rcParams['svg.fonttype']='none' #'path'

    mpl.rcParams['savefig.bbox'] = 'tight' #to avoid clipping mask cropping the axis label
    # mpl.rcParams['mathtext.fontset'] = 'cm' #this gives you nice font But! non compatible with illustrator

