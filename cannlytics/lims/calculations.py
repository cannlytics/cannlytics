"""
Calculation Parser | Cannlytics
Copyright (c) 2021-2022 Cannlytics

Authors: Keegan Skeate <https://github.com/keeganskeate>
Created: 6/8/2021
Updated: 6/8/2021
License: <https://github.com/cannlytics/cannlytics/blob/main/LICENSE>
"""
# Standard imports
import re

# External imports
try:
    import pandas as pd
    import numpy as np
except:
    pass


def calculate_results():
    """Calculate results by using analyte formula and
    instrument / analyst measurements.
    Calculate results by using analyte formula and
    instrument / analyst measurements.
    """
    # TODO: Implement a function that calculates results given a formula and results.
    raise NotImplementedError


# # Prepare testing dataset
# tags = np.array(['tag'+str(i) for i in np.random.randint(10, size=200)])  # randomly generate tag list
# vals = np.random.randint(20, size=200)  # generate a list of random integers

# raw_df = pd.DataFrame({
#     'tag': tags,
#     'value': vals
# })

# # Functions
# def parentheses_enclosed(s):
#     paren_order = re.findall(r'[\(\)]', s)
    
#     if paren_order.count('(') != paren_order.count(')'):
#         return False
    
#     curr_levels = []
#     nest_lv = 0
#     for p in paren_order:
#         if p == '(':
#             nest_lv += 1
#         else:
#             nest_lv -= 1
#         curr_levels.append(nest_lv)
#     if 0 in curr_levels[:-1]:
#         return False
#     else:
#         return True
    
    
# def remove_matched_parentheses(s):
#     if ')' in s:
#         # find the first ')'
#         end = s.find(')')
#         # find the last '(' before the first ')'
#         start = max([i for i, char in enumerate(s[:end]) if char == '(' ])
#         # remove the parentheses
#         return remove_matched_parentheses(s[:start] + s[end+1:])
#     else:
#         return s
    

# def interpret(f, df):
#     if re.match(r'\Atag[\d]+\Z', f):  # e.g. 'tag1'
#         return df[df.tag == f]['value'].values
    
#     elif parentheses_enclosed(f) and \
#         re.match(r'\Asum\(.+[\+\-].+\)\Z|\Aavg\(.+[\+\-].+\)\Z|\Amin\(.+[\+\-].+\)\Z|\Amax\(.+[\+\-].+\)\Z', f):
        
#         f_name = f[:3]  # get agg func name
#         f_stripped = f[4:-1]  # strip outer func
        
#         while re.match(r'\A\(.+\)\Z', f_stripped) and parentheses_enclosed(f_stripped):
#             f_stripped = f_stripped[1:-1]
            
#         comps = re.compile(r'[\+\-]').split(f_stripped)  # split by + or -
        
#         operators = re.findall(r'[\+\-]', f_stripped)
#         comps_final = []
#         temp_str = ''
#         for c in comps:
#             temp_str += c
#             if re.match(r'\Atag[\d]+\Z', temp_str) or parentheses_enclosed(temp_str):
#                 comps_final.append(f'{f_name}({temp_str})')
#                 if len(operators) > 0:
#                     comps_final.append(operators.pop(0))
#                 temp_str = ''
#             else:
#                 temp_str += operators.pop(0)
#         return interpret(''.join(comps_final), df)
    
#     elif re.match(r'\Asum\([^\(\)]+\)\Z', f):  # e.g. 'sum(tag1)'
#         return np.sum(interpret(f[4:-1], df))
    
#     elif re.match(r'\Aavg\([^\(\)]+\)\Z', f):  # e.g. 'avg(tag1)'
#         return np.average(interpret(f[4:-1], df))
    
#     elif re.match(r'\Amin\([^\(\)]+\)\Z', f):  # e.g. 'min(tag1)'
#         return np.min(interpret(f[4:-1], df))
    
#     elif re.match(r'\Amax\([^\(\)]+\)\Z', f):  # e.g. 'max(tag1)'
#         return np.max(interpret(f[4:-1], df))
    
#     elif re.match(r'\A\(.+\)\Z', f) and parentheses_enclosed(f):  # e.g. '(tag1-tag2)'
#         return interpret(f[1:-1], df)
    
#     elif f.replace('.', '', 1).isdigit():
#         return float(f)
    
#     else:
#         rest_f = remove_matched_parentheses(f)
#         if '+' in rest_f or '-' in rest_f:
#             comps = re.compile(r'[\+\-]').split(f)
#         else:
#             comps = re.compile(r'[\*\/]').split(f)
            
#         if comps[0].count('(') != comps[0].count(')'):
#             nested_level = comps[0].count('(') - comps[0].count(')')
#             pos = len(comps[0])
#             for comp in comps[1:]:
#                 if '(' in comp:
#                     nested_level += comp.count('(')
#                 if ')' in comp:
#                     nested_level -= comp.count(')')
#                 pos += len(comp) + 1  # +1 because of the operator inside parenthesis
#                 if nested_level == 0:
#                     break
#         else:
#             pos = len(comps[0])
        
#         left = f[:pos]  # left component
#         right = f[pos+1:]  # right component
#         operator = f[pos]  # the operator
#         if operator == '+':
#             return interpret(left, df) + interpret(right, df)
#         elif operator == '-':
#             return interpret(left, df) - interpret(right, df)
#         elif operator == '*':
#             return interpret(left, df) * interpret(right, df)
#         elif operator == '/':
#             denominator = interpret(right, df)
#             if denominator == 0 or denominator is np.nan: 
#                 return np.nan
#             else:
#                 return interpret(left, df) / interpret(right, df)
    
#     return np.nan
    

# # Verification
# assert np.sum(raw_df[raw_df.tag == 'tag1']['value'].values) == interpret('sum(tag1)', raw_df), "Wrong!"
# assert np.average(raw_df[raw_df.tag == 'tag1']['value'].values) == interpret('avg(tag1)', raw_df), "Wrong!"
# assert np.min(raw_df[raw_df.tag == 'tag1']['value'].values) == interpret('min(tag1)', raw_df), "Wrong!"
# assert np.max(raw_df[raw_df.tag == 'tag1']['value'].values) == interpret('max(tag1)', raw_df), "Wrong!"

# assert np.sum(raw_df[raw_df.tag == 'tag1']['value'].values) + \
#     np.sum(raw_df[raw_df.tag == 'tag2']['value'].values) == \
#     interpret('sum(tag1)+sum(tag2)', raw_df), "Wrong!"

# assert np.sum(raw_df[raw_df.tag == 'tag1']['value'].values) + \
#     np.sum(raw_df[raw_df.tag == 'tag2']['value'].values) + \
#     np.average(raw_df[raw_df.tag == 'tag3']['value'].values) == \
#     interpret('sum(tag1)+sum(tag2)+avg(tag3)', raw_df), "Wrong!"

# assert np.sum(raw_df[raw_df.tag == 'tag1']['value'].values) + \
#     np.sum(raw_df[raw_df.tag == 'tag2']['value'].values) * \
#     np.average(raw_df[raw_df.tag == 'tag3']['value'].values) == \
#     interpret('sum(tag1)+sum(tag2)*avg(tag3)', raw_df), "Wrong!"

# assert (
#     np.sum(raw_df[raw_df.tag == 'tag1']['value'].values) + \
#     (np.sum(raw_df[raw_df.tag == 'tag2']['value'].values) - \
#     np.sum(raw_df[raw_df.tag == 'tag3']['value'].values)) + 10
# ) * (
#     np.max(raw_df[raw_df.tag == 'tag4']['value'].values) + \
#     np.average(raw_df[raw_df.tag == 'tag5']['value'].values)
# ) * 0.2 == interpret('(sum(tag1+(tag2-tag3))+10)*(max(tag4)+avg(tag5))*0.2', raw_df), "Wrong!"

# print('All pass!')
