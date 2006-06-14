# Orca
#
# Copyright 2006 Sun Microsystems Inc.
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place - Suite 330,
# Boston, MA 02111-1307, USA.

"""Provides an HTTP server for Orca.  This currently serves mainly as
something that self-voicing applications can use as their speech
service."""

__id__        = "$Id$"
__version__   = "$Revision$"
__date__      = "$Date$"
__copyright__ = "Copyright (c) 2005-2006 Sun Microsystems Inc."
__license__   = "LGPL"

import threading
import BaseHTTPServer

import debug
import platform
import settings
import speech

_httpRequestThread = None

class _HTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    """Provides support for communicating with Orca via HTTP.  This is
    mainly to support self-voicing applications that want to use Orca
    as a speech service.

    The protocol is simple: POST content is 'stop', 'speak:<text>',
    or 'isSpeaking'.

    To test this, run:

      wget --post-data='speak:hello world' localhost:20433

    """

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write("<html><body><p>Orca %s</p></body></html>" \
                         % platform.version)

    def do_POST(self):
        contentLength = self.headers.getheader('content-length')
        if contentLength:
            contentLength = int(contentLength)
            inputBody = self.rfile.read(contentLength)
            debug.println(debug.LEVEL_FINEST,
                          "httpserver._HTTPRequestHandler received %s" \
                          % inputBody)
            if inputBody.startswith("speak:"):
                speech.speak(inputBody[6:])
                self.send_response(200, 'OK')
            elif inputBody == "stop":
                speech.stop()
                self.send_response(200, 'OK')
            elif inputBody == "isSpeaking":
                self.send_response(200, 'OK')
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write("%s" % speech.isSpeaking())
        else:
            debug.println(debug.LEVEL_FINEST,
                          "httpserver._HTTPRequestHandler received no data")

class _HTTPRequestThread(threading.Thread):
    """Runs a _HTTPRequestHandler in a separate thread."""

    def run(self):
        httpd = BaseHTTPServer.HTTPServer(('',
                                           settings.speechServerPort),
                                          _HTTPRequestHandler)
        httpd.serve_forever()

def init():
    """Creates an HTTP server that listens for speak commands from a
    separate port defined by settings.httpServerPort.  We run this
    as a daemon so it will die automatically when orca dies."""
    
    global _httpRequestThread
    
    if settings.httpServerPort and (not _httpRequestThread):
        try:
            _httpRequestThread = _httpRequestThread()
            _httpRequestThread.setDaemon(True)
            _httpRequestThread.start()
        except:
            debug.printException(debug.LEVEL_SEVERE)

def shutdown():
    """Stops the HTTP server.  [[[WDW - not implemented yet.]]]"""
    pass
