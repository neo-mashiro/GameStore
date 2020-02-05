"""
Student code for Word Wrangler game
"""

import urllib2
import codeskulptor
import poc_wrangler_provided as provided

WORDFILE = "assets_scrabble_words3.txt"


# Functions to manipulate ordered word lists

def remove_duplicates(list1):
    """
    Eliminate duplicates in a sorted list.

    Returns a new sorted list with the same elements in list1, but
    with no duplicates.

    This function can be iterative.
    """
    result = []
    for index in range(len(list1)):
        if list1[index] not in result:
            result.append(list1[index])
    return result

def intersect(list1, list2):
    """
    Compute the intersection of two sorted lists.

    Returns a new sorted list containing only elements that are in
    both list1 and list2.

    This function can be iterative.
    """
    result = []
    list3 = list(list1)
    list4 = list(list2)
    
    for index in range(len(list3)):
        if list3[index] in list4:
            result.append(list3[index])

    return result

# Functions to perform merge sort

def merge(list1, list2):
    """
    Merge two sorted lists.

    Returns a new sorted list containing those elements that are in
    either list1 or list2.

    This function can be iterative.
    """   
    list3 = list(list1)
    list4 = list(list2)
    
    if len(list3) == 0:
        return list4
    elif len(list4) == 0:
        return list3
        
    result = []
    while len(list3) > 0:
        if len(list4) == 0:
            return result + list3
        if list3[0] <= list4[0]:
            nxt = list3.pop(0)
        else:
            nxt = list4.pop(0)
        result.append(nxt)
        
    return result + list4
                
def merge_sort(list1):
    """
    Sort the elements of list1.

    Return a new sorted list with the same elements as list1.

    This function should be recursive.
    """
    # base case
    if len(list1) <= 1:
        return list1
    # recursive case
    mid = len(list1) / 2
    left = merge_sort(list1[:mid])
    right = merge_sort(list1[mid:])
    return merge(left, right)

# Function to generate all strings for the word wrangler game

def gen_all_strings(word):
    """
    Generate all strings that can be composed from the letters in word
    in any order.

    Returns a list of all strings that can be formed from the letters
    in word.

    This function should be recursive.
    """
    # base case
    if len(word) == 0:
        return [""]
    # recursive case
    first = word[0]
    rest = word[1:]
    rest_strings = gen_all_strings(rest)
    
    result = list(rest_strings)
    for each in rest_strings:
        for pos in range(len(each) + 1):
            result.append(each[:pos] + first + each[pos:])
            	
    return result

# Function to load words from a file

def load_words(filename):
    """
    Load word list from the file named filename.

    Returns a list of strings.
    """
    result = []
    url = codeskulptor.file2url(filename)  
    file = urllib2.urlopen(url)
    for line in file.readlines():
        result.append(line[:-1])
    return result

def run():
    """
    Run game.
    """
    words = load_words(WORDFILE)
    wrangler = provided.WordWrangler(words, remove_duplicates, 
                                     intersect, merge_sort, 
                                     gen_all_strings)
    provided.run_game(wrangler)

# Uncomment when you are ready to try the game
# run()

