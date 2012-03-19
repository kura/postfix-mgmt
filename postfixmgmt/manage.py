from flaskext.script import Manager
from postfixmgmt import app

manager = Manager(app)

@manager.command
def add_domain(name, description=False):
    print name

if __name__ == "__main__":
    manager.run()
