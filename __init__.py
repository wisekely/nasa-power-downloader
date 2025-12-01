# -*- coding: utf-8 -*-
def classFactory(iface):
    from .nasa_power_downloader import PowerDownloader
    return PowerDownloader(iface)