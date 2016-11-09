# -*- coding: utf-8 -*-
"""
/***************************************************************************
 BeyondTheBorder
                                 A QGIS plugin
 Lissage et schématisation carroyée
                             -------------------
        begin                : 2016-11-04
        copyright            : (C) 2016 by Insee Établissement de Strasbourg, Psar AU DG
        email                : lionel.cacheux@insee.fr
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load BeyondTheBorder class from file BeyondTheBorder.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .btb import BeyondTheBorder
    return BeyondTheBorder(iface)
