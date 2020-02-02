"""
Plot solutions to common recurrences
"""

import simpleplot
import math


# select index of recurrence for analysis
INDEX = 8

# dictionary of right hand sides for recurrences
LHS_DICT = {0 : lambda n : recur(n - 1) + 1,
            1 : lambda n : recur(n - 1) + n,
            2 : lambda n : 2 * recur(n - 1),
            3 : lambda n : n * recur(n - 1),
            4 : lambda n : recur(n / 2) + 1,
            5 : lambda n : recur(n / 2) + n,
            6 : lambda n : 2 * recur(n / 2),
            7 : lambda n : 2 * recur(n / 2) + 1,
            8 : lambda n : 2 * recur(n / 2) + n}

def recur(num):
    """
    Common recurrences, always make sure that recursive
    calls involve smaller integer values
    """    
    if num == 1:
        return 1    
    # Lookup righthand side of the recurrence using dictionary
    rhs = LHS_DICT[INDEX]    
    return rhs(num)



# Dictionary of solution
# These functions are upper bounds for the recurrence
SOL_DICT = {0 : lambda n : n,
            1 : lambda n : 0.5 * n * (n + 1),
            2 : lambda n : 2 ** (n - 1),
            3 : lambda n : math.factorial(n),
            4 : lambda n : math.log(n, 2) + 1,
            5 : lambda n : 2 * n - 1,
            6 : lambda n : n,
            7 : lambda n : 2 * n - 1,
            8 : lambda n : n * (math.log(n, 2) + 1)}


def plot_example(length):
    """
    Plot computed solutions to recurrences
    """
    rec_plot = []
    sol_plot = []
    sol = SOL_DICT[INDEX]
    for num in range(2, length):
        rec_plot.append([num, recur(num)])
        sol_plot.append([num, sol(num)])        
    simpleplot.plot_lines("Recurrence solutions", 600, 600, "number", "value", [rec_plot, sol_plot])

  
plot_example(130)