# -*- coding: utf-8 -*-
import os, sys
import re
import time

import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
from ga import ga

__addon__ = xbmcaddon.Addon()
__author__ = __addon__.getAddonInfo('author')
__scriptid__ = __addon__.getAddonInfo('id')
__scriptname__ = __addon__.getAddonInfo('name')
__version__ = __addon__.getAddonInfo('version')
__icon__ = __addon__.getAddonInfo('icon').decode('utf-8')
__language__ = __addon__.getLocalizedString
__cwd__ = xbmc.translatePath( __addon__.getAddonInfo('path') ).decode('utf-8')
__profile__ = xbmc.translatePath( __addon__.getAddonInfo('profile') ).decode('utf-8')

dbg = False
if 'true' == __addon__.getSetting('dbg'):
  dbg = True

silent = not dbg

if 'true' == __addon__.getSetting('if_active'):
  if_active = True
else:
  if_active = False

def update(actoin):
  payload = {}
  payload['an'] = __scriptname__
  payload['av'] = __version__
  payload['ec'] = 'screesaver_hooks'
  payload['ea'] = str(actoin)
  payload['ev'] = '1'
  ga().update(payload, None)

def log(msg):
  if dbg == True:
    xbmc.log((u"%s *** %s" % (__scriptid__, msg,)).encode('utf-8'),level=xbmc.LOGNOTICE)

class MyMonitor(xbmc.Monitor):
  def __init__(self, *args, **kwargs):
    xbmc.Monitor.__init__(self)

  #def onSettingsChanged(self):
    #self.update_settings()

  def onScreensaverActivated(self):
    start = __addon__.getSetting('svr_activate')
    if xbmc.Player().isPlaying() and 'true' == __addon__.getSetting('if_play'):
      delay = int(__addon__.getSetting('play_delay'))
    else:
      delay = int(__addon__.getSetting('delay'))

    log('Start screensaver hook')
    if start != '':
      log ('Start Delay %d min Exec: %s' % (delay, start))
      update('%s delay %d min' % (start, delay))
      xbmc.executebuiltin('AlarmClock (%s, System.Exec(%s), %s, %s)' % (__scriptid__, start, delay, silent))
      self.__if_active_ts = time.time() + (delay * 60)

  def onScreensaverDeactivated(self):
    stop = __addon__.getSetting('svr_deactivate')

    if xbmc.getGlobalIdleTime() > 3:
        return

    log('Stop screensaver hook')
    xbmc.executebuiltin('CancelAlarm(%s, %s)' % (__scriptid__, silent))

    if True == if_active and time.time() < self.__if_active_ts:
      log ('Not activated skip: %s' % (stop,))
      return

    if stop != '':
      log ('Stop Exec: %s' % (stop,))
      update(stop)
      xbmc.executebuiltin('System.Exec(%s)' % (stop))

if __name__ == '__main__':
  log('Monitor strt')
  update('Start')
  monitor = MyMonitor()
  while True:
    # Sleep/wait for abort for 3 seconds
    log ("Idle time: %d" % (xbmc.getGlobalIdleTime(),))
    if monitor.waitForAbort(3):
      # Abort was requested while waiting. We should exit
      break
  log('Exit')
  update('Stop')
  del monitor
