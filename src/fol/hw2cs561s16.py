'''
Created on Mar 1, 2016

@author: sharvani
'''
import re
import sys

import constants
import Rule

#function declarations
def getOp(predicate):
    predicateOperator = ""
    regexMatch = re.match(constants.PREDICATE_CONSTANT_REGEX, predicate) 
    if re.search(constants.PREDICATE_CONSTANT_REGEX, predicate):  
        predicateOperator = predicate[regexMatch.start(): regexMatch.end()]    
    return predicateOperator  

def setKnowledgeBaseDict(lines, numOfClausesInKB):
    knowledgeBaseDict = {}
    for i in range(constants.INPUT_FILE_KB_START_LINE_NUM, constants.INPUT_FILE_KB_START_LINE_NUM + numOfClausesInKB):
        rhs = constants.NULL_STRING
        lhs = constants.NULL_STRING
        if(lines[i].find(constants.IMPLIES) != -1):
            lhs = lines[i][0: lines[i].find(constants.IMPLIES)]
            rhs = lines[i][lines[i].find(constants.IMPLIES) + 4: ]
        else:
            rhs = lines[i]
        rhsOp = getOp(rhs)
        rule = Rule.Rule(lhs, rhs)
        rulesList = []
        if (knowledgeBaseDict.has_key(rhsOp)):
            rulesList = knowledgeBaseDict[rhsOp]
        rulesList.append(rule)
        knowledgeBaseDict[rhsOp] = rulesList
    return knowledgeBaseDict

def printStringOntoFile(str1):
    fileName = constants.OUTPUT_TXT
    outputFile = open(fileName, 'a')
    outputFile.write(str1)
    outputFile.close()

def replaceVariablesInPredicate(predicate):
    argsArray = getArgsOfPredicate(predicate)
    argsStringAfterVariablesReplacement = constants.OPEN_BRACKET
    count = 0
    for i in argsArray:
        if(re.search(constants.VARIABLE_REGEX, i)):
            argsStringAfterVariablesReplacement += constants.VARIABLE_REPLACEMENT
        else:
            argsStringAfterVariablesReplacement += i
        if((len(argsArray) != 1) and (count < (len(argsArray) - 1))):
            argsStringAfterVariablesReplacement += constants.COMMA
        count = count + 1
    argsStringAfterVariablesReplacement += constants.CLOSE_BRACKET
    originalArgs = predicate[predicate.find(constants.OPEN_BRACKET): ]
    predicate = predicate.replace(originalArgs, argsStringAfterVariablesReplacement)
    return predicate
    
def displayEntryInLog(askOrBooleanValue, predicate):
    predicate = replaceVariablesInPredicate(predicate)
    print askOrBooleanValue + ": " + predicate
    #str1 = askOrBooleanValue + ": " + predicate + "\n"
    #printStringOntoFile(str1)

def hasArgs(rule):
    if ((rule.find(constants.OPEN_BRACKET) != -1) and (rule.find(constants.CLOSE_BRACKET) != -1)):
        return True
    else:
        return False

def getArgsOfPredicate(predicate):
    argsArray = []
    if (hasArgs(predicate)):
        args = predicate[predicate.find(constants.OPEN_BRACKET) + 1: predicate.find(constants.CLOSE_BRACKET)]
        argsArray = re.sub(r'\s', '', args).split(',')
    return argsArray

def subst(substitutionSetThetaDict, rule):
    args = rule[rule.find(constants.OPEN_BRACKET): ]
    substitutedArgs = args;
    for key in substitutionSetThetaDict:
        if (substitutedArgs.find(key) != -1):
            substitutedArgs = substitutedArgs.replace(key, substitutionSetThetaDict[key])
    rule = rule.replace(args, substitutedArgs)
    return rule

def getFirstPredicateInRule(rule):
    if(rule.find(constants.AND) != -1):
        first = rule[0: rule.find(constants.AND)]
        first.strip()
        return first
    else:
        return rule

#TODO: how to make sure that after first is called, rest is called by default?
def getRestPredicatesInRule(rule):
    if(rule.find(constants.AND) != -1):
        rest = rule[rule.find(constants.AND) + 4: ]
        rest.strip()
        return rest
    else:
        return constants.NULL_STRING

def getReplacementVariablesForStandarization(replacementVariablesInRule, predicate):
    for i in getArgsOfPredicate(predicate):
        if(re.match(constants.VARIABLE_REGEX, i)):
            if(replacementVariablesInRule.has_key(i) == False):
                replacedVariable = i
                if(standardizedVariablesDict.has_key(i)):
                    replacedVariable = i + str(standardizedVariablesDict[i])
                    standardizedVariablesDict[i] = standardizedVariablesDict[i] + 1
                else:
                    replacedVariable = i + str(constants.STANDARDIZE_VARIABLE_COUNT_FIRST_VALUE)
                    standardizedVariablesDict[i] = constants.STANDARDIZE_VARIABLE_COUNT_FIRST_VALUE + 1
                replacementVariablesInRule[i] = replacedVariable
    return replacementVariablesInRule
    
def standardizeVariables(rule): #TODO: eliminate global variable standardizedVariablesDict
    replacementVariablesInRule = {}
    isLHS = True
    lhs = rule.getLHS()
    rhs = rule.getRHS()
    for rest in (lhs, rhs):
        standardizedLHSorRHS = constants.NULL_STRING
        while(True):
            first = getFirstPredicateInRule(rest)
            rest = getRestPredicatesInRule(rest)
            replacementVariablesInRule = getReplacementVariablesForStandarization(replacementVariablesInRule, first)
            first = subst(replacementVariablesInRule, first)
            if (standardizedLHSorRHS == constants.NULL_STRING):
                standardizedLHSorRHS = first
            else:
                standardizedLHSorRHS += constants.AND + first
            if(rest == constants.NULL_STRING):
                if(isLHS):
                    lhs = standardizedLHSorRHS
                else:
                    rhs = standardizedLHSorRHS 
                break
        isLHS = False
    standardizedRule = Rule.Rule(lhs, rhs)
    return standardizedRule

def fetchRulesForGoal(knowledgeBaseDict, goal):
    if(knowledgeBaseDict.has_key(goal)):
        return knowledgeBaseDict[goal]
    else:
        return []

def numberOfPredicates(rule):
    length = 0
    if(rule != constants.NULL_STRING):
        length = 1
        if(rule.find(constants.AND) != -1):
            length += rule.count(constants.AND) 
    return length

def isVariable(x):
    if (isinstance(x, basestring) and re.search(constants.VARIABLE_REGEX, x)):
        return True
    else:
        return False

def isCompoundStatement(stmt):
    if(isinstance(stmt, basestring) and (re.search(constants.PREDICATE_CONSTANT_REGEX, stmt)) and (hasArgs(stmt))):
        return True
    else:
        return False

def unifyVar(var, x, substitutionSetThetaDict):
    if(substitutionSetThetaDict.has_key(var)):
        return unify(substitutionSetThetaDict[var], x, substitutionSetThetaDict)
    elif(substitutionSetThetaDict.has_key(x)):
        return unify(var, substitutionSetThetaDict[x], substitutionSetThetaDict)
    #TODO: OCCUR_CHECK() and verify
    else:
        substitutionSetThetaDict[var] = x
        return substitutionSetThetaDict
    
def unify(x, y, substitutionSetThetaDict):
    if(substitutionSetThetaDict == constants.NONE):
        return constants.NONE
    elif (x == y):
        return substitutionSetThetaDict
    elif (isVariable(x)):
        return unifyVar(x, y, substitutionSetThetaDict)
    elif (isVariable(y)):
        return unifyVar(y, x, substitutionSetThetaDict)
    elif ((isCompoundStatement(x)) and (isCompoundStatement(y))):
        return unify(getArgsOfPredicate(x), getArgsOfPredicate(y), unify(getOp(x), getOp(y), substitutionSetThetaDict))
    elif ((isinstance(x, list)) and (isinstance(y, list))):
        xFirst = x.pop()
        yFirst = y.pop()
        return unify(x, y, unify(xFirst, yFirst, substitutionSetThetaDict))
    else:
        return constants.NONE

def folBackwardChainingOr(knowledgeBaseDict, goal, substitutionSetThetaDict):
    displayEntryInLog(constants.ASK, goal)
    printLog = constants.FALSE
    for rule in fetchRulesForGoal(knowledgeBaseDict, getOp(goal)):
        standardizedRule = standardizeVariables(rule)
        tempSubstitutionSetThetaDict = unify(standardizedRule.getRHS(), goal, dict(substitutionSetThetaDict))
        if(tempSubstitutionSetThetaDict == constants.NONE):
            printLog = constants.FALSE
            continue
        if(printLog == constants.TRUE):
            displayEntryInLog(constants.ASK, goal)
        for substitutionSetThetaDashDict in (folBackwardChainingAnd(knowledgeBaseDict, standardizedRule.getLHS(), tempSubstitutionSetThetaDict)):
            if(substitutionSetThetaDashDict == constants.NONE):
                continue
            else:
                yield substitutionSetThetaDashDict
        printLog = constants.TRUE
    yield constants.NONE

def folBackwardChainingAnd(knowledgeBaseDict, goals, substitutionSetThetaDict):
    if(substitutionSetThetaDict == constants.NONE):
        yield substitutionSetThetaDict
    elif(numberOfPredicates(goals) == 0):
        yield substitutionSetThetaDict
    else:
        first = getFirstPredicateInRule(goals)
        rest = getRestPredicatesInRule(goals)
        firstAfterSubstitution = subst(substitutionSetThetaDict, first)
        printLog = constants.TRUE
        for substitutionSetThetaDashDict in (folBackwardChainingOr(knowledgeBaseDict, firstAfterSubstitution, dict(substitutionSetThetaDict))):
            if(substitutionSetThetaDashDict == constants.NONE):
                if(printLog != constants.FALSE):
                    displayEntryInLog(constants.FALSE, firstAfterSubstitution)
                yield substitutionSetThetaDashDict
            else:
                displayEntryInLog(constants.TRUE, subst(substitutionSetThetaDashDict, firstAfterSubstitution))
                for substitutionSetThetaDoubleDashDict in (folBackwardChainingAnd(knowledgeBaseDict, rest, dict(substitutionSetThetaDashDict))):
                    yield substitutionSetThetaDoubleDashDict
            printLog = constants.FALSE
        yield constants.NONE

def folBackwardChainingAsk(knowledgeBaseDict, query):
    substitutionSetThetaDict = {}
    queryRule = Rule.Rule(constants.NULL_STRING, query)
    standardizedQuery = standardizeVariables(queryRule)
    substitutionSetThetaDashDict = (folBackwardChainingAnd(knowledgeBaseDict, standardizedQuery.getRHS(), dict(substitutionSetThetaDict))).next()
    if(substitutionSetThetaDashDict == constants.NONE):
        #printStringOntoFile(constants.FALSE)
        print constants.FALSE
    else:
        #printStringOntoFile(constants.TRUE)
        print constants.TRUE

#main
with open(sys.argv[2]) as f:
    lines = f.read().splitlines()
f.close()
query = lines[constants.INPUT_FILE_QUERY_LINE_NUM]
numOfClausesInKB = lines[constants.INPUT_FILE_NUM_OF_CLAUSES_IN_KB]
knowledgeBaseDict = setKnowledgeBaseDict(lines, int(numOfClausesInKB))
askedPredicatesStack = []
standardizedVariablesDict = {}
folBackwardChainingAsk(knowledgeBaseDict, query)
