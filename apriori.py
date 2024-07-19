# Working apriori algorithm 

import sys 
from itertools import combinations

min_supp = float(sys.argv[1])
min_supp = min_supp/100
input_file = sys.argv[2]
output_file = sys.argv[3]


def find_consequent(itemset, antecedent): 
    itemset_copy = itemset[:]
    for ant in antecedent:
        itemset_copy.remove(ant)

    return itemset_copy

def get_frequency(database, itemset): 
    freq = 0 
    for transaction in database: 
        is_subset = all(item in transaction for item in itemset)
        if is_subset: 
            freq += 1 
    return freq

def get_confidence(database, antecedent, consequent): 
    union_set = []
    for item in antecedent: 
        union_set.append(item)

    for item in consequent:
        union_set.append(item)
    
    union_freq = get_frequency(database, union_set)
    antecedent_freq = get_frequency(database, antecedent)
    
    return round(float(union_freq*100/antecedent_freq),2)

# write association rules onto file 

def make_association_rules(database, superset_list): 
    with open(output_file, 'w') as file:
        for itemset in superset_list:
            support = get_support(database, itemset) * 100
            for i in range(1,len(itemset)): 
                for antecedent in combinations(itemset, i): 
                    antecedent = list(antecedent)
                    con = find_consequent(itemset, antecedent)
                    confidence = get_confidence(database, antecedent, con)
                    ant_formatted = list_to_string(antecedent)
                    con_formatted = list_to_string(con)
                    file.write(f"{ant_formatted}\t{con_formatted}\t{support:.2f}\t{confidence:.2f}\n")      
    return

def list_to_string(given_list):
    list_str = '{' +  ', '.join(str(item) for item in given_list) + '}'
    return list_str

def extract_supersets(database, candidates_list): 
    supersets = []
    for k_sized_itemsets in reversed(candidates_list): 
        for itemset in k_sized_itemsets: 
            if not check_superset(supersets, itemset): 
                supersets.append(itemset)
    return supersets

# given a super list and a list, check if the list is already a subset of the superlist 

def check_superset(superset_list, pot_list):

    if len(superset_list) == 0: 
        return False

    for itemset in superset_list: 
        matches = 0
        for pot in pot_list: 
            if pot in itemset: 
                matches += 1
            if matches == len(pot_list):
                return True 

    return False 

def printout(database, frequency_patts):
    for k in frequency_patts: 
        for pattern in k: 
            supp = get_support(database, pattern)
          

def remove(itemset, item): 
    del(itemset[item])



# Makes a copy of the itemset only containing the candidates 

def filter_can(itemset, min_supp): 
    filtered_itemset = {}
    for item in itemset: 
        if itemset[item] >= float(min_supp): 
            filtered_itemset[item] = itemset[item]
    return filtered_itemset



def list_contains_sublist(list_of_lists, target_list): 

    for sublist in list_of_lists:
        if sorted(sublist) == sorted(target_list):
            return True
    return False


### given the previous itemset, construct the next batch of itemsets 

def joinset(database, itemset, k): 

    new_itemset = []

    i = 0 

    while i < len(itemset): 
        skip = 1 
        candidate_temp = []
           
        for j in range(i +1, len(itemset)): 
            matching_elements = matches(itemset[i], itemset[j])
            
            if matching_elements >= k : 
                    potential_candidate = sorted(combine(itemset[i], itemset[j]))
            
                    if not list_contains_sublist(new_itemset, potential_candidate):
                        new_itemset.append(potential_candidate)

        i+=1

    final_candidates = filter_frequent(database, new_itemset)
   
    return final_candidates 

#given two itemsets, return the number of matching elements 

def matches(itemset1, itemset2): 
    matches = 0 
    for item1 in itemset1:
        for item2 in itemset2: 
            if item1 == item2: 
                matches += 1

    return matches


#given two itemsets, append them to eachother without any copies 

def combine(itemset1, itemset2): 
    if itemset1 is None:
        return itemset2
    elif itemset2 is None: 
        return itemset1 
    else:
        set1 = set(itemset1)
        set2 = set(itemset2)
        combined_set = set1.union(set2)
        return list(combined_set)

# given an itemset of potential candidates, filters out those below the support threshold and returns a final candidate list 

def filter_frequent(database,itemset): 
    final_can = []
    for item in itemset: 
        if (get_support(database, item) >= min_supp): 
            final_can.append(item)
    return final_can

# given a set of numbers, determine conduct a lookup of its frequency 

def get_support(database, itemset): 
    freq = 0 
    total = 0 
    for transaction in database: 
        total += 1 
        is_subset = all(item in transaction for item in itemset)
        if is_subset: 
            freq += 1 
    result = float(freq/total)
    return result 

# database structure is a list of arrays where each index of the list represents an array of values in the transaction 

def main():
    itemsets = set()
    counts = dict()
    database = []



    with open(input_file, 'r') as dataset: 
        tran_count = 0 
        for transaction in dataset: 
            tran_count += 1
            transaction = transaction.strip()
            numbers = transaction.split()
            transaction_values = []
            for number in numbers: 
                number = int(number)
                counts[number] = counts.get(number, 0) + 1
                itemsets.add(number)
                transaction_values.append(number)
            database.append(transaction_values)

    # sorts candidates in ascending  order 

    cans = list(counts.keys())
    cans.sort()
    itemset = {i: counts[i] for i in cans}

    #First iteration of candidates 

    candidates_freq = filter_can(itemset, min_supp) 
    full_list = []
    candidates_list = [[]]
    for candidate in candidates_freq: 
        candidates_list[0].append(candidate)
    candidates_list[0] = [[x] for x in candidates_list[0]]

    # DATA MODEL [[[1,2], [3,4], [5,6]], [[1],[2],[3],[4],[5]]]

    k = 0

    #size 1 candidates are at index 0, therefore k-1 is the size of the itemset 

    while candidates_list[k]: 
        next_candidates = joinset(database, candidates_list[k], k) 
        
        if len(next_candidates) == 0: 
            break
            
        candidates_list.append(next_candidates)

        if len(candidates_list[k]) == 0 : 
            break
      
        k += 1 

    freq_supersets = extract_supersets(database, candidates_list)
    make_association_rules(database, freq_supersets)
    return


if __name__ == "__main__":
    main()
