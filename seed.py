"""Seed database with sample data from CSV Files."""

from csv import DictReader
from app import db
from models import User, Message, Follows

# import collections
# try:
#     from collections import abc
#     collections.MutableMapping = abc.MutableMapping
# except:
#     pass
import collections 
if sys.version_info.major == 3 and sys.version_info.minor >= 10

    from collections.abc import MutableMapping
else 
    from collections import MutableMapping






db.drop_all()
db.create_all()

with open('generator/users.csv') as users:
    db.session.bulk_insert_mappings(User, DictReader(users))

with open('generator/messages.csv') as messages:
    db.session.bulk_insert_mappings(Message, DictReader(messages))

with open('generator/follows.csv') as follows:
    db.session.bulk_insert_mappings(Follows, DictReader(follows))

db.session.commit()
