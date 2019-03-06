import sys
from getpass import getpass

from elasticsmapp.app.app import app, db
from elasticsmapp.app.auth import user_manager
from elasticsmapp.app.models import Role, User


def main():
    """Main entry point for script."""
    with app.app_context():
        password = getpass()
        assert password == getpass('Password (again):')
        user = User(username='crazyfrogspb',
                    password=user_manager.hash_password(password))
        user.roles.append(Role(name='admin'))
        user.roles.append(Role(name='moderator'))
        user.roles.append(Role(name='user'))
        db.session.add(user)
        db.session.commit()
        print('Done')


if __name__ == '__main__':
    sys.exit(main())
