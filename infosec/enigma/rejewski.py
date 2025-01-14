#!/usr/bin/env python
# encoding: utf-8

"""
   @author: Joshua Tallman
  @license: MIT Licence
  @contact: joshua.tallman@cui.edu
     @file: rejewski.py
     @time: 2020-08-14 20:31
"""

# For calculating the Rejewski Tables that allow a cryptanlyst to lookup
# scrambler settings based on having a collection of intercepts that have
# had their message key encrypted with the same daily key


from itertools import permutations
from itertools import product
import string
import enigma


def generate_mock_cribs(ref, L_rot, M_rot, R_rot, L_pos, M_pos, R_pos):
    """ Generates cribs for the 3-letter repeated message key. Returns cribs
        for all of the possible message keys sequences that could possibly
        be chosen for this selection of scramblers and starting positions.
        
        For example, initial settings II(J), I(R), III(T), B produces:
            ['YQRQVO', 'IECHLJ', 'LNBOGD', ..., 'ATJIZG', 'WDMNYL']
            
        The first element is the ciphertext that would be created if the
        message key included an A in any position. The second element is
        for B, third for C, and so on.
    """   
    cribs = []
    e = enigma.m3()
    for x in string.ascii_uppercase:    
        e.reset(ref, L_rot, M_rot, R_rot, L_pos, M_pos, R_pos)
        c = e.keypress(x) + e.keypress(x) + e.keypress(x) + \
            e.keypress(x) + e.keypress(x) + e.keypress(x)
        cribs.append((x*3, c))
    return cribs
    

def link_crib_pairs(cribs, pair_idx_a, pair_idx_b):
    """ Creates a full A-Z dict of the relationships between the cribs for a
        given message key (0xx3xx or x1xx4x or xx2xx5), as specified by the
        'pair_idx_a' and 'pair_idx_b' parameters.
        
        The cribs should include all possible message keys for an initial
        scrambler setting, such as II(J), I(R), III(T), B:
            ['YQRQVO', 'IECHLJ', 'LNBOGD', ..., 'ATJIZG', 'WDMNYL']
              |  |      |  |      |  |           |  |      |  |
              
        Produces a dictionary that looks like this (for positions 0 and 3):
            { 'Y':'Q', 'I':'H', 'L':'O', ..., 'A':'I', 'W':'N' }
    """
    pairs = {}
    for pt, crib in cribs:
        pairs[crib[pair_idx_a]] = crib[pair_idx_b]
    return pairs


def walk_chain(scratch_table, start):
    """ Counts the number of links in a Rejewski cycle, deleting each item
        from the link-pair table as it goes so that the cycle will not be
         counted a second time.
    """
    curr = scratch_table[start]
    prev = curr
    chain = curr

    count = 1
    while curr != start:            # keep looping until we complete a cycle
        curr = scratch_table[prev]  # next letter in the chain
        del scratch_table[prev]
        chain += curr
        prev = curr
        count += 1
    return (chain, count)


def calculate_chain_lengths(relationship_table):
    """ Count the lengths of all the unqiue chains in the given table.
    """
    
    # Our algorithm deletes items from the relationship table as it goes. We
    # create a copy of the table so as not to change the original data
    scratch = relationship_table.copy()

    # Create a CSV string containing the length of all chains
    chains = ""
    while len(scratch) > 0:                       # loop through all chains
        start  = list(sorted(scratch.keys()))[0]  # start of the next chain
        crib, length = walk_chain(scratch, start) # get the length
        chains += "{},".format(length)            # add length to the list
        del scratch[start]
    return chains[:-1]                            # omit the trailing comma


def calculate_chain_index(ref, L_rot, M_rot, R_rot, L_pos, M_pos, R_pos):
    """ Generates an index to access a Rejewski table for the given intial
        settings. The index is a string that combines the chain lengths for
        the 1st & 4th crib letters, the 2nd & 5th, and the 3rd and 6th.
        
        A valid index looks something like this: 10,10,3,3-9,3,9,3,1,1-13,13
    """

    # Get cribs for all of the possible message keys
    cribs = generate_mock_cribs(ref, L_rot, M_rot, R_rot, L_pos, M_pos, R_pos)

    # Link up the matching 1st & 4th, 2nd & 5th, and 3rd & 6th key positions
    crib_pairs_0_3 = link_crib_pairs(cribs, 0, 3)
    crib_pairs_1_4 = link_crib_pairs(cribs, 1, 4)
    crib_pairs_2_5 = link_crib_pairs(cribs, 2, 5)
    
    # Now calculate the lengths of all chains within the key position chains
    chains_0_3 = calculate_chain_lengths(crib_pairs_0_3)
    chains_1_4 = calculate_chain_lengths(crib_pairs_1_4)
    chains_2_5 = calculate_chain_lengths(crib_pairs_2_5)
    
    # Create a mutable string that will suffice as a dict key
    chain_index = "{}|{}|{}".format(chains_0_3, chains_1_4, chains_2_5)
    return chain_index


def generate_rejewski_table(rotor_list, reflector_list):
    """ Calculate a full Rejewski Chain-Link Table for the given set of rotors
        and the reflector. There are a little more than 100,000 entries in a 
        3-rotor, 1-reflector Enigma Machine.
        
        Results are indexed by the chain-link lengths with the values being a
        list of initial settings. For example:
        
           Sample index:     '10,10,3,3|9,3,9,3,1,1|9,9,4,4'
           Initial settings: ['II:I, I:Q, III:T | B', 'II:J, I:R, III:T | B']
    """
    rejewski_table = {}
    
    for ref in reflector_list:
        rotors   = permutations(rotor_list, 3)
        for rot in rotors:
            letters  = product(string.ascii_uppercase, repeat=3)
            for pos in letters:
                chain_index = calculate_chain_index(ref,
                                                    rot[0], rot[1], rot[2], 
                                                    pos[0], pos[1], pos[2])
                config_fmt = "{} | {}:{}, {}:{}, {}:{}"
                config = config_fmt.format(ref,
                                           rot[0], pos[0], 
                                           rot[1], pos[1], 
                                           rot[2], pos[2])
                if chain_index not in rejewski_table:
                    rejewski_table[chain_index] = [ config ]
                else:
                    rejewski_table[chain_index].append(config)
    
    return rejewski_table


if __name__ == "__main__":
   
    output = generate_rejewski_table(["I", "II", "III"], [ "B" ])
    print("\nRejewski Table Complete")

    max_len = 0
    max_idx = -1
    for key, value in output.items():
        if len(value) > max_len:
            max_len = len(value)
            max_idx = key

    sample = '12,12,1,1|13,13|3,3,5,3,3,1,1,5,1,1'
    settings = output[sample]

    print("  {} total indices".format(len(output)))
    print("  {} is the most common index".format(max_idx))
    print("  it has {} initial settings".format(max_len))
    print()
    print("  Sample index '{}' maps to intitial settings:".format(sample))
    print("  {}".format(settings))