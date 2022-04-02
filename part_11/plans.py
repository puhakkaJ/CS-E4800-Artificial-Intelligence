
#
# Branching plans
# Plans have two types of nodes
#   PlanEmpty: Do nothing, Here the execution ends.
#   PlanNode: Consists of two parts
#                action
#                list of pairs
#                    observation
#                    sub-plan
#                   so that the sub-plan is executed
#                   if the observation is made after
#                   the action is taken.
#              The observations must be exactly those observations
#              that are possible for the action.
#
# The methods for plans:
#  plan2str   Map a plan to a list of strings for displaying it.
#  plansize   Number of action nodes in a plan
#  plandepth  Highest number of actions on any plan through a plan
#  validate   Test that every execution terminates in a goal state
#

# Plan with action and observations followed by a sub-plan

class PlanNode:
    def __init__(self,action,children):
        self.action = action
        self.children = children

    def plan2str(self):
        plan = [str(self.action)]
        for o,p in self.children:
            if len(self.children) > 1:
                plan.append("  " + str(o))
            subplan = p.plan2str()
            for s in subplan:
                plan.append("    " + s)
        return plan

    # Size is number of action nodes in the plan.

    def plansize(self):
        sz = 1
        for o,p in self.children:
            sz = sz + p.plansize()
        return sz

    # Depth is the highest number of actions on any path through plan.

    def plandepth(self):
        depth = 0
        for o,p in self.children:
            depth2 = p.plandepth()
            if 1 + depth2 > depth:
                depth = 1 + depth2
        return depth

    # Test if all executions lead to a goal state.

    def validate(self,state,goalstates):
        for state2 in state.succs(self.action):
            covered = False
            for obs,subplan in self.children:
                if state2.compatible(obs):
                    if not subplan.validate(state2,goalstates):
                        print(str(state2))
                        return False
                    covered = True
            if not covered:
                print("Plan does not cover all states.")
                print(str(state2))
                return False
        return True

# The empty plan that marks the termination of an execution.

class PlanEmpty:
    def __init__(self):
        self.dummy = 1

    def plan2str(self):
        return []

    # Size is number of action nodes in the plan.

    def plansize(self):
        return 0

    # Depth is the highest number of actions on any path through plan.

    def plandepth(self):
        return 0

    # Test if all executions lead to a goal state.

    def validate(self,state,goalstates):
        if state in goalstates:
            return True
        else:
            return False
