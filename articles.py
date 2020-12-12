"""
Toolkit for pre-processing and analysis an 'Article'-format Pandas dataframe.

Name:   Arnold YS Yeung
Date:   2020-12-11
"""

import pandas as pd
import html
from collections import defaultdict
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import json
import os

from utils import *

class Articles:
    
    def __init__(self, dataframe, stop_words=None, date_range=[], verbose=False):
        
        self.mandatory_columns = ('DATE', 'TIME', 'TITLE', 'ID', 'TEXT', 
                                  'PLATFORMS', 'TOPICS', 'LANGUAGE')
        
        #   check input for all mandatory fields
        for column in self.mandatory_columns:
            if column not in dataframe.columns:
                raise ValueError('Cannot find ', column, ' column.')
        
        self.dataframe = dataframe
        self.verbose = verbose
        self.stop_words = stop_words
        
        if date_range == []:
            self.min_date = self.dataframe['DATE'].min()
            self.max_date = self.dataframe['DATE'].max()
        else:
            self.min_date = date_range[0]
            self.max_date = date_range[1]
        
        self.tokenized = False
        self.trend_count_score = defaultdict(int)
        self.trend_text_score = defaultdict(int)
        self.trend_norm_score = defaultdict(int)
    
    def remove_noise(self, columns):
        """
        Remove common noise in text. (E.g., '\n', '\t', HTML, URLs)
        """
        
        for column in columns:
            
            if column not in self.dataframe.columns:
                raise ValueError('Cannot find ', column, 'column.')
            
            if self.verbose:
                print("Removing \\n and \\t...")
            self.dataframe[column] = [text.replace('\n', '').replace('\t', '') 
                                      for text in self.dataframe[column]]
            
            #   convert HTML characters into Unicode
            if self.verbose:
                print("Converting HTML characters to Unicode...")
            self.dataframe[column] = [html.unescape(text) for text in
                                      self.dataframe[column]]
            
            #   remove URLs
            if self.verbose:
                print("Removing URLs...")
            self.dataframe[column] = [self._remove_url(text) for text in 
                                      self.dataframe[column]]
            
    def _remove_url(self, text):
        """
        Remove URLs starting with http or www from text. (Assumes URL is surrounded
        by " ")
        """
        
        text = ' '.join(token for token in text.split(' ') if not token.startswith('http'))
        text = ' '.join(token for token in text.split(' ') if not token.startswith('www'))
        
        return text
    
    def replace_punctuations(self, columns=[], replacement=" "):
        """
        Replace all punctuations in columns.
        """
        
        #   replace punctuations
        if self.verbose:
            print("Replacing punctuations with whitespace...")
        
        for column in columns:
            if column not in self.dataframe.columns:
                raise ValueError('Cannot find ', column, 'column.')
                
            self.dataframe[column] = [replace_punctuations(text) for text
                                      in self.dataframe[column]]
        return
                
    def tokenize(self, columns, sep=None, lower=True):
        """
        Tokenizes all strings in columns.
        """
        
        #   tokenize
        if self.verbose:
            print("Tokenizing...")
        
        for column in columns:
            if column not in self.dataframe.columns:
                raise ValueError('Cannot find ', column, 'column.')
                
            self.dataframe[column] = [tokenize(text) for text 
                                      in self.dataframe[column]]
        
        self.tokenized = True
        return
    
    def compute_trend(self, columns, column_weights=[], date_range=[]):
        """
        Compute trend scores for each unique token found in columns.
        INPUT:
            - columns (List[str]):              name of columns
            - column_weights(List[float]):      weights of columns (if empty, balanced)
            - date_range(list[str]):            min and max date inclusively (modifies self.min_date and self.max_date)
        """
        
        #   restart scores
        self.trend_count_score = defaultdict(int)
        self.trend_text_score = defaultdict(int)
        self.trend_norm_score = defaultdict(int)
        
        if self.verbose:
            print("Computing trend...")
        
        if self.tokenized is False:
            print("Please tokenized.")
            return
        
        if len(column_weights) != 0 and len(column_weights) != len(columns):
            raise ValueError('Mismatched column weights.')
            
        #   normalize column weights (from 0 to 1)
        if len(column_weights) != 0:
            sum_weights = sum(column_weights)
            for i in range(0, len(column_weights)):
                column_weights[i] = float(column_weights[i]) / sum_weights
        
        #   limit trends to our set date range
        if date_range != []:
            self.min_date = date_range[0]
            self.max_date = date_range[1]
        
        if self.verbose:
            print("Date range ", self.min_date, " ", self.max_date)
            
        mask = (self.dataframe['DATE'] >= self.min_date) & \
            (self.dataframe['DATE'] <= self.max_date)
        
        for i, column in enumerate(columns):
            
            if i < len(column_weights):
                weight = column_weights[i]
            else:
                weight = None
            
            if column not in self.dataframe.loc[mask].columns:
                raise ValueError('Cannot find ', column, 'column.')
            
            for tokens in self.dataframe.loc[mask][column]:
                self._compute_trend(tokens, weight)
        return

    
    def _compute_trend(self, tokens, weight=None):
        """
        Add the following tokens into the scores.
        """
        existing_tokens = set()
        
        if weight is None:
            weight = 1
        
        for token in tokens:            
            #   add each occurrence of token
            self.trend_count_score[token] += 1 * weight
            
            if token not in existing_tokens:
                #   add each text with token
                self.trend_text_score[token] += 1 * weight
                #   add normalized score for each token in text
                self.trend_norm_score[token] += tokens.count(token)/len(tokens) * weight
        
            existing_tokens.add(token)
    
    def remove_stop_words(self, columns):
        """
        Removes all stop words in columns.  Stop words include tokens containing digits.
        """
        
        #   remove stop words
        if self.verbose:
            print("Removing stop words...")
        
        if self.tokenized is False:
            print("Please tokenize first.")
            return
        
        if self.stop_words is None:
            print("Stop words not loaded.")
            return
        
        for column in columns:
            if column not in self.dataframe.columns:
                raise ValueError('Cannot find ', column, 'column.')
                
            self.dataframe[column] = [remove_stop_words(tokens, self.stop_words) 
                                            for tokens in self.dataframe[column]]
        return
        
    def lemmatize(self, columns):
        raise NotImplementedError()
    
    def load_dataframe(self, file):
        """
        Read dataframe from .csv file.
        """
        self.dataframe = pd.read_csv(file)
        return
            
    def save_dataframe(self, save_loc="", name="articles_dataframe.csv"):
        """
        Save dataframe to .csv file.
        """
        
        if save_loc == "":
            self.dataframe.to_csv("./"+name)
        else:
            self.dataframe.to_csv(save_loc+"/"+name)
        return
    
    def save_trend_scores(self, save_loc="", date_prefix=True):
        """
        Save trend score of each token into .json files.
        """
        
        if save_loc == "":
            save_loc = "."
        
        if date_prefix:
            prefix = self.min_date + "_" + self.max_date + "_"
        else:
            prefix = ""
        
        #   save token scores
        with open(save_loc+'/'+prefix+'trend_count_score.json', 'w') as fp:
            json.dump(self.trend_count_score, fp)
        with open(save_loc+'/'+prefix+'trend_text_score.json', 'w') as fp:
            json.dump(self.trend_text_score, fp)
        with open(save_loc+'/'+prefix+'trend_norm_score.json', 'w') as fp:
            json.dump(self.trend_norm_score, fp)
        
        return
    
    def load_trend_scores(self, method, file, date_prefix=True):
        """
        Load trend scores from file.
        """

        if method not in ("count", "norm", "text"):
            raise ValueError("Invalid method.")
        
        #   update date range based on prefixes
        if date_prefix:
            
            file_name = file.strip().split("/")[-1]
            
            prefixes = file_name.strip().split("_")
            self.min_date = prefixes[0]
            self.max_date = prefixes[1]
            if self.verbose:
                print("Date range changed to ", self.min_date, " to ", self.max_date)
            
        with open(file, 'r') as fp:
            if method == "count":
                self.trend_count_score = json.load(fp)
            elif method == "text":
                self.trend_text_score = json.load(fp)
            else:
                self.trend_norm_score = json.load(fp)
        
        return
        
    def rank_tokens(self):
        """
        Sort the unique tokens based on their trend scores.
        """
                
        #   sort the tokens based on scores
        self.count_trend_rank = [pair for pair in sorted(self.trend_count_score.items(), key=lambda item: item[1], reverse=True)]
        self.text_trend_rank = [pair for pair in sorted(self.trend_text_score.items(), key=lambda item: item[1], reverse=True)]
        self.norm_trend_rank = [pair for pair in sorted(self.trend_norm_score.items(), key=lambda item: item[1], reverse=True)]
     
        return

    def get_trending_words(self, method='count', n=10, top=True):
        """
        Get the top n trending words (and scores) using the specified method.
        """
        
        if method not in ('count', 'text', 'norm'):
            raise ValueError("Invalid method.")
        
        if top:
            if method == 'count' :
                return self.count_trend_rank[:n]
            elif method == 'text':
                return self.text_trend_rank[:n]
            
            return self.norm_trend_rank[:n]
        
        if method == 'count' :
            return self.count_trend_rank[-n:]
        elif method == 'text':
            return self.text_trend_rank[-n:]
        
        return self.norm_trend_rank[-n:]
    
    def plot_trends(self, method='count', n=10, top=True, save_file=""):
        """
        Plot the top (or bottom) n trending words and their respective scores.
        """
        
        if method not in ('count', 'text', 'norm'):
            raise ValueError("Invalid method.")
        
        rank = self.get_trending_words(method, n, top)
        
        #   convert to dataframe
        tokens = []
        scores = []
        for pair in rank:
            tokens.append(pair[0])
            scores.append(pair[1])
        
        plt.bar(tokens, scores)
        if top:
            plt.title('Top '+str(n)+' trending words ('
                      +str(self.min_date)+' to '+str(self.max_date)+')')
        else:
            plt.title('Bottom '+str(n)+' trending words (' 
                      +str(self.min_date)+' to '+str(self.max_date)+')')
        
        plt.xlabel('words')
        plt.ylabel(method+' score')
        plt.xticks(rotation=45)
        plt.show()
    
        if save_file != "":
            plt.savefig(save_file, format="png", dpi=1200, bbox_inches="tight")
        
    