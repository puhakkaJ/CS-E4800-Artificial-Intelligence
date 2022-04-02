
# The MasterMind code-breaking game
# https://en.wikipedia.org/wiki/Mastermind_(board_game)

# State space problems with observability
#
# States
#    applActions  actions applicabable in the state
#    succs        successor states of the state w.r.t. action
#    preds        predecessor states of the state w.r.t. action
#    compatible   Is the state compatible with an observation?

# Actions
#    observations observations possible after the action

MAXCODE = 2 # Code numbers are 1,...,MAXCODE
CODELEN = 3 # Length of the code. Standard MasterMind is CODELEN=4

# Observation after completing a guess
# posright   Number of correct colors in correct position
# poswrong   Number of correct colors in wrong position

class OBSmmcode:
    def __init__(self,i,j):
        self.posright = i
        self.poswrong = j
    def __str__(self):
        return "obsR" + str(self.posright) + "W" + str(self.poswrong)

class OBSmmnothing:
    def __init__(self):
        self.dummy = 1
    def __str__(self):
        return "NOOBS"

# MMsetCode(i,c)
#   Set color in position i (0..CODELEN-1) to c (1..MAXCODE)

class MMsetCode:
    def __init__(self,i,c):
        self.index = i
        self.value = c
    def __str__(self):
        return "Set [" + str(self.index) + "] = " + str(self.value)
    def __eq__(self,other):
        return isinstance(other,MMsetCode) and self.index == other.index and self.value == other.value
    def __hash__(self):
        return self.index + 100 * self.value
    def observations(self):
        return [OBSmmnothing()]

# After the guess is complete, compare the guess to the code
    
class MMcheckGuess:
    def __init__(self):
        self.dummy = 1
    def __str__(self):
        return "CheckGuess"
    def __eq__(self,other):
        return isinstance(other,MMcheckGuess)
    def __hash__(self):
        return 1
    def observations(self):
        return [ OBSmmcode(i,j) for i in range(0,CODELEN+1) for j in range(0,CODELEN+1) if i+j <= CODELEN ]

### States for MasterMind

class MMstate:
    def __init__(self,code,guess,checked):
        self.code = code
        self.guess = guess
        self.checked = checked
    def __hash__(self):
        return sum([ c+c*i*i for i,c in enumerate(self.code) ]) + sum([ 3*c+2*c*i*i for i,c in enumerate(self.guess) ]) + self.checked
    def __eq__(self,other):
        return isinstance(other,MMstate) and self.code == other.code and self.guess == other.guess and self.checked == other.checked
    def __str__(self):
        return "(" + ' '.join([str(w) for w in self.code]) + " : " + ' '.join([str(w) for w in self.guess]) + " : " + str(self.checked) + ")"
    def clonestate(self):
        return MMstate(self.code,self.guess.copy(),self.checked)

    # Which actions applicable in a state?

    def applActions(self):
        return [ MMcheckGuess() for i in [1] if self.guess[len(self.code)-1] > -1 and self.checked == 0 ] + [ MMsetCode(i,c) for i in range(1,len(self.code)) for c in range(1,MAXCODE+1) if self.guess[i] == -1 and self.guess[i-1] > -1 ] + [ MMsetCode(0,c) for c in range(1,MAXCODE+1) if self.checked == 1 ]

    # Successors of a state w.r.t. an action

    def succs(self,action):
        if isinstance(action,MMsetCode): # Successors with MMsetCode
            s = self.clonestate()
            s.guess[action.index] = action.value
            s.checked = 0
            if action.index == 0:
                for i in range(1,len(self.code)):
                    s.guess[i] = -1
            return {s}
        if isinstance(action,MMcheckGuess): # Successors with MMcheckGuess
            s = self.clonestate()
            s.checked = 1
            return {s}
        raise Exception("Unrecognized action " + str(action))

    # Predecessors of a state w.r.t. an action

    def preds(self,action):
        if isinstance(action,MMsetCode): # Predecessors with MMsetCode
            if self.guess[action.index] == action.value and (action.index == len(self.code)-1 or self.guess[action.index+1] == -1) and self.checked == 0:
                if action.index == 0:
                    # Generate all states in which digits 1,2,3,CODELEN-1
                    # can have any values, and digit 0 is action.value.
                    allcodes = [ list(l) for l in itertools.product(range(1,MAXCODE+1),repeat=CODELEN) ] + [ [ -1 for i in range(0,CODELEN) ] ]
                    return { MMstate(self.code,cd,1) for cd in allcodes }
                else:
                    s = self.clonestate()
                    s.guess[action.index] = -1
                    return {s}
            else:
                return set()
        if isinstance(action,MMcheckGuess): # Predecessors with MMcheckGuess
            if self.guess[len(self.code)-1] > -1 and self.checked == 1:
                s = self.clonestate()
                s.checked = 0
                return {s}
            else:
                return set()
        raise Exception("Unrecognized action " + str(action))

    # Is the state compatible with the observation?

    def compatible(self,observation):
        if isinstance(observation,OBSmmcode):
            rightposition = 0
            for i in range(0,len(self.code)):
                if self.code[i] == self.guess[i]:
                    rightposition = rightposition + 1
            rightcolor = 0
            for c in range(1,MAXCODE+1):
                cntc = 0
                cntg = 0
                for i in range(0,len(self.code)):
                    if self.code[i] == self.guess[i]:
                        continue
                    if self.code[i] == c:
                        cntc = cntc + 1
                    if self.guess[i] == c:
                        cntg = cntg + 1
                rightcolor = rightcolor + min(cntc,cntg)
            #print("COUNTS " + str(self) + " " + str(rightposition) + " " + str(rightcolor))
            if rightposition == observation.posright and rightcolor == observation.poswrong:
                #print("YES: compatible")
                return True
            else:
                #print("NO: incompatible")
                return False
        if isinstance(observation,OBSmmnothing):
            return True
        raise Exception("Unrecognized observation " + str(observation))

import itertools

# Initial states are all possible codes.

def MMinit(codelength):
    allcodes = [ list(l) for l in itertools.product(range(1,MAXCODE+1),repeat=codelength) ]
    return { MMstate(code,[ -1 for x in code ],1) for code in allcodes }

# Goal states are thoses state where the code and the guess agree.

def MMgoal(codelength):
    allcodes = [ list(l) for l in itertools.product(range(1,MAXCODE+1),repeat=codelength) ]
    return { MMstate(code,code,c) for code in allcodes for c in [0,1] }

# Generate a MasterMind problem with code length N.

def MMproblem(N):
    actions = [ MMsetCode(i,c) for i in range(0,N) for c in range(1,MAXCODE+1) ] + [ MMcheckGuess() ]
    return (MMinit(N),MMgoal(N),actions)

# Testing the algorithm with MasterMind.

from POplanFwd import POsolver

import sys

if __name__ == "__main__":
    instance = MMproblem(CODELEN)
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
