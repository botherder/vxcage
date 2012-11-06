VxCage
======

VxCage is a WSGI Python application for managing a malware samples repository with a REST API interface.

Requirements
------------

In order to install VxCage you need to have Python (2.7) installed. Following are the required libraries.

* [bottle.py](http://www.bottlepy.org/) -- `pip install bottle`
* [sqlalchemy](http://www.sqlalchemy.org) -- `pip install sqlalchemy`

If you want to enable the fuzzy hash, you need to install [ssdeep](http://ssdeep.sourceforge.net/) and the Python bindings, [pydeep](https://github.com/kbandla/pydeep).

VxCage also requires any database engine from the [ones supported](http://docs.sqlalchemy.org/en/rel_0_7/core/engines.html). Depending to which one you pick, you'll need the required Python API. For example, in the case of MySQL you'll also need [MySQLdb](http://mysql-python.sourceforge.net/) (`pip install mysqldb`).

If you plan to run VxCage with Apache, you'll need to have mod_wsgi installed. On Ubuntu/Debian systems ``apt-get install libapache2-mod-wsgi``.

Installation
------------

First thing first, extract VxCage to your selected location and open `api.conf` and configure the path to the local folder you want to use as a storage.
You also need to configure the connection string for your database. For example:

MySQL:

    mysql://user:pass@host/database

SQLite:

    sqlite:///database.db

PostgreSQL:

    postgresql://user:pass@host/database

Refer to [SQLAlchemy](http://docs.sqlalchemy.org/en/latest/core/engines.html)'s documentation for additional details.

Now proceeds installing Apache and required modes:

    # apt-get install apache2 libapache2-mod-wsgi

Enable the mod:

    # a2enmod wsgi

If you want to enable SSL, you need to generate a certificate with OpenSSL or buy one from a certified authority.
You can also use the `make-ssl-cert` utility as following:

    # make-ssl-cert /usr/share/ssl-cert/ssleay.cnf /path/to/apache.pem

Now create a virtual host for the domain you want to host the application on. We'll enable WSGI, SSL and a basic authentication.
A valid template is the following:

    <VirtualHost *:443>
        ServerName yourwebsite.tld

        WSGIDaemonProcess yourapp user=www-data group=www-data processes=1 threads=5
        WSGIScriptAlias / /path/to/app.wsgi

        <Directory /path/to/app.wsgi>
            WSGIProcessGroup yourgroup
            WSGIApplicationGroup %{GLOBAL}
            Order deny,allow
            Allow from all
        </Directory>

        <Location />
            AuthType Basic
            AuthName "Authentication Required"
            AuthUserFile "/path/to/users"
            Require valid-user
        </Location>

        SSLEngine on
        SSLCertificateFile /path/to/apache.pem

        ErrorLog /path/to/error.log
        LogLevel warn
        CustomLog /path/to/access.log combined
        ServerSignature Off
    </VirtualHost>

Now add your user:

    # htpasswd -c /path/to/users username

You should be ready to go. Make sure to restart Apache afterwards:

    # /etc/init.d/apache2 restart


Usage
-----

You can interact with your repository with the provided REST API.

Submit a sample:

    $ curl -F file=@sample.exe -F tags="tag1 tag2" http://yourdomain.tld/malware/add

Retrieve a sample:

    $ curl http://yourdomain.tld/malware/get/<md5> > sample.exe

Find a sample by MD5:

    $ curl -F md5=<md5> http://yourdomain.tld/malware/find

Find a sample by SHA-256:

    $ curl -F sha256=<sha256> http://yourdomain.tld/malware/find

Find a sample by Ssdeep (can also search for a substring of the ssdeep hash):

    $ curl -F ssdeep=<pattern> http://yourdomain.tld/malware/find

Find a sample by Tag:

    $ curl -F tag=<tag> http://yourdomain.tld/malware/find

List existing tags:

    $ curl http://yourdomain.tld/tags/list


In case you added a basic authentication, you will need to add `--basic -u "user:pass"`. In case you added SSL support with a generated certificate, you will need to add `--insecure` and obviously make the requests to https://yourdomain.tld.


Copying
-------

VxCage is licensed under [BSD 2-Clause](http://opensource.org/licenses/bsd-license.php) and is copyrighted to Claudio Guarnieri.


Contacts
--------

Twitter: [@botherder](http://twitter.com/botherder)
