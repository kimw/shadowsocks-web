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
```

update the supervisor configurations as:

```
TODO: add supervisor configs here.
```


###install shadowsocks

TODO: add shadowsocks installation guide here.


###install shadowsocks-web

set up your shadowsocks and shadowsocks-web as follow.

```sh
sudo addgroup --system shadowsocks
sudo adduser --system --shell /bin/false --ingroup shadowsocks --disabled-password --disabled-login shadowsocks
sudo adduser --system --shell /bin/false --ingroup shadowsocks --disabled-password --disabled-login shadowsocks-web
sudo adduser shadowsocks-web supervisor

sudo adduser $USER supervisor

cd /home/shadowsocks-web
sudo chown $USER .
git clone git@git.coding.net:kimw/ssweb.git .
sudo chown -R shadowsocks-web.shadowsocks .

sudo chown shadowsocks.shadowsocks /etc/shadowsocks.json
sudo chmod 660 /etc/shadowsocks.json
```

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
