============
Postfix MGMT
============

Usage
=====

Web
---

Start the web console using

  python postfixmgmt/server.py

And browse to

  http://localhost:5000

CLI
---

Base command

  python postfixmgmt/manage.py

Available commands
~~~~~~~~~~~~~~~~~~

Manage domains
_____________

  domain

List domains
____________

  domain -m list

Add a domain
____________

  domain -m add -n kura.io -d "Test domain"

Manage addresses
________________

  address


