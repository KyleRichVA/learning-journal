from sqlalchemy import (
    Column,
    Index,
    Integer,
    Text,
    DateTime,
    String,
    )

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    )

from zope.sqlalchemy import ZopeTransactionExtension

from pyramid.security import (
    Allow,
    Everyone,
    )

import datetime
import markdown
from os import environ

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()


class RootFactory(object):
    __acl__ = [(Allow, Everyone, 'read'),
               (Allow, environ['ADMIN_UN'], 'edit'),
               (Allow, environ['ADMIN_UN'], 'create')]

    def __init__(self, request):
        self.request = request


class Entry(Base):
    __tablename__ = 'entries'
    id = Column(Integer, primary_key=True)
    title = Column(String(length=128, convert_unicode=True), unique=True)
    text = Column(Text(convert_unicode=True))
    created = Column(DateTime, default=datetime.datetime.utcnow)

    @property
    def markdown(self):
        return markdown.markdown(self.text)

Index('my_index', Entry.title, unique=True, mysql_length=255)
