# -*- coding: utf-8 -*-
"""
Created on Wed Aug  2 13:37:01 2017

@author: dataquanty
"""

import pandas as pd
import numpy as np


folder = 'inputFiles/'
users = pd.read_csv(folder + 'users.dat',sep='::',header=None)
users.columns = ['UserID','Gender','Age','Occupation','Zip-code']

#users.to_csv('users.csv',sep=',',index=False)

movies = pd.read_csv(folder + 'movies.dat',sep='::',header=None)
movies.columns = ['MovieID','Title','Genres']


genres = ["Action","Adventure","Animation","Children's","Comedy","Crime",
 "Documentary","Drama","Fantasy","Film-Noir","Horror","Musical",
 "Mystery","Romance","Sci-Fi","Thriller","War","Western"]

for c in genres:
    movies[c]=(movies['Genres'].apply(lambda x: c in x)).astype('int')
    
movies = movies.drop('Genres',axis=1)

movies['Year']=movies['Title'].apply(lambda x: x[-5:-1] ).astype('int')
movies = movies.drop('Title',axis=1)

#movies.to_csv(folder + 'movies.csv',sep=',',index=False)


ratings = pd.read_csv(folder + 'training_ratings_for_kaggle_comp.csv')
ratings = ratings.drop('id',axis=1)
usersNrating = ratings.groupby('user').count()['movie'].reset_index()
usersNrating.columns = ['user','nRatingsUser']
usersAvrating = ratings.groupby('user').mean()['rating'].reset_index()
usersAvrating.columns = ['user','aveRatingsUser']
usersVarrating = ratings.groupby('user').var()['rating'].reset_index()
usersVarrating.columns = ['user','varRatingsUser']


moviesPop = ratings.groupby('movie').count()['user'].reset_index()
moviesPop.columns = ['movie','nRatingsMovie']
moviesAvrating = ratings.groupby('movie').mean()['rating'].reset_index()
moviesAvrating.columns = ['movie','aveRatingsMovie']
moviesVarrating = ratings.groupby('movie').var()['rating'].reset_index()
moviesVarrating.columns = ['movie','varRatingsMovie']

ratings = ratings.merge(usersNrating,how='left',left_on='user',right_on='user')
ratings = ratings.merge(usersAvrating,how='left',left_on='user',right_on='user')
ratings = ratings.merge(usersVarrating,how='left',left_on='user',right_on='user')
ratings = ratings.merge(moviesPop,how='left',left_on='movie',right_on='movie')
ratings = ratings.merge(moviesAvrating,how='left',left_on='movie',right_on='movie')
ratings = ratings.merge(moviesVarrating,how='left',left_on='movie',right_on='movie')



users = users.merge(ratings,how='inner',left_on='UserID',right_on='user') 
movies = movies.merge(users,how='inner',left_on='MovieID',right_on='movie') 

for c in genres:
    feat = movies[movies[c]==1].groupby(['user']).mean()['rating'].reset_index()
    feat.columns = ['user','ave'+c]
    movies = movies.merge(feat,how='left',left_on='user',right_on='user')

movies = movies.replace(np.nan,0)

movieAvCat = np.zeros(len(movies))
sumCatNotNull = np.zeros(len(movies))
movieMaxCat = np.zeros(len(movies))
for c in genres:
    movieAvCat+=movies[c]*movies['ave'+c]
    sumCatNotNull += movies[c]
    movieMaxCat = np.amax(np.vstack((movieMaxCat,movies[c]*movies['ave'+c])),axis=0)
    
movieAvCat/=sumCatNotNull
movies = movies.assign(movieAvCat=movieAvCat)
movies = movies.assign(movieMaxCat=movieMaxCat)

genresave = ['ave'+c for c in genres]
movies = movies.drop(genresave,axis=1)



finalFile = movies.replace(np.nan,0)
finalFile = finalFile.drop(['user','movie'],axis=1)
finalFile['Gender']=finalFile['Gender'].apply(lambda x: 0 if x=='M' else 1)
finalFile['Zip-code']=finalFile['Zip-code'].apply(lambda x: x.replace('-',''))


for c in finalFile.columns:
    try:
        finalFile[c]=finalFile[c].astype(float)
    except:
        print c
        
finalFile.to_csv(folder + 'train2.csv.gz',sep=',',index=False,compression='gzip')

