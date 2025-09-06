from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from data_models import db, Author, Book
from datetime import datetime
import requests

app = Flask(__name__)


basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, 'data', 'library.sqlite')}'
db.init_app(app)

with app.app_context():
    db.create_all()


@app.route('/')
def home():
    # Query-Parameter: sortieren und suchen
    sort_field = request.args.get('sort', 'id')       # 'title' oder 'author'
    direction = request.args.get('direction', 'asc')  # 'asc' oder 'desc'
    search_query = request.args.get('search', '').strip()  # Suchbegriff

    # Basis-Query: Bücher mit Author joinen
    books_query = Book.query.join(Author)

    # Suche implementieren
    if search_query:
        # Suche in Titel oder Autorname (case-insensitive)
        books_query = books_query.filter(
            db.or_(
                Book.title.ilike(f'%{search_query}%'),
                Author.name.ilike(f'%{search_query}%')
            )
        )

    # Sortierung
    if sort_field == 'title':
        books_query = books_query.order_by(Book.title.desc() if direction=='desc' else Book.title.asc())
    elif sort_field == 'author':
        books_query = books_query.order_by(Author.name.desc() if direction=='desc' else Author.name.asc())
    else:
        books_query = books_query.order_by(Book.id.asc())

    books = books_query.all()

    # Bücher für Jinja vorbereiten
    books_with_details = []
    for book in books:
        books_with_details.append({
            'title': book.title,
            'author_name': book.author.name,
            'cover_url': f"https://covers.openlibrary.org/b/isbn/{book.isbn}-M.jpg"
        })

    # Meldung, wenn keine Bücher gefunden wurden
    message = None
    if search_query and not books_with_details:
        message = f'Keine Bücher gefunden für "{search_query}".'

    return render_template('home.html', books=books_with_details,
                           sort_field=sort_field, direction=direction, search_query=search_query, message=message)

@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    success = False

    if request.method == 'POST':
        name = request.form.get('name')
        birth_date_str = request.form.get('birth_date')
        death_date_str = request.form.get('date_of_death')

        if not birth_date_str:
            return "Geburtsdatum ist erforderlich", 400

        birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
        date_of_death = datetime.strptime(death_date_str, '%Y-%m-%d').date() if death_date_str else None

        new_author = Author(name=name, birth_date=birth_date, date_of_death=date_of_death)
        db.session.add(new_author)
        db.session.commit()
        success = True

    return render_template('add_author.html', success=success)


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    success = False
    authors = Author.query.all()

    if not authors:
        return "Bitte zuerst ein Autor under /add_author hinzufügen", 400

    if request.method == 'POST':
        title = request.form.get('title')
        isbn = request.form.get('isbn')
        publication_year = request.form.get('publication_year')
        author_id = request.form.get('author_id')

        if not (title and isbn and publication_year and author_id):
            return "Alle Felder müssen ausgefüllt sein", 400

        # Neues Buch erstellen
        new_book = Book(
            title=title,
            isbn=isbn,
            publication_year=int(publication_year),
            author_id=int(author_id)
        )
        db.session.add(new_book)
        db.session.commit()
        success = True

    return render_template('add_book.html', authors=authors, success=success)


if __name__ == '__main__':
    app.run(debug=True)