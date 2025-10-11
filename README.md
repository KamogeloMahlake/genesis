
# Genesis

Genesis is a Django-based web application for reading, rating, and interacting with web novels. It features a full user system, advanced novel and chapter management, social interactions, and a polished, highly customizable frontend.

---

## Distinctiveness and Complexity

**Distinctiveness**  
- Implements a social web novel platform with a robust rating system, user profiles, bookmarks, and interactive comment threads.
- Integrates user profile customization, including avatars, bookmarks, and biographical data.
- Features rich client-side customization (fonts, colors, reading modes) using the static/novel JavaScript and CSS assets.

**Complexity**  
- The data model connects users, novels, chapters, ratings, tags, genres, and comments with complex relationships, including many-to-many and foreign key dependencies.
- The backend supports RESTful AJAX endpoints (for ratings/comments), authentication decorators, and robust error handling.
- The frontend (static/novel) enables persistent user settings, dynamic content loading, and seamless navigation between reading and stats pages.
- Advanced features such as chapter navigation with process saving, real-time statistics, and content export.

---

## File Overview

### Backend (Python/Django)
- **novel/models.py**  
  - Defines the main data entities: `User`, `Novel`, `Chapter`, `Rating`, `Comment`, etc.
  - Users have avatars, bookmarks, profile info, and can create novels.
  - Novels are linked to users (authors), can have tags, genres, ratings, and track statistics (views, comments, bookmarks).
  - Chapters are linked to novels and track views/comments.
  - Ratings and comments are linked to users and novels, supporting detailed feedback and discussion.

- **novel/views.py**  
  - Handles authentication, content browsing, rating submissions, comment deletion, and pagination.
  - Provides endpoints for AJAX actions (e.g., posting ratings) and uses Django’s decorators for security.
  - Renders key pages: user profiles, novel lists, chapter content, stats, etc.

### Frontend (static/novel)
Here are descriptions of the files you requested, suitable for inclusion in your README under a "Frontend File Overview" or similar section:

- **comments.js**  
  Handles the display and dynamic updating of comments on novels and chapters.  
  - Sends AJAX requests to fetch, post, or delete comments without page reloads.
  - Updates the DOM to show new comments instantly.
  - Supports threaded replies and may handle client-side validation or error display for comment actions.

- **ratings.js**  
  Manages the user rating system for novels.  
  - Enables users to submit ratings (such as stars or category-specific ratings) via interactive UI elements.
  - Sends rating data to the backend via AJAX and updates displayed averages and counts in real time.
  - Prevents duplicate ratings and gives feedback to users on successful or failed submissions.

- **tabs.js**  
  Controls the navigation and display of tabbed content within the novel reading interface.  
  - Allows switching between different sections such as "Details", "Comments", "Ratings", or "Chapters" without full-page reloads.
  - Listens for tab clicks and updates the visible content accordingly, improving user experience by making navigation seamless.

- `media/`: Directory for user-uploaded files and images.
  - `image.py`: (If present) Custom logic for image handling.
  - `novel-images/`: Contains image files associated with novels.
- `novel/`: Django app for managing novels.
  - `__init__.py`: App package marker.
  - `admin.py`: Django admin interface configuration for the app.
  - `apps.py`: App configuration.
  - `models.py`: Database models for novels and related entities.
  - `tests.py`: Unit tests for the app.
  - `urls.py`: URL routing for the app.
  - `views.py`: View logic for handling requests and responses.
  - `migrations/`: Database migration files.
  - `static/novel/`: Static files (CSS, JS, images) for the app.
    - `styles.css`: Main stylesheet for the novel app UI.
    - `comments.js`: Handles dynamic comment functionality for novels.
    - `ratings.js`: Manages user rating interactions for novels.
    - `tabs.js`: Provides tabbed navigation for novel details pages.
  - `templates/novel/`: HTML templates for rendering views.



## How to Run

1. **Clone and Install Dependencies**
    ```bash
    cd genesis
    pip install -r requirements.txt
    ```
2. **Apply Migrations**
    - Make sure PostgreSQL is running.
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```
3. **Run the Development Server**
    ```bash
    python manage.py runserver
    ```
   Visit [http://localhost:8000/](http://localhost:8000/) to use the app.

---

## Notable Model Relationships

- **User <-> Novel**: Users create novels and can bookmark them (many-to-many).
- **Novel <-> Chapter**: Each novel contains multiple chapters (one-to-many).
- **User <-> Rating/Comment**: Users can rate and comment on novels and chapters.
- **Novel <-> Tag/Genre**: Novels can have multiple tags and genres (many-to-many).
- **Novel/Chapter <-> Views/Stats**: Views and ratings are aggregated per novel and per chapter.
- **User Profile**: Stores avatars, bookmarks, biography, and reading stats.

---

## Additional Information

- Customizable reading interface (font, color, layout) for accessibility.
- Built with Python, Django, HTML, JavaScript, React, and CSS.

## Environment Variables (`.env`)
The `.env` file in the project root contains sensitive configuration for your Django and database setup. It should never be committed to version control.


- `DB_ENGINE`: The database backend to use (e.g., PostgreSQL).
- `DB_NAME`: Name of your database.
- `DB_USER`: Database username.
- `DB_PASSWORD`: Database password (keep this secure!).
- `DB_HOST`: Host address for the database server.
- `DB_PORT`: Port number for the database server.

---
