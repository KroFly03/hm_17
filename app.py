# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
api = Api(app)

movie_ns = api.namespace('movies')
director_ns = api.namespace('directors')
genre_ns = api.namespace('genres')


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Str()


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Str()


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)

genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)


@movie_ns.route('/')
class MoviesView(Resource):
    def get(self):
        director_id = request.args.get('director_id')
        genre_id = request.args.get('genre_id')
        try:

            movies = db.session.query(Movie).all()

            if director_id is not None:
                movies = db.session.query(Movie).filter(Movie.director_id == director_id).all()
            if genre_id is not None:
                movies = db.session.query(Movie).filter(Movie.genre_id == genre_id).all()
            if genre_id is not None and director_id is not None:
                movies = db.session.query(Movie).filter(Movie.genre_id == genre_id, Movie.director_id == director_id).all()

            return movies_schema.dump(movies), 200
        except Exception as ex:
            return "Not found"+str(director_id)+str(genre_id)+str(ex), 404

    def post(self):
        data = request.json
        movie = Movie(**data)

        with db.session.begin():
            db.session.add(movie)

        return "Movie created", 201


@movie_ns.route('/<int:id>')
class MovieView(Resource):
    def get(self, id):
        try:
            movie = db.session.query(Movie).filter(Movie.id == id).one()
            return movie_schema.dump(movie)
        except Exception:
            return "Not found", 404

    def put(self, id):
        movie = db.session.query(Movie).get(id)
        if movie is None:
            return "Not found", 404

        data = request.json

        movie.title = data.get('title')
        movie.description = data.get('description')
        movie.trailer = data.get('trailer')
        movie.year = data.get('year')
        movie.rating = data.get('rating')
        movie.genre_id = data.get('genre_id')
        movie.director_id = data.get('director_id')

        db.session.add(movie)
        db.session.commit()

        return "Movie updated", 204

    def delete(self, id):
        movie = db.session.query(Movie).get(id)
        if movie is None:
            return "Not found", 404

        db.session.delete(movie)
        db.session.commit()

        return "Movie deleted", 204


@director_ns.route('/')
class DirectorsView(Resource):
    def get(self):
        try:
            directors = db.session.query(Director).all()
            return directors_schema.dump(directors), 200
        except Exception:
            return "Not found", 404

    def post(self):
        data = request.json
        director = Director(**data)

        with db.session.begin():
            db.session.add(director)

        return "Director created", 201


@director_ns.route('/<int:id>')
class DirectorView(Resource):
    def get(self, id):
        try:
            director = db.session.query(Director).filter(Director.id == id).one()
            return director_schema.dump(director)
        except Exception:
            return "Not found", 404

    def put(self, id):
        director = db.session.query(Director).get(id)
        if director is None:
            return "Not found", 404

        data = request.json

        director.name = data.get('name')

        db.session.add(director)
        db.session.commit()

        return "Director updated", 204

    def delete(self, id):
        director = db.session.query(Director).get(id)
        if director is None:
            return "Not found", 404

        db.session.delete(director)
        db.session.commit()

        return "Director deleted", 204


@genre_ns.route('/')
class GenresView(Resource):
    def get(self):
        try:
            genres = db.session.query(Genre).all()
            return genres_schema.dump(genres), 200
        except Exception:
            return "Not found", 404

    def post(self):
        data = request.json
        genre = Genre(**data)

        with db.session.begin():
            db.session.add(genre)

        return "Genre created", 201


@genre_ns.route('/<int:id>')
class GenreView(Resource):
    def get(self, id):
        try:
            genre = db.session.query(Genre).filter(Genre.id == id).one()
            return genre_schema.dump(genre)
        except Exception:
            return "Not found", 404

    def put(self, id):
        genre = db.session.query(Genre).get(id)
        if genre is None:
            return "Not found", 404

        data = request.json

        genre.name = data.get('name')

        db.session.add(genre)
        db.session.commit()

        return "Genre updated", 204

    def delete(self, id):
        genre = db.session.query(Genre).get(id)
        if genre is None:
            return "Not found", 404

        db.session.delete(genre)
        db.session.commit()

        return "Genre deleted"+str(id), 204


if __name__ == '__main__':
    app.run(debug=True)
