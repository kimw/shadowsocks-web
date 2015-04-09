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
import pprint
import json
from colorama import Fore

import userlib
import common
from common import infoo, warnn, errr, debugg
from controller import SupervisorController


define("base_url", type=str, default="", help="the url prefix")
define("host", type=str, default='localhost', help="run on the given host")
define("port", type=int, default=8888, help="run on the given port")
define("debug", type=bool, default=False, help="running in debug mode")
define("service_name", type=str, default="shadowsocks",
       help="shadowsocks's service name in supervisor")
define("cookie_secret", type=str, default=None,
       help="You must specify the cookie_secret option. It should be a long "
            "random sequence of bytes to be used as the HMAC secret for the "
            "signature. You can create this HMAC string with --hmac option.")
define("hmac", type=None, default=False, help="create a HMAC string")
define("config", type=str, metavar="path", help="path to config file")


class BaseHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.user = self.application.settings["user"]  # make the variable name shorter

    @property
    def config(self):
        """Make the variable name shorter."""
        return self.application.config

    @property
    def config_filename(self):
        """Make the variable name shorter."""
        return self.application.config_filename

    @property
    def svservname(self):
        """Make the variable name shorter."""
        return self.application.settings["svservname"]

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

        if self.user.find(username=username, password=password):
            self.set_secure_cookie("_t", self.get_argument("username"))
            self.redirect(self.get_argument("next", "/"))
            return

        # Create account by password in the config file while first time login.
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
        if common.is_python3() or common.is_python2():
            msg = SupervisorController(self.svservname).get_info()
            self.render("dashboard.html", msg=msg)
        else:
            raise NotImplementedError


class ConfigHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        def shorter(method, password, host, port):
            uri = "%s:%s@%s:%s" % (method, password, host, port)
            uri_base64 = base64.b64encode(uri.encode("utf-8")).decode("utf-8")
            port_password = dict(port=port, password=password)
            return port_password, uri, uri_base64

        items = dict(server=self.config["server"], method=self.config["method"],
            timeout=self.config["timeout"], workers=self.config["workers"])
        if self.config["port_password"] is None:
            items["length"] = 1
            port_password, uri, uri_base64 = shorter(self.config["method"],
                self.config["password"], self.config["server"],
                self.config["server_port"])
            items[0] = {"port_password": port_password, "uri": uri,
                "uri_base64": uri_base64}
        else:
            items["length"] = len(self.config["port_password"].items())
            i = 0
            for port, password in self.config["port_password"].items():
                port_password, uri, uri_base64 = shorter(self.config["method"],
                    password, self.config["server"], port)
                items[i] = {"port_password": port_password, "uri": uri,
                    "uri_base64": uri_base64}
                i += 1
        self.render("config.html", items=items)

    @tornado.web.authenticated
    def post(self):
        config = dict()
        config["server"] = self.get_argument("server")
        config["method"] = self.get_argument("method")
        config["timeout"] = int(self.get_argument("timeout"))
        config["workers"] = int(self.get_argument("workers", 1))
        config["port"] = self.get_arguments("port")
        config["password"] = self.get_arguments("password")

        # because of security reason, the `user` option must edit in cli.
        # so, we just keep the original value of `user` from config file.
        if self.config["user"] is not None:
            config["user"] = self.config["user"]

        # keep the original value of 'web' from config file
        if self.config["web"] is not None:
            config["web"] = self.config["web"]

        # check if the values in `config` are valid.
        # validating config["server"]
        if not common.is_ipaddress(config["server"]):
            raise ValueError
        # validating config["method"]
        if not common.is_valid_method(config["method"]):
            raise ValueError
        # validating config["timeout"]
        if config["timeout"] < 300:
            raise ValueError
        # validating config["workers"]
        if config["workers"] < 1:
            raise ValueError
        # validating config["port"]
        for i in range(len(config["port"])):
            if int(config["port"][i]) < 1 or int(config["port"][i]) > 65535:
                raise ValueError
        # validating config["password"]
        for i in range(len(config["password"])):
            if config["password"][i] is None:
                raise ValueError

        if len(config["port"]) > 1:
            _ = dict()
            for i in range(len(config["port"])):
                _[config["port"][i]] = config["password"][i]
            config["port_password"] = _
            del config["port"]
            del config["password"]
        else:
            config["server_port"] = int(config["port"][0])
            config["password"] = config["password"][0]
            del config["port"]

        try:
            with open(self.config_filename, "wt") as f:
                json.dump(config, f, indent=4, sort_keys=True)
        except PermissionError:
            msg = ("Don't have the permission to write config file '%s'."
                    % self.config_filename)
            logging.error(msg)
            self.render("error.html", message=msg)
            return
        self.application.config = common.load_shadowsocks_config(
            self.config_filename)
        self.redirect("/config")


class PlaneConfigHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        def shorter(method, password, host, port):
            uri = "%s:%s@%s:%s" % (method, password, host, port)
            uri_base64 = base64.b64encode(uri.encode("utf-8")).decode("utf-8")
            port_password = dict(port=port, password=password)
            return port_password, uri, uri_base64

        items = dict(server=self.config["server"], method=self.config["method"])
        if self.config["port_password"] is None:
            items["length"] = 1
            port_password, uri, uri_base64 = shorter(self.config["method"],
                self.config["password"], self.config["server"],
                self.config["server_port"])
            items[0] = {"port_password": port_password, "uri": uri,
                "uri_base64": uri_base64}
        else:
            items["length"] = len(self.config["port_password"].items())
            i = 0
            for port, password in self.config["port_password"].items():
                port_password, uri, uri_base64 = shorter(self.config["method"],
                    password, self.config["server"], port)
                items[i] = {"port_password": port_password, "uri": uri,
                    "uri_base64": uri_base64}
                i += 1
        common.moo()
        self.write("<pre>%s</pre>" % pprint.pformat(items))


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


if common.is_python2():
    PermissionError = IOError


def main(config, config_filename):
    if not options.cookie_secret:
        logging.warn("\n\n\t\t!!! WARNNING !!!\n\n"
              "You must specify the cookie_secret option. It should be a long "
              "random sequence of bytes to be used as the HMAC secret for the "
              "signature.\n\n"
              "To keep the Shadowsocks Web Interface runable as always it be, "
              "it's signed by a random cookie_secret option. Yes, this chould "
              "keep the service runable, but also effects the users have to "
              "re-login every time the system administrator restart the "
              "service or reboot the system. YOU ARE NOTICED.\n\n"
              "You can create this HMAC string by typing following on server:\n"
              "\t%s --hmac" % sys.argv[0])
        options.cookie_secret = common.hmacstr(
            key=common.randomstr(1000),
            msg=common.randomstr(1000),
            hashtype='sha512')

    handlers = [
        (options.base_url + r"/", RootHandler),
        (options.base_url + r"/dashboard", DashboardHandler),
        (options.base_url + r"/login", LoginHandler),
        (options.base_url + r"/logout", LogoutHandler),
        (options.base_url + r"/config", ConfigHandler),
        (options.base_url + r"/control", ServiceControlHandler),
        (options.base_url + r"/control/start", ServiceControlHandler,
            dict(action="start")),
        (options.base_url + r"/control/stop", ServiceControlHandler,
            dict(action="stop")),
        (options.base_url + r"/control/restart", ServiceControlHandler,
            dict(action="restart")),
        (options.base_url + r"/hideme", PlaneConfigHandler),
    ]
    user = userlib.User("ssweb.db")
    user.db_init()
    settings = dict(
        template_path=os.path.join(os.path.dirname(__file__),
                                   "templates/default"),
        static_path=os.path.join(os.path.dirname(__file__),
                                 "templates/default/assets"),
        static_url_prefix=options.base_url+"/static/",
        cookie_secret=options.cookie_secret,
        login_url="/login",
        xsrf_cookies=True,
        debug=options.debug,
        user=user,
        svservname=options.service_name)

    application = tornado.web.Application(handlers, **settings)
    application.config = config
    application.config_filename = config_filename
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port, options.host)
    infoo("shadowsocks-web start at %s:%s" % (options.host, options.port))
    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        infoo("shadowsocksweb is stoped.")


def start(demo=False):
    if demo:
        # load demo options. it will escape config file.
        cookie_secret = common.hmacstr(common.randomstr(), common.randomstr())
        args = [sys.argv[0], "--debug", "--host=0.0.0.0", "--port=8080",
            "--base_url=/ssweb", "--service_name=shadowsocks",
            "--cookie_secret=" + cookie_secret, "--logging=debug"]
        options.parse_command_line(args)
    else:
        # pre-parse the command line options. it will be over write by 'load
        # options from config file'. by then, it yet loaded.
        options.parse_command_line()

        if options.config is not None:
            # load options from specified config file
            if not os.path.isfile(options.config):
                errr("Can't find config file '%s'." % options.config)
                exit(1)
            else:
                config = common.load_config(options.config)
                if config is not None:
                    infoo("Load config from file '%s'." % options.config)
                    args = [sys.argv[0]]
                    for item in config:
                        args += ["--%s=%s" % (item, config[item])]
                    try:
                        options.parse_command_line(args)
                    except tornado.options.Error:
                        errr("Error on config file option.")
                        sys.exit(1)
        else:
            # load options from config file, if the file exists.
            config_file = common.find_config_file()
            if config_file is not None:
                config = common.load_config(config_file)
                if config is not None:
                    infoo("Load config from file '%s'." % config_file)
                    args = [sys.argv[0]]
                    for item in config:
                        args += ["--%s=%s" % (item, config[item])]
                    try:
                        options.parse_command_line(args)
                    except tornado.options.Error:
                        errr("Error on config file option.")
                        sys.exit(1)

        # load options from command line
        try:
            options.parse_command_line()
        except tornado.options.Error:
            errr("Error on command line option.")
            sys.exit(1)
    debugg("options: %s" % json.dumps(options.as_dict(), sort_keys=True))
    logging.debug("options: %s" % json.dumps(options.as_dict(), sort_keys=True))

    # load shadowsocks configuration
    ss_config_filename = common.find_shadowsocks_config_file()
    if ss_config_filename is None:
        errr("Can't find any shadowsocks config file. Are you sure there "
             "installed shadowsocks already?")
        exit(1)
    config = common.load_shadowsocks_config(ss_config_filename)
    infoo("Loading shadowsocks config from file '%s'." % ss_config_filename)
    main(config, ss_config_filename)


def print_hmac():
    key = common.randomstr()
    msg = common.randomstr()
    print((Fore.GREEN + "HMAC-MD5    ( 32 bits):" + Fore.RESET + " %s")
        % common.hmacstr(key, msg, "md5"))
    print((Fore.GREEN + "HMAC-SHA224 ( 56 bits):" + Fore.RESET + " %s")
        % common.hmacstr(key, msg, "sha224"))
    print((Fore.GREEN + "HMAC-SHA256 ( 64 bits):" + Fore.RESET + " %s")
        % common.hmacstr(key, msg, "sha256"))
    print((Fore.GREEN + "HMAC-SHA512 (128 bits):" + Fore.RESET + " %s")
        % common.hmacstr(key, msg, "sha512"))


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--hmac":
        print_hmac()
    elif len(sys.argv) == 2 and sys.argv[1] == "--demo":
        start(demo=True)
    else:
        start()

# vim: tw=78 ts=8 et sw=4 sts=4 fdm=indent
