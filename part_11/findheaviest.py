
# State space problems with observability
#
# States
#    applActions  actions applicabable in the state
#    succs        successor states of the state w.r.t. action
#    preds        predecessor states of the state w.r.t. action
#    compatible   Is the state compatible with an observation?

# Actions
#    observations observations possible after the action

### Description
#
# The goal is to identify the heaviest object among a set
# of object, by comparing the weights of pairs of objects.
#
# The problem is parameterized by the number of objects.

### Observations for the weighing problem

class OBSlessThan:
    def __init__(self,i,j):
        self.package1 = i
        self.package2 = j
    def __str__(self):
        return str(self.package1) + " < " + str(self.package2)

class OBSnothing:
    def __init__(self):
        self.dummy = 1
    def __str__(self):
        return "NOOBS"

### Actions for the weighing problem

class WeightChoose:
    def __init__(self,p):
        self.package = p
    def __str__(self):
        return "Choose " + str(self.package)
    def __eq__(self,other):
        return isinstance(other,WeightChoose) and self.package == other.package
    def __hash__(self):
        return self.package
    def observations(self):
        return [OBSnothing()]
    
class WeightCompare:
    def __init__(self,p1,p2):
        self.package1 = p1
        self.package2 = p2
    def __str__(self):
        return "Compare " + str(self.package1) + "-" + str(self.package2)
    def __eq__(self,other):
        return isinstance(other,WeightCompare) and self.package1 == other.package1 and self.package2 == other.package2
    def __hash__(self):
        return self.package1 + 100*self.package2
    def observations(self):
        return [ OBSlessThan(self.package1,self.package2), OBSlessThan(self.package2,self.package1) ]

### States for the weighing problem

class WeightState:
    def __init__(self,weights,chosen):
        self.weights = weights
        self.chosen = chosen

    def __hash__(self):
        return self.chosen + sum([ x+x*(pow(len(self.weights),index)) for index,x in enumerate(self.weights) ])
    def __eq__(self,other):
        return isinstance(other,WeightState) and self.chosen == other.chosen and self.weights == other.weights

    def __str__(self):
        return "(" + ','.join([str(w) for w in self.weights]) + ":" + str(self.chosen) + ")"

    def clonestate(self):
        return WeightState(self.weights,self.chosen)

    # Which actions applicable in a state?
    # Both actions can only be taken if no package has been chosen,
    # so the last action in every execution is always WeightChoose.

    def applActions(self):
        return [ WeightChoose(i) for i in range(0,len(self.weights)) if self.chosen == -1 ] + [ WeightCompare(i,j) for i in range(0,len(self.weights)) for j in range(0,len(self.weights)) if i<j and self.chosen == -1]

    # Successors of a state w.r.t. an action

    def succs(self,action):
        if isinstance(action,WeightChoose): # Successors with WeightChoose
            s = self.clonestate()
            s.chosen = action.package
            return {s}
        if isinstance(action,WeightCompare): # Successors with WeightCompare
            return {self}
        raise Exception("Unrecognized action " + str(action))

    # Predecessors of a state w.r.t. an action

    def preds(self,action):
        if isinstance(action,WeightChoose): # Predecessors with WeightChoose
            if self.weights[action.package] == len(self.weights):
                s = self.clonestate()
                s.chosen = -1
                return {s}
            else:
                return set()
        if isinstance(action,WeightCompare): # Predecessors with WeightChoose
            if self.chosen == -1:
                return {self}
            else:
                return set()
        raise Exception("Unrecognized action " + str(action))

    # Is the state compatible with the observation?

    def compatible(self,observation):
        if isinstance(observation,OBSlessThan):
            if self.weights[observation.package1] < self.weights[observation.package2]:
                return True
            return False
        if isinstance(observation,OBSnothing):
            return True
        raise Exception("Unrecognized observation " + str(observation))

import itertools

# For every permutation of the weights [1,2,3,...,N] there is
# one initial state. Initially the 'chosen' package is -1.

def WEIGHTinit(packages):
    weights = list(range(1,packages+1))
    perms = list(itertools.permutations(weights))
    return { WeightState(list(p),-1) for p in perms }

# Goal states are all permutations of the packages, but
# the chosen package must be the one with weight N.

def WEIGHTgoal(packages):
    weights = list(range(1,packages+1))
    perms = list(itertools.permutations(weights))
    return { WeightState(list(p),i) for p in perms for i in range(0,packages) if p[i]==packages }

# Generate a weighing problem with N packages

def WEIGHTproblem(N):
    actions = [ WeightChoose(i) for i in range(0,N) ] + [ WeightCompare(i,j) for i in range(0,N) for j in range(0,N) if i<j ]
    return (WEIGHTinit(N),WEIGHTgoal(N),actions)

# Testing the algorithm with the weighing problem.

from POplanFwd import POsolver

import sys

if __name__ == "__main__":
    instance = WEIGHTproblem(4)
    inits,goals,actions = instance
    for s in inits:
        print(str(s))
    print("Number of initial states is " + str(len(inits)))
    plan = POsolver(instance)
    if plan == None:
        print("No plan found")
    else:
        # Show plan's text representation (a list of strings).
        for s in plan.plan2str():
            print(s)
        # Show plan statistics
        print("Plan found: size " + str(plan.plansize()) + " depth " + str(plan.plandepth()))
        # Test that execution from every initial state reaches goals.
        for state in inits:
            plan.validate(state,goals)
