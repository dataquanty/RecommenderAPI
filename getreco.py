#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Aug  3 09:48:42 2017

@author: dataquanty
"""

import pandas as pd
import numpy as np
from sklearn.externals import joblib


class GetReco:
        
    def __init__(self):
        #load
        folder = 'inputFiles/'
        self.movies = pd.read_csv(folder + 'movies.csv',sep=',')
        moviesInitial = pd.read_csv(folder + 'movies.dat',sep='::',header=None,engine='python')
        moviesInitial.columns = ['MovieID','Title','Genres']
        self.moviesInitial = moviesInitial
        self.users = pd.read_csv(folder + 'users.csv',sep=',')
        ratings = pd.read_csv(folder + 'training_ratings_for_kaggle_comp.csv')
        self.ratings = ratings.drop('id',axis=1)
        self.model = joblib.load(folder + 'sklean_modelTest2.pkl')
        
        
    def addUser(self,gender,age,occupation,zipcode):
        #add new user
        if(gender not in ['M','F'] or age not in [1,18,25,35,45,50,56] or occupation>20):
            print 'Input type error'
            return 0
        userId = max(self.users['UserID'])+1
        userIn = pd.DataFrame([[userId,gender,age,occupation,zipcode]],columns=self.users.columns)
        self.users=self.users.append(userIn)
        
        return userId
        
    
    def addData(self,userId,itemId,rating):
        #add recommendation
        if(userId not in self.users['UserID'].values or itemId not in self.movies['MovieID'].values):
            return 0
        else:
            ratingIn = pd.DataFrame([[userId,itemId,rating]],columns=self.ratings.columns)
            self.ratings = self.ratings.append(ratingIn)
            return 1
            
        
        
        
    def getAllRatings(self,userId):
        #get all ratings for a userId
        ratings = self.ratings
        ratings = ratings[ratings['user']==userId].sort_values('rating',ascending=False).head(20)
        print ratings.merge(self.moviesInitial,left_on='movie',right_on='MovieID')
        
    
    def predictInterests(self,userId):
        #
        usersU = self.users[self.users['UserID']==userId]
        if(len(usersU)==0):
            return ''
        #usersU['fakeKey']=np.repeat(1,len(usersU))
        
        
        finalFile = self.computeTrainingData(userId)
        #print finalFile
        finalFile['Zip-code']=np.repeat(1,len(finalFile))
        X = np.array(finalFile.drop('rating',axis=1))
        
        
        
        y_pred = self.model.predict(X)
        finalFile['ratingRec']=y_pred
        outputDf = finalFile[['UserID','MovieID','ratingRec']]
        outputDf = outputDf.merge(self.ratings,how='left',left_on=['MovieID','UserID'],right_on=['movie','user'])
        outputDf = outputDf[['UserID','MovieID','ratingRec','rating']]
        outputDf = outputDf.sort_values('ratingRec',ascending=False).head(20)
        outputDf= outputDf.merge(self.moviesInitial,on='MovieID')
        return outputDf.to_json(orient='index')
    
    def computeTrainingData(self,userId):
        users = self.users
        movies = self.movies
        ratings = self.ratings
        
        #Add additional movies to ratings
        usersU = users[users['UserID']==userId]
        if(len(usersU)==0):
            return ''
        
        usersU = usersU.assign(fakeKey = np.repeat(1,len(usersU)))
        moviesU = movies.assign(fakeKey = np.repeat(1,len(movies)))
        moviesU = moviesU.merge(usersU,on=['fakeKey'])
        moviesU = moviesU[['UserID', 'MovieID']]
        moviesU = moviesU.assign(ratingFake=np.repeat(0,len(moviesU)))
        
        ratingsU = ratings[ratings['user']==userId]
        moviesU = moviesU.merge(ratingsU,how='left',left_on='MovieID',right_on='movie')
        moviesU['rating']= moviesU['rating'].replace(np.nan,0)+moviesU['ratingFake']
        moviesU = moviesU[['UserID','MovieID','rating']]
        moviesU.columns = ratings.columns
        
        ratings = ratings[ratings['user']!=userId].append(moviesU)
        
        
        genres = ["Action","Adventure","Animation","Children's","Comedy","Crime",
                  "Documentary","Drama","Fantasy","Film-Noir","Horror","Musical",
                  "Mystery","Romance","Sci-Fi","Thriller","War","Western"]
        
        usersNrating = ratings[ratings['rating']>0].groupby('user').count()['movie'].reset_index()
        usersNrating.columns = ['user','nRatingsUser']
        usersAvrating = ratings[ratings['rating']>0].groupby('user').mean()['rating'].reset_index()
        usersAvrating.columns = ['user','aveRatingsUser']
        usersVarrating = ratings[ratings['rating']>0].groupby('user').var()['rating'].reset_index()
        usersVarrating.columns = ['user','varRatingsUser']
        
        #count non zeros
        moviesPop = ratings[ratings['rating']>0].groupby('movie').count()['user'].reset_index()
        moviesPop.columns = ['movie','nRatingsMovie']
        moviesAvrating = ratings[ratings['rating']>0].groupby('movie').mean()['rating'].reset_index()
        moviesAvrating.columns = ['movie','aveRatingsMovie']
        moviesVarrating = ratings[ratings['rating']>0].groupby('movie').var()['rating'].reset_index()
        moviesVarrating.columns = ['movie','varRatingsMovie']
        
        ratings = ratings.merge(usersNrating,how='left',left_on='user',right_on='user')
        ratings = ratings.merge(usersAvrating,how='left',left_on='user',right_on='user')
        ratings = ratings.merge(usersVarrating,how='left',left_on='user',right_on='user')
        ratings = ratings.merge(moviesPop,how='left',left_on='movie',right_on='movie')
        ratings = ratings.merge(moviesAvrating,how='left',left_on='movie',right_on='movie')
        ratings = ratings.merge(moviesVarrating,how='left',left_on='movie',right_on='movie')
        
        
        ratings = ratings[ratings['user']==userId]
        users = users.merge(ratings,how='inner',left_on='UserID',right_on='user') 
        movies = movies.merge(users,how='inner',left_on='MovieID',right_on='movie') 
        
        # Filter out on userId ?????
        for c in genres:
            feat = movies[(movies[c]==1) & (movies['rating']>0)].groupby(['user']).mean()['rating'].reset_index()
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
        finalFile['Zip-code']=finalFile['Zip-code'].apply(lambda x: str(x).replace('-',''))
        
        
        for c in finalFile.columns:
            try:
                finalFile[c]=finalFile[c].astype(float)
            except:
                print c
        
        return finalFile
        
        
    def getMovieList(self):
        #
        pass
        
    
