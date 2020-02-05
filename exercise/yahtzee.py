"""
Planner for Yahtzee
Simplifications:  only allow discard and roll, only score against upper level
"""

# Used to increase the timeout, if necessary
import codeskulptor
codeskulptor.set_timeout(20)

# this function of generating all sequences is very important
def gen_all_sequences(outcomes, length):
    """
    Iterative function that enumerates the set of all sequences of
    outcomes of given length.
    """
    
    answer_set = set([()])
    for dummy_idx in range(length):
        temp_set = set()
        for partial_sequence in answer_set:
            for item in outcomes:
                new_sequence = list(partial_sequence)
                new_sequence.append(item)
                temp_set.add(tuple(new_sequence))
        answer_set = temp_set
    return answer_set


# this function of generating all sorted sequences is very important
def gen_sorted_sequences(outcomes, length):
    """
    Function that creates all sorted sequences via gen_all_sequences
    """    
    all_sequences = gen_all_sequences(outcomes, length)
    sorted_sequences = [tuple(sorted(sequence)) for sequence in all_sequences]
    return set(sorted_sequences)
    
    
def score(hand):
    """
    Compute the maximal score for a Yahtzee hand according to the
    upper section of the Yahtzee score card.

    hand: full yahtzee hand

    Returns an integer score 
    """
    scoreboard = {}
    for dice in hand:
        if dice not in scoreboard.keys():
            scoreboard[dice] = dice
        else:
            scoreboard[dice] += dice
    
    max_score = 0
    for dice, score in scoreboard.items():
        if score >= max_score:
            max_score = score
            
    return max_score


def expected_value(held_dice, num_die_sides, num_free_dice):
    """
    Compute the expected value based on held_dice given that there
    are num_free_dice to be rolled, each with num_die_sides.

    held_dice: dice that you will hold -- a sorted tuple
    num_die_sides: number of sides on each die
    num_free_dice: number of dice to be rolled

    Returns a floating point expected value
    """
    outcomes = list(range(1, num_die_sides + 1))
    sequences = gen_all_sequences(outcomes, num_free_dice)
    prob = 1.0 / len(sequences)
    
    ev = 0
    for seq in sequences:
        seq_hand = list(held_dice)
        seq_hand += list(seq)
        seq_hand.sort()
        seq_score = score(seq_hand)
        ev += prob * seq_score
            
    return ev


def gen_all_holds(hand):
    """
    Generate all possible choices of dice from hand to hold.

    hand: full yahtzee hand

    Returns a set of tuples, where each tuple is dice to hold
    """
    all_holds = set([()])

    for dice in hand:
        for subset in set(all_holds):
            nxt_subset = list(subset)
            nxt_subset.append(dice)
            nxt_subset.sort()
            all_holds.add(tuple(nxt_subset))
    
    return all_holds


def strategy(hand, num_die_sides):
    """
    Compute the hold that maximizes the expected value when the
    discarded dice are rolled.

    hand: full yahtzee hand
    num_die_sides: number of sides on each die

    Returns a tuple where the first element is the expected score and
    the second element is a tuple of the dice to hold
    """

    holds = gen_all_holds(hand)
    
    max_ev = 0.0
    best_hold = ()
    for hold in holds:
        ev = expected_value(hold, num_die_sides, len(hand) - len(hold))
        if ev > max_ev:
            max_ev = ev
            best_hold = hold
            
    return (max_ev, best_hold)


def run_example():
    """
    Compute the dice to hold and expected score for an example hand
    """
    num_die_sides = 6
    hand = (1, 1, 1, 5, 6)
    hand_score, hold = strategy(hand, num_die_sides)
    print "Best strategy for hand", hand, "is to hold", hold, "with expected score", hand_score
    
    
run_example()


#import poc_holds_testsuite
#poc_holds_testsuite.run_suite(gen_all_holds)
                                       
    
    
    



