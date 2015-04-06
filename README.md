shadowsocks-web
===============

shadowsocks-web (or you can call it as ssweb) is a shadowsocks web interface. which can:

1. stat shadowsocks running information
2. controll shadowsocks (start / stop / restart)
3. manage the shadowsocks configuration file
4. display shadowcosks qrcode

currently, shadowsocks-web implement the goals above by supervisor unix sock.
it may control shadowsocks directly sometimes in the furture.

license
-------
The license is still in choosing. But you can use it as free anyway.

install
-------
under constrction.

config
------
under constrction.

TODO
----
- [ ] check if supervisor installed in run time.
- [x] parse shadowsocks json config file in run time.
- [x] change shadowsocks json config file in run time.
- [ ] change shadowsocks-web config file in run time.
- [ ] need an error message html page.
- [ ] create default shadowsocks json config file in cli.
- [ ] create shadowsocks-web config file in cli. (in json format? combine with the ss config file?)
- [ ] ready to run in async mode?
- [ ] fully support template
