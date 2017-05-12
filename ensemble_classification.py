from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.grid_search import GridSearchCV
from sklearn.ensemble import VotingClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.pipeline import FeatureUnion
from sklearn.decomposition import PCA
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_selection import SelectKBest
from sklearn.cross_validation import train_test_split
from sklearn.feature_selection import SelectFromModel
from sklearn import svm
from nltk.corpus import stopwords
import _pickle as cPickle
import numpy as np
from scipy import sparse
import pandas as pd
import string
import os
os.chdir('C:\\Users\\Stevens\\Desktop\\BIA_660\\Project')

'''
importing data
'''

# input dataset
X = pd.read_csv('data_4_29.csv',sep=",",usecols=(3,4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18))

# output dataset
y = pd.read_csv('data_4_29.csv',sep=",",usecols=['Response'])

#=======================================================================================
'''
pre-processing data
'''

# replace non-letters/numbers with space and remove duplicate spaces
X['text'].replace({r'[^\x00-\x7F]+':''}, regex=True, inplace=True)
exclude = set(string.punctuation)
def remove_punctuation(x):
    try:
        x = ''.join(ch for ch in x if ch not in exclude)
    except:
        pass
    return x
X['text'] = X['text'].apply(remove_punctuation)


'''
pre-processing categorical data
'''

# converting the categorical data to binary variables
X_cat = pd.get_dummies(X, columns=['reposted',	 'laundry',	 'parking',	 'cat',	 'dog',	 'smoking',
                               'has_ft2',	 'furnished',	 'borough',	 'Section',])

# drop numerical variable from categorical table
X_cat.drop('price', axis=1, inplace=True)
X_cat.drop('date_available_from_today', axis=1, inplace=True)
X_cat.drop('days_on_cl', axis=1, inplace=True)
X_cat.drop('images', axis=1, inplace=True)
X_cat.drop('post_time', axis=1, inplace=True)
X_cat.drop('text', axis=1, inplace=True)

'''
pre-processing numeric data
'''

# create numerical variable
X_num = pd.DataFrame(X, columns=['price', 'date_available_from_today', 'days_on_cl', 'images', 'post_time'])

'''
pre-processing text data
'''

# create text variable
X_text = X['text']

# TF-IDF Vectorization for weighted frequency of words and transform into vector of 1/0
tvf = TfidfVectorizer(stop_words=stopwords.words('english'))
X_text = tvf.fit_transform(X_text)

'''
stacking all features into one matrix
'''

X = sparse.hstack((X_text, X_cat, X_num))
X = X.toarray()


# create training and testing variables and response
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1)

y_train = y_train.as_matrix()
y_test = y_test.as_matrix()


#=======================================================================================
'''
Decomposition and Feature Selection
'''

# Feature Selection
clf = RandomForestClassifier(n_estimators=100, n_jobs=1)
clf.fit(X_train, y_train.ravel())
sfm = SelectFromModel(clf, threshold=0.05)
X_train = sfm.fit_transform(X_train, y_train.ravel())


#=======================================================================================
'''
Ensemble Methods: Voting 
'''

clf1 = RandomForestClassifier (n_estimators=100, n_jobs=-1, criterion='gini')
clf2 = RandomForestClassifier (n_estimators=100, n_jobs=-1, criterion='entropy')
clf3 = ExtraTreesClassifier (n_estimators=100, n_jobs=-1, criterion='gini')
clf4 = ExtraTreesClassifier (n_estimators=100, n_jobs=-1, criterion='entropy')
clf5 = GradientBoostingClassifier (learning_rate=0.05, subsample=0.5, max_depth=6, n_estimators=50)
clf6 = DecisionTreeClassifier()
clf7 = svm.SVC(gamma=0.001, C=100)
clf8 = KNN_classifier=KNeighborsClassifier()
clf9 = GaussianNB()
lr = LogisticRegression()

# assembling classifiers
predictors=[('RF_g', clf1), ('RF_E', clf2), ('ET_g', clf3), ('ET_e', clf4),
            ('GB', clf5), ('DT',clf6), ('SVM',clf7), ('KNN',clf8), ('NB',clf9)]

# building voting
VT=VotingClassifier(predictors)

#fitting model
VT.fit(X_train,y_train)

#=======================================================================================
'''
running classification prediction
'''

# running prediction
predicted=VT.predict(X_test)

#print the accuracy
print(accuracy_score(predicted, y_test))

#=======================================================================================
'''
Ensemble Methods: Stacking
'''

sclf = StackingClassifier(classifiers=predictors, meta_classifier=lr)


VT.fit(counts_train,labels_train)

#use the VT classifier to predict
predicted=VT.predict(X_test)

#print the accuracy
print (accuracy_score(predicted,y_test))

