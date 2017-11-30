import no_ref_codes as nrc
from prettytable import PrettyTable
import inquirer
import os
import sys
import re
sys.path.append(os.path.realpath('.'))

questions = [
  inquirer.List('size',
                message="Which disease would you like to find relations for?",
                choices=['Congestive Heart Failure', 'Diabetes', "Hypertension", "Obesity"],
            ),]
answers = inquirer.prompt(questions)

code_choices = {"Hypertension": ['4010', '4011', '4019'], "Congestive Heart Failure": ['4280'], "Diabetes": ["25000", "25001", "25002"], "Obesity": ["27800", "27801"]}

demo_list = [{"from": "DIAGNOSES_ICD", "to":"DIAGNOSES_ICD", \
                "results":["D_ICD_DIAGNOSES", "ICD9_CODE"],"from_index": 4, "print_index": 3},\
             {"from": "LABEVENTS", "to":"DIAGNOSES_ICD", \
             "results":["D_LABITEMS", "ITEMID"], "from_index": 3, "print_index": 2}, \
             {"from": "PRESCRIPTIONS", "to":"DIAGNOSES_ICD", \
             "results":["PRESCRIPTIONS", "DRUG"], "from_index":7, "print_index": 7}]

result_list = {"DIAGNOSES_ICD": ["Diagnoses",list()], \
                "LABEVENTS": ["Lab Tests",list()], \
                "PRESCRIPTIONS": ["Medications",list()]}
print(("Okay, finding relations for {}").format(answers['size']))
for item in demo_list:
    grouping_base = nrc.no_ref_codes(code_choices[answers['size']])
    grouping_base.code_generation(item["from"], 20000, item['from_index'])
    patient_data = grouping_base.sparse_matrix_generation_by_visit()
    X, y = grouping_base.array_generation_for_ml_visit(item['to'], patient_data)
    list_out = grouping_base.learning_by_target_lasso(X, y)
    ordered_list, ordered_dict = grouping_base.order_output_matrix(list_out)

    query_tuple = list()
    for res in ordered_list[0:10]: 
        query_tuple.append(ordered_dict[res])

    query_string = ("SELECT * FROM mimiciii.{0} WHERE {1} in {2} LIMIT 10;"\
                        ).format(item["results"][0], item["results"][1], tuple(query_tuple))
    grouping_base.cur.execute(query_string)
    query_result = grouping_base.cur.fetchall()
    result_list[item['from']][1].append(query_result)

keys = list(result_list.keys())
result_table = PrettyTable([result_list[keys[0]][0],\
                            result_list[keys[1]][0],\
                            result_list[keys[2]][0]])
try:
    for index, item in enumerate(result_list[keys[0]][1][0]):
        result_table.add_row([
            result_list[keys[0]][1][0][index][demo_list[0]["print_index"]],\
            result_list[keys[1]][1][0][index][demo_list[1]["print_index"]],\
            result_list[keys[2]][1][0][index][demo_list[2]["print_index"]]])
except IndexError as ex:
    pass
finally:
    print(result_table)

