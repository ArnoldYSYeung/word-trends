"""
Toolkit for pre-processing Thomson Reuters dataframe (./rna002_RTRS_2013_06.csv).

Name:   Arnold YS Yeung
Date:   2020-12-11
"""

import pandas as pd

class TRArticles:
    
    def __init__(self, dataframe, languages=['en'], verbose=False):
        
        self.dataframe = dataframe
        self.languages = languages
        self.verbose = verbose
        
    def remove_duplicate_ids(self, identifier, fill_columns=[]):
        """
        Remove duplicate articles based on identifier.
        """
        if identifier not in self.dataframe.columns:
            raise ValueError('Cannot find ', identifier,' column.')
        for column in fill_columns:
            if column not in self.dataframe.columns:
                raise ValueError('Cannot find ', column, ' column.')
        
        if self.verbose:
            print("Removing duplicate IDs based on: ", identifier)
            before_num_rows = self.dataframe.shape[0]
            
        #   get rows where fill_columns are not NaN
        if fill_columns != []:    
            fill_df = {}
            for fill_column in fill_columns:
                #   create a map for filling in remaining rows which have missing values in fill_column
                fill_df[fill_column] = self.dataframe.set_index(identifier)[fill_column].dropna()
                fill_df[fill_column] = fill_df[fill_column].groupby(fill_df[fill_column].index).first()            
                fill_df[fill_column] = self.dataframe[identifier].map(fill_df[fill_column])
                        
        self.dataframe = self.dataframe.drop_duplicates(subset=identifier)
        
        if fill_columns != []:
            for fill_column in fill_columns:
                #   fill in remaining rows which have missing values in fill_column with map
                self.dataframe[fill_column] = self.dataframe[fill_column].fillna(fill_df[fill_column])
    
        if self.verbose:
            after_num_rows = self.dataframe.shape[0]
            
            print(before_num_rows-after_num_rows, " rows (", 
                  round((before_num_rows-after_num_rows)/before_num_rows*100, 2),
                  "%) were removed.")
        return  
    
    def remove_internal_calls(self, column, internal_calls=[]):
        """
        Remove all rows where column starts with one of the internal_calls. internal_calls
        are markers used to indicate rows which are not articles.
        """
        if column not in self.dataframe.columns:
            raise ValueError('Cannot find ', column, " column.")
        
        if self.verbose:
            print("Removing internal calls for ", column, ".")
            before_num_rows = self.dataframe.shape[0]
        
        for internal_call in internal_calls:
            self.dataframe = self.dataframe.loc[~self.dataframe[column].str.startswith(internal_call)]
        
        if self.verbose:
            after_num_rows = self.dataframe.shape[0]
            
            print(before_num_rows-after_num_rows, " rows (", 
                  round((before_num_rows-after_num_rows)/before_num_rows*100, 2),
                  "%) were removed.")
        
        return
    
    def filter_language(self):
        """
        Filters out all languages aside from those in self.languages.
        """
        
        if 'LANGUAGE' not in self.dataframe.columns:
            raise ValueError('Cannot find LANGUAGE column.')
        
        if self.verbose:
            print("Filtering for the following languages: ", self.languages)
            before_num_rows = self.dataframe.shape[0]
        
        self.dataframe = self.dataframe[self.dataframe['LANGUAGE'].isin(self.languages)]
        
        if self.verbose:
            after_num_rows = self.dataframe.shape[0]
            
            print(before_num_rows-after_num_rows, " rows (", 
                  round((before_num_rows-after_num_rows)/before_num_rows*100, 2),
                  "%) were removed.")
        
        return
    
    def concatenate_columns(self, columns, new_column="", remove=False):
        """
        Concatenate the values of two columns to combine the columns. If remove, remove
        columns[1] from self.dataframe.
        """
        
        for column in columns:
            if column not in self.dataframe.columns:
                raise ValueError('Cannot find ', column, ' column.')
        
        if new_column == "":
            concat_column = columns[0]
        else:
            concat_column = new_column
        
        if self.verbose:
            print("Concatenating columns: ", columns, " to ", concat_column)
        
        
        #   make all NaN into empty strings
        self.dataframe[columns] = self.dataframe[columns].fillna('')
        
        self.dataframe[concat_column] = self.dataframe[columns[0]].astype(str) + self.dataframe[columns[1]].astype(str)
        #self.dataframe[concat_column] = self.dataframe[columns].apply(lambda x: ''.join(x.map(str)), axis=1)
        
        if remove:
            if new_column == "":
                self.dataframe = self.dataframe.drop(labels=columns[1], axis=1)
            elif concat_column not in columns:
                self.dataframe = self.dataframe.drop(labels=columns, axis=1)
        
        return
    
    def convert_string_to_set(self, columns=[], sep=" "):
        """
        Convert tokens within a string to a set.
        """
        
        for column in columns:
            if column not in self.dataframe.columns:
                raise ValueError('Cannot find ', column, ' column.')
            
            self.dataframe[column] = self.dataframe[column].apply(lambda x: set(x.split(sep)))

        return 
    
    def get_headers(self):
        """
        Get headers of self.dataframe.
        """
        return self.dataframe.columns
    
    def reformat_dataframe(self, rename_dict={}, drop_columns=[], keep=False):
        """
        Drop and rename the self.dataframe.columns.
        """
        
        if self.verbose:
            print("Reformatting dataframe...")
        
        #   drop columns
        reformatted_df = self.dataframe.drop(labels=drop_columns, axis=1, errors='ignore')
        
        #   rename columns
        reformatted_df = reformatted_df.rename(rename_dict, axis=1, errors='ignore')
        
        if keep:
            self.dataframe = reformatted_df
            if self.verbose:
                print("self.dataframe modified.")
        
        return reformatted_df
    
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