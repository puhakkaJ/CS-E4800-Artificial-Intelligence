#!/usr/bin/python3

from time import time
from SATreachability import reachability2fma
import z3_wrapper
from z3 import Solver, Bool, BoolRef, And, Or, Not, sat
#from dpll import dpll

def solve_problem(instance,T):
    print("Solving problem with horizon length " + str(T))
    init,goal,actions = instance
    formula = reachability2fma(init, goal, actions, T)
    #print(str(formula))
    clauses = formula.clauses()
    #for c in clauses:
    #    print(c)
    starting_time = time()
    if False: # Use DPLL
        allvars = list(formula.vars())
        print("Total of " + str(len(allvars)) + " variables")
        result,model = dpll(clauses,allvars.copy())
        if result:
            print("SATISFIABLE")
            truevars = [ v for v in allvars if model[v] ]
        else:
            print("UNSATISFIABLE")
            return
    else: # Use Z3
        result = {True: "Satisfiable", False: "Unsatisfiable"}
        z3_result, m, z3_duration = z3_wrapper.solve(clauses)
        print("Z3 result:",end=' ')
        print(result[z3_result],end=',  ')
        print("runtime : {}(s)".format(z3_duration))
        if z3_result:
            truevars = []
            for v in formula.vars():
                if m[Bool(v)]:
                    truevars.append(v)
        else:
            return
    print("PLAN:")
    plan = []
    for v in truevars:
        if v.startswith("ACTION"):
            name,t = v.split("@")
            plan.append( (name[6:],int(t)) )
    plan.sort(key = (lambda e : e[1]))
    for a,t in plan:
        print(str(t) + ": " + a)

# Robot with two arms moving objects from room 1 to room 2,
# with at most one object held in each arm at a time.
# Plans are repeating the sequence of picking up object(s),
# moving to room 2, dropping off the object(s),
# and then possibly repeating after moving back to room 1.

# Variable for denoting that hand is free, i.e. not holding anything

def freehand(hand):
    return "free" + hand

# Variable for hand holding something

def holds(hand,obj):
    return "holds" + hand + obj

# Variable for object is located in a room (and not being held by the robot)

def at(obj,room):
    return "at" + obj + "_" + room

# Generate problem instance

def gripper(N):
    ROBOT = "R"
    objects = [ "obj" + str(i) for i in range(0,N) ]
    hands = ["RIGHT","LEFT"]
    rooms = ["1","2"]

    init = [ at(obj,"1") for obj in objects ] + [at(ROBOT,"1"),freehand("LEFT"),freehand("RIGHT")]
    goal = [ at(obj,"2") for obj in objects ]


    # Pick up object in hand

    pickups = [ ("pickup" + room + hand + obj,
                 [freehand(hand),at(obj,room),at(ROBOT,room)],
                 [holds(hand,obj)],
                 [at(obj,room),freehand(hand)]) for hand in hands for obj in objects for room in rooms ]

    # Drop off object from hand

    dropoffs = [ ("drop" + room + hand + obj,
                  [holds(hand,obj),at(ROBOT,room)],
                  [at(obj,room),freehand(hand)],
                  [holds(hand,obj)])  for hand in hands for obj in objects for room in rooms ]

    # Move ROBOT from room 1 to room 2, or vice versa.
    moves = [("move1to2",[at(ROBOT,"1")],[at(ROBOT,"2")],[at(ROBOT,"1")]),
             ("move2to1",[at(ROBOT,"2")],[at(ROBOT,"1")],[at(ROBOT,"2")])]

    # All actions
    actions = pickups + dropoffs + moves

    return (init,goal,actions)

def main():
    # Test the gripper problem.
    # With 5 or 6 objects horizon of length 12 is needed.
    # Until horizon 11 formulas are unsatisfiable. Last one is satisfiable.
    # Additional 2 objects always require 4 steps longer horizon.
    # The runtimes for the last (hardest) unsatisfiable formulas
    # grow exponentially, roughly doubling every step.
    # The satisfiable formulas after them tend to be much easier.
    print("Gripper with 1 object")
    for i in range(0,4):
        solve_problem(gripper(1),i)
    print("Gripper with 5 objects")
    for i in range(0,12):
        solve_problem(gripper(5),i)

main()
