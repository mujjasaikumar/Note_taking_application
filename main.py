from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import re
import jwt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisisasecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notes.db'
db = SQLAlchemy(app)


# Basic email validation
def is_valid_email(email):
    # Regular expression for basic email validation
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))


# User model
class User(db.Model):
    userid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)  # Add email field
    password = db.Column(db.String(100), nullable=False)


# Notes model
class Notes(db.Model):
    note_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.userid'), nullable=False)
    post_content = db.Column(db.Text, nullable=False)
    last_modified = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    modified_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


# Note version history model
class NoteVersionHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    note_id = db.Column(db.Integer, db.ForeignKey('notes.note_id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    modified_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


# Notes shared model
class NotesShared(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    note_id = db.Column(db.Integer, db.ForeignKey('notes.note_id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.userid'), nullable=False)
    shared_with_user_id = db.Column(db.Integer, db.ForeignKey('user.userid'), nullable=False)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        # Process POST request for login
        username = request.json.get('username', '')
        password = request.json.get('password', '')
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            # Generate a JWT token with user id and expiry time
            token = jwt.encode({'user': username, 'exp': datetime.utcnow() + timedelta(minutes=1)},
                               app.config['SECRET_KEY'])
            return jsonify(({'message': f'Login successful: Logged in as {username}', 'token': token}))
        return jsonify({'message': 'Invalid credentials'}), 401
    else:
        # Handle GET request for login (if needed)
        # For example, you might want to return a login form
        return jsonify({'message': 'This endpoint only accepts POST requests for login'})


# Signup endpoint with email validation
@app.route('/signup', methods=['POST'])
def signup():
    if request.method == 'POST':
        username = request.json.get('username', '')
        email = request.json.get('email', '')
        password = request.json.get('password', '')

        # Validate email format
        if not is_valid_email(email):
            return jsonify({'message': 'Invalid email format'}), 400

        # Check if email is already taken
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            return jsonify({'message': 'Email already exists'}), 400

        # Check if username is already taken
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return jsonify({'message': 'Username already exists'}), 400

        # Create new user
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({'message': 'Signup successful'}), 201
    else:
        # Handle GET request for signup (if needed)
        # For example, you might want to return a signup form
        return jsonify({'message': 'This endpoint only accepts POST requests for signup'})


@app.route('/notes/create', methods=['POST'])
def create_note():
    if request.method == 'POST':
        username = request.json.get('username', '')
        password = request.json.get('password', '')
        user = User.query.filter_by(username=username, password=password).first()
        if not user:
            return jsonify({'message': 'Invalid credentials'}), 401

        # If user is authenticated, proceed with note creation
        content = request.json.get('content', '')
        current_time = datetime.utcnow()  # Get current time
        new_note = Notes(user_id=user.userid, post_content=content, last_modified=current_time, modified_date=current_time)
        db.session.add(new_note)
        db.session.commit()

        # Save a copy of the note in the version history
        version = NoteVersionHistory(note_id=new_note.note_id, content=new_note.post_content, modified_date=current_time)
        db.session.add(version)
        db.session.commit()
        return jsonify({'message': 'Note created successfully', 'note_id': new_note.note_id}), 201


@app.route('/notes/<int:note_id>', methods=['GET'])
def get_note(note_id):
    if request.method == 'GET':
        # Process POST request for login
        username = request.json.get('username', '')
        password = request.json.get('password', '')
        user = User.query.filter_by(username=username, password=password).first()
        if not user:
            return jsonify({'Error': 'User does nor exist'}), 401
        note = Notes.query.get(note_id)
        if note:
            if note:
                # Check if the requesting user is the owner of the note
                if note.user_id == user.userid:
                    return jsonify({'note_id': note.note_id, 'content': note.post_content})
                else:
                    # Check if the note is shared with the requesting user
                    shared_note = NotesShared.query.filter_by(note_id=note_id,
                                                              shared_with_user_id=user.userid).first()
                    if shared_note:
                        return jsonify({'note_id': note.note_id, 'content': note.post_content})
            return jsonify({'Error': 'You are not authorised to view this note'})
        return jsonify({'message': 'Note not found'}), 404


@app.route('/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    if request.method == 'PUT':
        # Get the existing note
        note = Notes.query.get(note_id)
        if not note:
            return jsonify({'message': 'Note not found'}), 404

        # Verify the user
        username = request.json.get('username', '')
        password = request.json.get('password', '')
        user = User.query.filter_by(username=username, password=password).first()
        if not user:
            return jsonify({'message': 'Invalid credentials'}), 401

        # Check if the user is the author of the note or if the note has been shared with the user
        if note.user_id != user.userid and not NotesShared.query.filter_by(note_id=note_id, shared_with_user_id=user.userid).first():
            return jsonify({'message': 'You are not authorized to update this note'}), 403

        # Update the note content
        new_content = request.json.get('content', '')
        note.post_content = new_content
        note.last_modified = datetime.utcnow()

        # Save a copy of the previous version in the version history
        version = NoteVersionHistory(note_id=note.note_id, content=note.post_content, modified_date=datetime.utcnow())
        db.session.add(version)
        db.session.commit()

        return jsonify({'message': 'Note updated successfully'})


@app.route('/notes/version-history/<int:note_id>', methods=['GET'])
def get_version_history(note_id):
    # Check if note ID exists
    note = Notes.query.get(note_id)
    if not note:
        return jsonify({'message': 'No notes found for the given ID'}), 404

    # Verify the user
    username = request.json.get('username', '')
    password = request.json.get('password', '')
    user = User.query.filter_by(username=username, password=password).first()
    if not user:
        return jsonify({'message': 'Invalid credentials'}), 401
    # Get all versions of the note from version history
    versions = NoteVersionHistory.query.filter_by(note_id=note_id).order_by(NoteVersionHistory.modified_date.desc()).all()

    # Prepare response data
    version_history = [{'version_id': version.id, 'content': version.content, 'modified_date': version.modified_date}
                       for version in versions]

    return jsonify({'note_id': note_id, 'version_history': version_history})


@app.route('/notes/share', methods=['POST'])
def share_note():
    if request.method == 'POST':
        # Get note ID and user IDs from request
        note_id = request.json.get('note_id')
        shared_with_user_id = request.json.get('shared_with_user_id')

        # Check if note exists
        note = Notes.query.get(note_id)
        if not note:
            return jsonify({'message': 'Note not found'}), 404

        # Verify user authorization
        username = request.json.get('username', '')
        password = request.json.get('password', '')
        user = User.query.filter_by(username=username, password=password).first()
        if not user or user.userid != note.user_id:
            return jsonify({'message': 'Unauthorized to share this note'}), 403

        # Share the note with specified users
        shared_with_user = User.query.get(shared_with_user_id)
        if not shared_with_user:
            return jsonify({'message': f'User with ID {shared_with_user_id} not found'}), 404

        # Create entry in NotesShared table
        shared_note = NotesShared(note_id=note_id, author_id=user.userid, shared_with_user_id=shared_with_user_id)
        db.session.add(shared_note)

        db.session.commit()
        return jsonify({'message': 'Note shared successfully'}), 201


if __name__ == '__main__':
    # Create the database tables if they don't exist
    with app.app_context():
        db.create_all()
    app.run(debug=True)
