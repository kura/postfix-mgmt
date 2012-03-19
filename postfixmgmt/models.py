import datetime
from flask import Flask
from flaskext.sqlalchemy import SQLAlchemy
from postfixmgmt import app, db
from postfixmgmt.auth import create_password


def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(128))
    active = db.Column(db.Boolean(), default=False)

    def __init__(self, email, password, active):
        self.email = email
        self.password = password
        self.active = active

    def __repr__(self):
        return '<Admin %r>' % self.email


class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.id'))
    admin = db.relationship('Admin', single_parent=True)
    key = db.Column(db.String(128), unique=True)
    
    def __init__(self, user, key):
        self.user = user
        self.key = key
        
    def __repr__(self):
        return '<Session %r>' % self.key


class Domain(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, index=True)
    description = db.Column(db.String())

    def __init__(self, name, description):
        self.name = name
        self.description = description

    def __repr__(self):
        return '<Domain %r>' % self.name
    
    def __unicode__(self):
        return self.name
    
    def __str__(self):
        return str(self.__unicode__())


class Address(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), index=True)
    domain_id = db.Column(db.Integer, db.ForeignKey('domain.id'), index=True)
    domain = db.relationship('Domain', single_parent=True, backref=db.backref('addresses', lazy='dynamic'))
    password = db.Column(db.String(128))
    active = db.Column(db.Boolean(), default=False)

    def __init__(self, username, domain, password, active):
        self.username = username
        self.domain = domain
        self.password = self.password
        self.active = active

    def __repr__(self):
        return '<Address %r@%r>' % (self.username, self.domain.name)
    
    def __unicode__(self):
        return '%s@%s' % (self.username, self.domain)
    
    def __str__(self):
        return str(self.__unicode__())

class Alias(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(128), index=True)
    domain_id = db.Column(db.Integer, db.ForeignKey('domain.id'), index=True)
    domain = db.relationship('Domain', single_parent=True, backref=db.backref('aliases', lazy='dynamic'))
    goto = db.Column(db.String(254), index=True)
    active = db.Column(db.Boolean(), default=False)
    
    def __init__(self, username, domain, goto, active):
        self.username = username
        self.domain = domain
        self.goto = goto
        self.active = active
    
    def __repr__(self):
        return '<Alias %r@%r:%r>' % (self.username, self.domain.name, self.goto)
    
    def __unicode__(self):
        return self.goto
    
    def __str__(self):
        return str(self.__unicode__())
