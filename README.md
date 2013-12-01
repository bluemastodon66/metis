# info
Ver.1.0
Last Updated On 2013.11.28
# Extra Server
Redis-Server

# requirements
linux ubuntu:
    apt-get install redis-server
    apt-get install python-mysqldb
    apt-get install python-imaging
    apt-get install python-redis

# Web Server
Nginx (recommended)

# DataBase
Mysql 4.x (InnoDB supported)

# Other Packages of python
Tornado 3.1.1
SqlAlchemy 0.8
--------------------------------------
# installation

create db
import to db from /sql/struction-only.ssql
python install.py
    this will add default admin account
    default account is 'admin' password is '1234'
    you can change the default admin account's name and password at the very top of line (install.py).

# settings (settings.py)
All the settings of this project would be located in settings.py
Including:
Mysql Db Settings
Redis Settings
Cookis Secret
WebRoot path

--------------------------------------
command line:
py_email_test.py # to test your email is valid or not
py_img_test.py # to test your image lib is working fine?




