import numpy as np
from sklearn.naive_bayes import BernoulliNB
from sklearn.neural_network import MLPClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import SGDClassifier

class ml_methods(object):

    def __init__(self):
        pass

    def MLP(self, X, y) -> list:
        classify = MLPClassifier()
        classify.fit(X, y)
        return(classify.coefs_)
    
    def GBC(self, X, y):
        classify = GradientBoostingClassifier()
        classify.fit(X, y)
        return(classify.feature_importances_)

    def SGD(self, X, y):
        classify = SGDClassifier()
        classify.fit(X, y)
        return(classify.coef_[0])
