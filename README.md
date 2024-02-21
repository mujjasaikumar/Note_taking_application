

## Note Taking Application Documentation

### PythonAnywhere URL

This app is hosted on PythonAnywhere at the following URL:

```
https://saikumar.pythonanywhere.com/
```

Please note that due to limited features and storage capacity on free tier PythonAnywhere account, occasional errors may occur.

### Introduction

The Notes Taking API provides endpoints for users to perform various operations related to notes management. It allows users to sign up, log in, create, update, share notes, and retrieve the version history of notes.


### Database Schema
![image](https://github.com/mujjasaikumar/Note_taking_application/assets/95629853/ffff0ec7-a481-44a9-9447-a4218eebcf8e)


### Installation

To run the Note Management System locally, follow these steps:

1. Clone the repository:

```
git clone https://github.com/mujjasaikumar/Note_taking_application.git
```

2. Install dependencies:

```
pip install -r requirements.txt
```

3. Run the application:

```
python main.py
```

### Endpoints

#### 1. Login

- **URL:** `/login`
- **Methods:** `POST`
- **Description:** Authenticates users and generates a JWT token for authorized access to protected endpoints.
- **Parameters:** Passed as raw JSON data in the request body.
  - `username`: Username of the user (required)
  - `password`: Password of the user (required)
- **Response:**
  - Successful login:
    ```json
    {
        "message": "Login successful: Logged in as {username}",
        "token": "{JWT token}"
    }
    ```
  - Invalid credentials:
    ```json
    {
        "message": "Invalid credentials"
    }
    ```

#### 2. Signup

- **URL:** `/signup`
- **Method:** `POST`
- **Description:** Allows users to create a new account.
- **Parameters:** Passed as raw JSON data in the request body.
  - `username`: Username of the user (required)
  - `email`: Email address of the user (required)
  - `password`: Password of the user (required)
- **Response:**
  - Successful signup:
    ```json
    {
        "message": "Signup successful"
    }
    ```
  - Email or username already exists:
    ```json
    {
        "message": "Email already exists"
    }
    ```
    or
    ```json
    {
        "message": "Username already exists"
    }
    ```

#### 3. Create Note

- **URL:** `/notes/create`
- **Method:** `POST`
- **Description:** Allows users to create a new note.
- **Parameters:** Passed as raw JSON data in the request body.
  - `username`: Username of the user (required)
  - `password`: Password of the user (required)
  - `content`: Content of the note (required)
- **Response:**
  - Successful note creation:
    ```json
    {
        "message": "Note created successfully",
        "note_id": "{note_id}"
    }
    ```

#### 4. Get Note

- **URL:** `/notes/<int:note_id>`
- **Method:** `GET`
- **Description:** Allows users to retrieve a specific note by its ID.
- **Parameters:** Passed as raw JSON data in the request body.
  - `username`: Username of the user (required)
  - `password`: Password of the user (required)
- **Response:**
  - Successful retrieval:
    ```json
    {
        "note_id": "{note_id}",
        "content": "{note_content}"
    }
    ```
  - Unauthorized access:
    ```json
    {
        "Error": "User does not exist"
    }
    ```
  - Note not found:
    ```json
    {
        "message": "Note not found"
    }
    ```

#### 5. Update Note

- **URL:** `/notes/<int:note_id>`
- **Method:** `PUT`
- **Description:** Allows users to update the content of a specific note.
- **Parameters:** Passed as raw JSON data in the request body.
  - `username`: Username of the user (required)
  - `password`: Password of the user (required)
  - `content`: New content of the note (required)
- **Response:**
  - Successful update:
    ```json
    {
        "message": "Note updated successfully"
    }
    ```

#### 6. Get Version History

- **URL:** `/notes/version-history/<int:note_id>`
- **Method:** `GET`
- **Description:** Allows users to retrieve the version history of a specific note.
- **Parameters:** Passed as raw JSON data in the request body.
  - `username`: Username of the user (required)
  - `password`: Password of the user (required)
- **Response:**
  - Successful retrieval:
    ```json
    {
        "note_id": "{note_id}",
        "version_history": [
            {
                "version_id": "{version_id}",
                "content": "{content}",
                "modified_date": "{modified_date}"
            },
            ...
        ]
    }
    ```

#### 7. Share Note

- **URL:** `/notes/share`
- **Method:** `POST`
- **Description:** Allows users to share a specific note with other users.
- **Parameters:** Passed as raw JSON data in the request body.
  - `username`: Username of the user (required)
  - `password`: Password of the user (required)
  - `note_id`: ID of the note to be shared (required)
  - `shared_with_user_id`: ID of the user to whom the note will be shared (required)


### Testing

The application includes unit tests for each API endpoint. To run the tests, execute the following command:

```
python test_main.py
```

### Scope of Enhancement

1. **User Profile Management**: Implement features for users to manage their profiles, including updating email addresses and changing passwords.

2. **Tagging System**: Implement a tagging system for notes, allowing users to categorize and organize their notes efficiently.
   
3. **Secure Password Storage**: Implement secure password storage in the database using hashing and salting techniques.

4. **Authentication based login**: Implement OTP based authentication for secure login.


### Contributors

- Saikumar Mujja
---
