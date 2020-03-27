from flask import Flask, request
from flask_cors import CORS
import json
import ast
from pert import PERT
from collections import Counter


app = Flask(__name__)
CORS(app)

@app.route('/hit', methods=['GET'])
def hit():
    return "Hit!"

@app.route('/montecarlo', methods=['POST'])
def montecarlo():
    request_json_dict = ast.literal_eval(request.data.decode('utf-8'))
    day_list, percentage_list = montecarlo_pert(
        optimistic=float(request_json_dict["montecarlo_parameters"]["optimistic"].replace(",", ".")),
        likely=float(request_json_dict["montecarlo_parameters"]["likely"].replace(",", ".")), 
        pessimistic=float(request_json_dict["montecarlo_parameters"]["pessimistic"].replace(",", ".")), 
        certainty_level=float(request_json_dict["montecarlo_parameters"]["certainty_level"].replace(",", ".")), 
        card_count=int(request_json_dict["montecarlo_parameters"]["card_count"]), 
        run_count=int(request_json_dict["montecarlo_parameters"]["run_count"]),
        outlier_cards_string=request_json_dict["montecarlo_parameters"]["outlier_cards"]
        )

    # day_percentage_dict = dict(zip(day_list, percentage_list))

    result_list = []
    for i in range(0, len(day_list)):
        day_percentage = {"day": day_list[i], "%": round(percentage_list[i])}
        result_list.append(day_percentage)
    
    return json.dumps(result_list)

def montecarlo_pert(optimistic, likely, pessimistic, certainty_level, card_count, run_count, outlier_cards_string=[]):
    pert_lambda = float(certainty_level * 2)

    outlier_cards = []
    if len(outlier_cards_string) > 0:
        card_count = card_count - len(outlier_cards)
        for card in outlier_cards_string:
            outlier_cards.append(float(card.replace(",", ".")))

    total_days_list = []
    for run in range(0, run_count):
        pert = PERT(optimistic, likely, pessimistic, lamb=pert_lambda)
        pert_result_list = pert.rvs(card_count)
        run_result_sum = sum(pert_result_list)

        for card in outlier_cards:
                run_result_sum = run_result_sum + card

        total_days_list.append(round(run_result_sum))

    day_counts = Counter(total_days_list).items()
    sorted_day_counts = sorted(day_counts, key=lambda f:f[0])

    day_list = []
    count_list = []
    for day in sorted_day_counts:
        day_list.append(day[0])
        if len(count_list) == 0:
            count_list.append(day[1])
        else:
            count_list.append(day[1] + count_list[len(count_list) - 1])

    percentage_list = [(c/run_count)*100 for c in count_list]

    print(day_list)
    print(" ")
    print(count_list)
    print(" ")
    print(percentage_list)
    print(" ")

    return day_list, percentage_list
