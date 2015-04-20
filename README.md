shadowsocks-web
===============

shadowsocks-web (or you can say ssweb) is a shadowsocks web interface, which can:

1. Statistics shadowsocks run time information.
2. Control shadowsocks (start / stop / restart).
3. Manage the shadowsocks configurations, and config file.
4. Display shadowsocks qrcode for easier mobile surfer.

Currently, shadowsocks-web implement the goals above by supervisor unix sock.
Maybe it could able to control shadowsocks directly sometimes in the future.


LICENSE
-------
The license is still in choosing.  But you can use it as free.


INSTALL
-------

For keep the shadowsocks-web run up well, the supervisor, shadowsocks, and nginx is needed.
In this guide, we will install the applications above and shadowsocsk-web it-self step by step.
In this guide, I assume that you have a ubuntu box, and use `apt-get` to install applications what we need.
If you have a box with different system, just replace this command as you need. (e.g., yum in centos)


###Install supervisor

supervisor is a service runner.
It helps us to keep shadowsocks and shadowsocks-web run in back as a daemon.
On ubuntu box, you can install supervisor by command:

```shell
sudo apt-get install supervisor
```

By default, the ubuntu installed supervisor run as root.
As you known, it's not safe.
So, I deside to set up a new user named as 'supervisor' and a new user group 'supervisor', and keep application running under it's permission by following commands.

```shell
sudo addgroup --system supervisor
sudo adduser --system --shell /bin/false --ingroup supervisor --disabled-password --disabled-login supervisor
sudo chown -R supervisor.supervisor /var/log/supervisor
```

The default supervisord config file have some secure insurece.
You can make some modification to take care of this issue ;-)
All modifications are one change and one add.

1. Change the 'chmod' option in '[unix_http_server]' section to 0660 instead of default 0700.
2. Add a new 'chown' option in the same section as in the sample following:

```
[unix_http_server]
file=/var/run/supervisor.sock
chmod=0660                    ; the default chmod=0700, we changed this option into 0660
chown=supervisor:supervisor   ; superviosor will run as user 'supervisor' and under 'supervisor' group

[supervisord]
logfile=/var/log/supervisor/supervisord.log
pidfile=/var/run/supervisord.pid
childlogdir=/var/log/supervisor
directory=/home/supervisor

[rpcinterface:supervisor]
supervisor.rpcinterface_factory=supervisor.rpcinterface:make_main_rpcinterface

[supervisorctl]
serverurl=unix:///var/run/supervisor.sock

[include]
files=/etc/supervisor/conf.d/*.conf
```


###Install shadowsocks

After the supervisor installation completed, we should start to install shadowsocks.
If you have installed shadowsocks already, you'd better glance at this section.
Make sure your shadowsocks has the same configurations, if you decide to keep up follow me with this guide.

First of all we should install shadowsocks.

```shell
sudo pip install shadowsocks
```

Because some distribution dose not installed python-pip (a.k.a pip) by default, you may get 'command not found: python-pip' error sometimes.
If you get this error, try to install python-pip (a.k.a pip) before going.

Limit application running under a specified user is always a good idea.
So, we'll create a new user and user group as the same name 'shadowsocks' as follow.
If you've installed shadowsocks by your own, and did not care about this issue, you'd better update it yourself.

```shell
sudo addgroup --system shadowsocks
sudo adduser --system --shell /bin/false --ingroup shadowsocks --disabled-password --disabled-login shadowsocks
```

If you want your shadowsocks run as a daemon by supervisor, you could create a supervisor config file as follow.
TODO: This file should be placed in path '/etc/supervisor/conf.d/shadowsocks.conf', if you follow me from the start of this guide. Or ??decided?? by yourself, if you didn't.

```
; '/etc/supervisor/conf.d/shadowsocks.conf'

[program:shadowsocks]
command=/usr/local/bin/ssserver -c /etc/shadowsocks.json
directory=/home/shadowsocks
autostart=true
redirect_stderr=true
stdout_logfile=/var/log/supervisor/shadowsocks.log
stderr_logfile=/var/log/supervisor/shadowsocks.err
```


###Install shadowsocks-web

set up your shadowsocks and shadowsocks-web as follow.

```shell
sudo adduser --system --shell /bin/false --ingroup shadowsocks --disabled-password --disabled-login shadowsocks-web
sudo adduser shadowsocks-web supervisor

sudo adduser $USER supervisor

cd /home/shadowsocks-web
sudo chown $USER .
git clone git@git.coding.net:kimw/ssweb.git .
sudo chown -R shadowsocks-web.shadowsocks .

sudo chown shadowsocks.shadowsocks /etc/shadowsocks.json

sudo pip install tornado

python web.py --make-config > /tmp/shadowsocks.json
sudo mv /tmp/shadowsocks.json /etc/shadowsocks.json
sudo chown shadowsocks.shadowsocks /etc/shadowsocks.json
sudo chmod 660 /etc/shadowsocks.json
```

'/etc/supervisor/conf.d/shadowsocks-web.conf'

```
[program:shadowsocks-web]
command=/usr/bin/python /home/shadowsocks-web/web.py
directory=/home/shadowsocks-web
autostart=true
autorestart=true
user=shadowsocks-web
redirect_stderr=true
stdout_logfile=/var/log/supervisor/ssweb.log
stderr_logfile=/var/log/supervisor/ssweb-stderr.log
environment=HOME=/home/shadowsocks-web
```

Now we restart the supervisor service.

```shell
sudo service supervisor restart
```


###Install nginx

Because of secure reason, we'd better use the nginx face to internet and hide
shadowsocks-web behind it.

TODO: add docs here.


###Check

TODO: Now you can open any browser that you favorite, and type
http://x.x.x.x:8888/ssweb.


UNINSTALL
---------

###Uninstall shadowsocks-web

```shell
sudo supervisorctl stop shadowsocks-web
```

clean up stuffs other.

```shell
sudo deluser shadowsocks-web
sudo rm -rf /home/shadowsocks-web
```


###Uninstall shadowsocks

```shell
sudo supervisorctl stop shadowsocks
sudo pip uninstall shadowsocks
```

clean up stuffs other.

```shell
sudo deluser shadowsocks
sudo delgroup shadowsocks
sudo rm -rf /home/shadowsocks
```


###Uninstall supervisor

```shell
sudo apt-get remove supervisor
```

clean up stuffs other.

```shell
sudo deluser supervisor
sudo delgroup supervisor
sudo rm -rf /home/supervisor
```

###Uninstall nginx

TODO: add docs here.


CONFIG
------
under construction.
