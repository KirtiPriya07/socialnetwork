# socialnetwork

## Prerequisites
Before you begin, ensure you have met the following requirements:
- **Python**: Make sure you have Python 3.6 or higher installed. You can download it from [python.org](https://www.python.org/downloads/).
- **PostgreSQL**: Install PostgreSQL on your machine. You can find the installation instructions at [postgresql.org](https://www.postgresql.org/download/).
- **Docker**: If you plan to use Docker, make sure you have Docker and Docker Compose installed. You can download Docker from [docker.com](https://www.docker.com/products/docker-desktop).
- **Git**: Ensure you have Git installed to clone the repository. You can download it from [git-scm.com](https://git-scm.com/downloads).


## Installation Steps

### Local Installation (Without Docker)
1. Clone the repository:
   git clone [repository_url]
   cd [repository_name]

2. Create a virtual environment and activate it:
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate

3. Install dependencies:
   pip install -r requirements.txt

4. Set up the PostgreSQL database:
   - Create a database and user in PostgreSQL, and update your Django `settings.py` with the appropriate credentials.

5. Run migrations:
   python manage.py migrate

6. Start the development server:
   python manage.py runserver

### Installation Through Docker
1. Clone the repository:
   git clone [repository_url]
   cd [repository_name]

2. Build the Docker images:
   docker-compose build

3. Start the containers:
   docker-compose up

4. Run migrations inside the Docker container:
   docker-compose exec web python manage.py migrate

## API Documentation

### Authentication

- **POST /api/signup/**
  - **Description**: Register a new user.
  - **Request**:
    ```json
    { "email": "user@example.com" }
    ```
  - **Response**:
    ```json
    { "message": "User created successfully." }
    ```

- **POST /api/login/**
  - **Description**: Log in an existing user.
  - **Request**:
    ```json
    { "email": "user@example.com", "password": "your_password" }
    ```
  - **Response**:
    ```json
    { "token": "your_jwt_token" }
    ```

### User Management

- **GET /api/users/**
  - **Description**: Search for users by email or name.
  - **Query Parameters**: `q` (search term)
  - **Response**:
    ```json
    { "results": [ { "id": 1, "name": "John Doe", "email": "john@example.com" }, ... ] }
    ```

### Friend Management

- **POST /api/send_request/**
  - **Description**: Send a friend request to another user.
  - **Request**:
    ```json
    { "recipient_email": "friend@example.com" }
    ```
  - **Response**:
    ```json
    { "message": "Friend request sent." }
    ```

- **GET /api/pending_requests/**
  - **Description**: View pending friend requests received by the user.
  - **Response**:
    ```json
    { "pending_requests": [ { "id": 1, "sender_email": "friend@example.com" }, ... ] }
    ```

- **POST /api/reject_request/**
  - **Description**: Reject a friend request.
  - **Request**:
    ```json
    { "request_id": 1 }
    ```
  - **Response**:
    ```json
    { "message": "Friend request rejected." }
    ```

- **POST /api/accept_request/**
  - **Description**: Accept a friend request.
  - **Request**:
    ```json
    { "request_id": 1 }
    ```
  - **Response**:
    ```json
    { "message": "Friend request accepted." }
    ```

- **GET /api/view_friends/**
  - **Description**: View the list of friends.
  - **Response**:
    ```json
    { "friends": [ { "id": 1, "name": "John Doe", "email": "john@example.com" }, ... ] }
    ```
### Block Management

- **POST /api/block_user/**
  - **Description**: Block a user, preventing them from sending friend requests or viewing your profile.
  - **Request**:
    ```json
    { "user_email": "user_to_block@example.com" }
    ```
  - **Response**:
    ```json
    { "message": "User blocked successfully." }
    ```

- **POST /api/unblock_user/**
  - **Description**: Unblock a previously blocked user.
  - **Request**:
    ```json
    { "user_email": "user_to_unblock@example.com" }
    ```
  - **Response**:
    ```json
    { "message": "User unblocked successfully." }
    ```

- **GET /api/blocked_users/**
  - **Description**: View the list of blocked users.
  - **Response**:
    ```json
    { "blocked_users": [ { "id": 1, "name": "Blocked User", "email": "blocked@example.com" }, ... ] }
    ``` 


## Design Choices
- **Database**: PostgreSQL was chosen for its advanced features like full-text search and efficient handling of large datasets.
- **Authentication**: JWT was implemented for secure and stateless authentication, allowing for easy token refreshing.
- **Caching**: Redis was used to optimize response times and reduce database load, particularly for frequently accessed data.
