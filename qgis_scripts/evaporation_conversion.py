from qgis.analysis import QgsRasterCalculatorEntry, QgsRasterCalculator
from qgis.core import QgsLayerDefinition
import glob

def convert_evaporation(raster_file, output_directory):
    name = raster_file[raster_file.rfind('\\')+1:raster_file.rfind('.')]

    layer = QgsRasterLayer(raster_file)

    ras = QgsRasterCalculatorEntry()
    ras.ref = 'layer@1'
    ras.raster = layer
    ras.bandNumber = 1

    calc_expression = 'layer@1 * 8 * 0.0393701'

    calc = QgsRasterCalculator(calc_expression, output_directory, 'GTiff', layer.extent(), layer.width(), layer.height(), [ras])
    calc.processCalculation()

masked_average_files = glob.glob('./masked_average/*.geotiff')

for file in masked_average_files:
    name = file[file.rfind('\\')+1:file.rfind('_')]
    print(name)
    convert_evaporation(file, './masked_average_converted_swmm/' + name + '_masked_converted.geotiff')
