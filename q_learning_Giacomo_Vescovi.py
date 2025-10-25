# -*- coding: utf-8 -*-
"""
Created on Wed Jan  8 14:05:18 2025

This code is based on the various programming sheets handed during the course CIT413036

@author: Giacomo Vescovi
"""


# importing libraries ############################### 

import matplotlib.pyplot as plt
import numpy as np
import random
import operator



# parameters ########################################

T     = 3     #Time horizon
u     = 1.0   #CRR parameter, up factor change
d     = -.5   #CRR parameter, down factor change
q     = .5    #CRR parameter, probability of up change
gamma = .95
start_state= (0., 8., 100.)



# function to compute all admissible actions #########

def get_admissible_actions(p, w):
    
    max_num_assets = int(np.floor(w/p))
    
    
    return [p * i for i in range(max_num_assets + 1)]



# we compute all possible states #####################

def get_all_states():
    
    states = [start_state]
    
    
    
    for state in states:
        if state[0] < T:
            for a in get_admissible_actions(state[1],state[2]):
                for R in [d,u]:
                    
                    new_state = ( state[0] + 1,
                                  state[1] * (1+R),
                                  state[2] + R * a
                                )
                    states.append(new_state)
                    
    
    states = list(set(states))

    return states


# we compute the step function ##########################

def step(state, action): #state = [time, price, wealth]
    time   = state[0]
    price  = state[1]
    wealth = state[2]
    assert action <= wealth   #check that no more money is invested than the current wealth        
    assert action %  price  == 0   #only integer number of assets can be bought
   
    
    time = time + 1 

    R = np.random.choice((d,u), p=(1-q,q))   
    
    price = price * (1+R)    
    wealth = wealth + action * R  
    
     
    reward = 0
    if time == T:
        reward = np.log(wealth)

        
    
    
    return (time, price, wealth), reward


def b_policy (state, q_table, epsilon):
    #l = len(q_table[state])
    l= 1
    admissible_actions = list(q_table[state].keys())
    
    
    if state[1]> state[2]:
        return 0
    
    control = np.random.choice((1,0), p =(epsilon/l, 1- epsilon/l)) 
    optimal_action = max(q_table[state].items(), key = operator.itemgetter(1) )[0]
    if control ==0: 
        action = optimal_action
    else:
        admissible_actions.remove(optimal_action) #we remove the optimal action to avoid choosing it
        action = random.choice(admissible_actions)
    
    return action
    
        
    
        


def Q_learning(iterations):
    states = get_all_states()
    
    # inizialisation 
    q_table = {state: {action: 0 for action in get_admissible_actions(state[1], state[2]) } for state in states}
    state_action_visits = {state: {action: 0 for action in get_admissible_actions(state[1], state[2]) } for state in states}
    learning_rate = {state: {action: 0 for action in get_admissible_actions(state[1], state[2]) } for state in states}
    
    
    for i in range(iterations):
        epsilon = 0.6
        state = random.choice(states) #we start from a random state
        t= state[0]
        while t<=T:
            action = b_policy(state, q_table, epsilon)
            
            if t< T:
                next_state, reward = step(state, action)
            
                next_best_action = max(q_table[next_state].items(), key = operator.itemgetter(1) )[0]
            
                q_learning_target = reward + gamma* q_table[next_state][next_best_action]
                q_table[state][action] += learning_rate[state][action] * (q_learning_target-q_table[state][action])
            
                state_action_visits[state][action] += 1
                learning_rate[state][action] = 1/(1+state_action_visits[state][action])
                
                state = next_state
                t = next_state[0]
            
            else: 
                q_learning_target = np.log(state[2])
                q_table[state][action] += learning_rate[state][action] * (q_learning_target-q_table[state][action])
                
                t=4
            
                state_action_visits[state][action] += 1
                learning_rate[state][action] = 1/(1+state_action_visits[state][action])
            
    return q_table


def optimal_investment_plotting(iterations):
    q_table = Q_learning(iterations)
    plot_states = []
    plot_states_opt = []
    min_wealth = + np.inf
    max_wealth = - np.inf
    states= get_all_states()
    for state in states:
        if state[0]<T:
            best_action = max(q_table[state].items(), key = operator.itemgetter(1) )[0]
            plot_states_opt.append((state[2], best_action))
    
    
    for state in states:
        for action in get_admissible_actions(p=state[1], w=state[2]):
            if state[0]<T:
                plot_states.append((state[2],action))
            if min_wealth > state[2]:
                min_wealth = state[2]
            if max_wealth < state[2]:
                max_wealth = state[2]
                
    fig, ax = plt.subplots()
    ax.scatter(*zip(*plot_states), c='#0065bd')
    ax.scatter(*zip(*plot_states_opt), c='#F7811E')
    opt_frac = -q/d-(1-q)/u
    ax.plot([min_wealth, 400], [opt_frac*min_wealth, opt_frac*400], c='black')
    plt.xlabel("Total Wealth ( " + str(iterations) + " iterations) ")
    plt.ylabel("Wealth in Financial Asset")
    plt.savefig("opt_policy")
    plt.show()
                











            
            
        

    


    
    
    
    
    
    
    
    
