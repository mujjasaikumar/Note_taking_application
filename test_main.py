import unittest
import json
from main import app, db, User, Notes, NotesShared, NoteVersionHistory


class TestAPI(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        self.app = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_signup(self):
        with app.app_context():
            # Create a user
            user = User(username='test_user', email='test@example.com', password='test_password')
            db.session.add(user)
            db.session.commit()

            # Attempt to signup with the same username
            response = self.app.post('/signup', json={'username': 'test_user', 'email': 'test2@example.com',
                                                      'password': 'test_password'})
            data = json.loads(response.data)
            self.assertEqual(response.status_code, 400)
            self.assertEqual(data['message'], 'Username already exists')

            # Attempt to signup with a new username
            response = self.app.post('/signup', json={'username': 'test_user2', 'email': 'test2@example.com',
                                                      'password': 'test_password'})
            data = json.loads(response.data)
            self.assertEqual(response.status_code, 201)
            self.assertEqual(data['message'], 'Signup successful')

    def test_login(self):
        with app.app_context():
            # Check if the user already exists
            existing_user = User.query.filter_by(username='test_user').first()
            if not existing_user:
                # Create a user
                user = User(username='test_user', email='test@example.com', password='test_password')
                db.session.add(user)
                db.session.commit()

            # Test valid login
            response = self.app.post('/login', json={'username': 'test_user', 'password': 'test_password'})
            data = json.loads(response.data)
            self.assertEqual(response.status_code, 200)
            self.assertTrue('token' in data)
            self.assertEqual(data['message'], 'Login successful: Logged in as test_user')

            # Test invalid login
            response = self.app.post('/login', json={'username': 'test_user', 'password': 'wrong_password'})
            data = json.loads(response.data)
            self.assertEqual(response.status_code, 401)
            self.assertEqual(data['message'], 'Invalid credentials')

            # Test missing fields
            response = self.app.post('/login', json={})
            data = json.loads(response.data)
            self.assertEqual(response.status_code, 401)
            self.assertEqual(data['message'], 'Invalid credentials')

    def test_create_note(self):
        with app.app_context():
            # Check if the user already exists
            existing_user = User.query.filter_by(username='test_user').first()
            if not existing_user:
                # Create a user
                user = User(username='test_user', email='test@example.com', password='test_password')
                db.session.add(user)
                db.session.commit()

            # Test note creation with valid credentials
            response = self.app.post('/notes/create', json={'username': 'test_user', 'password': 'test_password', 'content': 'Test note'})
            data = json.loads(response.data)
            self.assertEqual(response.status_code, 201)
            self.assertEqual(data['message'], 'Note created successfully')
            self.assertTrue('note_id' in data)

            # Test note creation with missing fields
            response = self.app.post('/notes/create', json={})
            data = json.loads(response.data)
            self.assertEqual(response.status_code, 401)
            self.assertEqual(data['message'], 'Invalid credentials')

            # Test note creation with invalid credentials
            response = self.app.post('/notes/create', json={'username': 'test_user', 'password': 'wrong_password', 'content': 'Test note'})
            data = json.loads(response.data)
            self.assertEqual(response.status_code, 401)
            self.assertEqual(data['message'], 'Invalid credentials')

            # Test note creation with non-existent user
            response = self.app.post('/notes/create', json={'username': 'non_existent_user', 'password': 'test_password', 'content': 'Test note'})
            data = json.loads(response.data)
            self.assertEqual(response.status_code, 401)
            self.assertEqual(data['message'], 'Invalid credentials')

    def test_get_note(self):
        with app.app_context():
            # Check if the user already exists
            existing_user = User.query.filter_by(username='test_user').first()
            if not existing_user:
                # Create a user
                user = User(username='test_user', email='test@example.com', password='test_password')
                db.session.add(user)
                db.session.commit()

            # Create a note
            note = Notes(user_id=user.userid, post_content='Test note')
            db.session.add(note)
            db.session.commit()

            # Test getting a note with valid credentials and note exists
            response = self.app.get(f'/notes/{note.note_id}', json={'username': 'test_user', 'password': 'test_password'})
            data = json.loads(response.data)
            self.assertEqual(response.status_code, 200)
            self.assertTrue('note_id' in data)
            self.assertTrue('content' in data)
            self.assertEqual(data['content'], 'Test note')

            # Test getting a note with invalid credentials
            response = self.app.get(f'/notes/{note.note_id}', json={'username': 'test_user', 'password': 'wrong_password'})
            data = json.loads(response.data)
            self.assertEqual(response.status_code, 401)
            self.assertEqual(data['Error'], 'User does nor exist')

            # Test getting a note with non-existent note id
            response = self.app.get('/notes/999', json={'username': 'test_user', 'password': 'test_password'})
            data = json.loads(response.data)
            self.assertEqual(response.status_code, 404)
            self.assertEqual(data['message'], 'Note not found')

            # Test getting a note where user is not authorized to view
            # Create another user
            another_user = User(username='another_user', email='another@example.com', password='test_password')
            db.session.add(another_user)
            db.session.commit()
            # Share the note with the new user
            shared_note = NotesShared(note_id=note.note_id, author_id=user.userid, shared_with_user_id=another_user.userid)
            db.session.add(shared_note)
            db.session.commit()
            # Try to access the note with the new user's credentials
            response = self.app.get(f'/notes/{note.note_id}', json={'username': 'another_user', 'password': 'test_password'})
            data = json.loads(response.data)
            self.assertEqual(response.status_code, 200)
            self.assertTrue('note_id' in data)
            self.assertTrue('content' in data)
            self.assertEqual(data['content'], 'Test note')

    def test_update_note(self):
        with app.app_context():
            # Check if the user already exists
            existing_user = User.query.filter_by(username='test_user').first()
            if not existing_user:
                # Create a user
                user = User(username='test_user', email='test@example.com', password='test_password')
                db.session.add(user)
                db.session.commit()
            # Fetch the user again after committing to get the user ID
            user = User.query.filter_by(username='test_user').first()

            # Create a note
            note = Notes(user_id=user.userid, post_content='Original content')
            db.session.add(note)
            db.session.commit()

            # Test updating the note with valid credentials (as the author)
            response = self.app.put(f'/notes/{note.note_id}',
                                    json={'username': 'test_user', 'password': 'test_password',
                                          'content': 'Updated content'})
            data = json.loads(response.data)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['message'], 'Note updated successfully')
            self.assertEqual(Notes.query.get(note.note_id).post_content, 'Updated content')

            # Test updating the note with invalid credentials
            response = self.app.put(f'/notes/{note.note_id}',
                                    json={'username': 'test_user', 'password': 'wrong_password',
                                          'content': 'Updated content'})
            data = json.loads(response.data)
            self.assertEqual(response.status_code, 401)
            self.assertEqual(data['message'], 'Invalid credentials')

            # Create another user
            another_user = User(username='another_user3', email='another3@example.com', password='test_password')
            db.session.add(another_user)
            db.session.commit()

            # Share the note with the new user
            shared_note = NotesShared(note_id=note.note_id, author_id=user.userid,
                                      shared_with_user_id=another_user.userid)
            db.session.add(shared_note)
            db.session.commit()

            # Test updating the note with credentials of the shared user
            response = self.app.put(f'/notes/{note.note_id}',
                                    json={'username': 'another_user3', 'password': 'test_password',
                                          'content': 'Updated by shared user'})
            data = json.loads(response.data)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(data['message'], 'Note updated successfully')
            self.assertEqual(Notes.query.get(note.note_id).post_content, 'Updated by shared user')

            # Test updating the note with credentials of a user who is neither the author nor shared user
            new_user = User(username='random_user', email='random@example.com', password='test_password')
            db.session.add(new_user)
            db.session.commit()

            response = self.app.put(f'/notes/{note.note_id}',
                                    json={'username': 'random_user', 'password': 'test_password',
                                          'content': 'Updated by random user'})
            data = json.loads(response.data)
            self.assertEqual(response.status_code, 403)
            self.assertEqual(data['message'], 'You are not authorized to update this note')

    def test_get_version_history(self):
        with app.app_context():
            # Check if the user already exists
            existing_user = User.query.filter_by(username='test_user').first()
            if not existing_user:
                # Create a user
                user = User(username='test_user', email='test@example.com', password='test_password')
                db.session.add(user)
                db.session.commit()

            user = User.query.filter_by(username='test_user').first()
            # Create a note
            note = Notes(user_id=user.userid, post_content='Original content')
            db.session.add(note)
            db.session.commit()

            # Request the version history of the note
            response = self.app.get(f'/notes/version-history/{note.note_id}',
                                    json={'username': 'test_user', 'password': 'test_password'})
            data = json.loads(response.data)

            # Check if the response contains the expected data
            self.assertEqual(response.status_code, 200)
            self.assertIn('note_id', data)
            self.assertIn('version_history', data)

    def test_share_note(self):
        with app.app_context():
            # Check if the user already exists
            existing_user = User.query.filter_by(username='test_user').first()
            if not existing_user:
                # Create a user
                user = User(username='test_user', email='test@example.com', password='test_password')
                db.session.add(user)
                db.session.commit()
            # Fetch the user again after committing to get the user ID
            user = User.query.filter_by(username='test_user').first()
            note = Notes(user_id=user.userid, post_content='Original content2')
            db.session.add(note)
            db.session.commit()

            # Create another user to share the note with
            shared_user = User(username='shared_user', email='shared@example.com', password='shared_password')
            db.session.add(shared_user)
            db.session.commit()

            # Share the note with the new user
            response = self.app.post('/notes/share',
                                     json={'username': 'test_user', 'password': 'test_password',
                                           'note_id': note.note_id, 'shared_with_user_id': shared_user.userid})
            data = json.loads(response.data)

            # Check if the note was successfully shared
            self.assertEqual(response.status_code, 201)
            self.assertEqual(data['message'], 'Note shared successfully')

            # Check if the note is now present in the shared user's notes
            shared_notes = NotesShared.query.filter_by(shared_with_user_id=shared_user.userid).all()
            self.assertTrue(any(note.note_id == shared_notes[0].note_id for note in shared_notes))


if __name__ == '__main__':
    unittest.main()
