from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Author(db.Model):
    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    date_of_death = db.Column(db.Date, nullable=True)

    def __repr__(self):
        return f"<Author {self.name}>"

    def __str__(self):
        death = self.date_of_death.isoformat() if self.date_of_death else "-"
        return f"{self.name} ({self.birth_date.isoformat()} - {death})"

class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(20), nullable=False, unique=True)  # ISBN, Pflichtfeld, eindeutig
    title = db.Column(db.String(200), nullable=False)             # Titel, Pflichtfeld
    publication_year = db.Column(db.Integer, nullable=False)      # Erscheinungsjahr, Pflichtfeld

    # Foreign Key zu Author
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=False)
    author = db.relationship('Author', backref=db.backref('books', lazy=True))

    def __repr__(self):
        return f"<Book id={self.id} title='{self.title}' isbn='{self.isbn}'>"

    def __str__(self):
        return f"{self.title} ({self.publication_year}) by {self.author.name if self.author else 'Unknown'}"



