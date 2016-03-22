from learning_journal.models import Entry
from learning_journal.views import good_login


def test_entry_creation(session):
    test_entry = Entry(title=u"Test Entry", text=u"Here is my test entry")
    session.add(test_entry)
    session.flush()
    assert session.query(Entry).filter(Entry.title==u"Test Entry")


def test_good_login(auth_req):
    auth_req.params = {'username': 'owner', 'password': 'sounders'}
    assert good_login(auth_req)

def test_list_view(app, one_entry):
    response = app.get('/')
    assert response.status_code == 200
    actual = response.text
    assert one_entry.title in actual


def test_entry_view(app, session):
    test_entry = session.query(Entry).filter(Entry.title==u"Test Entry").first()
    url = '/entry/{id}'.format(id=test_entry.id)
    response = app.get(url)
    assert test_entry.title in response.text
    assert test_entry.text in response.text


def test_add_entry_view(app, session):
    url = '/entry/add'
    response = app.get(url)
    assert response.status_code == 200
    assert '<form method="POST">' in response.text
    app.post(url, {'title': 'Add Test', 'text': 'new text'})
    assert session.query(Entry).filter(Entry.title==u"Add Test").first()


def test_edit_entry_view(app, session):
    one_entry = session.query(Entry).filter(Entry.title==u"Test Entry").first()
    url = '/entry/{id}/edit'.format(id=one_entry.id)
    response = app.get(url)
    assert response.status_code == 200
    starting_page = response.text
    assert one_entry.title in starting_page
    assert one_entry.text in starting_page
    app.post(url, {'title': "New Title", 'text': 'new text'})
    edited_response = app.get(url)
    assert edited_response.status_code == 200
    edited_page = edited_response.text
    assert "New Title" in edited_page
    assert "new text" in edited_page
