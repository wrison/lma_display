# Global variables for pylma
import numpy as np
import matplotlib.cm as cm
from matplotlib.colors import ListedColormap
from lma_util import LmaNetwork

#LMA global variables
have_lma = False
fig_lma = None
lma_init = False
sa_init = False
lma_sta_lat = None
lma_sta_lng = None
min_pwr = -20.0
max_pwr = 60.0
marker_size = 2.0
thumb_marker_size = 0.25
black_background = False
map_file = None
lma_cmap = cm.jet  # Colormap

network = LmaNetwork()

lma_limits = {'min_alt' : 0.0, 'max_alt' : 20000.0, 
              'centerX' : 0.0, 'centerY' : 0.0, 'span': 300000.0, 'min_lat' : 0.0, 'max_lat' : 90.0,
              'min_chi2' : 0.0, 'max_chi2' : 5.0, 'min_numsta' : 5,
              'min_t' : np.datetime64('2000-01-01T00:00:00Z',dtype='datetime64[ns]'),
              'max_t' : np.datetime64('2000-01-02T00:00:01Z',dtype='datetime64[ns]')}

# 16 colors pulled from the LMA colormap for "color by power" plots
power_colors = []
for x in np.arange(0.0,1.001,1.0/15.0):
    power_colors.append([[lma_cmap(x)[0], lma_cmap(x)[1],lma_cmap(x)[2]]])

# Colors for density maps
density_colors =np.array([[255, 255, 255, 255],
              [255,  85, 255, 255],
              [127,   0, 255, 255],
              [  0,   0, 255, 255],
              [  0, 127, 255, 255],
              [  0, 255, 255, 255],
              [  0, 255,   0, 255],
              [  0, 127,  63, 255],
              [ 63, 127, 127, 255],
              [255, 255,   0, 255],
              [255, 191, 127, 255],
              [255, 127,   0, 255],
              [255,   0, 127, 255],
              [255,   0,   0, 255],
              [191,   0,   0, 255],
              [127,   0,   0, 255],
              [  0,   0,   0, 255],
              [127, 127, 127, 255],
              [191, 191, 191, 255],
              [255, 255, 255, 255]],dtype="double")/255.0

den_cm = ListedColormap(density_colors)
