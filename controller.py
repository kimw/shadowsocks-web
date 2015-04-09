# -*- coding: utf-8 -*-
import os
import datetime
from common import is_python2, is_python3
import socket
if is_python2():
    from httplib import HTTPConnection
    from xmlrpclib import Transport, ServerProxy, Fault
elif is_python3():
    from http.client import HTTPConnection
    from xmlrpc.client import Transport, ServerProxy, Fault


class SupervisorController(object):
    def __init__(self, servicename):

        class UnixStreamHTTPConnection(HTTPConnection):
            def connect(self):
                self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                self.sock.connect(self.host)

        class UnixStreamTransport(Transport, object):
            def __init__(self, socket_path):
                self.socket_path = socket_path
                super(UnixStreamTransport, self).__init__()

            def make_connection(self, host):
                return UnixStreamHTTPConnection(self.socket_path)

        if not os.path.exists('/var/run/supervisor.sock'):
            raise RuntimeError('supervisor is not running.')

        self.server = ServerProxy(
            'http://',
            transport=UnixStreamTransport('/var/run/supervisor.sock'))
        self.servicename = servicename

    def get_info(self):
        result = None
        try:
            r = self.server.supervisor.getProcessInfo(self.servicename)
            result = dict(
                    name=r['name'],
                    state=r['statename'],
                    start=datetime.datetime.fromtimestamp(r['start']),
                    epoch_start=r['start'],
                    stop=datetime.datetime.fromtimestamp(r['stop']),
                    epoch_stop=r['stop'],
                    now=datetime.datetime.fromtimestamp(r['now']),
                    epoch_now=r['now'],
                    uptime='0',
                )
            if result['state'] == 'RUNNING':
                result['uptime'] = result['epoch_now'] - result['epoch_start']
        except Fault:
            pass
        return result

    def start(self):
        try:
            self.server.supervisor.startProcess(self.servicename)
        except Fault:
            pass

    def stop(self):
        try:
            self.server.supervisor.stopProcess(self.servicename)
        except Fault:
            pass

    def restart(self):
        try:
            self.server.supervisor.stopProcess(self.servicename)
            self.server.supervisor.startProcess(self.servicename)
        except Fault:
            pass

# vim: tw=78 ts=8 et sw=4 sts=4 fdm=indent
