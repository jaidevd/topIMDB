from datetime import datetime
from gramex import config
import os
import pandas as pd

op = os.path
datafile = "movies.csv"


def not_too_old(path, days=1):
    td = datetime.now() - datetime.fromtimestamp(op.getmtime(path))
    return td.days <= days


def download():
    if op.isfile(datafile) and not_too_old(datafile):
        config.app_log.info('Found a recent file movies.csv.')
        return
    config.app_log.info('Downloading newer IMDB data...')
    movies = pd.read_csv(
        "http://datasets.imdbws.com/title.basics.tsv.gz",
        sep="\t",
        usecols=["tconst", "primaryTitle", "startYear", "genres", "titleType"],
        index_col="tconst"
    )
    ratings = pd.read_csv(
        "http://datasets.imdbws.com/title.ratings.tsv.gz", sep="\t",
        index_col="tconst"
    )
    df = pd.concat([movies, ratings], axis=1)
    df = df[df['numVotes'] > 10_000].reset_index()
    df.rename(columns={
        'index': 'ID',
        'averageRating': 'Rating',
        'startYear': 'Year',
        'numVotes': 'Votes',
        'primaryTitle': 'Title',
        'genres': 'Genre',
        'titleType': 'Type',
    }, inplace=True)
    df.sort_values('Votes', ascending=False, inplace=True)
    df.to_csv('movies.csv', encoding='utf-8', index=False)
    config.app_log.info('Done! The dataset is available at "movies.csv".')
