import sys
from werkzeug.datastructures import ImmutableDict, MultiDict
from flask import request
from flaskext.script import Manager
from postfixmgmt import app, db, __version__
from postfixmgmt.models import Domain
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

if __name__ == "__main__":
    manager.run()
