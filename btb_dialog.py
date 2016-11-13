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
# from qgis.core import QgsCoordinateReferenceSystem
# from qgis.gui import QgsProjectionSelectionWidget
from qgis.gui import QgsMessageBar
from processing.core.ProcessingConfig import ProcessingConfig
from PyQt4.QtCore import QUrl

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
        self.buttonBox_2.rejected.connect(self.reject)
        self.buttonBox.accepted.connect(self.browse)
        self.btnAdd.clicked.connect(self.onAdd)
        self.availableAttributes.doubleClicked.connect(self.onAdd)
        self.btnRemove.clicked.connect(self.onRemove)
        self.selectedAttributes.doubleClicked.connect(self.onRemove)
        
        # self.grid.toggled.connect(self.radio_grid)
        self.selectGrid.clicked.connect(self.browseForGrid)
        # self.mQgsProjectionSelectionWidget.setCrs(QgsCoordinateReferenceSystem('EPSG:4326'))
        # self.useCanvasCRS()
        self.lastOpenedFile = None
        # self.selectFileName.clicked.connect(self.browse)
        self.oldPath = ''
        self.webView.load(QUrl('https://cran.r-project.org/web/packages/btb/index.html'))
        
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
            self.availableAttributes.addItems(fieldList)    
            if hasattr(layer, 'geometryType') and layer.geometryType() == qgis.QGis.NoGeometry:
                self.xLabel.setEnabled(True)
                self.yLabel.setEnabled(True)
                self.xCoord.setEnabled(True)
                self.xCoord.addItems(fieldList)
                if 'x' in fieldList:
                    self.xCoord.setCurrentIndex(fieldList.index('x'))
                self.yCoord.setEnabled(True)
                self.yCoord.addItems(fieldList)
                if 'y' in fieldList:
                    self.yCoord.setCurrentIndex(fieldList.index('y'))               
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
        self.legendOnlyTestSelectedOptions
        if len(self.selectedAttributes) == 0 :
            iface.messageBar().pushMessage("Error", "No attribute selected", level=QgsMessageBar.CRITICAL, duration=3)
            return
        elif ( self.mGroupBoxUserGrid.isCollapsed() == False and self.inputGrid.text() ==''):
            iface.messageBar().pushMessage("Error", "No grid selected", level=QgsMessageBar.CRITICAL, duration=3)  
            return  
        # test percentile list    
        quantileText = self.quantileList.text()
        quantileText = quantileText.strip().replace(';',' ')
        quantileList = quantileText.split()       
        try:

            temp = [float(elem) for elem in quantileList]
            self.RquantileList = ','.join(quantileList)          
        except:
            iface.messageBar().pushMessage("Error", "Percentiles list incorrect", level=QgsMessageBar.CRITICAL, duration=3)
            return   
            
        fileName0 = QtGui.QFileDialog.getSaveFileName(self, 'Save Shapefile as',
                                        self.oldPath, "Shapefile (*.shp);;All files (*)")
        fileName = os.path.splitext(fileName0)[0]+ u'.shp'
        if os.path.splitext(fileName0)[0] != '':
            self.oldPath = os.path.dirname(fileName)
        layername = os.path.splitext(os.path.basename(fileName))[0]
        self.outputFile = fileName
        if (layername=='.shp'):
            return       
        # self.outputFile.setText(fileName)
     
        self.accept() 
    
    def testOptions (self):
        if len(self.selectedAttributes) == 0 :
            iface.messageBar().pushMessage("Error", "No attribute selected", level=QgsMessageBar.CRITICAL, duration=3)
            return
        elif ( self.mGroupBoxUserGrid.isCollapsed() == False and self.inputGrid.text() ==''):
            iface.messageBar().pushMessage("Error", "No grid selected", level=QgsMessageBar.CRITICAL, duration=3)  
            return
        else :
            self.browse   
            self.accept()    
    def testR (self):
        if ProcessingConfig.getSetting('ACTIVATE_R')==False:
            iface.messageBar().pushMessage("Error", "R not activated", level=QgsMessageBar.CRITICAL, duration=3)
            self.reject()
            
    def legendOnlyTestSelectedOptions( self ):


        # list of custom radiuses for the circles in the legend
        print 'test'
        quantileList = self.quantileList.text()
        print quantileList
        quantileList = quantileList.strip().replace(';',' ')
        print quantileList
        # self.legendOnlyValuesList = quantileList.split()
        '''
            if len(self.legendOnlyValuesList) == 0:  # automatic VALUES for the circles in the legend 
                legendError = False
                self.legendOnlyValuesList = []
            else:

            try:			
                for i in range(len(self.legendOnlyValuesList)):  # custom values for the circles in the legend
                   self.legendOnlyValuesList[i] = float(self.legendOnlyValuesList[i])
                       self.legendOnlyValuesList.sort()
                       quantileListError = False
            except:   # if error in customisation -> automatic values for legend + warning message
                quantileListError = True
        '''