"""
Cookie Clicker Simulator
"""

import simpleplot
import math

# Used to increase the timeout, if necessary
import codeskulptor
codeskulptor.set_timeout(20)

import poc_clicker_provided as provided

# http://www.codeskulptor.org/#poc_clicker_provided.py

# Constants
SIM_TIME = 10000000000.0

class ClickerState:
    """
    Simple class to keep track of the game state.
    """
    
    def __init__(self):
        self._total_cookies = 0.0
        self._curr_cookies = 0.0
        self._time = 0.0
        self._cps = 1.0
        self._history = [(0.0, None, 0.0, 0.0)]
        # a time, an item that was bought at that time (or None), the cost of the item, and the total number of cookies produced by that time
        
    def __str__(self):
        """
        Return human readable state
        """
        return "\n" + "total cookies: " + str(self._total_cookies) + "\n" + \
        "curr cookies: " + str(self._curr_cookies) + "\n" + \
        "time elapsed: " + str(self._time) + "\n" + "curr cps: " + str(self._cps)
        
    def get_cookies(self):
        """
        Return current number of cookies 
        (not total number of cookies)
        
        Should return a float
        """
        return self._curr_cookies
    
    def get_cps(self):
        """
        Get current CPS

        Should return a float
        """
        return self._cps
    
    def get_time(self):
        """
        Get current time

        Should return a float
        """
        return self._time
    
    def get_history(self):
        """
        Return history list

        History list should be a list of tuples of the form:
        (time, item, cost of item, total cookies)

        For example: [(0.0, None, 0.0, 0.0)]

        Should return a copy of any internal data structures,
        so that they will not be modified outside of the class.
        """
        return list(self._history)

    def time_until(self, cookies):
        """
        Return time until you have the given number of cookies
        (could be 0.0 if you already have enough cookies)

        Should return a float with no fractional part
        """
        diff = cookies - self._curr_cookies
        if diff <= 0:
            time = 0.0
        else:
            time = math.ceil(diff / self._cps)
        return time
    
    def wait(self, time):
        """
        Wait for given amount of time and update state

        Should do nothing if time <= 0.0
        """
        if time <= 0.0:
            return None
            
        self._time += time
        self._total_cookies += self._cps * time
        self._curr_cookies += self._cps * time
        
    
    def buy_item(self, item_name, cost, additional_cps):
        """
        Buy an item and update state

        Should do nothing if you cannot afford the item
        """
        if cost > self._curr_cookies:
            return
            
        self._curr_cookies -= cost
        self._cps += additional_cps
        hist = tuple([self._time, item_name, cost, self._total_cookies])
        self._history.append(hist)

    
def simulate_clicker(build_info, duration, strategy):
    """
    Function to run a Cookie Clicker game for the given
    duration with the given strategy.  Returns a ClickerState
    object corresponding to the final state of the game.
    """

    build = build_info.clone()
    game = ClickerState()
    
    while game.get_time() <= duration:
        time_left = duration - game.get_time()
        item = strategy(game.get_cookies(), game.get_cps(), game.get_history(), time_left, build)
        if item == None:
            break
        cost = build.get_cost(item)
        additional_cps = build.get_cps(item)
        wait_time = game.time_until(cost)
        if wait_time > time_left:
            break
        game.wait(wait_time)
        game.buy_item(item, cost, additional_cps)
        build.update_item(item)
        
    time_left = duration - game.get_time()
    if time_left > 0:
        game.wait(time_left)

    return game


def strategy_cursor_broken(cookies, cps, history, time_left, build_info):
    """
    Always pick Cursor!

    Note that this simplistic (and broken) strategy does not properly
    check whether it can actually buy a Cursor in the time left.  Your
    simulate_clicker function must be able to deal with such broken
    strategies.  Further, your strategy functions must correctly check
    if you can buy the item in the time left and return None if you
    can't.
    """
    return "Cursor"

def strategy_none(cookies, cps, history, time_left, build_info):
    """
    Always return None

    This is a pointless strategy that will never buy anything, but
    that you can use to help debug your simulate_clicker function.
    """
    return None

def strategy_cheap(cookies, cps, history, time_left, build_info):
    """
    Always buy the cheapest item you can afford in the time left.
    """
    min_cost = 999999999999.0
    min_item = None
    for item in build_info.build_items():
        cost = build_info.get_cost(item)
        if cost > cookies and math.ceil((cost - cookies) / cps) > time_left:
            continue
        if cost < min_cost:
            min_cost = cost
            min_item = item
    return min_item

def strategy_expensive(cookies, cps, history, time_left, build_info):
    """
    Always buy the most expensive item you can afford in the time left.
    """
    max_cost = -999999999999.0
    max_item = None
    for item in build_info.build_items():
        cost = build_info.get_cost(item)
        if cost > cookies and math.ceil((cost - cookies) / cps) > time_left:
            continue
        if cost > max_cost:
            max_cost = cost
            max_item = item
    return max_item

def strategy_best(cookies, cps, history, time_left, build_info):
    """
    The best strategy that you are able to implement.
    """
    max_benefit = 0
    best_item = None
    for item in build_info.build_items():
        # calculate cost, new_cps
        cost = build_info.get_cost(item)
        new_cps = build_info.get_cps(item)
        if (cost - cookies) > 0 and math.ceil((cost - cookies) / cps) > time_left:
            continue

        # calculate net benefits of buying the item
        benefit = new_cps / cost
        if benefit > max_benefit:
            max_benefit = benefit
            best_item = item
    return best_item
        
        
def run_strategy(strategy_name, time, strategy):
    """
    Run a simulation for the given time with one strategy.
    """
    state = simulate_clicker(provided.BuildInfo(), time, strategy)
    print strategy_name, ":", state

    # Plot total cookies over time

    # Uncomment out the lines below to see a plot of total cookies vs. time
    # Be sure to allow popups, if you do want to see it

    # history = state.get_history()
    # history = [(item[0], item[3]) for item in history]
    # simpleplot.plot_lines(strategy_name, 1000, 400, 'Time', 'Total Cookies', [history], True)

def run():
    """
    Run the simulator.
    """    
    run_strategy("Cursor", SIM_TIME, strategy_cursor_broken)
    run_strategy("None", SIM_TIME, strategy_none)

    # Add calls to run_strategy to run additional strategies
    run_strategy("Cheap", SIM_TIME, strategy_cheap)
    run_strategy("Expensive", SIM_TIME, strategy_expensive)
    run_strategy("Best", SIM_TIME, strategy_best)
    
run()
