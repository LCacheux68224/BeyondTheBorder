# -*- coding: utf-8 -*-
"""
/***************************************************************************
 BeyondTheBorderDialog
                                 A QGIS plugin
 Lissage et schématisation carroyée
                             -------------------
        begin                : 2016-11-04
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Insee Établissement de Strasbourg, Psar AU DG
        email                : lionel.cacheux@insee.fr
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

from PyQt4 import QtGui, uic, QtCore
import qgis.core as qgis
from qgis.utils import iface
from qgis.core import QgsCoordinateReferenceSystem
from qgis.gui import QgsProjectionSelectionWidget

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'btb_dialog_base.ui'))


class BeyondTheBorderDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(BeyondTheBorderDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.inputLayer.currentIndexChanged.connect(self.populateAttributes)        
        self.buttonBox.rejected.connect(self.reject)
        self.buttonBox.accepted.connect(self.accept)
        self.btnAdd.clicked.connect(self.onAdd)
        self.availableAttributes.doubleClicked.connect(self.onAdd)
        self.btnRemove.clicked.connect(self.onRemove)
        self.selectedAttributes.doubleClicked.connect(self.onRemove)
        self.grid.toggled.connect(self.radio_grid)
        self.selectGrid.clicked.connect(self.browseForGrid)
        # self.mQgsProjectionSelectionWidget.setCrs(QgsCoordinateReferenceSystem('EPSG:4326'))
        self.useCanvasCRS()
        self.lastOpenedFile = None
        self.selectFileName.clicked.connect(self.browse)
        self.oldPath = ''
        
        
    def populateLayers( self ):
        self.inputLayer.clear()     #InputTable
        myList = []
        myList = [layer.name() for layer in qgis.QgsMapLayerRegistry.instance().mapLayers().values() 
            if hasattr(layer, 'geometryType') and layer.geometryType() in (qgis.QGis.NoGeometry, qgis.QGis.Point, qgis.QGis.Polygon)]
        self.inputLayer.addItems( myList )
    '''    
        def populateGrid( self ):
            self.analysisLayer.clear()     #InputTable
            myList = []
            myList = [layer.name() for layer in qgis.QgsMapLayerRegistry.instance().mapLayers().values() 
                if hasattr(layer, 'geometryType') and layer.geometryType() == (qgis.QGis.Polygon)]
            self.analysisLayer.addItems( myList )
    '''   
        
    def populateAttributes( self ):
        layerName = self.inputLayer.currentText()
        self.availableAttributes.clear()
        self.selectedAttributesList = []
        self.selectedAttributes.clear()
        self.xCoord.clear()
        self.yCoord.clear()
        if layerName != "":         
            layer = qgis.QgsMapLayerRegistry.instance().mapLayersByName(layerName)[0]
            fieldList = [field.name()
               for field in list(layer.pendingFields().toList())
               if field.type() in (QtCore.QVariant.Double, QtCore.QVariant.Int)]
            # print fieldList
            self.availableAttributes.addItems(fieldList)    
            if hasattr(layer, 'geometryType') and layer.geometryType() == qgis.QGis.NoGeometry:
                self.xLabel.setEnabled(True)
                self.yLabel.setEnabled(True)
                self.xCoord.setEnabled(True)
                self.xCoord.addItems(fieldList)
                self.yCoord.setEnabled(True)
                self.yCoord.addItems(fieldList)
            else:
                self.xLabel.setEnabled(False)
                self.yLabel.setEnabled(False)
                self.xCoord.setEnabled(False)
                self.yCoord.setEnabled(False)            

    def onAdd(self):
        selectedItem = self.availableAttributes.currentItem()
        if selectedItem is not None and selectedItem.text() not in self.selectedAttributesList:
            self.selectedAttributesList.append(selectedItem.text())          
            self.populateSelectedAttributes()

    def onRemove(self):
        selectedItem = self.selectedAttributes.currentItem()
        if selectedItem is not None and selectedItem.text() in self.selectedAttributesList :
            self.selectedAttributesList.remove(selectedItem.text())           
            self.populateSelectedAttributes()
            
    def populateSelectedAttributes( self):
        layerName = self.inputLayer.currentText()
        self.selectedAttributes.clear()
        if layerName != "":         
            layer = qgis.QgsMapLayerRegistry.instance().mapLayersByName(layerName)[0]
            fieldList = [field.name()
               for field in list(layer.pendingFields().toList())
               if field.type() in (QtCore.QVariant.Double, QtCore.QVariant.Int)]
            # print fieldList
            self.selectedAttributes.addItems(self.selectedAttributesList)

    def useCanvasCRS(self):
        # use the CRS of the project
        srs=iface.mapCanvas().mapRenderer().destinationCrs()
        if 'EPSG' in srs.authid() :
            # crsString = srs.authid().split(':')[1]
            self.mQgsProjectionSelectionWidget.setCrs(QgsCoordinateReferenceSystem(srs.authid()))
            
    def radio_grid(self):
        if self.grid.isChecked():
            self.inputGrid.setEnabled(True)
            self.selectGrid.setEnabled(True)
            self.label_11.setEnabled(True)

        else:
            self.inputGrid.setEnabled(False)
            self.selectGrid.setEnabled(False)
            self.label_11.setEnabled(False)       
            self.inputGrid.clear()
            
    def browseForGrid( self ):
        # dir = self.sourceDir
        filters = "Shapefile (*.shp)"
        selected_filter = "Images (*.shp)"
        options = "QFileDialog.List" # ???
        fileName0 = QtGui.QFileDialog.getOpenFileName(self, "Open Shapefile", self.lastOpenedFile, "*.shp") 
        self.inputGrid.setText(fileName0)

    def browse( self ):
        fileName0 = QtGui.QFileDialog.getSaveFileName(self, 'Save as',
                                        self.oldPath, "Shapefile (*.shp);;All files (*)")
        fileName = os.path.splitext(fileName0)[0]+ u'.shp'
        if os.path.splitext(fileName0)[0] != '':
            self.oldPath = os.path.dirname(fileName)
        layername = os.path.splitext(os.path.basename(fileName))[0]
        if (layername=='.shp'):
            return
       
        self.outputFile.setText(fileName)      