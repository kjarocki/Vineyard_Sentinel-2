# import required libraries
import rasterio
from rasterio import plot
import matplotlib.pyplot as plt
import os
import fiona
import rasterio.mask
import numpy as np
import pyproj
from matplotlib import pyplot as plt
from scipy.special import comb
import datetime as dt
import matplotlib.dates as mdates



def sort_tupple(tup):
    """return a tupple sorted by second element"""
    lst = len(tup)
    for i in range(0, lst):

        for j in range(0, lst - i - 1):
            if tup[j][1] > tup[j + 1][1]:
                temp = tup[j]
                tup[j] = tup[j + 1]
                tup[j + 1] = temp
    return tup


class Sentinel2:

    def __init__(self, core_path):
        self.core_path = core_path
        full_path = self.get_full_path()

    def get_full_path(self):
        folders = os.listdir(self.core_path)
        print(folders)
        full_paths = []

        for folder in folders:
            if folder[0] == 'S':
                path = self.core_path + '/' + folder + '/GRANULE/'
                folders_inside = os.listdir(path)
                for folder_inside in folders_inside:
                    if folder_inside[0] == 'L':
                        full_path = path + folder_inside + '/IMG_DATA/R10m/'
                        full_paths.append(full_path)

        self.full_paths = full_paths

    def calculate_ndvi(self):
        for i in self.full_paths:
            images = os.listdir(i)

            with rasterio.open(i + images[0][0:23] + 'B04_10m.jp2', driver='JP2OpenJPEG')  as red:
                RED = red.read()

            with rasterio.open(i + images[0][0:23] + 'B08_10m.jp2', driver='JP2OpenJPEG')  as nir:
                NIR = nir.read()

                # with rasterio.open(i+images[0][0:23]+ 'B02_10m.jp2', driver='JP2OpenJPEG')  as blue:
            #     BLUE = blue.read()
            ndvi = (NIR.astype(float) - RED.astype(float)) / ((NIR.astype(float) + RED.astype(float)))
            # evi = 2.5*(NIR.astype(float) - RED.astype(float)) / (NIR.astype(float)+(6*RED.astype(float))-(7.5*BLUE.astype(float))+1)

            profile = red.meta
            profile.update(driver='GTiff')
            profile.update(dtype=rasterio.float32)

            with rasterio.open(
                    '/Volumes/Konrad Jarocki/Vineyard_Sentinel2/results/NDVI/full_Italy/' + images[0][0:23] + '0.NDVI.TIFF',
                    'w', **profile) as dst:
                dst.write(ndvi.astype(rasterio.float32))
            print(images[0][0:23])
        # with fiona.open("/Users/konradjarocki/repos/Vineyard_Sentinel-2/Masks/Areas/Italy/Italy_WGS_2.shp", "r") as shapefile:
        #     shapes = [feature["geometry"] for feature in shapefile]
        #
        # with rasterio.open('/Volumes/Konrad Jarocki/Vineyard_Sentinel2/results/NDVI/full_Italy/'+images[0][0:23]+ '_NDVI.TIFF', 'r') as src:
        #     for shape in shapes:
        #
        #         print(src.crs, shape)
        #     out_image, out_transform = rasterio.mask.mask(src, shapes, crop=True, filled = True)
        #     out_meta = src.meta
        #
        # out_meta.update({"driver": "GTiff", "height": out_image.shape[1],
        #                  "width": out_image.shape[2], "transform": out_transform})
        # out_image[out_image == 0] = np.nan
        #
        # with rasterio.open('/Volumes/Konrad Jarocki/Vineyard_Sentinel2/results/NDVI/cropped_Italy/c'+images[0][0:23]+ '_NDVI.TIFF', 'w', **out_meta) as dst:
        #
        #     dst.write(out_image.astype(rasterio.float32))


def get_histogram(point, fig, ax, name, deg=13):
    histogram = []
    y = []
    raw_x = []
    images = os.listdir('/Volumes/My Passport/Konrad/NDVI_results/')
    for image in images:
        if image[0] == 'T':
            with rasterio.open('/Volumes/My Passport/Konrad/NDVI_results/' + image, 'r') as dst:
                for val in dst.sample([point]):
                    histogram.append((val[0], float(image[7:15])))
    histogram = sort_tupple(histogram)

    for i in histogram:
        y.append(i[0])
        raw_x.append(i[1])

    date_fmt = '%Y%m%d.0'
    dt_x = [dt.datetime.strptime(str(i), date_fmt) for i in raw_x]
    print(dt_x)
    x = [mdates.date2num(i) - 18000.0 for i in dt_x]
    x2 = [mdates.date2num(i) for i in dt_x]

    plt.ylim(-0.25, 1)

    coefficients = np.polyfit(x, y, deg)

    poly = np.poly1d(coefficients)

    new_x = np.linspace(x[0], x[-1], 200)
    new_x2 = np.linspace(x2[0], x2[-1], 200)

    new_y = poly(new_x)

    ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=1))
    ax.plot(new_x2, new_y, label=name)
    ax.legend()
    date_formatter = mdates.DateFormatter('%y/%m/%d')
    ax.xaxis.set_major_formatter(date_formatter)
    fig.autofmt_xdate()


def get_histogram_bezier(point, fig, ax, name, deg=13):
    histogram = []
    y = []
    raw_x = []
    images = os.listdir('/Volumes/My Passport/Konrad/NDVI_results/')
    for image in images:
        if image[0] == 'T':
            with rasterio.open('/Volumes/My Passport/Konrad/NDVI_results/' + image, 'r') as dst:
                for val in dst.sample([point]):
                    histogram.append((val[0], float(image[7:15])))
    histogram = sort_tupple(histogram)

    for i in histogram:
        y.append(i[0])
        raw_x.append(i[1])

    date_fmt = '%Y%m%d.0'
    dt_x = [dt.datetime.strptime(str(i), date_fmt) for i in raw_x]
    print(dt_x)
    x = [mdates.date2num(i) - 18000.0 for i in dt_x]
    x2 = [mdates.date2num(i) for i in dt_x]

    plt.ylim(-0.25, 1)

    data = np.column_stack([x, y])
    xvals, yvals = bezier_curve(data, nTimes=1000)

    ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=1))
    ax.plot(xvals, yvals, label=name)
    ax.legend()
    date_formatter = mdates.DateFormatter('%y/%m/%d')
    ax.xaxis.set_major_formatter(date_formatter)
    fig.autofmt_xdate()


def crop_with_surrounding():
    files = os.listdir('/Volumes/My Passport/Konrad/NDVI_results/')
    for file in files:
        if file[0] == 'T':
            with fiona.open("area.shp", "r") as shapefile:
                shapes = [feature["geometry"] for feature in shapefile]

            with rasterio.open('/Volumes/My Passport/Konrad/NDVI_results/' + file, 'r') as src:
                out_image, out_transform = rasterio.mask.mask(src, shapes, crop=True, filled=True)
                out_meta = src.meta

            out_meta.update({"driver": "GTiff", "height": out_image.shape[1], "width": out_image.shape[2],
                             "transform": out_transform})
            out_image[out_image == 0] = np.nan

            with rasterio.open('/Volumes/My Passport/Konrad/Cropped2/a' + file, 'w', **out_meta) as dst:
                dst.write(out_image.astype(rasterio.float32))


def bernstein_poly(i, n, t):
    """
     The Bernstein polynomial of n, i as a function of t
    """

    return comb(n, i) * (t ** (n - i)) * (1 - t) ** i


def bezier_curve(points, nTimes=50):
    nPoints = len(points)
    xPoints = np.array([p[0] for p in points])
    yPoints = np.array([p[1] for p in points])

    t = np.linspace(0.0, 1.0, nTimes)

    polynomial_array = np.array([bernstein_poly(i, nPoints - 1, t) for i in range(0, nPoints)])

    xvals = np.dot(xPoints, polynomial_array)
    yvals = np.dot(yPoints, polynomial_array)

    return xvals, yvals


# point = (356215,6219780) # Forest
# point11 = (356853.2,6219669.7) # Field 1 Point 1
# point12 = (356903.8,6219769.2) # Field 1 Point 2
# point13 = (356997.2,6219861.6) # Field 1 Point 3
# point21 = (356996.3,6219741.2) # Field 2 Point 4
# point22 = (357011.0,6219686.4) # Field 2 Point 5
# point23 = (356946.3,6219691.3) # Field 2 Point 6
# point4 = (359263.3,6217037.4) # Building
#
# fig, ax = plt.subplots()
# get_histogram(point,fig, ax, 'Forest' )
# get_histogram(point11,fig, ax, 'Point 1 (Cult. 1)' )
# get_histogram(point12,fig, ax, 'Point 2 (Cult. 1)' )
# get_histogram(point13,fig, ax, 'Point 3 (Cult. 1)' )
# get_histogram(point21,fig, ax, 'Point 4 (Cult. 2)' )
# get_histogram(point22,fig, ax, 'Point 5 (Cult. 2)' )
# get_histogram(point23,fig, ax, 'Point 6 (Cult. 2)' )
#
# get_histogram(point4,fig, ax, 'Building', 8 )
#
# plt.title('Normalized difference vegetation index (NDVI).')
# plt.show()
#
# point = (356215,6219780) # Forest
# point11 = (356853.2,6219669.7) # Field 1 Point 1
# point12 = (356903.8,6219769.2) # Field 1 Point 2
# point13 = (356997.2,6219861.6) # Field 1 Point 3
# point21 = (356996.3,6219741.2) # Field 2 Point 4
# point22 = (357011.0,6219686.4) # Field 2 Point 5
# point23 = (356946.3,6219691.3) # Field 2 Point 6
# point4 = (359263.3,6217037.4) # Building
#
# fig, ax = plt.subplots()
# get_histogram_bezier(point,fig, ax, 'Forest' )
# get_histogram_bezier(point11,fig, ax, 'Point 1 (Cult. 1)' )
# get_histogram_bezier(point12,fig, ax, 'Point 2 (Cult. 1)' )
# get_histogram_bezier(point13,fig, ax, 'Point 3 (Cult. 1)' )
# get_histogram_bezier(point21,fig, ax, 'Point 4 (Cult. 2)' )
# get_histogram_bezier(point22,fig, ax, 'Point 5 (Cult. 2)' )
# get_histogram_bezier(point23,fig, ax, 'Point 6 (Cult. 2)' )
#
# get_histogram_bezier(point4,fig, ax, 'Building', 8 )
#
# plt.title('Normalized difference vegetation index (NDVI).')
# plt.show()
test = Sentinel2('/Volumes/Konrad Jarocki/Vineyard_Sentinel2/Downloads/raw_Italy')
test.get_full_path()
test.calculate_ndvi()
print('working!')