
from logic import *

# Mapping from actions and initial and goal states to a formula

# Turn variable name 'x' to an atomic formula 'x@t'.

def timedVar(varname,time):
    return ATOM(varname + "@" + str(time))

# Turn action name 'x' to an atomic formula 'x@t'.

def timedAction(varname,time):
    return ATOM("ACTION" + varname + "@" + str(time))

# Two actions cannot be taken at the same time?

def exclusive(c1,pe1,ne1,c2,pe2,ne2):
    return (bool(set(c1) & set(ne2))) or (bool(set(ne1) & set(c2)))

# DO NOT MODIFY ANY DEFINITION ABOVE THIS LINE

# Map a reachability problem to a propositional formula

def reachability2fma(init,goal,actions,T):
    initvars = { v for v in init }
    goalvars = { v for v in goal }
    actioncvars = { v for n,c,pe,ne in actions for v in c }
    actionpvars = { v for n,c,pe,ne in actions for v in pe }
    actionnvars = { v for n,c,pe,ne in actions for v in ne }
    varsets = [initvars,goalvars,actioncvars,actionpvars,actionnvars]
    allStateVars = set().union(*varsets)

    initformulas = [ timedVar(v,0) for v in initvars ] + [ NOT(timedVar(v,0)) for v in allStateVars if v not in initvars ]

    goalformulas = [ timedVar(v,T) for v in goalvars ]

    preconditions = [ IMPL(timedAction(n,t),timedVar(x,t)) for n,c,pe,ne in actions for t in range(0,T) for x in c ]

    posEffects = [IMPL(timedAction(n, t), timedVar(x, t + 1)) for n, c, pe, ne in actions for t in range(0, T) for x in pe]

    negEffects = [IMPL(timedAction(n, t), NOT(timedVar(x, t + 1))) for n, c, pe, ne in actions for t in range(0, T) for x in ne]


    list1 = []
    for x in allStateVars:
        for t in range(0, T):
            or1 = []
            for n, c, pe, ne in actions:
                if x in pe:
                    or1 = or1 + [timedAction(n, t)]
            list1 = list1 + [IMPL(AND([NOT(timedVar(x, t)), timedVar(x, t +1 )]), OR(or1))]

    posFrameAxioms = list1

    list2 = []
    for x in allStateVars:
        for t in range(0,T):
            or2 = []
            for n, c, pe, ne in actions:
                if x in ne:
                    or2 = or2 + [timedAction(n, t)]
                    
            list2 = list2 + [IMPL(AND([timedVar(x, t), NOT(timedVar(x, t + 1))]), OR(or2))]

    negFrameAxioms = list2

    list3 = []
    for n1, c1, pe1, ne1 in actions:
        for n2, c2, pe2, ne2 in actions:
            if exclusive(c1, pe1, ne1, c2, pe2, ne2):
                if n1 != n2:
                    for t in range(0, T):
                        list3 = list3 + [NOT(AND([timedAction(n1, t)] + [timedAction(n2, t)]))]

    actionMutexes = list3

    return AND(initformulas + goalformulas + preconditions + posEffects + negEffects + posFrameAxioms + negFrameAxioms + actionMutexes)
