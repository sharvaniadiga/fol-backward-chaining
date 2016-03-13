'''
Created on Mar 3, 2016

@author: sharvani
'''

class Rule(object):
    
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = rhs
    
    def getLHS(self):
        return self.lhs
    
    def setLHS(self, value):
        self.lhs = value
        
    def getRHS(self):
        return self.rhs
    
    def setRHS(self, value):
        self.rhs = value