# ============================================================
# KODI Banners - Version 1.9 by D. Lanik (2016)
# ------------------------------------------------------------
# Display banners when playing any video
# ------------------------------------------------------------
# License: GPL (http://www.gnu.org/licenses/gpl-3.0.html)
# ============================================================

import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs
import urlparse
import os
import re
import sys
from PIL import Image
import CommonFunctions as common


# ============================================================
# Define Overlay Class
# ============================================================


class OverlayText(object):

    def __init__(self, windowid):

        self.showing = False
        self.window = xbmcgui.Window(windowid)
        viewport_w, viewport_h = self._get_skin_resolution()

        pos = "20,20".split(",")
        pos_x = (viewport_w + int(pos[0]), int(pos[0]))[int(pos[0]) > 0]
        pos_y = (viewport_h + int(pos[1]), int(pos[1]))[int(pos[1]) > 0]
        self.imageTop = xbmcgui.ControlImage(pos_x, pos_y, 1240, 120, os.path.join("resources", "media", "banners", "generic_01.jpg"), aspectRatio=0)

        pw = int((viewport_w - 1240) / 2)
        ph = int((viewport_h - 60) / 2)
        pp = "%3d,%3d" % (pw, ph)
        pos = pp.split(",")
        pos_x = (viewport_w + int(pos[0]), int(pos[0]))[int(pos[0]) > 0]
        pos_y = (viewport_h + int(pos[1]), int(pos[1]))[int(pos[1]) > 0]
        self.imageCenter = xbmcgui.ControlImage(pos_x, pos_y, 1240, 120, os.path.join("resources", "media", "banners", "generic_01.jpg"), aspectRatio=0)

        pos = "20,-140".split(",")
        pos_x = (viewport_w + int(pos[0]), int(pos[0]))[int(pos[0]) > 0]
        pos_y = (viewport_h + int(pos[1]), int(pos[1]))[int(pos[1]) > 0]
        self.imageBottom = xbmcgui.ControlImage(pos_x, pos_y, 1240, 120, os.path.join("resources", "media", "banners", "generic_01.jpg"), aspectRatio=0)

    def scaleimage(self, width, height, yoffset):
        viewport_w, viewport_h = self._get_skin_resolution()

        if width > viewport_w:
            if yoffset > 0:
                width = viewport_w - (yoffset * 2)
                xpos = yoffset
            else:
                width = viewport_w
                xpos = 0
        else:
            xpos = (viewport_w - width) / 2

        self.imageBottom.setHeight(height)
        self.imageBottom.setWidth(width)
        self.imageBottom.setPosition(xpos, viewport_h - height - yoffset)

        self.imageCenter.setHeight(height)
        self.imageCenter.setWidth(width)
        self.imageCenter.setPosition(xpos, (viewport_h - height) / 2 )

        self.imageTop.setHeight(height)
        self.imageTop.setWidth(width)
        self.imageTop.setPosition(xpos, yoffset)

    def show(self):
        self.showing = True
        self.window.addControl(self.imageBottom)
        self.window.addControl(self.imageCenter)
        self.window.addControl(self.imageTop)

    def hide(self):
        self.showing = False
        self.window.removeControl(self.imageBottom)
        self.window.removeControl(self.imageCenter)
        self.window.removeControl(self.imageTop)

    def _close(self):
        if self.showing:
            self.hide()
        else:
            pass
        try:
            self.window.clearProperties()
        except Exception:
            pass

# ============================================================
# Get resolution
# ============================================================

    def _get_skin_resolution(self):

        aspect_ratio = xbmc.getInfoLabel('Skin.AspectRatio')

        xml = os.path.join(xbmc.translatePath('special://skin/'), 'addon.xml')
        with open(xml) as f:
            xml_file = f.read()
        res_extension_point = common.parseDOM(xml_file, 'extension', attrs={'point': 'xbmc.gui.skin'})[0]

        res_lines = res_extension_point.splitlines()

        skin_resolution = [res if aspect_ratio in res else res_lines for res in res_lines][0]

        xval = int(re.findall('width="(\d{3,4})"', skin_resolution)[0])
        yval = int(re.findall('height="(\d{3,4})"', skin_resolution)[0])

        return xval, yval

# ============================================================
# Display banner
# ============================================================


def displayBanner(imageloc, displaytime, position):
    global myWidget
    global intYOffset
    global __addon__

    __addon__ = xbmcaddon.Addon(id='service.banners.mod')

    ActWin = xbmcgui.getCurrentWindowId()
    myWidget = OverlayText(ActWin)
    myWidget.show()

    if position == 'top':
        myWidget.imageBottom.setImage("")
        myWidget.imageCenter.setImage("")
        myWidget.imageTop.setImage(imageloc)
    elif position == 'bottom':
        myWidget.imageBottom.setImage(imageloc)
        myWidget.imageCenter.setImage("")
        myWidget.imageTop.setImage("")
    else:
        myWidget.imageBottom.setImage("")
        myWidget.imageCenter.setImage(imageloc)
        myWidget.imageTop.setImage("")

    image = Image.open(open(imageloc, 'rb'))
    width, height = image.size
    myWidget.scaleimage(width, height, intYOffset)

    xbmc.log('BANNERS >> STANDALONE INITIALIZING OVERLAY')

    xbmc.sleep(displaytime)

    try:
        myWidget._close()
    except Exception:
        pass

    myWidget = None


# ============================================================
# ------------------------------------------------------------
# Main
# ------------------------------------------------------------
# ============================================================

__addon__ = xbmcaddon.Addon(id='service.banners.mod')
__version__ = __addon__.getAddonInfo('version')
__addonwd__ = xbmc.translatePath(__addon__.getAddonInfo('path').decode("utf-8"))

myWidget = None
rt = None
intYOffset = int(__addon__.getSetting('yoffset'))

if __name__ == '__main__':

    xbmc.log("BANNERS >> STANDALONE STARTED VERSION %s" % (__version__))

    myWidget = None

    try:
        params = urlparse.parse_qs('&'.join(sys.argv[1:]))

        imageloc = params.get('imageloc', None)[0]
        displaytime = int(params.get('displaytime', None)[0])
        position = params.get('position', None)[0]
    except Exception:
        imageloc = None
        displaytime = None
        position = None

    if imageloc and displaytime and position:
        success = xbmcvfs.exists(imageloc)

        if success and 1000 < displaytime < 43200000 and (position == 'top' or position == 'bottom' or position == 'center'):
            xbmc.log("BANNERS >> STANDALONE DISPLAY IMAGE: " + str(imageloc) + " >> TIMEOUT: " + str(displaytime) + " >> POSITION: " + str(position))
            displayBanner(imageloc, displaytime, position)
        else:
            xbmc.log("BANNERS >> STANDALONE DISPLAY IMAGE ERROR: " + str(imageloc) + " >> TIMEOUT: " + str(displaytime) + " >> POSITION: " + str(position))
    else:
        __addon__.openSettings()

    xbmc.log("BANNERS >> STANDALONE FINISHED")
