from qgis.analysis import QgsRasterCalculatorEntry, QgsRasterCalculator
from qgis.core import QgsLayerDefinition, QgsCoordinateTransformContext, QgsCoordinateReferenceSystem


def average_narr(raster_file, output_directory, start_year=1979, start_month=1, end_year=2014, end_month=12, ):
    # INPUTS:
    #   raster_file: path to the multi-band raster file
    #   output_directory: folder to store the twelve monthly average geotiffs
    #   start_year: earliest is 1979 for NARR data
    #   start_month: start month of the data set (January = 1, December = 12)
    #   end_year: end year
    #   end_month: end month of the data set (January = 1, December = 12) Ex. 12 will give you all months including December


    layer = QgsRasterLayer(raster_file, 'evap.mon.mean')
    bands = layer.bandCount()

    jan, feb, mar, apr, may, jun, jul, aug, sep, oct, nov, dec = [], [], [], [], [], [], [], [], [], [], [], []
    months = [dec, jan, feb, mar, apr, may, jun, jul, aug, sep, oct, nov]

    start_band = (start_year - 1979) * 12 + start_month
    end_band = (end_year - 1979) * 12 + end_month

    if bands <= end_band:  # Input validation to prevent looping past the total number of bands available
        end_band = bands

    for i in range(start_band, end_band+1):
        months[i % 12].append(i)

    for month in months:
        calc_expression = '('
        for band in month[:-1]:  # Add all of the years data
            calc_expression += '"evap.mon.mean@' + str(band) + '" + '
        calc_expression += '"evap.mon.mean@' + str(month[-1]) + '")'
        calc_expression += ' / ' + str(end_year - start_year + 1)  # Divide by the total number of years


        # Create a list of CalculatorEntry objects (each of the bands we use in the calculation)
        raster_bands = []
        for band in month:
            ras = QgsRasterCalculatorEntry()
            ras.ref = 'evap.mon.mean@' + str(band)
            ras.raster = layer
            ras.bandNumber = band
            raster_bands.append(ras)

        calc = QgsRasterCalculator(calc_expression, output_directory + str(month[0]) + '.geotiff', 'GTIFF', layer.extent(), layer.width(), layer.height(), raster_bands)
        calc.processCalculation()

