shadowsocks-web
===============

shadowsocks-web (or you can say ssweb) is a shadowsocks web interface, which can:

1. stat shadowsocks run time information
2. controll shadowsocks (start / stop / restart)
3. manage the shadowsocks configurations, and config file
4. display shadowsocks qrcode for easier mobile sufering.

currently, shadowsocks-web implement the goals above by supervisor unix sock.
it may control shadowsocks directly sometimes in the furture.


LICENSE
-------
The license is still in choosing. But you can use it as free.


INSTALL
-------

###install supervisor

```sh
sudo apt-get install supervisor
```

set up your supervisor as follow.

```sh
sudo addgroup --system supervisor
sudo adduser --system --shell /bin/false --ingroup supervisor --disabled-password --disabled-login supervisor
sudo chown -R supervisor.supervisor /var/log/supervisor
```

update the supervisor configurations as:

```
[unix_http_server]
file=/var/run/supervisor.sock
chmod=0660
chown=supervisor:supervisor

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


###install shadowsocks

```sh
sudo pip install shadowsocks
```

```sh
sudo addgroup --system shadowsocks
sudo adduser --system --shell /bin/false --ingroup shadowsocks --disabled-password --disabled-login shadowsocks
```

'/etc/supervisor/conf.d/shadowsocks.conf'

```
[program:shadowsocks]
command=/usr/local/bin/ssserver -c /etc/shadowsocks.json
directory=/home/shadowsocks
autostart=false
redirect_stderr=true
stdout_logfile=/var/log/supervisor/shadowsocks.log
stderr_logfile=/var/log/supervisor/shadowsocks-err.log
```


###install shadowsocks-web

set up your shadowsocks and shadowsocks-web as follow.

```sh
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

###Restart supervisor

```sh
sudo service supervisor restart
```


UNINSTALL
---------

###uninstall shadowsocks-web

```sh
sudo supervisorctl stop shadowsocks-web
```

clean up stuffs other.

```sh
sudo deluser shadowsocks-web
sudo rm -rf /home/shadowsocks-web
```


###uninstall shadowsocks

```sh
sudo supervisorctl stop shadowsocks
sudo pip uninstall shadowsocks
```

clean up stuffs other.

```sh
sudo deluser shadowsocks
sudo delgroup shadowsocks
sudo rm -rf /home/shadowsocks
```


###uninstall supervisor

```sh
sudo apt-get remove supervisor
```

clean up stuffs other.

```sh
sudo deluser supervisor
sudo delgroup supervisor
sudo rm -rf /home/supervisor
```


CONFIG
------
under constrction.
