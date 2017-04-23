# pyweb
A minimalistic Python 3 web framework.
It is built around Python WSGI web server interface and provides useful libraries such as cookies, session, database and cache.


## Features
   - It's very close to WSGI standard. You'll still see environ, start_response and response_body.
     This framework doesn't try to abstract it away.

   - Small: The overall framework is aimed to be less than 10,000 lines of code.
     Thin: There is no abstraction. You should be able to see how everything works.
     Explicit: As with The Zen of Python, there is less magic happening here. Everything should be clear and explicit.

   - Use only Python 3 standard library.
     The only exception are "psycopg2" for PostgreSQL database access and "redis" for cache and session.
     Nothing else.

   - Others:
        - 256-bit session id.
        - Fast. More than 2,500 requests/sec with database connection.


## How to install
```
 1. Use GCC 4.4 by default:
       - We must use GCC 4.4, otherwise we'll encounter "Segmentation fault" when "import numpy".
       # /usr/bin/gcc --version
       gcc (GCC) 4.1.2 20080704 (Red Hat 4.1.2-55)
       # yum install gcc44.x86_64 gcc44-c++.x86_64
       =============================================================================================================================================================================================================================================
        Package                                                       Arch                                               Version                                                             Repository                                        Size
       =============================================================================================================================================================================================================================================
       Installing:
        gcc44                                                         x86_64                                             4.4.7-1.el5                                                         base                                              12 M
        gcc44-c++                                                     x86_64                                             4.4.7-1.el5                                                         base                                             5.2 M
       Installing for dependencies:
        binutils220                                                   x86_64                                             2.20.51.0.2-5.29.el5                                                base                                             986 k
        libstdc++44-devel                                             x86_64                                             4.4.7-1.el5                                                         base                                             4.1 M
       Transaction Summary
       =============================================================================================================================================================================================================================================
       Install       4 Package(s)
       Upgrade       0 Package(s)
       Total download size: 22 M
       Is this ok [y/N]: y

       # mv /usr/bin/gcc /usr/bin/gcc.bck
       # ln -s /usr/bin/gcc44 /usr/bin/gcc
       # /usr/bin/gcc --version
       gcc (GCC) 4.4.7 20120313 (Red Hat 4.4.7-1)




 2. Installing Redis:
       - Refs:
            http://serverfault.com/questions/667857/redis-installation-on-centos-6-5
            http://sharadchhetri.com/2014/10/04/install-redis-server-centos-7-rhel-7/

       - Install Redis:
            - On RHEL 5:
                 # yum install epel-release
                   Or without yum: # rpm -Uvh http://dl.fedoraproject.org/pub/epel/5/x86_64/epel-release-5-4.noarch.rpm		--> older redis (redis 2)
                 # rpm -Uvh http://rpms.famillecollet.com/enterprise/remi-release-5.rpm						--> in order to use the latest version of redis
            - On RHEL 6:
                 # yum install epel-release
                 # rpm -Uvh http://rpms.famillecollet.com/enterprise/remi-release-6.rpm

            # yum --enablerepo=remi list available | grep -i redis
            php-nrk-Predis.noarch                         1.0.1-1.el5.remi           remi
            php-pecl-redis.x86_64                         2.2.7-1.el5.remi.5.4       remi
            python-redis.noarch                           2.0.0-2.el5                epel
            redis.x86_64                                  3.0.1-1.el5.remi           remi

            # yum --enablerepo=remi install redis
            =============================================================================================================================================================================================================================================
             Package                                                  Arch                                                   Version                                                          Repository                                            Size
            =============================================================================================================================================================================================================================================
            Installing:
             redis                                                    x86_64                                                 3.0.1-1.el5.remi                                                 remi                                                 500 k
            Installing for dependencies:
             jemalloc                                                 x86_64                                                 3.6.0-2.el5                                                      epel                                                 110 k
            Transaction Summary
            =============================================================================================================================================================================================================================================
            Install       2 Package(s)
            Upgrade       0 Package(s)
            Total download size: 610 k
            Is this ok [y/N]: y
            Importing GPG key 0x00F97F56 "Remi Collet <RPMS@FamilleCollet.com>" from /etc/pki/rpm-gpg/RPM-GPG-KEY-remi
            Is this ok [y/N]: y


       - Configure Redis:
            # vi /etc/redis.conf
bind 127.0.0.1							--> default
logfile /var/log/redis/redis.log				--> default
dir /var/lib/redis/						--> default
maxmemory 20000000						--> add this line


       - To enable overcommit_memory so that background save does not fail under low memory condition (OPTIONAL, NOT WORKING ON HOSTGATOR!):
            # vi /etc/sysctl.conf
# For Redis
vm.overcommit_memory = 1
            # sysctl -p						--> or reboot


       - Start Redis:
            # ntsysv
                 [*] redis					--> check it
            # service redis start
            # ps -ef | grep redis-server
            redis     5562     1  0 08:28 ?        00:00:00 /usr/bin/redis-server 127.0.0.1:6379
            # netstat -nlp | grep -i redis
            tcp        0      0 127.0.0.1:6379              0.0.0.0:*                   LISTEN      5562/redis-server 1


       - To uninstall Redis (OPTIONAL):
            # service redis stop
            # tar cvzf redis_20150526.tgz /var/log/redis /var/lib/redis /etc/redis.conf*
            # yum remove redis
            Is this ok [y/N]: y
            # rm -rf /etc/redis.conf.bck /etc/redis.conf.rpmsave /var/log/redis /var/lib/redis




 3. Install Python 3.5:
       - Install:
            - Refs:
                 http://stackoverflow.com/questions/8087184/installing-python3-on-rhel
                 k:\DATA\SLB\ProSource 2013.1\tips.txt
            $ wget --no-check-certificate https://www.python.org/ftp/python/3.5.0/Python-3.5.0.tgz
            $ tar xvzf Python-3.*.tgz
            $ cd Python-3.*
            $ ./configure --prefix=/opt/python3
            $ make
            $ make test					--> OPTIONAL
            $ su
            # make install
            # ln -s /opt/python3/bin/python3 /usr/bin/
            # ln -s /opt/python3/bin/pip3 /usr/bin/
            # /usr/bin/python3 -V
            Python 3.5.0

       - Update Python Installer:
            # pip3 --trusted-host pypi.python.org install --upgrade pip

       - Uninstall (OPTIONAL):
            # rm /usr/bin/python3.4
            # rm /usr/bin/python3
            # rm /usr/bin/pip3.4
            # rm -rf /opt/python3.4




 4. Install Numpy:
       - PIP has become standard package with Python now.
       - PIP will install the packages on /opt/python3.4/lib/python3.4/site-packages/

       - Test:
            # python3 -c "import numpy; numpy.test()"
            Traceback (most recent call last):
              File "<string>", line 1, in <module>
            ImportError: No module named 'numpy'


       - Install numpy:
            - Make sure you are using GCC 4.4.
            # pip3 install numpy
            # pip3 install nose						--> for numpy.test()


       - Test afterwards:
            # python3 -c "import numpy; numpy.test()"
            Ran 5234 tests in 43.511s
            OK (KNOWNFAIL=6, SKIP=17)




 5. Install Python Redis:
       - Test:
            # python3 -c "import redis"
            Traceback (most recent call last):
              File "<string>", line 1, in <module>
            ImportError: No module named 'redis'


       - Install Python Redis:
            # pip3 install redis


       - Test afterwards:
            # python3 -c "import redis"
            #




 6. Install UWSGI:
       - Refs:
            https://uwsgi-docs.readthedocs.org/en/latest/WSGIquickstart.html

       # pip3 install uwsgi

       $ vi uwsgi_test.py
#!/usr/bin/python3

def application(env, start_response):
        start_response('200 OK', [('Content-Type','text/html')])
        return [b"Hello World"]

       # /sbin/iptables -F				--> turn off firewall
       # /sbin/iptables -L -v
       Chain INPUT (policy ACCEPT 6 packets, 396 bytes)
       Chain FORWARD (policy ACCEPT 0 packets, 0 bytes)
       Chain OUTPUT (policy ACCEPT 458K packets, 94M bytes)

       $ /opt/python3/bin/uwsgi --http :9090 --wsgi-file uwsgi_test.py
       - Browse to: http://192.168.10.163:9090/
         You should see "Hello World".

       $ cd /data/prog/pyweb/
       $ /opt/python3/bin/uwsgi --http :9090 --wsgi-file start.py
       - Browse to: http://192.168.10.163:9090/
         On browser you should see "Welcome!".
       - Browse to: http://192.168.10.163:9090/user/johny?q=abc
         On browser you should see "From controller.user.index()".
         On console you should see the following:
            Path: /user/johny
            Matched Path: /user
            Extended Path: /johny
            Query String: q=abc
            [pid: 4043|app: 0|req: 2/2] 192.168.10.149 () {36 vars in 571 bytes} [Mon Dec  8 07:58:55 2014] GET /user/johny?q=abc => generated 28 bytes in 0 msecs (HTTP/1.1 200) 1 headers in 44 bytes (1 switches on core 0)

       - Tips:
            - If there is a crash on your application code, it's should not effect the subsequent calls because uwsgi will automatically restart the application.
              But in order to fix it, you would need to fix the .py code and restart the uwsgi.

            - To get the statistics of UWSGI:
                 $ elinks --source http://127.0.0.1:9191/




 6. Install PostgreSQL 9.3:
       - Refs: http://www.if-not-true-then-false.com/2012/install-postgresql-on-fedora-centos-red-hat-rhel/

       - Uninstall the currently installed PostgreSQL:
            # rpm -qa | grep -i postgresql
            # rpm -ev postgresql-jdbc-8.1.407-1jpp.4 postgresql-contrib-8.1.23-6.el5_8 postgresql-tcl-8.1.23-6.el5_8 postgresql-test-8.1.23-6.el5_8 postgresql-python-8.1.23-6.el5_8 postgresql-8.1.23-6.el5_8 postgresql-devel-8.1.23-6.el5_8 postgresql-odbc64-09.00.0200-1.el5 postgresql-pl-8.1.23-6.el5_8 postgresql-odbc-08.01.0200-3.1 postgresql-docs-8.1.23-6.el5_8 postgresql-server-8.1.23-6.el5_8

            - This leaves *only* "postgresql-libs-8.1.23-6.el5_8.i386" and "postgresql-libs-8.1.23-6.el5_8.x86_64" packages which are required by the system.


       - Upgrade from PostgreSQL 8.1:
            - On RHEL 5:
                 # rpm -Uvh http://yum.postgresql.org/9.4/redhat/rhel-5-x86_64/pgdg-redhat94-9.4-1.noarch.rpm
            - On RHEL 6:
                 # rpm -Uvh http://yum.postgresql.org/9.4/redhat/rhel-6-x86_64/pgdg-redhat94-9.4-2.noarch.rpm

            # yum list available | grep -i postgresql
            # yum install postgresql94 postgresql94-server postgresql94-devel
            =============================================================================================================================================================================================================================================
             Package                                                         Arch                                               Version                                                         Repository                                          Size
            =============================================================================================================================================================================================================================================
            Installing:
             postgresql94                                                    x86_64                                             9.4.2-1PGDG.rhel5                                               pgdg94                                             1.7 M
             postgresql94-devel                                              x86_64                                             9.4.2-1PGDG.rhel5                                               pgdg94                                             1.8 M
             postgresql94-server                                             x86_64                                             9.4.2-1PGDG.rhel5                                               pgdg94                                             5.9 M
            Installing for dependencies:
             libxslt                                                         x86_64                                             1.1.17-4.el5_8.3                                                base                                               424 k
             postgresql94-libs                                               x86_64                                             9.4.2-1PGDG.rhel5                                               pgdg94                                             227 k
            Transaction Summary
            =============================================================================================================================================================================================================================================
            Install       5 Package(s)
            Upgrade       0 Package(s)
            Total download size: 10 M
            Is this ok [y/N]: y

            - Note: We require "postgresql-devel" package in order to install "psycopg2".

            # rpm -qa | grep -i postgresql | sort
            postgresql94-9.4.2-1PGDG.rhel5
            postgresql94-devel-9.4.2-1PGDG.rhel5
            postgresql94-libs-9.4.2-1PGDG.rhel5
            postgresql94-server-9.4.2-1PGDG.rhel5
            postgresql-libs-8.1.23-10.el5_10


       - Initialize the database
            # service postgresql-9.4 initdb
            Initializing database:                                     [  OK  ]


       - Start the database automatically:
            # service postgresql-9.4 start
            # chkconfig --list postgresql-9.4
            postgresql-9.4  0:off   1:off   2:off   3:off   4:off   5:off   6:off
            # ntsysv
            [X] postgresql-9.4				--> or: chkconfig postgresql-9.4 on
            # chkconfig --list postgresql-9.4
            postgresql-9.4  0:off   1:off   2:on    3:on    4:on    5:on    6:off


       - Install Python driver:
            # pip3 install psycopg2
            ...
            Successfully installed psycopg2-2.6

            - If you have error "Error: pg_config executable not found." while installing psycopg2:
                 - Ref: http://stackoverflow.com/questions/11618898/pg-config-executable-not-found
                 # export PATH=$PATH:/usr/pgsql-9.4/bin
                 # pip3 install psycopg2

            # python3 -c "import psycopg2"


       - Access PostgreSQL for the first time:
            # su - postgres
            postgres$ psql
            postgres=# \du
                                         List of roles
             Role name |                   Attributes                   | Member of
            -----------+------------------------------------------------+-----------
             postgres  | Superuser, Create role, Create DB, Replication | {}
            postgres=# CREATE USER myuser WITH PASSWORD 'Password1';
            CREATE ROLE
            postgres=# CREATE DATABASE mytest;
            CREATE DATABASE
            postgres=# GRANT ALL PRIVILEGES ON DATABASE mytest TO myuser;
            GRANT
            postgres=# \du
                                         List of roles
             Role name |                   Attributes                   | Member of
            -----------+------------------------------------------------+-----------
             myuser    |                                                | {}
             postgres  | Superuser, Create role, Create DB, Replication | {}
            postgres=# \q


            # vi /var/lib/pgsql/9.4/data/pg_hba.conf		--> Ref: https://help.ubuntu.com/community/PostgreSQL
# local	all		all					peer			--> comment this (OPTIONAL)
local	all		all					md5			--> add this line to allow Unix domain socket connections (OPTIONAL)
# host	all		all		127.0.0.1/32		ident			--> comment this
host	all		all		127.0.0.1/32		md5			--> add this line
# host	all		all		::1/128			ident			--> comment this
host	all		all		::1/128			md5			--> add this line


            # service postgresql-9.4 restart
            kevin$ psql --host 127.0.0.1 --port 5432 --dbname mytest --username myuser --password
            Password for user myuser: Password1
            psql (9.4.2)
            Type "help" for help.
            mytest=> \q


       - Code example: https://wiki.python.org/moin/UsingDbApiWithPostgres




 7. Nginx:
       - Ref: http://wiki.nginx.org/Install

       - Installation:
            - On RHEL 5:
                 # cat > /etc/yum.repos.d/nginx.repo
[nginx]
name=nginx repo
baseurl=http://nginx.org/packages/centos/5/$basearch/
gpgcheck=0
enabled=1
            - On RHEL 6:
                 # cat > /etc/yum.repos.d/nginx.repo
[nginx]
name=nginx repo
baseurl=http://nginx.org/packages/centos/6/$basearch/
gpgcheck=0
enabled=1

            # yum list available | grep -i nginx
            collectd-nginx.x86_64                       4.10.9-1.el5                 epel
            munin-nginx.noarch                          2.0.25-2.el5                 epel
            nginx.x86_64                                1.8.0-1.el5.ngx              nginx
            nginx-debug.x86_64                          1.8.0-1.el5.ngx              nginx
            nginx-debuginfo.x86_64                      1.8.0-1.el5.ngx              nginx
            nginx-nr-agent.noarch                       2.0.0-7.el5.ngx              nginx

            # yum install nginx.x86_64
            =============================================================================================================================================================================================================================================
             Package                                               Arch                                                   Version                                                            Repository                                             Size
            =============================================================================================================================================================================================================================================
            Installing:
             nginx                                                 x86_64                                                 1.8.0-1.el5.ngx                                                    nginx                                                 362 k
            Transaction Summary
            =============================================================================================================================================================================================================================================
            Install       1 Package(s)
            Upgrade       0 Package(s)
            Total download size: 362 k
            Is this ok [y/N]: y




       - Configure Nginx:
            - Ref for Virtual Hosting: http://uwsgi-docs.readthedocs.org/en/latest/Nginx.html
            # vi /etc/nginx/conf.d/uwsgi_params
uwsgi_param QUERY_STRING $query_string;
uwsgi_param REQUEST_METHOD $request_method;
uwsgi_param CONTENT_TYPE $content_type;
uwsgi_param CONTENT_LENGTH $content_length;
uwsgi_param REQUEST_URI $request_uri;
uwsgi_param PATH_INFO $document_uri;
uwsgi_param DOCUMENT_ROOT $document_root;
uwsgi_param SERVER_PROTOCOL $server_protocol;
uwsgi_param REMOTE_ADDR $remote_addr;
uwsgi_param REMOTE_PORT $remote_port;
uwsgi_param SERVER_ADDR $server_addr;
uwsgi_param SERVER_PORT $server_port;
uwsgi_param SERVER_NAME $server_name;

            # vi /etc/nginx/conf.d/default.conf
upstream uwsgicluster {
	# server localhost:9000;
	server unix:///tmp/uwsgi.sock;
}

server {
	listen 80;
	server_name imvm-ps2016;
	access_log /data/www/imvm-ps2016/log/access_log;
	error_log /data/www/imvm-ps2016/log/error_log;
	location / {
		root /data/www/imvm-ps2016/html;
	}
	location ~ ^/q(/.*)?$ {
		uwsgi_pass uwsgicluster;
		include uwsgi_params;
	}
}

server {
	listen 80;
	server_name www.indokita.com;
	access_log /data/www/www.indokita.com/log/access_log;
	error_log /data/www/www.indokita.com/log/error_log;
	location / {
		root /data/www/www.indokita.com/html;
	}
	location ~ ^/(place|q|user)(/.*)?$ {
		uwsgi_pass uwsgicluster;
		include uwsgi_params;
	}
}

server {
	listen 80;
	server_name www.indosatu.com;
	access_log /data/www/www.indosatu.com/log/access_log;
	error_log /data/www/www.indosatu.com/log/error_log;
	location / {
		root /data/www/www.indosatu.com/html;
	}
}




       - Set up directories:
            # mkdir /data/www
            # chown kevin:kevin /data/www


            $ mkdir -p /data/www/imvm-ps2016
            $ mkdir -p /data/www/imvm-ps2016/html
            $ cat > /data/www/imvm-ps2016/html/index.html
<html>
<body>
	Welcome to imvm-ps2016
</body>
</html>
            $ mkdir -p /data/www/imvm-ps2016/log


            $ mkdir -p /data/www/www.indokita.com
            $ mkdir -p /data/www/www.indokita.com/html
            $ cat > /data/www/www.indokita.com/html/index.html
<html>
<body>
	Welcome to www.indokita.com
</body>
</html>
            $ mkdir -p /data/www/www.indokita.com/log


            $ mkdir -p /data/www/www.indosatu.com
            $ mkdir -p /data/www/www.indosatu.com/html
            $ cat > /data/www/www.indosatu.com/html/index.html
<html>
<body>
	Welcome to www.indosatu.com
</body>
</html>
            $ mkdir -p /data/www/www.indosatu.com/log




       - Turn off SELinux:
            # sestatus
            SELinux status:                 enabled
            SELinuxfs mount:                /selinux
            Current mode:                   enforcing
            Mode from config file:          enforcing
            Policy version:                 24
            Policy from config file:        targeted
            # vi /etc/selinux/config
            SELINUX=disabled					--> default: SELINUX=enforcing
            # setenforce permissive


       - Start Nginx:
            # ntsysv
                 [*] nginx					--> check it
            # service nginx start

       - Browse to: http://www.indokita.com/
         You should see: Welcome to www.indokita.com

       - Browse to: http://www.indosatu.com/
         You should see: Welcome to www.indosatu.com




    Nginx misc (OPTIONAL):
       - Enable zip compression:
server {
        listen 80;
        server_name imvm-ps2016;
        access_log /data/www/imvm-ps2016/log/access_log;
        error_log /data/www/imvm-ps2016/log/error_log;
        location / {
                root /data/www/imvm-ps2016/html;
                gzip on;
        }
        location ~ ^/q(/.*)?$ {
                uwsgi_pass uwsgicluster;
                include uwsgi_params;
        }
        gzip on;
        gzip_types text/html text/css application/javascript;
        gzip_min_length 128;
}
```
