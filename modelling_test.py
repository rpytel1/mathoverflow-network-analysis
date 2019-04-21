import function as fn
import pickle
import hypothesis_testing as ht


# Produces the final score for each user at the last day
# of recording
def get_final_ranking(trust_dict):
    rank_dict = {}
    for user, history in trust_dict.items():
        rank_dict[user] = history[max(list(map(lambda x: int(x), list(history.keys()))))]
    return rank_dict


file = open(r'C:\Users\Vasilis\PycharmProjects\mathoverflow-network-analysis\pickles\myEdges\mathoverflow\a2q.pkl', 'rb')
nodes_a2q = pickle.load(file)
edges_a2q = pickle.load(file)
file.close()

file = open(r'C:\Users\Vasilis\PycharmProjects\mathoverflow-network-analysis\pickles\myEdges\mathoverflow\c2q.pkl', 'rb')
nodes_c2q = pickle.load(file)
edges_c2q = pickle.load(file)
file.close()

file = open(r'C:\Users\Vasilis\PycharmProjects\mathoverflow-network-analysis\pickles\myEdges\mathoverflow\c2a.pkl', 'rb')
nodes_c2a = pickle.load(file)
edges_c2a = pickle.load(file)
file.close()

path = r'C:\Users\Vasilis\PycharmProjects\mathoverflow-network-analysis\data\mathoverflow\sx-mathoverflow.txt'
# filename = r'modelling/best/second_attempt_degree.png'
filename = r'modelling/second_right_attempt_degree.png'

print('Creating user dictionary...')
user_dict = fn.create_user_interactions_dict(path, nodes_a2q, edges_a2q, nodes_c2q, edges_c2q, nodes_c2a, edges_c2a)
print('Setting up the model...')
interactions_dict = fn.calculate_interaction_model(user_dict)
interval_dict = fn.calculate_interval(user_dict)
trust_dict = fn.calculate_trust(interactions_dict, interval_dict)
final_trust = get_final_ranking(trust_dict)
ht.modeling_ranking(final_trust, 'Reputation')
# filehandler = open("modelling/final_modelled_score.pickle", "wb")
# pickle.dump(get_final_ranking(trust_dict), filehandler)
# filehandler.close()
print('Initiating timestamps...')
timestamps = fn.initiate_timestamps(edges_a2q, edges_c2q, edges_c2a)
print('Creating the metric dictionaries...')
degree_dict, in_degree_dict, out_degree_dict = fn.calculate_degree_per_time(user_dict)
print('Aggregating per day...')
aggregated_degree_dict = fn.aggregate_user_dict_by_granularity(degree_dict, 'day', timestamps)
aggregated_trust_dict = fn.aggregate_user_dict_by_granularity(trust_dict, 'day', timestamps)
binned_timestamps = fn.aggregate_timestamps_by_granularity(timestamps, 'day')
print('Making the charts...')
# fn.make_modelled_trust_chart(aggregated_degree_dict, aggregated_trust_dict, binned_timestamps,
#                     [k[0] for k in sorted(final_trust.items(), key=lambda kv: kv[1], reverse=True)[0:100]], filename)
fn.make_modelled_trust_chart(aggregated_degree_dict, aggregated_trust_dict, binned_timestamps, [], filename)
