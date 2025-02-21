# My Library - A Social Media for Book Lovers

## 📚 Description
"My Library" is a dynamic web application designed as a social media platform for book enthusiasts. Users can register, log in, add books to their virtual bookshelf, post reviews, comment on other users' reviews, and interact with a community of fellow readers. The app ensures secure user authentication and authorization, allowing only the original author to edit or delete their content.

---

## 🚀 Features
- **User Registration and Login:** Secure user authentication using Flask-Bcrypt for password hashing.
- **Add and Display Books:** Users can add books to their library with details like title, author, and rating.
- **Review and Comment System:** Users can write reviews for books and add comments to other users' reviews.
- **CRUD Operations:** Users can create, read, update, and delete their posts and comments.
- **User Authorization:** Only content creators can edit or delete their own posts and comments.
- **Responsive UI:** Built with Bootstrap-Flask for a modern, mobile-friendly design.
- **Persistent Storage:** Uses SQLite with SQLAlchemy ORM for database management.

---

## 🛠️ Technologies and Tools Used
- **Frontend:** HTML, CSS, Bootstrap-Flask
- **Backend:** Python, Flask
- **Database:** SQLite with SQLAlchemy ORM
- **Security:** Flask-Bcrypt for password hashing
- **Validation:** WTForms for form validation and CSRF protection
- **Version Control:** Git & GitHub

---

## ⚙️ Installation and Setup

### Prerequisites
- Python (>= 3.8)
- Git

### Instructions

1. **Clone the Repository:**
```bash
git clone <repository_url>
cd files-library-project
```

2. **Create a Virtual Environment:**
```bash
python -m venv .venv
source .venv/bin/activate # On Windows use: .venv\Scripts\activate
```

3. **Install Required Packages:**
```bash
pip install -r requirements.txt
```

4. **Initialize the Database:**
```bash
python
>>> from main import db
>>> db.create_all()
>>> exit()
```

5. **Run the Application:**
```bash
flask run
```

6. **Access the App:**
Open your browser and go to `http://127.0.0.1:5000`

---

## 📖 How to Use
- **Sign Up:** Create an account on the registration page.
- **Log In:** Access your profile and the main library.
- **Add Books:** Click on 'Add Book' to submit a new book entry.
- **Write Reviews and Comments:** Interact with books and users by leaving reviews and comments.
- **Edit or Delete Your Content:** Only your own content can be modified or removed.

---

## 🌟 Future Improvements
- Add profile pictures for users.
- Implement a search functionality for books and users.
- Enhance the commenting feature with nested replies.
- Introduce a rating system for user reviews.

---

## 👤 Author
Built by **Paolo Ibanez Medina**

---

