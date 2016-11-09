# -*- coding: utf-8 -*-
"""
/***************************************************************************
 BeyondTheBorder
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QVariant
from PyQt4.QtGui import QAction, QIcon
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from btb_dialog import BeyondTheBorderDialog
import os.path
from qgis.core import * # QgsVectorLayer, QgsField, QgsMapLayerRegistry, QgsVectorFileWriter, QgsFeature
import tempfile
import shutil
import processing
from qgis.utils import iface
import qgis.core as qgis
import re

class BeyondTheBorder:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'BeyondTheBorder_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Beyond the border')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'BeyondTheBorder')
        self.toolbar.setObjectName(u'BeyondTheBorder')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('BeyondTheBorder', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference
        self.dlg = BeyondTheBorderDialog()

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToVectorMenu(
                self.menu,
                action)
            print str(processing.algs.r.RUtils.RUtils.RScriptsFolder())
            RscriptFolder = processing.algs.r.RUtils.RUtils.RScriptsFolder()

            shutil.copyfile(self.plugin_dir+"/rscript/btb_LissageGrille.rsx", RscriptFolder+"/btb_LissageGrille.rsx")
            shutil.copyfile(self.plugin_dir+"/rscript/btb_Schematisation_de_carreaux.rsx", RscriptFolder+"/btb_Schematisation_de_carreaux.rsx")
            shutil.copyfile(self.plugin_dir+"/rscript/btb_Schematisation_de_carreaux.rsx.help", RscriptFolder+"/btb_Schematisation_de_carreaux.rsx.help")

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/BeyondTheBorder/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'btb'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginVectorMenu(
                self.tr(u'&Beyond the border'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.populateLayers()
        self.dlg.outputFile.setText('')
        #if self.dlg.grid.isChecked():
        #    self.dlg.populateGrid()
        self.dlg.useCanvasCRS()
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result == 1:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            
            inputLayer = QgsMapLayerRegistry.instance().mapLayersByName(self.dlg.inputLayer.currentText())[0]
            # attributeList = [field for field in inputLayer.pendingFields() if field.typeName in ('Integer', 'Real')]
            newAttributeList = []
            newAttributeList.extend([QgsField('x', QVariant.Int, "Integer", 10)])
            newAttributeList.extend([QgsField('y', QVariant.Int, "Integer", 10)])

                
            valueFieldNames = self.dlg.selectedAttributesList

            if isinstance(valueFieldNames, str):
                valueFieldNames = (valueFieldNames,)
            listeIndex = [inputLayer.fieldNameIndex(element) \
                    for element in valueFieldNames]
            
            newAttributeList.extend([inputLayer.pendingFields()[elem] for elem in listeIndex])
            features = inputLayer.getFeatures()
            listGeom = []
            if inputLayer.geometryType() == qgis.QGis.NoGeometry:
                coordNames = [self.dlg.xCoord.currentText(), self.dlg.yCoord.currentText()]
                coordIndex = [inputLayer.fieldNameIndex(element) \
                    for element in coordNames]
            for element in features :
                outFeat = QgsFeature()
                if inputLayer.geometryType() == qgis.QGis.NoGeometry:
                    x = element.attributes()[coordIndex[0]]
                    y = element.attributes()[coordIndex[1]]
                else:    
                    # currentValues = [] # list(element.geometry().centroid().asPoint())
                    x = int(element.geometry().centroid().asPoint()[0])
                    y = int(element.geometry().centroid().asPoint()[1])
                currentValues = [x,y]
                currentValues.extend([(element.attributes()[i]) for i in listeIndex]) 
                # currentValues.extend([(element.attributes()[i]) for i in listeIndex])
                outFeat.setAttributes(currentValues)    
                listGeom.append(outFeat)               
            
            tempLayer = QgsVectorLayer('Point?crs=epsg:4326', 'tempLayer','memory')
            tempLayer.dataProvider().addAttributes(newAttributeList)
            tempLayer.dataProvider().addFeatures(listGeom)
            tempLayer.updateFields()
            tempLayer.commitChanges()
            srs=self.dlg.mQgsProjectionSelectionWidget.crs().authid()
            if 'EPSG' in srs :
                layerCRS =  int(srs.split(':')[1])
            cellsize = int(self.dlg.cellsize.value())
            bandwidth = int(self.dlg.bandwidth.value())
            dirpath = tempfile.mkdtemp()
            sortie = str(re.sub('\\\\','/',dirpath) + "/output.csv")
            
            QgsVectorFileWriter.writeAsVectorFormat(tempLayer, sortie, "utf8", None, "CSV")
            print "sortie : ", sortie
            outputFile = self.dlg.outputFile.text()
            print "outputFile : ", outputFile
            if self.dlg.noGrid.isChecked():    
                processingOutput = processing.runalg("r:btbschematisationdecarreaux",sortie,cellsize,bandwidth,layerCRS,outputFile)
                smoothedDatas = QgsVectorLayer(processingOutput['grille_lissee '],'grille_lissee','ogr')
                QgsMapLayerRegistry.instance().addMapLayer(smoothedDatas)                
            else:
                smoothedDatasPath = str(re.sub('\\\\','/',dirpath) + "/lissage.dbf")
                gridLayerPath = self.dlg.inputGrid.text()
                print "gridLayerPath :", gridLayerPath
                processing.runalg("r:btblissagegrille",sortie, cellsize,bandwidth, re.sub('\.shp','.dbf',gridLayerPath), smoothedDatasPath)
                smoothedDatas = QgsVectorLayer(smoothedDatasPath,'donnees_lissee','ogr')
                gridLayer = QgsVectorLayer(gridLayerPath,'grille_de_lissage','ogr') 
                QgsMapLayerRegistry.instance().addMapLayer(gridLayer)
                fieldList = [field.name() for field in list(smoothedDatas.pendingFields().toList())]
                print "fields 1 : ",fieldList
                fieldList.remove(u'x')
                fieldList.remove(u'y')
                fieldList.remove('ID')
                print "fields 2 : ", fieldList
                joinObject = QgsVectorJoinInfo()
                joinObject.joinLayerId = smoothedDatas.id()
                joinObject.prefix = ''
                joinObject.joinFieldName = 'ID'
                joinObject.targetFieldName = 'ID'
                # joinObject.setJoinFieldNamesSubset(fieldList)
                joinObject.memoryCache = True
                gridLayer.addJoin(joinObject)
                print 'fields 3 :', str([field.name() for field in list(gridLayer.pendingFields().toList())])
                QgsVectorFileWriter.writeAsVectorFormat(gridLayer, outputFile,"utf-8", None, "ESRI Shapefile")
                resultLayer = QgsVectorLayer(outputFile,'sortie','ogr')
                QgsMapLayerRegistry.instance().addMapLayer(resultLayer)
                del smoothedDatas
            # shutil.rmtree(dirpath)
            
