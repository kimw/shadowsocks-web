# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, with_statement

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define, options

import os
import sys
import logging
import base64

import userlib
import common
from controller import SupervisorController


define('port', type=int, default=8888, help='run on the given port')
define('addr', type=str, default='localhost', help='run on the given address')
define('debug', type=bool, default=False, help='running in debug mode')
define('demo', type=bool, default=False, help='running in demo mode')
define('servicename', type=str, default='shadowsocks',
       help='shadowsocks\'s service name in supervisor')
define('cookie_secret', type=str, default=None,
       help='You must specify the cookie-secret option. It should be a long '
            'random sequence of bytes to be used as the HMAC secret for the '
            'signature.\n'
            'You can create this HMAC string with --hmac option.')
define('hmac', type=None, default=False, help='create a HMAC string')
define('base_url', type=str, default='', help='TODO: add description')


class BaseHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.user = self.application.settings["user"]  # make it shorter
        self.svservname = self.application.settings["svservname"]  # make it shorter

    @property
    def config(self):
        return self.application.config

    def get_current_user(self):
        return self.get_secure_cookie("_t")

    def redirect(self, url, permanent=False, status=None):
        if url[:len(options.base_url)] != options.base_url:
            url = options.base_url + url
        tornado.web.RequestHandler.redirect(self, url, permanent, status)

    def render(self, template_name, **kwargs):
        kwargs["base_url"] = options.base_url
        tornado.web.RequestHandler.render(self, template_name, **kwargs)


class LoginHandler(BaseHandler):
    def initialize(self):
        if self.request.method == "GET":
            self.first_time_login = True
        else:
            self.first_time_login = False
        BaseHandler.initialize(self)

    def get(self):
        if not self.get_current_user():
            self.render("login.html", message=None,
                    next=self.get_argument("next", "/"))
            return
        self.redirect("/")

    def post(self):
        username = self.get_argument("username")
        password = self.get_argument("password")
        print("username=%s, password=%s" % (username, password))

        if self.user.find(username=username, password=password):
            self.set_secure_cookie("_t", self.get_argument("username"))
            self.redirect(self.get_argument("next", "/"))
            return

        # Create account by password in the config file while first time login.
        print("self.user.count=", self.user.count)
        print("password=%s, config[\"password\"]=%s" % (password, config["password"]))
        if (self.user.count == 0 and password == config["password"]):
            self.user.add(username, password)
            self.set_secure_cookie("_t", self.get_argument("username"))
            self.redirect(self.get_argument("next", "/"))
            return

        self.render("login.html", message="login error",
                next=self.get_argument("next", "/"))


class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_all_cookies()
        self.redirect("/")


class RootHandler(BaseHandler):
    def get(self):
        self.redirect("/dashboard")


class DashboardHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        # TODO: It's currently support Python 3 only.
        #       Add python 2 support ASAP.
        if common.is_python3():
            msg = SupervisorController(self.svservname).get_info()
            self.render("dashboard.html", msg=msg)
        else:
            raise NotImplementedError


class ConfigHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        items = []
        if not self.config["port_password"]:
            _config = {
                "server": self.config["server"],
                "port": self.config["server_port"],
                # "password": self.config["password"].decode("utf-8"),
                "password": self.config["password"],
                "method": self.config["method"]
            }
            constr = "%s:%s@%s:%s" % (_config["method"], _config["password"],
                _config["server"], _config["port"])
            # b64str = base64.b64encode(constr.encode("utf-8")).decode("utf-8")
            b64str = base64.b64encode(constr.encode("utf-8"))
            items += [(_config, constr, b64str)]
        else:
            for port, password in self.config["port_password"].items():
                _config = {
                    "server": self.config["server"],
                    "port": port,
                    # "password": password.decode("utf-8"),
                    "password": password,
                    "method": self.config["method"]
                }
                constr = "%s:%s@%s:%s" % (_config["method"],
                    _config["password"], _config["server"], _config["port"])
                # b64str = base64.b64encode(constr.encode("utf-8")).decode("utf-8")
                b64str = base64.b64encode(constr.encode("utf-8"))
                items += [(_config, constr, b64str)]
        self.render("config.html", items=items)


class PlaneConfigHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        items = []
        if not self.config["port_password"]:
            _config = {
                "server": self.config["server"],
                "port": self.config["server_port"],
                # "password": self.config["password"].decode("utf-8"),
                "password": self.config["password"],
                "method": self.config["method"]
            }
            constr = "%s:%s@%s:%s" % (_config["method"], _config["password"],
                _config["server"], _config["port"])
            # b64str = base64.b64encode(constr.encode("utf-8")).decode("utf-8")
            b64str = base64.b64encode(constr.encode("utf-8"))
            items += [(_config, constr, b64str)]
        else:
            for port, password in self.config["port_password"].items():
                _config = {
                    "server": self.config["server"],
                    "port": port,
                    # "password": password.decode("utf-8"),
                    "password": password,
                    "method": self.config["method"]
                }
                constr = "%s:%s@%s:%s" % (_config["method"],
                    _config["password"], _config["server"], _config["port"])
                # b64str = base64.b64encode(constr.encode("utf-8")).decode("utf-8")
                b64str = base64.b64encode(constr.encode("utf-8"))
                items += [(_config, constr, b64str)]
        from pprint import pformat
        self.write('<pre>%s</pre>' % pformat(items))


class ServiceControlHandler(BaseHandler):
    def initialize(self, action=None):
        self.action = action
        BaseHandler.initialize(self)

    @tornado.web.authenticated
    def get(self):
        if self.action is None:
            self.render("control.html")
        elif self.action == "start":
            m = SupervisorController(self.svservname).start()
            self.redirect("/dashboard")
        elif self.action == "stop":
            m = SupervisorController(self.svservname).stop()
            self.redirect("/dashboard")
        elif self.action == "restart":
            m = SupervisorController(self.svservname).restart()
            self.redirect("/dashboard")
        else:
            self.redirect("/")


def main(config):
    if not options.cookie_secret:
        logging.warn('\n\n\t\t!!! WARNNING !!!\n\n'
              'You must specify the cookie_secret option. It should be a long '
              'random sequence of bytes to be used as the HMAC secret for the '
              'signature.\n\n'
              'To keep the Shadowsocks Web Interface runable as always it be, '
              'it\'s signed by a random cookie-secret option. Yes, this chould '
              'keep the service runable, but also effects the users have to '
              're-login every time the system administrator restart the '
              'service or reboot the system. YOU ARE NOTICED.\n\n'
              'You can create this HMAC string by typing following on server:\n'
              '\t%s --hmac' % sys.argv[0])
        options.cookie_secret = common.hmacstr(
            key=common.randstr(1000),
            msg=common.randstr(1000),
            hashtype='sha512')

    handlers = [
        (options.base_url + r'/', RootHandler),
        (options.base_url + r'/dashboard', DashboardHandler),
        (options.base_url + r'/login', LoginHandler),
        (options.base_url + r'/logout', LogoutHandler),
        (options.base_url + r'/config', ConfigHandler),
        (options.base_url + r'/control', ServiceControlHandler),
        (options.base_url + r'/control/start', ServiceControlHandler, dict(action="start")),
        (options.base_url + r'/control/stop', ServiceControlHandler, dict(action="stop")),
        (options.base_url + r'/control/restart', ServiceControlHandler, dict(action="restart")),
        (options.base_url + r'/hideme', PlaneConfigHandler),
    ]
    user = userlib.User("ssweb.db")
    user.db_init()
    settings = dict(
        template_path=os.path.join(os.path.dirname(__file__),
                                   'templates/default'),
        static_path=os.path.join(os.path.dirname(__file__),
                                 'templates/default/assets'),
        static_url_prefix=options.base_url+"/static/",
        cookie_secret=options.cookie_secret,
        login_url="/login",
        xsrf_cookies=True,
        debug=options.debug,
        user=user,
        svservname=options.servicename,
    )

    application = tornado.web.Application(handlers, **settings)
    application.config = config
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port, options.addr)
    print('shadowsocks-web start at %s:%s' % (options.addr, options.port))
    tornado.ioloop.IOLoop.instance().start()

def start_with_config(config):
    tornado.options.parse_command_line('')
    main(config)

if __name__ == "__main__":
    try:
        tornado.options.parse_command_line()
    except tornado.options.Error:
        sys.exit(1)

    if len(sys.argv) == 2 and sys.argv[1] == "--hmac":
        key = common.randomstr()
        msg = common.randomstr()
        print("HMAC-MD5    ( 32 bits): %s" % common.hmacstr(key, msg, "md5"))
        print("HMAC-SHA224 ( 56 bits): %s" % common.hmacstr(key, msg, "sha224"))
        print("HMAC-SHA256 ( 64 bits): %s" % common.hmacstr(key, msg, "sha256"))
        print("HMAC-SHA512 (128 bits): %s" % common.hmacstr(key, msg, "sha512"))

    elif len(sys.argv) == 2 and sys.argv[1] == "--demo":
        options.debug = True
        options.port = 8080
        options.addr = "0.0.0.0"
        options.servicename = "shadowsocks"
        options.cookie_secret = common.hmacstr(key=common.randomstr(),
                                               msg=common.randomstr())
        options.base_url = r"/ssweb"
        ss_config_filename = common.find_shadowsocks_config_file()
        if ss_config_filename is None:
            print("Can't find any shadowsocks config file. Are you sure there "
                  "installed shadowsocks already?")
            exit(1)
        print("Loading shadowsocks config file from '%s'" % ss_config_filename)
        config = common.load_shadowsocks_config(ss_config_filename)
        main(config)

    else:
        tornado.options.print_help()
        sys.exit(0)

# vim: tw=78 ts=8 et sw=4 sts=4 fdm=indent
