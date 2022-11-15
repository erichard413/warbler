"""Seed database with sample data from CSV Files."""

from csv import DictReader
from app import db
from models import User, Message, Follows



import collections
# from collections.abc import MutableMapping
try:
    from collections import abc
    collections.MutableMapping = abc.MutableMapping
except:
    pass


db.drop_all()
db.create_all()

username='admin'
password='password'
email='erik@erikrichard.com'


admin_user = User.signup(username, email, password)
admin_user.is_admin=True
db.session.add(admin_user)
db.session.commit()

with open('generator/users.csv') as users:
    db.session.bulk_insert_mappings(User, DictReader(users))

with open('generator/messages.csv') as messages:
    db.session.bulk_insert_mappings(Message, DictReader(messages))

with open('generator/follows.csv') as follows:
    db.session.bulk_insert_mappings(Follows, DictReader(follows))

db.session.commit()
