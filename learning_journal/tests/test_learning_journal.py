from learning_journal.models import Entry
from learning_journal.views import good_login


def login(username, password, app):
    """Helper function for logins for testing."""
    login = {'username': username, 'password': password}
    return app.post('/login', params=login)


def test_entry_creation(session):
    test_entry = Entry(title=u"Test Entry", text=u"Here is my test entry")
    session.add(test_entry)
    session.flush()
    assert session.query(Entry).filter(Entry.title == u"Test Entry")


def test_good_login(auth_req):
    auth_req.params = {'username': 'owner', 'password': 'sounders'}
    assert good_login(auth_req)


def test_bad_login_pw(auth_req):
    auth_req.params = {'username': 'owner', 'password': 'seahawks'}
    assert not good_login(auth_req)


def test_bad_login_un(auth_req):
    auth_req.params = {'username': 'someone', 'password': 'sounders'}
    assert not good_login(auth_req)


def test_list_view(app, one_entry):
    response = app.get('/')
    actual = response.text
    assert one_entry.title in actual


def test_entry_view(app, session):
    test_entry = session.query(Entry).filter(
        Entry.title == u"Test Entry").first()
    url = '/entry/{id}'.format(id=test_entry.id)
    response = app.get(url)
    assert test_entry.title in response.text
    assert test_entry.text in response.text


def test_add_entry_view(app, session):
    login("owner", "sounders", app)
    url = '/entry/add'
    app.get(url)
    app.post(url, {'title': 'Add Test', 'text': 'new text'})
    session.flush()
    assert session.query(Entry).filter(Entry.title == u"Add Test")


def test_edit_entry_view(app, session):
    login("owner", "sounders", app)
    one_entry = session.query(Entry).filter(Entry.title == u"Test Entry").first()
    url = '/entry/{id}/edit'.format(id=one_entry.id)
    response = app.get(url)
    starting_page = response.text
    assert one_entry.title in starting_page
    assert one_entry.text in starting_page
    app.post(url, {'title': u"New Title", 'text': u'new text'})
    assert session.query(Entry).filter(Entry.title == u"New Title")


def test_logout_view(app, session):
    # Login and log out and check if you can visit a protected page.
    login("owner", "sounders", app)
    app.get('/logout')
    assert u'Log In' in app.get('/').text
