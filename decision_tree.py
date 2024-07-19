import sys 
import math 
import pandas as pd 



#read all data into an array 

train_file = sys.argv[1]
test_file = sys.argv[2]
result_file = sys.argv[3]


path_to_train_file = f'datasets/{train_file}'
path_to_test_file = f'datasets/{test_file}'

# given the data, find the attribute that gives the highest info gain 


def att_index(attributes, att): 
    i = 0 
    for attribute in attributes: 
        if attribute == att: 
            return i 
        i +=1

    
#assuming we have data, find info
def info(data):
    total = len(data)
    outcomes = find_outcomes(data, -1)
    outcomes_dict = {}
    for outcome in outcomes: 
        outcomes_dict[outcome] = 0
        for row in data: 
            if row[-1] == outcome:
                outcomes_dict[outcome] += 1
    info_val = 0 
    for outcome in outcomes: 
        p_out = outcomes_dict[outcome]/total
        info_val += info_formula(p_out)

    return info_val


def info_formula(p):
    return -1 * p * math.log2(p)

def info_att(data, attribute_index): 
    total = len(data)
    branches = question(data, attribute_index)

    info_attribute = 0 
    for trans in branches.values(): 

        p_branch = (len(trans)/total)*info(trans)

        info_attribute += p_branch

    return info_attribute
    
def gain(info,info_a): 
    return info - info_a


def split_info(data, att_index): 
    total = len(data)
    branches = question(data, att_index)
    split_info = 0 
    for trans in branches.values(): 
        split_info += -1 * len(trans)/total * math.log2(len(trans)/total)

    return split_info


def gain_ratio(data, att_index): 
    info1 = info(data)
    info_after = info_att(data, att_index)
    gain = info1-info_after
    sp_info = split_info(data, att_index)
    if sp_info == 0: 
        return 0 
    final = gain/sp_info
    return final

# given an attribute split based on that attribute 
def question(data, att_index): 

    branches = {}
    outcomes = find_outcomes(data, att_index)
    for outcome in outcomes: 
        branch = [line for line in data if outcome == line[att_index]]
        branches[outcome] = branch

    return branches


#given the data, finds the attribute that is best to split on 

def best_split(data, attributes):
    num_atts = len(attributes) - 1
    best_splitter_gain, best_splitter_att = 0, -1
    for att in range(0,num_atts): 
        gain_rat = gain_ratio(data, att)
        if gain_rat > best_splitter_gain:
            best_splitter_att = att 
            best_splitter_gain = gain_rat

    if best_splitter_gain == 0: 
        return None 
    return best_splitter_att

# given an attribute, return each unique outcome 

def find_outcomes(data, att_index):
    outcomes = set()
    for tran in data: 
        outcomes.add(tran[att_index])
    return(outcomes)


class Decision_Node:

    def __init__(self, question, branches):
        self.question = question
        self.branches = branches
            

class Leaf_Node: 

    def __init__(self, predictions): # predictions, is all the data in that node 
        self.predictions = predictions 





def build_tree(data, attributes):  
    split_node = best_split(data, attributes)
    
    if split_node is None: 
        return Leaf_Node(data)

    branches = question(data, split_node)

    mother_branch = [] # tree of decision nodes

    child_nodes = {}
    for outcome, branch_data in branches.items(): 
        child_nodes[outcome] = build_tree(branch_data)

    return Decision_Node(split_node, child_nodes)


def traverse(sample_row, dec_node):
    question_index = dec_node.question
    counter = 0 
    branch_num = len(dec_node.branches)

    for branch_key, node in dec_node.branches.items(): 
        comparison_att = sample_row[question_index] # looks at the attribute of the sample against question attribute 
        
        if comparison_att == branch_key:

            if isinstance(node, Leaf_Node): 
                classified_as = node.predictions 
                
                count_classifier_final = {}
                for leaf in classified_as: 
                    class_label = leaf[-1]
                    count_classifier_final[leaf[-1]] = count_classifier_final.get(class_label, 0) + 1
                final_assignment = max(count_classifier_final, key=count_classifier_final.get)
                sample_row.append(final_assignment) 
                return
            elif isinstance(node, Decision_Node):
                traverse(sample_row, node)
        else: 
            counter += 1 
            if counter == branch_num: 
                if isinstance(node, Leaf_Node): 
                    classified_as = node.predictions 
                    count_classifier_final = {}
                    for leaf in classified_as: 
                        class_label = leaf[-1]
                        count_classifier_final[leaf[-1]] = count_classifier_final.get(class_label, 0) + 1
                    final_assignment = max(count_classifier_final, key=count_classifier_final.get)
                    sample_row.append(final_assignment) 
                    return
                elif isinstance(node, Decision_Node):
                    traverse(sample_row, node)

    with open(path_to_test_file) as test_file: 
        att_line = test_file.readline().strip()
        atts  =  att_line.split('\t')
        test_set = []
        for line in test_file: 
            row = line.strip()
            row  = row.split('\t')
            test_set.append(row)

    with open(path_to_train_file, 'r') as train_file: 
        attributes_line = train_file.readline().strip()
        attributes = attributes_line.split('\t')
        training_dataset = []
        for line in train_file: 
            transaction = line.strip()
            transaction = transaction.split('\t')
            training_dataset.append(transaction)

        split = question(training_dataset, 0)

        gain_final = gain_ratio(training_dataset, 1)

        best = best_split(training_dataset, attributes)

        finalidk = build_tree(training_dataset)

        question_index = finalidk.question

    with open(result_file, "w") as r_file: 
        att_str = "\t".join(attributes) + "\n"
        r_file.write(att_str)
        for row in test_set: 
            traverse(row, finalidk)
            sentence = "\t".join(row) + "\n"
            r_file.write(sentence)
