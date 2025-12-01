# -*- coding: utf-8 -*-
"""
NASA POWER Data Downloader for QGIS
Easy access to NASA POWER daily climate data (point & regional)
Live preview, OSM background, Africa-first view
Author: Wise GIS (wisekely@gmail.com)
"""

from qgis.PyQt.QtWidgets import QMessageBox, QAction
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import Qt
from qgis.core import (
    QgsRasterLayer, QgsProject, QgsCoordinateReferenceSystem,
    QgsCoordinateTransform, QgsPointXY, QgsGeometry, QgsFeature,
    QgsVectorLayer, QgsMarkerSymbol, QgsFillSymbol, QgsRectangle
)
import urllib.request
import urllib.error
import urllib.parse
import tempfile
import webbrowser
import os


class PowerDownloader:
    def __init__(self, iface):
        self.iface = iface
        self.dlg = None
        self.total_jobs = 1
        self.current_job = 0

    def initGui(self):
        icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
        self.action = QAction(QIcon(icon_path), "NASA POWER Downloader", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addPluginToMenu("&Web", self.action)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        self.iface.removePluginMenu("&Web", self.action)
        self.iface.removeToolBarIcon(self.action)
        self.remove_temp_layers()

    def remove_temp_layers(self):
        names = ["NASA POWER Point Marker", "NASA POWER Bounding Box", "OpenStreetMap (Standard)"]
        for layer in list(QgsProject.instance().mapLayers().values()):
            if layer.name() in names:
                QgsProject.instance().removeMapLayer(layer.id())
        self.iface.mapCanvas().refresh()

    def run(self):
        from .nasa_power_downloader_dialog import PowerDownloaderDialog
        self.dlg = PowerDownloaderDialog()

        # Default values
        self.dlg.latEdit.setText("-1.2921")
        self.dlg.lonEdit.setText("36.8219")
        self.dlg.startEdit.setText("20240101")
        self.dlg.endEdit.setText("20241231")
        self.dlg.formatCombo.setCurrentIndex(0)

        # Uncheck all parameters
        for name in ["check_PRECTOT", "check_T2M", "check_T2M_MAX", "check_T2M_MIN",
                     "check_RH2M", "check_WS2M", "check_WD2M", "check_ALLSKY_SFC_SW_DWN",
                     "check_CLRSKY_SFC_SW_DWN", "check_QV2M", "check_PS", "check_T2MDEW"]:
            getattr(self.dlg, name).setChecked(False)

        # OSM background by default
        if hasattr(self.dlg, "check_osm"):
            self.dlg.check_osm.setChecked(True)
            self.dlg.check_osm.stateChanged.connect(self.toggle_osm_layer)
            self.toggle_osm_layer(2)  # Load OSM immediately

        self.dlg.progressBar.setVisible(False)

        # Live preview connections
        for widget in [self.dlg.latEdit, self.dlg.lonEdit, self.dlg.topLatEdit,
                       self.dlg.topLonEdit, self.dlg.bottomLatEdit, self.dlg.bottomLonEdit]:
            widget.textChanged.connect(self.update_preview)
        self.dlg.radio_point.toggled.connect(self.update_preview)
        self.dlg.radio_area.toggled.connect(self.update_preview)

        # Buttons
        self.dlg.downloadButton.setText("Download")
        self.dlg.downloadButton.clicked.connect(self.download_data)
        self.dlg.mapExtentButton.clicked.connect(self.use_map_extent)
        self.dlg.cancelButton.clicked.connect(self.dlg.close)

        self.dlg.show()

        # ZOOM TO FULL AFRICA FIRST
        africa_extent = QgsRectangle(-18.0, -35.0, 52.0, 38.0)
        self.iface.mapCanvas().setExtent(africa_extent)
        self.iface.mapCanvas().refresh()

        # THEN SHOW RED MARKER ON TOP
        self.update_preview()

    def toggle_osm_layer(self, state):
        name = "OpenStreetMap (Standard)"
        # Remove existing OSM
        for layer in list(QgsProject.instance().mapLayers().values()):
            if layer.name() == name:
                QgsProject.instance().removeMapLayer(layer.id())
        if state == 2:  # checked
            url = "type=xyz&url=https://tile.openstreetmap.org/{z}/{x}/{y}.png&zmax=19&zmin=0&crs=EPSG:3857"
            layer = QgsRasterLayer(url, name, "wms")
            if layer.isValid():
                QgsProject.instance().addMapLayer(layer, False)
                root = QgsProject.instance().layerTreeRoot()
                root.insertLayer(len(root.children()), layer)  # very bottom

    def update_preview(self):
        self.remove_temp_layers()

        if self.dlg.radio_point.isChecked():
            try:
                lat = float(self.dlg.latEdit.text())
                lon = float(self.dlg.lonEdit.text())
                if -90 <= lat <= 90 and -180 <= lon <= 180:
                    vl = QgsVectorLayer("Point?crs=epsg:4326", "NASA POWER Point Marker", "memory")
                    sym = QgsMarkerSymbol.createSimple({
                        'name': 'circle', 'color': '#ff0000', 'size': '10',
                        'outline_color': 'white', 'outline_width': '3'
                    })
                    vl.renderer().setSymbol(sym)
                    f = QgsFeature()
                    f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(lon, lat)))
                    vl.dataProvider().addFeature(f)
                    vl.updateExtents()
                    QgsProject.instance().addMapLayer(vl, False)
                    root = QgsProject.instance().layerTreeRoot()
                    root.insertLayer(0, vl)  # on top
            except:
                pass
        else:
            try:
                n = float(self.dlg.topLatEdit.text())
                w = float(self.dlg.topLonEdit.text())
                s = float(self.dlg.bottomLatEdit.text())
                e = float(self.dlg.bottomLonEdit.text())
                if n > s and w < e:
                    vl = QgsVectorLayer("Polygon?crs=epsg:4326", "NASA POWER Bounding Box", "memory")
                    sym = QgsFillSymbol.createSimple({
                        'color': '255,0,0,60', 'outline_color': 'red', 'outline_width': '4'
                    })
                    vl.renderer().setSymbol(sym)
                    ring = [QgsPointXY(w,n), QgsPointXY(e,n), QgsPointXY(e,s), QgsPointXY(w,s), QgsPointXY(w,n)]
                    f = QgsFeature()
                    f.setGeometry(QgsGeometry.fromPolygonXY([ring]))
                    vl.dataProvider().addFeature(f)
                    vl.updateExtents()
                    QgsProject.instance().addMapLayer(vl, False)
                    root = QgsProject.instance().layerTreeRoot()
                    root.insertLayer(0, vl)  # on top
                    self.iface.mapCanvas().setExtent(vl.extent())
                    self.iface.mapCanvas().refresh()
            except:
                pass

    def get_selected_parameters(self):
        param_map = {
            self.dlg.check_PRECTOT: "PRECTOT",
            self.dlg.check_T2M: "T2M",
            self.dlg.check_T2M_MAX: "T2M_MAX",
            self.dlg.check_T2M_MIN: "T2M_MIN",
            self.dlg.check_RH2M: "RH2M",
            self.dlg.check_WS2M: "WS2M",
            self.dlg.check_WD2M: "WD2M",
            self.dlg.check_ALLSKY_SFC_SW_DWN: "ALLSKY_SFC_SW_DWN",
            self.dlg.check_CLRSKY_SFC_SW_DWN: "CLRSKY_SFC_SW_DWN",
            self.dlg.check_QV2M: "QV2M",
            self.dlg.check_PS: "PS",
            self.dlg.check_T2MDEW: "T2MDEW"
        }
        return [code for cb, code in param_map.items() if cb.isChecked()]

    def get_selected_format(self):
        return {0: ("CSV", ".csv"), 1: ("JSON", ".json"), 2: ("NETCDF", ".nc"), 3: ("ICASA", ".csv")}.get(
            self.dlg.formatCombo.currentIndex(), ("CSV", ".csv"))

    def use_map_extent(self):
        canvas = self.iface.mapCanvas()
        extent = canvas.extent()
        src_crs = canvas.mapSettings().destinationCrs()
        dest_crs = QgsCoordinateReferenceSystem("EPSG:4326")
        if src_crs != dest_crs:
            extent = QgsCoordinateTransform(src_crs, dest_crs, QgsProject.instance()).transformBoundingBox(extent)

        self.dlg.radio_area.setChecked(True)
        self.dlg.topLatEdit.setText(f"{extent.yMaximum():.6f}")
        self.dlg.topLonEdit.setText(f"{extent.xMinimum():.6f}")
        self.dlg.bottomLatEdit.setText(f"{extent.yMinimum():.6f}")
        self.dlg.bottomLonEdit.setText(f"{extent.xMaximum():.6f}")
        self.update_preview()
        self.iface.messageBar().pushSuccess("NASA POWER", "Map extent applied!")

    def _download_single(self, url, fmt, suffix, name):
        self.current_job += 1
        self.dlg.progressBar.setValue(int((self.current_job / self.total_jobs) * 100))
        try:
            with urllib.request.urlopen(url) as response:
                tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
                tmp.write(response.read())
                tmp.close()
            if fmt in ["CSV", "JSON", "ICASA"]:
                webbrowser.open(tmp.name)
                self.iface.messageBar().pushSuccess("NASA POWER", f"{name} opened")
            else:
                layer = QgsRasterLayer(tmp.name, f"NASA POWER - {name}")
                if layer.isValid():
                    QgsProject.instance().addMapLayer(layer)
                    self.iface.messageBar().pushSuccess("NASA POWER", f"{name} loaded")
                else:
                    webbrowser.open(tmp.name)
        except urllib.error.HTTPError as e:
            QMessageBox.critical(self.dlg, "HTTP Error", f"{e.code}\n{url}")
        except Exception as e:
            QMessageBox.critical(self.dlg, "Error", str(e))

    def download_data(self):
        self.dlg.progressBar.setVisible(True)
        self.dlg.progressBar.setValue(0)
        self.current_job = 0

        start = self.dlg.startEdit.text().strip()
        end = self.dlg.endEdit.text().strip()
        params = self.get_selected_parameters()
        fmt, suffix = self.get_selected_format()

        if not params:
            QMessageBox.warning(self.dlg, "Error", "Select at least one parameter")
            self.dlg.progressBar.setVisible(False)
            return
        if not start or not end:
            QMessageBox.warning(self.dlg, "Error", "Enter start and end dates")
            self.dlg.progressBar.setVisible(False)
            return

        self.total_jobs = len(params) if self.dlg.radio_area.isChecked() else 1

        try:
            if self.dlg.radio_point.isChecked():
                lat = self.dlg.latEdit.text().strip()
                lon = self.dlg.lonEdit.text().strip()
                query = urllib.parse.urlencode({
                    "parameters": ",".join(params), "community": "AG",
                    "latitude": lat, "longitude": lon, "start": start, "end": end, "format": fmt
                }, safe=",")
                url = f"https://power.larc.nasa.gov/api/temporal/daily/point?{query}"
                self._download_single(url, fmt, suffix, "Point")

            else:
                tl_lat = float(self.dlg.topLatEdit.text())
                tl_lon = float(self.dlg.topLonEdit.text())
                br_lat = float(self.dlg.bottomLatEdit.text())
                br_lon = float(self.dlg.bottomLonEdit.text())
                if tl_lat <= br_lat or tl_lon >= br_lon:
                    raise ValueError("Invalid bounding box")

                if fmt == "NETCDF":
                    QMessageBox.information(self.dlg, "Format", "NETCDF only for points → using CSV")
                    fmt, suffix = "CSV", ".csv"

                for param in params:
                    query = urllib.parse.urlencode({
                        "parameters": param, "community": "AG",
                        "latitudemin": br_lat, "latitudemax": tl_lat,
                        "longitudemin": tl_lon, "longitudemax": br_lon,
                        "start": start, "end": end, "format": fmt
                    })
                    url = f"https://power.larc.nasa.gov/api/temporal/daily/regional?{query}"
                    self._download_single(url, fmt, suffix, param)

        except Exception as e:
            QMessageBox.critical(self.dlg, "Error", str(e))
        finally:
            self.dlg.progressBar.setVisible(True)
            self.dlg.progressBar.setValue(100)
            self.dlg.downloadButton.setText("Download Again")
            self.iface.messageBar().pushSuccess("NASA POWER", "Download complete!")