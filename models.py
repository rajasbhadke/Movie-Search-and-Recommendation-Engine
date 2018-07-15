from py2neo import Graph, Node, Relationship ,authenticate
from passlib.hash import bcrypt
from datetime import datetime
import uuid

# import flaskapp.config as config

# url = os.environ.get('GRAPHENEDB_URL', 'http://localhost:7474')
# username = os.environ.get('NEO4J_USERNAME')
# password = os.environ.get('NEO4J_PASSWORD')
# graph = Graph(url + '/db/data/', username=username, password=password)

authenticate("localhost:11001", "neo4j", "root")
graph = Graph()
class User:
    def __init__(self, username):
        self.username = username

    def find(self):
        user = graph.find_one("User", "username", self.username)
        return user

    def register(self, password):
        if not self.find():
            user = Node("User", username=self.username, password=bcrypt.encrypt(password),followers=0)
            graph.create(user)
            return True
        else:
            return False

    def verify_password(self, password):
        user = self.find()
        if user:
            return bcrypt.verify(password, user['password'])
        else:
            return False

class Movie:
    def __init__(self, id):
        self.id = id

    def find(self):
        movie = graph.find_one("Movie", "id", self.id)
        return movie

    def movie_node(self,movie_attr):
        if not self.find():
            movie = Node("Movie", id=self.id,title=movie_attr['original_title'],tagline=movie_attr['tagline'],
                                  overview=movie_attr['overview'],vote_count=movie_attr['vote_count'],
                                  vote_average=movie_attr['vote_average'],popularity=movie_attr['popularity'])
            graph.create(movie)
            return True
        else:
            return False

class Genre:
    def __init__(self, type):
        self.type = type

    def find(self):
        genre = graph.find_one("Genre", "type", self.type)
        return genre

    def genre_node(self):
        if not self.find():
            genre = Node("Genre", type=self.type)
            graph.create(genre)
            return True
        else:
            return False


class Year:
    def __init__(self, year):
        self.year = year

    def find(self):
        year = graph.find_one("Year", "year", self.year)
        return year

    def year_node(self):
        if not self.find():
            year = Node("Year", year=self.year)
            graph.create(year)
            return True
        else:
            return False



class Company:
    def __init__(self, name):
        self.name = name

    def find(self):
        company = graph.find_one("Company", "name", self.name)
        return company

    def company_node(self):
        if not self.find():
            company = Node("Company", name=self.name)
            graph.create(company)
            return True
        else:
            return False

class Producer:
    def __init__(self, name):
        self.name = name

    def find(self):
        producer = graph.find_one("Producer", "name", self.name)
        return producer

    def producer_node(self):
        if not self.find():
            producer = Node("Producer", name=self.name)
            graph.create(producer)
            return True
        else:
            return False


class Director:
    def __init__(self, name):
        self.name = name

    def find(self):
        director = graph.find_one("Director", "name", self.name)
        return director

    def director_node(self):
        if not self.find():
            director = Node("Director", name=self.name)
            graph.create(director)
            return True
        else:
            return False

class Actor:
    def __init__(self, name):
        self.name = name

    def find(self):
        actor = graph.find_one("Actor", "name", self.name)
        return actor

    def actor_node(self):
        if not self.find():
            actor = Node("Actor", name=self.name)
            graph.create(actor)
            return True
        else:
            return False

class Character:
    def __init__(self, name):
        self.name = name

    def find(self):
        character = graph.find_one("Character", "name", self.name)
        return character

    def character_node(self):
        if not self.find():
            character = Node("Character", name=self.name)
            graph.create(character)
            return True
        else:
            return False

class Rating:
    def __init__(self, rating):
        self.rating = rating

    def find(self):
        rat = graph.find_one("Rating", "rating", self.rating)
        return rat

    def rating_node(self):
        if not self.find():
            rat = Node("Rating", rating=self.rating)
            graph.create(rat)
            return True
        else:
            return False
