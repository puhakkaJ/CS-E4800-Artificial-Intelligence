
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
# In this problem, there is a randomly picked number as the initial
# state, and the goal is to transform that number to 1 by
# actions -1, +2, and Mod 2, which have different observations
# which test whether the number is a prime or composite, or
# if it is even or odd.
#

### Observations for the weighing problem

class OBSprime:
    def __init__(self):
        self.dummy = 1
    def __str__(self):
        return "prime"

class OBScomposite:
    def __init__(self):
        self.dummy = 1
    def __str__(self):
        return "composite"

class OBSodd:
    def __init__(self):
        self.dummy = 1
    def __str__(self):
        return "odd"

class OBSeven:
    def __init__(self):
        self.dummy = 1
    def __str__(self):
        return "even"

class OBSnothingN:
    def __init__(self):
        self.dummy = 1
    def __str__(self):
        return "NOOBS"

### Actions for the weighing problem

class NumMinus1:
    def __init__(self):
        self.dummy = 0
    def __str__(self):
        return "Minus1"
    def __eq__(self,other):
        return isinstance(other,NumMinus1)
    def __hash__(self):
        return 0
    def observations(self):
        return [OBSprime(),OBScomposite()]
    
class NumPlus2:
    def __init__(self):
        self.dummy = 0
    def __str__(self):
        return "Plus2"
    def __eq__(self,other):
        return isinstance(other,NumPlus2)
    def __hash__(self):
        return 1
    def observations(self):
        return [OBSodd(),OBSeven()]
    
class NumMod2:
    def __init__(self):
        self.dummy = 0
    def __str__(self):
        return "Mod2"
    def __eq__(self,other):
        return isinstance(other,NumMod2)
    def __hash__(self):
        return 1
    def observations(self):
        return [OBSnothingN()]
    

### States for the weighing problem

class NumState:
    def __init__(self,n):
        self.n = n

    def __hash__(self):
        return self.n
    def __eq__(self,other):
        return isinstance(other,NumState) and self.n == other.n

    def __str__(self):
        return str(self.n)

    def clonestate(self):
        return NumState(self.n)

    # Which actions applicable in a state?
    # Both actions can only be taken if no package has been chosen,
    # so the last action in every execution is always WeightChoose.

    def applActions(self):
        actions1 = []
        actions2 = []
        actions3 = []
        if self.n >= 1 and self.n <= 7:
            actions1 = [ NumMinus1() ]
        if self.n >= 0 and self.n <= 5:
            actions2 = [ NumPlus2() ]
        if self.n >= 1 and self.n <= 7:
            actions3 = [ NumMod2() ]
        return actions1 + actions2 + actions3

    # Successors of a state w.r.t. an action

    def succs(self,action):
        if isinstance(action,NumMod2):
            s = self.clonestate()
            s.n = self.n % 2
            return {s}
        if isinstance(action,NumMinus1):
            s = self.clonestate()
            s.n = self.n - 1
            return {s}
        if isinstance(action,NumPlus2):
            s = self.clonestate()
            s.n = self.n + 2
            return {s}
        raise Exception("Unrecognized action " + str(action))

    # Predecessors of a state w.r.t. an action

    def preds(self,action):
        if isinstance(action,NumMod2):
            if self.n == 0:
                return set([ NumState(i) for i in [0,2,4,6]])
            else:
                return set([ NumState(i) for i in [1,3,5,7]])
        if isinstance(action,NumMinus1):
            if self.n > 6:
                return set()
            s = self.clonestate()
            s.n = self.n + 1
            return {s}
        if isinstance(action,NumPlus2):
            if self.n < 2:
                return set()
            s = self.clonestate()
            s.n = self.n - 2
            return {s}
        raise Exception("Unrecognized action " + str(action))

    # Is the state compatible with the observation?

    def compatible(self,observation):
        if isinstance(observation,OBSeven):
            return (self.n % 2 == 0)
        if isinstance(observation,OBSodd):
            return (self.n % 2 == 1)
        if isinstance(observation,OBSprime):
            return (self.n in [0,1,2,3,5,7])
        if isinstance(observation,OBScomposite):
            return (self.n in [4,6])
        if isinstance(observation,OBSnothingN):
            return True
        raise Exception("Unrecognized observation " + str(observation))

import itertools

# For every permutation of the weights [1,2,3,...,N] there is
# one initial state. Initially the 'chosen' package is -1.

def NUMinit():
    return { NumState(i) for i in range(0,6) }

# Goal states are all permutations of the packages, but
# the chosen package must be the one with weight N.

def NUMgoal():
    return { NumState(1) }

# Generate a weighing problem with N packages

def NUMproblem():
    actions = [ NumPlus2(), NumMinus1(), NumMod2() ]
    return (NUMinit(),NUMgoal(),actions)

# Testing the algorithm with the weighing problem.

from POplanFwd import POsolver

import sys

if __name__ == "__main__":
    instance = NUMproblem()
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
