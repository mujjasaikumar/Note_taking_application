

## Notes Taking API Documentation

### Introduction

The Notes Taking API provides endpoints for users to perform various operations related to notes management. It allows users to sign up, log in, create, update, share notes, and retrieve the version history of notes.

### Base URL

The base URL for accessing the API is `http://localhost:5000/` when running locally.

### Authentication

Authentication is performed using JSON Web Tokens (JWT) generated upon successful login. The token is included in the request headers for authorized access to protected endpoints.

### Endpoints

#### 1. Login

- **URL:** `/login`
- **Methods:** `POST`, `GET`
- **Description:** Authenticates users and generates a JWT token for authorized access to protected endpoints.
- **Parameters:**
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
- **Parameters:**
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
- **Parameters:**
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
- **Parameters:**
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
- **Parameters:**
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
- **Parameters:**
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
- **Parameters:**
  - `username`: Username of the user (required)
  - `password`: Password of the user (required)
  - `note_id`: ID of the note to be shared (required)
  - `shared_with_user_id`: ID of the user to whom the note will be shared (required)
