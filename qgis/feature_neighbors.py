################################################################################
# Copyright 2014 Ujaval Gandhi
# Modified 2019 by Matas Lauzadis to support QGIS >= 3.5 and Python version >= 3.0
#
#This program is free software; you can redistribute it and/or
#modify it under the terms of the GNU General Public License
#as published by the Free Software Foundation; either version 2
#of the License, or (at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
################################################################################


from qgis.utils import iface
from PyQt5.QtCore import QVariant


def neighbors(name_field, sum_field=None):
    # INPUTS:
    #   name_field:
    #       Provide values from your layer.
    #       For example, if your identifier field is called 'XYZ', then provide the parameter 'XYZ'.
    #
    #   sum_field: - Optional
    #       For example, if the field that you want to sum up is called 'VALUES', then
    #       change the line below to _SUM_FIELD = 'VALUES'
    #       If no parameter is provided, no values will be summed, and the only additional attribute will be the neighbors.

    _NAME_FIELD = name_field
    _SUM_FIELD = sum_field


    # Names of the new fields to be added to the layer
    _NEW_NEIGHBORS_FIELD = 'NEIGHBORS'
    if sum_field is not None:
        _NEW_SUM_FIELD = 'SUM'

    layer = iface.activeLayer()

    # Create 2 new fields in the layer that will hold the list of neighbors and sum
    # of the chosen field.
    layer.startEditing()
    layer.dataProvider().addAttributes([QgsField(_NEW_NEIGHBORS_FIELD, QVariant.String)])
    if sum_field is not None:
        layer.dataProvider().addAttributes([QgsField(_NEW_SUM_FIELD, QVariant.Int)])
    layer.updateFields()
    # Create a dictionary of all features
    feature_dict = {f.id(): f for f in layer.getFeatures()}

    # Build a spatial index
    index = QgsSpatialIndex()
    for f in feature_dict.values():
        index.insertFeature(f)

    # Loop through all features and find features that touch each feature
    for f in feature_dict.values():
        print('Working on %s' % f[_NAME_FIELD])
        geom = f.geometry()
        # Find all features that intersect the bounding box of the current feature.
        # We use spatial index to find the features intersecting the bounding box
        # of the current feature. This will narrow down the features that we need
        # to check neighboring features.
        intersecting_ids = index.intersects(geom.boundingBox())
        # Initalize neighbors list and sum
        neighbors = []
        neighbors_sum = 0
        for intersecting_id in intersecting_ids:
            # Look up the feature from the dictionary
            intersecting_f = feature_dict[intersecting_id]

            # For our purpose we consider a feature as 'neighbor' if it touches or
            # intersects a feature. We use the 'disjoint' predicate to satisfy
            # these conditions. So if a feature is not disjoint, it is a neighbor.
            if (f != intersecting_f and
                not intersecting_f.geometry().disjoint(geom)):
                neighbors.append(intersecting_f[_NAME_FIELD])
                if sum_field is not None:
                    neighbors_sum += intersecting_f[_SUM_FIELD]
        f[_NEW_NEIGHBORS_FIELD] = ','.join(neighbors)
        if sum_field is not None:
            f[_NEW_SUM_FIELD] = neighbors_sum
        # Update the layer with new attribute values.
        layer.updateFeature(f)

    layer.commitChanges()
    print('Processing complete.')
    return 0


neighbors('NAME')  # Modify this line with your inputs to use in QGIS