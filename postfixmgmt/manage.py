import sys
from werkzeug.datastructures import MultiDict
from flask import request
from flaskext.script import Manager, prompt_pass, prompt_choices
from postfixmgmt import app, db, __version__
from postfixmgmt.models import Domain, Address
from postfixmgmt.forms import DomainAddForm


manager = Manager(app)

def validate_fields(fields):
    for name, field in fields._fields.iteritems():
        return validate_field(field)

def validate_field(field):
    if field.validate(field.raw_data):
        return True
    return False

def print_field_errors(obj, fields):
    print "Errors where found when adding '%s'" % obj
    for name, field in fields._fields.iteritems():
        for error in field.errors:
            print "- %s" % error
    sys.exit()

def list_domains():
    print "Domains:"
    for d in Domain.query.all():
        print "- %s" % d.name, "[%s]" % d.description if d.description else ""

def add_domain(**values):
    request.form = DomainAddForm(MultiDict(values))
    if not validate_fields(request.form):
        print_field_errors(values['name'], request.form)
    d = Domain(values['name'], values['description'])
    db.session.add(d)
    db.session.commit()
    print "Domain '%s' successfully added" % values['name']

def delete_domain(**values):
    if not values['name']:
        print "You need to provide a domain"
        sys.exit()
    d = Domain.query.filter_by(name=values['name']).first()
    if not d:
        print "Could not find domain '%s'" % values['name']
        sys.exit()
    db.session.delete(d)
    db.session.commit()
    print "Domain '%s' successfully removed" % values['name']

def edit_domain(**values):
    if not values['name']:
        print "You need to provide a domain"
        sys.exit()
    d = Domain.query.filter_by(name=values['name']).first()
    if not d:
        print "Could not find domain '%s'" % values['name']
        sys.exit()
    d.description = values['description']
    db.session.add(d)
    db.session.commit()
    print "Domain '%s' successfully modified" % values['name']

@manager.option("-d", "--desc", dest="description", help="Description of the domain. [default: '']")
@manager.option("-n", "--name", dest="name", help="Domain name")
@manager.option("-m", "--method", dest="method", choices=('list', 'add', 'edit', 'del'), required=True)
def domain(**values):
    if values['method'] == 'list':
        list_domains()
    if values['method'] == 'add':
        add_domain(**values)
    if values['method'] == 'del':
        delete_domain(**values)
    if values['method'] == 'edit':
        edit_domain(**values)

@manager.option("-a", "--active", dest="active")
@manager.option("-u", "--username", dest="username")
@manager.option("-d", "--domain", dest="domain")
@manager.option("-m", "--method", dest="method", choices=('list', 'add', 'edit', 'del'), required=True)
def address(**values):
    if values['method'] == "list":
        list_addresses(**values)
    if values['method'] == "add":
        add_address(**values)

def list_addresses(**values):
    if values['domain']:
        domains = (Domain.query.filter_by(name=values['domain']).first(),)
    else:
        domains = Domain.query.all()
    for d in domains:
        print "Addresses for %s:" % d.name
        for a in Address.query.filter_by(domain=d):
            print "- %s@%s active:%s" % (a.username, a.domain.name, a.active)

def add_address(**values):
    domain = prompt_choices("Domain (%s@DOMAIN)" % values['username'], (d.name for d in Domain.query.order_by('-name')))
    passwd = prompt_pass("Password")

if __name__ == "__main__":
    manager.run()
