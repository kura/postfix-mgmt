import os
import hashlib
from flask import Flask, render_template, request, redirect, session, escape, flash, g, url_for, abort
from postfixmgmt import app, db, __version__, smart_str
from postfixmgmt.models import Admin, get_or_create, Session, Domain, Address, Alias
from postfixmgmt.auth import create_password, check_password, md5_password
from postfixmgmt.forms import LoginForm, DomainAddForm, DomainEditForm, AddressAddForm, AddressEditForm, \
     AddressPasswordEditForm, AliasAddForm, AliasEditForm, AdminAddForm, AdminEditForm, AdminEditPassword


@app.before_request
def before_request():
    g.version = __version__
    if 'email' in session:
        g.user = get_admin()

@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'admin'):
        g.user = None

def is_logged_in():
    if 'email' not in session or 'token' not in session:
        return False
    if Admin.query.filter_by(email=session['email']).first() and \
       Session.query.filter_by(key=session['token']).first():
        return True
    return False

@app.route("/")
def index():
    if not is_logged_in():
        flash("You need to log in to access this page")
        return redirect(url_for("login"))
    else:
        return render_template("index.html")

@app.route("/domains")
def domains_index():
    if not is_logged_in():
        flash("You need to log in to access this page")
        return redirect(url_for("login"))
    else:
        return render_template("domain_index.html", 
                               domains=Domain.query.all())

@app.route("/domain/add", methods=['GET', 'POST'])
def domain_add():
    if not is_logged_in():
        flash("You need to log in to access this page")
        return redirect(url_for("login"))
    form = DomainAddForm(request.form)
    if form.validate_on_submit():
        d = Domain(request.form['name'], request.form['description'])
        db.session.add(d)
        db.session.commit()
        flash("Domain '%s' successfully added" % request.form['name'])
        return redirect(url_for("domains_index"))
    return render_template("domain_add.html", form=form)

@app.route("/domain/edit/<name>", methods=['GET', 'POST'])
def domain_edit(name):
    if not is_logged_in():
        flash("You need to log in to access this page")
        return redirect(url_for("login"))
    d = Domain.query.filter_by(name=name).first()
    if not d:
        flash("Valid domain '%s'" % (name))
        return redirect(url_for("domains_index"))
    form = DomainEditForm(obj=d)
    if form.validate_on_submit():
        form = DomainEditForm(obj=request.form)
        d = Domain.query.filter_by(id=request.form['id']).first()
        d.description = request.form['description']
        db.session.add(d)
        db.session.commit()
        flash("Domain '%s' successfully modified" % (d.name))
        return redirect(url_for("domains_index"))
    return render_template("domain_edit.html", form=form, name=name)

@app.route("/domain/delete/<name>")
def domain_delete(name):
    if not is_logged_in():
        flash("You need to log in to access this page")
        return redirect(url_for("login"))
    if not name:
        flash("Invalid domain")
        return redirect(url_for("domains_index"))
    d = Domain.query.filter_by(name=name).first()
    if not d:
        flash("Invalid domain")
        return redirect(url_for("domains_index"))
    for a in Address.query.filter_by(domain=d).all():
        db.session.delete(u)
    db.session.delete(d)
    db.session.commit()
    flash("Domain '%s' successfully deleted" % d.name)
    return redirect(url_for("domains_index"))

@app.route("/addresses")
def addresses_index():
    if not is_logged_in():
        flash("You need to log in to access this page")
        return redirect(url_for("login"))
    else:
        return render_template("address_index.html", 
                               addresses=Address.query.all())

@app.route("/address/add", methods=['GET', 'POST'])
def address_add():
    if not is_logged_in():
        flash("You need to log in to access this page")
        return redirect(url_for("login"))
    form = AddressAddForm(request.form)
    choices = [(d.name, d.name) for d in Domain.query.order_by('-name')]
    form.domain.choices = choices
    if form.validate_on_submit():
        form = AddressAddForm(request.form)
        form.domain.choices = choices
        d = Domain.query.filter_by(name=request.form['domain']).first()
        active = False
        if 'active' in request.form and request.form['active'] == "y": active = True
        a = Address(request.form['username'], d, \
                    md5_password(request.form['password']), active)
        db.session.add(a)
        db.session.commit()
        flash("Address '%s@%s' successfully added" % (a.username, a.domain.name))
        return redirect(url_for("addresses_index"))
    return render_template("address_add.html", form=form)

@app.route("/address/edit/<username>/<domain>", methods=['GET', 'POST'])
def address_edit(username, domain):
    if not is_logged_in():
        flash("You need to log in to access this page")
        return redirect(url_for("login"))
    a = Address.query.filter_by(username=username, 
                                domain=Domain.query.filter_by(name=domain).first()
                                ).first()
    if not a:
        flash("Valid address '%s@%s'" % (username, domain))
        return redirect(url_for("addresses_index"))
    form = AddressEditForm(obj=a)
    choices = [(d.name, d.name) for d in Domain.query.order_by('-name')]
    form.domain.choices = choices
    form.domain.default = (domain, domain)
    if form.validate_on_submit():
        form = AddressEditForm(obj=request.form)
        d = Domain.query.filter_by(name=request.form['domain']).first()
        active = False
        if 'active' in request.form and request.form['active'] == "y":
            active = True
        a = Address.query.filter_by(id=request.form['id']).first()
        a.username = request.form['username']
        a.domain = d
        a.active = active
        db.session.add(a)
        db.session.commit()
        flash("Address '%s@%s' successfully modified" % (a.username, a.domain.name))
        return redirect(url_for("addresses_index"))
    return render_template("address_edit.html", form=form, 
                           username=a.username, domain=a.domain.name)

@app.route("/address/password/<username>/<domain>", methods=['GET', 'POST'])
def address_password_edit(username, domain):
    if not is_logged_in():
        flash("You need to log in to access this page")
        return redirect(url_for("login"))
    a = Address.query.filter_by(username=username, 
                                domain=Domain.query.filter_by(name=domain).first()
                                ).first()
    if not a:
        flash("Invalid address '%s@%s'" % (username, domain))
        return redirect(url_for("addresses_index"))
    form = AddressPasswordEditForm(obj=a)
    if form.validate_on_submit():
        form = AddressPasswordEditForm(obj=request.form)
        a = Address.query.filter_by(id=request.form['id']).first()
        if not a:
            flash("Invalid address '%s@%s'" % (username, domain))
            return redirect(url_for("addresses_index"))
        a.password = md5_password(request.form['password'])
        db.session.add(a)
        db.session.commit()
        flash("Address '%s@%s' successfully modified" % (a.username, a.domain.name))
        return redirect(url_for("addresses_index"))
    return render_template("address_password_edit.html", form=form, 
                           username=a.username, domain=a.domain.name)

@app.route("/address/delete/<username>/<domain>")
def address_delete(username, domain):
    domain = Domain.query.filter_by(name=domain).first()
    if not is_logged_in():
        flash("You need to log in to access this page")
        return redirect(url_for("login"))
    if not username:
        flash("Invalid user")
        return redirect(url_for("addresses_index"))
    if not domain:
        flash("Invalid domain")
        return redirect(url_for("addresses_index"))
    a = Address.query.filter_by(username=username, domain=domain).first()
    if not a:
        flash("Invalid address: '%s@%s'" % (username, domain))
        return redirect(url_for("addresses_index"))
    db.session.delete(a)
    db.session.commit()
    flash("Address '%s@%s' successfully deleted" % (a.username, a.domain))
    return redirect(url_for("addresses_index"))

@app.route("/address/clone/<username>/<domain>")
def address_clone(username, domain):
    print "not done"

@app.route("/aliases")
def aliases_index():
    if not is_logged_in():
        flash("You need to log in to access this page")
        return redirect(url_for("login"))
    else:
        return render_template("alias_index.html", 
                               aliases=Alias.query.all())

@app.route("/alias/add", methods=['GET', 'POST'])
def alias_add():
    if not is_logged_in():
        flash("You need to log in to access this page")
        return redirect(url_for("login"))
    form = AliasAddForm(request.form)
    choices = [(d.name, d.name) for d in Domain.query.order_by('-name')]
    form.domain.choices = choices
    if form.validate_on_submit():
        form.domain.choices = choices
        d = Domain.query.filter_by(name=request.form['domain']).first()
        active = False
        if 'active' in request.form and request.form['active'] == "y":
            active = True
            
        a = Alias(request.form['username'], d, request.form['goto'], active)
        db.session.add(a)
        db.session.commit()
        flash("Alias '%s@%s' to '%s' successfully added" % (request.form['username'], request.form['domain'], request.form['goto']))
        return redirect(url_for("aliases_index"))
    return render_template("alias_add.html", form=form)

@app.route("/alias/edit/<username>/<domain>", methods=['GET', 'POST'])
def alias_edit(username, domain):
    if not is_logged_in():
        flash("You need to log in to access this page")
        return redirect(url_for("login"))
    a = Alias.query.filter_by(username=username, 
                              domain=Domain.query.filter_by(name=domain).first()
                              ).first()
    if not a:
        flash("Invalid alias '%s@%s'" % (username, domain))
        return redirect(url_for("aliases_index"))
    form = AliasEditForm(obj=a)
    choices = [(d.name, d.name) for d in Domain.query.order_by('-name')]
    form.domain.choices = choices
    if form.validate_on_submit():
        form = AliasEditForm(obj=request.form)
        form.domain.choices = choices
        a = Alias.query.filter_by(id=request.form['id']).first()
        a.username = request.form['username']
        a.domain = Domain.query.filter_by(name=request.form['domain']).first()
        a.goto = request.form['goto']
        db.session.add(a)
        db.session.commit()
        flash("Alias '%s@%s' to '%s' successfully modified" % (a.username, a.domain.name, a.goto))
        return redirect(url_for("aliases_index"))
    return render_template("alias_edit.html", form=form, username=username, domain=domain)

@app.route("/alias/delete/<username>/<domain>")
def alias_delete(username, domain):
    if not is_logged_in():
        flash("You need to log in to access this page")
        return redirect(url_for("login"))
    if not id:
        flash("Invalid alias")
        return redirect(url_for("aliases_index"))
    a = Alias.query.filter_by(username=username, 
                              domain=Domain.query.filter_by(name=domain).first()
                              ).first()
    if not a:
        flash("Invalid alias '%s@%s'" % (username, domain))
        return redirect(url_for("aliases_index"))
    db.session.delete(a)
    db.session.commit()
    flash("Alias '%s@%s' to '%s' successfully deleted" % (a.username, a.domain.name, a.goto))
    return redirect(url_for("aliases_index"))

@app.route("/admins")
def admins_index():
    if not is_logged_in():
        flash("You need to log in to access this page")
        return redirect(url_for("login"))
    else:
        return render_template("admin_index.html", admins=Admin.query.all())
    
@app.route("/admin/add", methods=['GET', 'POST'])
def admin_add():
    if not is_logged_in():
        flash("You need to log in to access this page")
        return redirect(url_for("login"))
    form = AdminAddForm(request.form)
    if form.validate_on_submit():
        active = False
        if 'active' in request.form and request.form['active'] == "y": active = True
        a = Admin(request.form['email'], 
                    create_password(request.form['password']), active)
        db.session.add(a)
        db.session.commit()
        flash("Admin '%s' successfully added" % (a.email))
        return redirect(url_for("admins_index"))
    return render_template("admin_add.html", form=form)

@app.route("/admin/edit/<id>", methods=['GET', 'POST'])
def admin_edit(id):
    return "hi"

@app.route("/admin/password/<id>", methods=['GET', 'POST'])
def admin_password_edit(id):
    return "hi"

@app.route("/admin/delete/<id>", methods=['GET', 'POST'])
def admin_delete(id):
    return "hi"

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        session['email'] = request.form['email']
        token = hashlib.sha512(os.urandom(128)).hexdigest()
        session['token'] = token
        s = Session(Admin.query.filter_by(email=session['email']).first(), token)
        db.session.add(s)
        db.session.commit()
        flash("Welcome back")
        return redirect(url_for('index'))
    return render_template("login.html", form=form)

@app.route("/logout/")
def logout():
    s = Session.query.filter_by(key=session['token']).first()
    db.session.delete(s)
    db.session.commit()
    if 'email' in session:
        session.pop('email', None)
    if 'token' in session:
        session.pop('token', None)
    flash("Goodbye")
    return redirect("/login")

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404

def get_admin():
    return Admin.query.filter_by(email=session['email']).first()

if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000)
