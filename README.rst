============
Postfix MGMT
============

Installation
============

Install all requirements

  pip install -r reqs.txt

Install postfix-mgmt

   python setup.py install

Create an admin account

   python manage.py admin -m add -e YOU@DOMAIN.TLD -a 1

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
**************

List domains
____________

  domain -m list

Add a domain
____________

  domain -m add -n kura.io -d "Test domain"

Manage addresses
****************

List addresses
______________

  address -m list

List addresses, filtering by domain
___________________________________

  address -m list -d kura.io

