from pyramid.response import Response
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
from pyramid.session import check_csrf_token
from pyramid.security import (
    remember,
    forget,
    )
from sqlalchemy.exc import DBAPIError, SQLAlchemyError
from sqlalchemy import desc
from passlib.hash import sha256_crypt
from .models import (
    DBSession,
    Entry,
    )

from wtforms import Form, StringField, TextAreaField, validators

class EntryForm(Form):
    """WTForm for adding or editing entries."""
    title = StringField(u'Title', [validators.required(),
                        validators.length(max=128)])
    text = TextAreaField(u'Entry', [validators.required()])


def good_login(request):
    """Return true if the request is a valid login."""
    username = request.params.get('username')
    password = request.params.get('password')
    settings = request.registry.settings
    if not (username and password):  # UN or PW is missing
        return False
    if username == settings.get('auth.username'):
        return sha256_crypt.verify(password, settings.get('auth.password'))
    return False


@view_config(route_name='list', renderer='templates/list_template.jinja2',
             permission='read')
def list_view(request):
    """View for home page."""
    entries = DBSession.query(Entry).order_by(desc(Entry.created))
    return {'entries': entries, 'title': "Kyle's Learning Journal"}


@view_config(route_name='detail', renderer='templates/detail_template.jinja2',
             permission='read')
def detail_view(request):
    """View for single entry."""
    id = request.matchdict['id']
    entry = DBSession.query(Entry).filter(
        Entry.id == id).first()
    title = "Learning Journal Entry {}".format(id)
    return {'entry': entry, 'entry_text': entry.markdown, 'title': title}


@view_config(route_name='add_entry',
             renderer='templates/add_entry_template.jinja2',
             permission='create')
def add_entry_view(request):
    """View for adding entry page."""
    entry_form = EntryForm(request.POST)
    if request.method == 'POST' and entry_form.validate():
        check_csrf_token(request)
        if DBSession.query(Entry).filter(
                Entry.title == entry_form.title.data).all():
            #import pdb; pdb.set_trace()
            return {'title': 'Add Entry', 'form': entry_form,
                    'error': 'Title Already Used'}
        new_entry = Entry(title=entry_form.title.data,
                          text=entry_form.text.data)
        DBSession.add(new_entry)
        return HTTPFound(request.route_url('list'))
    return {'title': 'Add Entry', 'form': entry_form}


@view_config(route_name='edit_entry',
             renderer='templates/edit_entry_template.jinja2',
             permission='edit')
def edit_entry_view(request):
    """View for page editing an entry"""
    id = request.matchdict['id']
    current_entry = DBSession.query(Entry).filter(Entry.id == id).first()
    edited_form = EntryForm(request.POST, current_entry)
    if request.method == 'POST' and edited_form.validate():
        check_csrf_token(request)
        # If we try to edit the title to something already in DB
        if (DBSession.query(Entry).filter(
                Entry.title == edited_form.title.data).all() and
                current_entry.title != edited_form.title.data):
            return {'title': 'Add Entry', 'form': edited_form,
                    'error': 'Title Already Used'}
        current_entry.title = edited_form.title.data
        current_entry.text = edited_form.text.data
        return HTTPFound(request.route_url("detail", id=current_entry.id))
    return {'title': 'Add Entry', 'form': edited_form}


@view_config(route_name='login', renderer='templates/login_template.jinja2',
             permission='read')
def login_view(request):
    """View for login page."""
    error = ''
    if request.method == 'POST':
        if good_login(request):
            headers = remember(request, request.params['username'])
            return HTTPFound(request.route_url('list'), headers=headers)
        error = 'Bad Login'
    return {'error': error}


@view_config(route_name='logout')
def logout_view(request):
    """Logout View."""
    headers = forget(request)
    return HTTPFound(request.route_url('list'), headers=headers)


conn_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_learning-journal_db" script
    to initialize your database tables.  Check your virtual
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""
