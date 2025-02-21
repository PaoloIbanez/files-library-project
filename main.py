from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Float, ForeignKey, Text, DateTime
from datetime import datetime
from flask_bcrypt import Bcrypt

app = Flask(__name__)
# -------------------------------------
# Configurations
# -------------------------------------
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///new-books-collection.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "090909"  # Replace with a strong secret key

bcrypt = Bcrypt(app)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)

# ------------------ MODELS ------------------ #
class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    # One-to-many relationship to reviews and comments
    reviews = relationship("Review", backref="user", lazy=True)
    comments = relationship("Comment", backref="user", lazy=True)
    # One-to-many for Book (the user is the book owner)
    books = relationship("Book", backref="owner", lazy=True)

class Book(db.Model):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)
    # The user who created this book
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # One-to-many relationship to reviews
    reviews = relationship("Review", backref="book", lazy=True)

class Review(db.Model):
    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(DateTime, default=datetime.utcnow)

    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False)

    # One-to-many relationship to comments
    comments = relationship("Comment", backref="review", lazy=True)

class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(DateTime, default=datetime.utcnow)

    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    review_id = db.Column(db.Integer, db.ForeignKey("reviews.id"), nullable=False)

with app.app_context():
    db.create_all()

# ------------------ AUTH ROUTES ------------------ #
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash("Account created successfully!", "success")
        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = db.session.execute(db.select(User).where(User.email == email)).scalar()
        if user and bcrypt.check_password_hash(user.password, password):
            session["user_id"] = user.id
            flash("Logged in successfully!", "success")
            return redirect(url_for("home"))
        else:
            flash("Login failed. Check your email and password.", "danger")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))

# ------------------ MAIN ROUTES ------------------ #
@app.route("/")
def home():
    """Display all books in a card layout (plus reviews, if you'd like)."""
    all_books = db.session.execute(db.select(Book).order_by(Book.title)).scalars().all()

    # Check if user is logged in
    user_id = session.get("user_id")
    user = None
    if user_id:
        user = db.session.execute(db.select(User).where(User.id == user_id)).scalar()

    return render_template("index.html", all_books=all_books, user=user)

@app.route("/add", methods=["GET", "POST"])
def add():
    """Add a new book to the database (owner = session user)."""
    if request.method == "POST":
        # Must be logged in
        if not session.get("user_id"):
            flash("You must be logged in to add a book.", "danger")
            return redirect(url_for("login"))

        title = request.form["title"]
        author = request.form["author"]
        rating = request.form["rating"]
        user_id = session["user_id"]  # The user creating the book

        new_book = Book(title=title, author=author, rating=rating, user_id=user_id)
        db.session.add(new_book)
        db.session.commit()

        flash("Book added successfully!", "success")
        return redirect(url_for("home"))

    return render_template("add.html")

@app.route("/edit/<int:book_id>", methods=["GET", "POST"])
def edit(book_id):
    """Edit a book's rating if you're the owner."""
    book_to_update = db.get_or_404(Book, book_id)

    # Check ownership
    if not session.get("user_id") or book_to_update.user_id != session["user_id"]:
        flash("You cannot edit someone else's book.", "danger")
        return redirect(url_for("home"))

    if request.method == "POST":
        new_rating = request.form["rating"]
        book_to_update.rating = new_rating
        db.session.commit()
        flash("Book rating updated!", "success")
        return redirect(url_for("home"))
    return render_template("edit.html", book=book_to_update)

@app.route("/delete/<int:book_id>")
def delete(book_id):
    """Delete a book from the database if you're the owner."""
    book_to_delete = db.get_or_404(Book, book_id)

    # Check ownership
    if not session.get("user_id") or book_to_delete.user_id != session["user_id"]:
        flash("You cannot delete someone else's book.", "danger")
        return redirect(url_for("home"))

    db.session.delete(book_to_delete)
    db.session.commit()
    flash("Book deleted!", "info")
    return redirect(url_for("home"))

# ------------------ REVIEW ROUTES ------------------ #
@app.route("/book/<int:book_id>")
def view_book(book_id):
    """
    Show a single book's details and all its reviews.
    You'd create a 'book_detail.html' template for this.
    """
    book = db.get_or_404(Book, book_id)
    user_id = session.get("user_id")
    user = None
    if user_id:
        user = db.session.execute(db.select(User).where(User.id == user_id)).scalar()
    return render_template("book_detail.html", book=book, user=user)

@app.route("/book/<int:book_id>/review", methods=["POST"])
def add_review(book_id):
    """Add a review for a particular book."""
    user_id = session.get("user_id")
    if not user_id:
        flash("You must be logged in to review a book.", "danger")
        return redirect(url_for("login"))

    review_content = request.form["review_content"]
    new_review = Review(content=review_content, user_id=user_id, book_id=book_id)
    db.session.add(new_review)
    db.session.commit()
    flash("Review added!", "success")
    return redirect(url_for("view_book", book_id=book_id))

@app.route("/review/<int:review_id>/edit", methods=["GET", "POST"])
def edit_review(review_id):
    """Edit a review if you're the owner."""
    review = db.get_or_404(Review, review_id)
    user_id = session.get("user_id")
    if not user_id or review.user_id != user_id:
        flash("You cannot edit someone else's review.", "danger")
        return redirect(url_for("home"))

    if request.method == "POST":
        new_content = request.form["review_content"]
        review.content = new_content
        db.session.commit()
        flash("Review updated!", "success")
        return redirect(url_for("view_book", book_id=review.book_id))

    # 'review_edit.html' or similar needed
    return render_template("review_edit.html", review=review)

@app.route("/review/<int:review_id>/delete")
def delete_review(review_id):
    """Delete a review if you're the owner."""
    review = db.get_or_404(Review, review_id)
    user_id = session.get("user_id")
    if not user_id or review.user_id != user_id:
        flash("You cannot delete someone else's review.", "danger")
        return redirect(url_for("home"))

    db.session.delete(review)
    db.session.commit()
    flash("Review deleted!", "info")
    return redirect(url_for("view_book", book_id=review.book_id))

# ------------------ COMMENT ROUTES ------------------ #
@app.route("/review/<int:review_id>/comment", methods=["POST"])
def add_comment(review_id):
    """Add a comment to a review."""
    user_id = session.get("user_id")
    if not user_id:
        flash("You must be logged in to comment.", "danger")
        return redirect(url_for("login"))

    comment_content = request.form["comment_content"]
    review = db.get_or_404(Review, review_id)

    new_comment = Comment(content=comment_content, user_id=user_id, review_id=review_id)
    db.session.add(new_comment)
    db.session.commit()

    flash("Comment added!", "success")
    return redirect(url_for("view_book", book_id=review.book_id))

@app.route("/comment/<int:comment_id>/delete")
def delete_comment(comment_id):
    """Delete a comment if you're the owner."""
    comment = db.get_or_404(Comment, comment_id)
    user_id = session.get("user_id")
    if not user_id or comment.user_id != user_id:
        flash("You cannot delete someone else's comment.", "danger")
        return redirect(url_for("home"))

    review_id = comment.review_id
    db.session.delete(comment)
    db.session.commit()
    flash("Comment deleted!", "info")
    return redirect(url_for("view_book", book_id=comment.review.book_id))

@app.route("/profile")
def profile():
    user_id = session.get("user_id")
    if not user_id:
        flash("You must be logged in to see your profile.", "danger")
        return redirect(url_for("login"))

    user = db.session.execute(db.select(User).where(User.id == user_id)).scalar()
    return render_template("profile.html", user=user)

if __name__ == "__main__":
    app.run(debug=True)
