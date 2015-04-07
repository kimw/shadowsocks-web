# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, with_statement

import sys
import os
import random
import hmac
import json
import hashlib
from colorama import Fore, Back, Style


def hmacstr(key, msg, hashtype='sha256'):
    """
    Returns HMAC string in specified hash type. Or raise NotImplementedError on
    wrong type.

    The hash type chould be one of MD5, SHA224, SHA256 and SHA512.

    By default, the hash type is SHA256.
    """
    if hashtype.lower() == 'md5':
        hmacstr = hmac.HMAC(key.encode('utf8'), msg.encode('utf8'),
                            hashlib.md5).hexdigest()
        return hmacstr
    elif hashtype.lower() == 'sha224':
        hmacstr = hmac.HMAC(key.encode('utf8'), msg.encode('utf8'),
                            hashlib.sha224).hexdigest()
        return hmacstr
    elif hashtype.lower() == 'sha256':
        hmacstr = hmac.HMAC(key.encode('utf8'), msg.encode('utf8'),
                            hashlib.sha256).hexdigest()
        return hmacstr
    elif hashtype.lower() == 'sha512':
        hmacstr = hmac.HMAC(key.encode('utf8'), msg.encode('utf8'),
                            hashlib.sha512).hexdigest()
        return hmacstr
    else:
        raise NotImplementedError


def randomstr(leng=50):
    """
    Returns specified length random string including letters both upper and
    lower, and numbers.

    By default, the length is 50.
    """
    return ''.join(random.choice('abcdefghijklmnopqrstuvwxyz'
                                 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                                 '0123456789'
                                 '')
                   for i in range(leng))


def is_python2():
    info = sys.version_info
    if info[0] == 2:
        return True
    else:
        return False


def is_python3():
    info = sys.version_info
    if info[0] == 3:
        return True
    else:
        return False


def from_unicode_to_utf8(input):
    """
    Convert all unicode strings in the `input` into UTF-8.

    Only support Python 2.x.
    """
    if is_python2():
        if isinstance(input, dict):
            return dict((from_unicode_to_utf8(key), from_unicode_to_utf8(value)) for key, value in input.iteritems())
        elif isinstance(input, list):
            return [from_unicode_to_utf8(element) for element in input]
        elif isinstance(input, unicode):
            return input.encode('utf8')
        else:
            return input
    else:
        raise NotImplementedError


def load_shadowsocks_config(filename):
    """Returns shadowsocks config in a dictionary."""
    assert os.path.isfile(filename)
    with open(filename) as f:
        j = json.load(f)
    if is_python2():
        j = from_unicode_to_utf8(j)
    j.setdefault("port_password", None)
    j.setdefault("workers", 1)
    j.setdefault("user", None)
    return j


def load_config(filename):
    """Returns shadowsocks-web config in a dictionary."""
    assert os.path.isfile(filename)
    with open(filename) as f:
        j = json.load(f)
    j = j.get("web", None)
    if is_python2():
        j = from_unicode_to_utf8(j)
    return j


def find_shadowsocks_config_file(deeply=False):
    """
    Find the shadowsocks config file in system.

    It will try in order as following:
        1. ./shadowsocks.json
        2. ~/shadowsocks.json
        3. ~/.shadowsocks.json
        4. /etc/shadowsocks.json
        5. /etc/shadowsocks/config.json
        6. /etc/shadowsocks-libev/config.json
    And returns the first one met (deeply == False, by default) or all the
    filenames that found (deeply == True).

    If there's nothing found, it returns None.
    """
    check_list = [
        os.path.abspath("shadowsocks.json"),
        os.path.join(os.environ["HOME"], "shadowsocks.json"),
        os.path.join(os.environ["HOME"], ".shadowsocks.json"),
        "/etc/shadowsocks.json",
        "/etc/shadowsocks/config.json",
        "/etc/shadowsocks-libev/config.json"]
    if not deeply:
        for filename in check_list:
            if os.path.isfile(filename):
                return filename
    else:
        config_files = []
        for filename in check_list:
            if os.path.isfile(filename):
                config_files += [filename]
        if config_files:
            return config_files
    return None


def find_config_file(deeply=False):
    """An alias of find_shadowsocks_config_file()."""
    return find_shadowsocks_config_file(deeply)


def moo():
    s = ("\x20\x20\x20\x20\x20\x20\x20\x20\x20\x28\x5f\x5f\x29\x0a\x20\x20\x20"
         "\x20\x20\x20\x20\x20\x20\x28\x1b\x5b\x33\x33\x6d\x6f\x6f\x1b\x5b\x33"
         "\x39\x6d\x29\x0a\x20\x20\x20\x2f\x2d\x2d\x2d\x2d\x2d\x2d\x5c\x2f\x0a"
         "\x20\x20\x2f\x20\x7c\x20\x20\x20\x20\x7c\x7c\x0a\x20\x1b\x5b\x33\x31"
         "\x6d\x2a\x1b\x5b\x33\x39\x6d\x20\x20\x2f\x5c\x2d\x2d\x2d\x2f\x5c\x0a"
         "\x20\x20\x20\x20\x1b\x5b\x33\x32\x6d\x7e\x7e\x20\x20\x20\x7e\x7e\x1b"
         "\x5b\x33\x39\x6d\x0a\x2e\x2e\x2e\x2e\x22\x48\x61\x76\x65\x20\x79\x6f"
         "\x75\x20\x6d\x6f\x6f\x65\x64\x20\x74\x6f\x64\x61\x79\x3f\x22\x2e\x2e"
         "\x2e")
    print(s)


def is_ipaddress(address):
    """
    Check if 'address' is a valid IP4/IP6 address.
    Returns True on valid, or False on not.

    This procedure will raise a NotImplementedError exception on algorithm
    error.
    """
    if is_python2():
        import socket
        # try IP4 address
        try:
            socket.inet_pton(socket.AF_INET, address)
        except socket.error:
            pass
        else:
            return True
        # try IP6 address
        try:
            socket.inet_pton(socket.AF_INET6, address)
        except socket.error:
            return False
        else:
            return True

        raise NotImplementedError  # should never reach this line
    elif is_python3():
        import ipaddress
        try:
            ipaddress.ip_address(address)
        except ValueError:
            return False
        else:
            return True

        raise NotImplementedError  # should never reach this line
    else:
        raise NotImplementedError  # should never reach this line


def is_valid_method(method):
    """
    Check if 'method' is a valid shadowsocks method.
    Returns True on valid, or False on not.
    """
    valid_methods = ["aes-128-cfb", "aes-192-cfb", "aes-256-cfb", "aes-128-ofb",
        "aes-192-ofb", "aes-256-ofb", "aes-128-ctr", "aes-192-ctr",
        "aes-256-ctr", "aes-128-cfb8", "aes-192-cfb8", "aes-256-cfb8",
        "aes-128-cfb1", "aes-192-cfb1", "aes-256-cfb1", "bf-cfb",
        "camellia-128-cfb", "camellia-192-cfb", "camellia-256-cfb", "cast5-cfb",
        "chacha20", "des-cfb", "idea-cfb", "rc2-cfb", "rc4", "rc4-md5",
        "salsa20", "seed-cfb", "table"]
    if method in valid_methods:
        return True
    return False


def infoo(msg):
    print(Fore.GREEN + msg + Fore.RESET)


def warnn(msg):
    print(Fore.YELLOW + msg + Fore.RESET)


def errr(msg):
    print(Fore.RED + msg + Fore.RESET)


def debugg(msg):
    print(Fore.BLACK + Style.BRIGHT + msg + Style.RESET_ALL)

# vim: tw=78 ts=8 et sw=4 sts=4 fdm=indent
