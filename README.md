# Real-Time Chat App with Flask and Socket.IO

This is a real-time chat application built using Flask and Socket.IO. The application allows users to register, log in, create or join chat rooms, and communicate in real-time.

## Features

- User registration and login
- Create or join chat rooms
- Public and private chat rooms
- Real-time messaging with Socket.IO
- Display online users count

## Technologies Used

- Flask
- Flask-SQLAlchemy
- Flask-SocketIO
- Tailwind CSS
- SQLite

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/realtime-chat-app.git
    cd realtime-chat-app
    ```

2. Create a virtual environment and activate it:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Run the application:
    ```bash
    flask run
    ```

5. Open your browser and navigate to `http://localhost:5000`.

## Usage

1. Register a new account or log in with an existing account.
2. Create a new chat room or join an existing one using the room code.
3. Start chatting in real-time with other users in the room.

## Project Structure

- `app.py`: The main Flask application file.
- `templates/`: Contains HTML templates for different pages.
- `static/`: Contains static files like CSS and JavaScript.
- `requirements.txt`: Lists the Python dependencies.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Acknowledgements

- [Flask](https://flask.palletsprojects.com/)
- [Socket.IO](https://socket.io/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/)
- [Flask-SocketIO](https://flask-socketio.readthedocs.io/)
