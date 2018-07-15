#pandas-csv-imports

import pandas as pd
import numpy as np
# import matplotlib.pyplot as plt
# import seaborn as sns
# from scipy import stats
from ast import literal_eval
# from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
# from sklearn.metrics.pairwise import linear_kernel, cosine_similarity
# from nltk.stem.snowball import SnowballStemmer
# from nltk.stem.wordnet import WordNetLemmatizer
# from nltk.corpus import wordnet
import json
import re



from models import *
from py2neo import Node, Relationship,Graph,authenticate
import json
from flask import Flask, request, session, redirect, url_for, render_template, flash,Response
# from py2neo import Graph, NodeMatcher
authenticate("localhost:11001", "neo4j", "root")
app = Flask(__name__)
app.secret_key = "super secret key"

@app.route('/populate_stop/')
def populate_graph():
    md = pd.read_csv('../input/movies_metadata.csv', low_memory=False)
    md['production_companies'] = md['production_companies'].fillna('[]').apply(literal_eval).apply(lambda x: [i['name'] for i in x] if isinstance(x, list) else [])
    md['genres'] = md['genres'].fillna('[]').apply(literal_eval).apply(lambda x: [i['name'] for i in x] if isinstance(x, list) else [])
    vote_counts = md[md['vote_count'].notnull()]['vote_count'].astype('int')
    vote_averages = md[md['vote_average'].notnull()]['vote_average'].astype('int')
    C = vote_averages.mean()
    vote_counts = md[md['vote_count'].notnull()]['vote_count'].astype('int')
    m = vote_counts.quantile(0.95)
    md = md[(md['vote_count'] >= m) & (md['vote_count'].notnull()) & (md['vote_average'].notnull())]
    md['vote_count'] = md['vote_count'].astype('int')
    md['vote_average'] = md['vote_average'].astype('int')
    def weighted_rating(x):
        v = x['vote_count']
        R = x['vote_average']
        return (v/(v+m) * R) + (m/(m+v) * C)
    md['wr'] = md.apply(weighted_rating, axis=1)
    md = md.sort_values('wr', ascending=False)
    pattern = re.compile('[\W_]+')
    avoid_keys = ["vote_count","vote_average","popularity","genres","production_companies"]
    for index, row in md.iterrows():
        for key,value in row.items():
            if str(key) not in avoid_keys:
                row[key] = str(row[key])
                row[key] = row[key].lower()
                row[key] = pattern.sub(' ',row[key])
        if index == 1000:
            break;
        if not Movie(row['id']).find():

            if pd.isnull(row['tagline']):
                row['tagline'] = "empty"
            Movie(row['id']).movie_node({'original_title':row['original_title'],'overview':row['overview'],
                                        'tagline':row['tagline'],'vote_count':row['vote_count'],
                                        'vote_average':row['vote_average'],'popularity':row['popularity']})
            for i in row['genres']:
                # print(i)
                i = str(i)
                i = i.lower()
                i = pattern.sub(' ',i)
                if not Genre(i).find():
                    Genre(i).genre_node()
                    # print(1)

                movie = graph.find_one("Movie", "id", row['id'])
                genre = graph.find_one("Genre", "type", i)
                ab = Relationship(movie,"has_genre",genre)
                graph.create(ab)

            for i in row['production_companies']:
                i = str(i)
                i = i.lower()
                i = pattern.sub(' ',i)
                if not Company(i).find():
                    Company(i).company_node()

                movie = graph.find_one("Movie", "id", row['id'])
                company = graph.find_one("Company", "name", i)
                ab = Relationship(movie,"production_company",company)
                graph.create(ab)

            if not Year(row['release_date'][0:4]).find():
                Year(row['release_date'][0:4]).year_node()

            movie = graph.find_one("Movie", "id", row['id'])
            year = graph.find_one("Year", "year", row['release_date'][0:4])
            ab = Relationship(movie,"release_year",year)
            graph.create(ab)

    return Response(md.head())

    # return Response(md.head())
@app.route('/populate2_stop/')
def populate_graph2():
    md = pd.read_csv('../input/movies_metadata.csv', low_memory=False)
    md['production_companies'] = md['production_companies'].fillna('[]').apply(literal_eval).apply(lambda x: [i['name'] for i in x] if isinstance(x, list) else [])
    md['genres'] = md['genres'].fillna('[]').apply(literal_eval).apply(lambda x: [i['name'] for i in x] if isinstance(x, list) else [])
    vote_counts = md[md['vote_count'].notnull()]['vote_count'].astype('int')
    vote_averages = md[md['vote_average'].notnull()]['vote_average'].astype('int')
    C = vote_averages.mean()
    vote_counts = md[md['vote_count'].notnull()]['vote_count'].astype('int')
    m = vote_counts.quantile(0.95)
    md = md[(md['vote_count'] >= m) & (md['vote_count'].notnull()) & (md['vote_average'].notnull())]
    md['vote_count'] = md['vote_count'].astype('int')
    md['vote_average'] = md['vote_average'].astype('int')
    def weighted_rating(x):
        v = x['vote_count']
        R = x['vote_average']
        return (v/(v+m) * R) + (m/(m+v) * C)
    md['wr'] = md.apply(weighted_rating, axis=1)
    cr = pd.read_csv('../input/credits.csv', low_memory=False)
    cr2 = pd.read_csv('../input/credits.csv', low_memory=False)
    cr['cast'] = cr['cast'].fillna('[]').apply(literal_eval).apply(lambda x: [ [i['name'],i['character']] for i in x ] if isinstance(x, list) else [])
    cr['crew'] = cr['crew'].fillna('[]').apply(literal_eval).apply(lambda x: [ i['name'] for i in x if i['job']=="Director" ] if isinstance(x, list) else [])
    cr2['crew'] = cr2['crew'].fillna('[]').apply(literal_eval).apply(lambda x: [ i['name'] for i in x if i['job']=="Producer" ] if isinstance(x, list) else [])
    cr['wr'] = md['wr']
    cr2['wr'] = md['wr']
    cr = cr.sort_values('wr', ascending=False)
    cr2 = cr2.sort_values('wr', ascending=False)
    pattern = re.compile('[\W_]+')
    for index, row in cr.iterrows():
        if index == 1000:
            break;
        for i in row['crew']:
            # print(i)
            i = str(i)
            i = i.lower()
            i = pattern.sub(' ',i)
            if not Director(i).find():
                Director(i).director_node()
                # print(1)

            movie = graph.find_one("Movie", "id", str(row['id']))
            director = graph.find_one("Director", "name", i)
            print(row['id'])
            try:
                ab = Relationship(director,"directed",movie)
                print(ab)
                graph.create(ab)
            except:
                pass

    for index, row in cr2.iterrows():
        if index == 1000:
            break;
        for i in row['crew']:
            # print(i)
            i = str(i)
            i = i.lower()
            i = pattern.sub(' ',i)
            if not Producer(i).find():
                Producer(i).producer_node()
                # print(1)

            movie = graph.find_one("Movie", "id", str(row['id']))
            producer = graph.find_one("Producer", "name", i)
            try:
                ab = Relationship(producer,"produced",movie)
                graph.create(ab)
            except:
                pass

    for index, row in cr.iterrows():
        if index == 1000:
            break;
        for i in row['cast']:
            # print(i)
            i[0] = str(i[0])
            i[0] = i[0].lower()
            i[0] = pattern.sub(' ',i[0])
            i[1] = str(i[1])
            i[1] = i[1].lower()
            i[1] = pattern.sub(' ',i[1])
            if not Actor(i[0]).find():
                Actor(i[0]).actor_node()

            if not Character(i[1]).find():
                Character(i[1]).character_node()
                # print(1)

            movie = graph.find_one("Movie", "id", str(row['id']))
            actor = graph.find_one("Actor", "name", i[0])
            character = graph.find_one("Character", "name", i[1])
            try:
                ab = Relationship(actor,"acted_in",movie)
                bc = Relationship(character,"character_of",movie)
                ca = Relationship(actor,"played",character)
                graph.create(ab)
                graph.create(bc)
                graph.create(ca)
            except:
                pass
    return Response(cr.head())

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if len(username) < 1:
            flash('Your username must be at least one character.')
        elif len(password) < 5:
            flash('Your password must be at least 5 characters.')
        elif not User(username).register(password):
            flash('A user with that username already exists.')
        else:

            User(username).register(password)
            session['username'] = username
            flash('Logged in.')
            return redirect(url_for('index'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not User(username).verify_password(password):
            flash('Invalid login.')
        else:
            session['username'] = username
            flash('Logged in.')
            return redirect(url_for('index'))

    return render_template('login.html')


@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/find_friends', methods=['GET', 'POST'])
def find_friends():
    all_users = graph.run("MATCH (users:User) RETURN users.username").data()
    follow_count = graph.run("MATCH (users:User) RETURN users.followers").data()
    l1 = [all_users[i]['users.username'] for i in range(len(all_users))]
    l2 = [follow_count[i]['users.followers'] for i in range(len(follow_count))]

    query = """
       MATCH (u:User)-[:FOLLOWS]->(v:User)
       WHERE u.username={user}
       RETURN v.username
       """
    if_follows = graph.data(query, user=session['username'])
    all_follows = [if_follows[i]['v.username'] for i in range(len(if_follows))]
    l3 = []
    for i in l1:
        if i in all_follows:
            l3.append(1)
        else:
            l3.append(0)
    zipped = zip(l1,l2,l3)
    print(all_follows)
    # for i in l:
    #     user = graph.find_one("User", "username", i)
    #     user['followers'] = 0
    #     user.push()
    return render_template('find_friends.html',zipped=zipped)

@app.route('/make_friends/<friend>', methods=['GET', 'POST'])
def make_friends(friend):
    user1 = graph.find_one("User", "username", session['username'])
    user2 = graph.find_one("User", "username", friend)
    ab = Relationship(user1,"FOLLOWS",user2)
    graph.create(ab)
    user2['followers'] = user2['followers'] + 1
    user2.push()
    return redirect(url_for('find_friends'))

@app.route('/delete_friends/<friend>', methods=['GET', 'POST'])
def delete_friends(friend):
    # user1 = graph.find_one("User", "username", session['username'])
    user2 = graph.find_one("User", "username", friend)
    # ab = Relationship(user1,"FOLLOWS",user2)
    # graph.create(ab)
    query = """
       MATCH (u:User)-[r:FOLLOWS]->(v:User)
       WHERE u.username={user} AND v.username={user3}
       DELETE r
       """
    if_follows = graph.data(query, user=session['username'],user3=friend)
    user2['followers'] = user2['followers'] - 1
    user2.push()
    return redirect(url_for('find_friends'))


@app.route('/search_bar', methods=['GET', 'POST'])
def search_bar():
    if request.method == 'POST':
        name = request.form['name']
        try:
            movie = graph.find_one("Movie", "title", name)
            cast=[]
            genre=[]
            prod=[]
            direc=[]
            for rel in graph.match(start_node=movie, rel_type="has_genre"):
                genre.append(rel.end_node()["type"])
            for rel in graph.match(end_node=movie, rel_type="acted_in"):
                cast.append(rel.start_node()["name"])
            for rel in graph.match(end_node=movie, rel_type="produced"):
                prod.append(rel.start_node()["name"])
            for rel in graph.match(end_node=movie, rel_type="directed"):
                direc.append(rel.start_node()["name"])
            cast = " , ".join(cast)
            genre = " , ".join(genre)
            prod = " , ".join(prod)
            direc = " , ".join(direc)
            return render_template('movie_info.html',info={"movie":movie,"cast":cast,"genre":genre,"prod":prod,"direc":direc})
        except:
            return Response("No results found")
        
    
    return render_template('search_bar.html')
if __name__ == "__main__":
    app.debug = True
    app.run()
