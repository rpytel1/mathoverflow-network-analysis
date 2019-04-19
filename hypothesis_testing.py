import pickle
import pandas as pd
import networkx as nx
from operator import itemgetter
from scipy.stats import spearmanr
import function as fn

names = ['a2q', 'c2q', 'c2a', 'total']


def closeness_centrality(t, cc_type='in'):
    if cc_type == 'in':
        print('\n----------IN Closeness Centrality - UpVotes----------\n')
    else:
        print('\n----------OUT Closeness Centrality - UpVotes----------\n')

    closeness_centrality = [[], [], []]
    for j in range(1, 4):
        if cc_type == 'in':
            with open('centralities/closeness/{0}_{1}_in_cc.pickle'.format(t, names[j - 1]), 'rb') as handle:
                cc = pickle.load(handle)
        else:
            with open('centralities/closeness/{0}_{1}_out_cc.pickle'.format(t, names[j - 1]), 'rb') as handle:
                cc = pickle.load(handle)
        for i, v in cc.items():
            closeness_centrality[j - 1].append([i, v])
        closeness_centrality[j - 1].sort(key=itemgetter(1), reverse=True)
        for i, v in enumerate(closeness_centrality[j - 1]):
            closeness_centrality[j - 1][i] = [v[0], v[1], i + 1]

    df = pd.read_csv('data/mathoverflow/mathoverflow_dataset.csv')
    upvotes_dict = dict(zip(df.UserId, df.UpVotes))

    upvotes_list = [[k, v] for k, v in upvotes_dict.items()]
    upvotes_list.sort(key=itemgetter(1), reverse=True)
    for i, v in enumerate(upvotes_list):
        upvotes_list[i] = [v[0], v[1], i + 1]

    upvotes_dict = {int(r[0]): float(r[1]) for r in upvotes_list}

    for ind, layer in enumerate(closeness_centrality):
        closeness_centrality[ind] = {int(r[0]): float(r[1]) for r in layer}

    for i in range(3):
        temp_upvotes_dict = {k: v for k, v in upvotes_dict.items() if k in closeness_centrality[i]}
        upvotes_df = pd.DataFrame(temp_upvotes_dict.items(), columns=['UserId', 'UpVotes'])

        closeness_centrality_dict = {k: v for k, v in closeness_centrality[i].items() if k in temp_upvotes_dict}
        closeness_centrality_df = pd.DataFrame(closeness_centrality_dict.items(),
                                               columns=['UserId', 'ClosenessCentrality'])

        merged_df = pd.merge(upvotes_df, closeness_centrality_df, on='UserId')
        merged_df.UserId.nunique()

        print('--------------------{}-------------------'.format(names[i]))
        print(spearmanr(merged_df.UpVotes.values, merged_df.ClosenessCentrality.values))


def degree_centrality(t, degree_type='in'):
    if degree_type == 'in':
        print('\n----------In-Degree Centrality - Reputation----------\n')
    else:
        print('\n----------Out-Degree Centrality - Reputation----------\n')
    G_degrees = [[], [], []]
    for j in range(1, 4):
        G_degrees[j - 1] = []
        G = nx.read_gpickle('pickles/graphs/{0}/{1}.gpickle'.format(t, names[j - 1]))
        if degree_type == 'in':
            d = G.in_degree(weight='weight')
            s = len(list(d)) - 1
            for i, v in G.in_degree(weight='weight'):
                G_degrees[j - 1].append([i, v / s])
        else:
            d = G.out_degree(weight='weight')
            s = len(list(d)) - 1
            for i, v in G.out_degree(weight='weight'):
                G_degrees[j - 1].append([i, v / s])
        G_degrees[j - 1].sort(key=itemgetter(1), reverse=True)
        for i, v in enumerate(G_degrees[j - 1]):
            G_degrees[j - 1][i] = [v[0], v[1], i + 1]

    df = pd.read_csv('data/mathoverflow/mathoverflow_dataset.csv')
    reputation_dict = dict(zip(df.UserId, df.Reputation))

    reputation_list = [[k, v] for k, v in reputation_dict.items()]
    reputation_list.sort(key=itemgetter(1), reverse=True)
    for i, v in enumerate(reputation_list):
        reputation_list[i] = [v[0], v[1], i + 1]

    for ind, layer in enumerate(G_degrees):
        G_degrees[ind] = {int(r[0]): float(r[1]) for r in layer}

    reputation_dict = {int(r[0]): float(r[1]) for r in reputation_list}

    for i in range(3):
        temp_reputation_dict = {k: v for k, v in reputation_dict.items() if k in G_degrees[i]}
        reputation_df = pd.DataFrame(list(temp_reputation_dict.items()), columns=['UserId', 'Reputation'])

        degree_values_dict = {k: v for k, v in G_degrees[i].items() if k in temp_reputation_dict}
        degree_values_df = pd.DataFrame(list(degree_values_dict.items()), columns=['UserId', 'Degree'])

        merged_df = pd.merge(reputation_df, degree_values_df, on='UserId')
        merged_df.UserId.nunique()

        print('--------------------{}-------------------'.format(names[i]))
        print(spearmanr(merged_df.Reputation.values, merged_df.Degree.values))


def eigenvector_centrality(t, ec_type='in'):
    if ec_type == 'in':
        print('\n---------- IN EigenVector Centrality - Views----------\n')
    else:
        print('\n----------OUT EigenVector Centrality - Views----------\n')
    eigenvector_centrality = [[], [], []]
    for j in range(1, 4):
        G = nx.read_gpickle('pickles/graphs/{0}/{1}.gpickle'.format(t, names[j - 1]))
        if ec_type == 'out':
            ec = nx.eigenvector_centrality(G.reverse(), weight='weight')
        else:
            ec = nx.eigenvector_centrality(G, weight='weight')
        for i, v in ec.items():
            eigenvector_centrality[j - 1].append([i, v])
        eigenvector_centrality[j - 1].sort(key=itemgetter(1), reverse=True)
        for i, v in enumerate(eigenvector_centrality[j - 1]):
            eigenvector_centrality[j - 1][i] = [v[0], v[1], i + 1]

    df = pd.read_csv('data/mathoverflow/mathoverflow_dataset.csv')
    views_dict = dict(zip(df.UserId, df.ViewCount))

    views_list = [[k, v] for k, v in views_dict.items()]
    views_list.sort(key=itemgetter(1), reverse=True)
    for i, v in enumerate(views_list):
        views_list[i] = [v[0], v[1], i + 1]

    views_dict = {int(r[0]): float(r[1]) for r in views_list}

    for ind, layer in enumerate(eigenvector_centrality):
        eigenvector_centrality[ind] = {int(r[0]): float(r[1]) for r in layer}

    for i in range(3):
        temp_views_dict = {k: v for k, v in views_dict.items() if k in eigenvector_centrality[i]}
        views_df = pd.DataFrame(temp_views_dict.items(), columns=['UserId', 'Views'])

        eigenvector_centrality_dict = {k: v for k, v in eigenvector_centrality[i].items() if k in temp_views_dict}
        eigenvector_centrality_df = pd.DataFrame(eigenvector_centrality_dict.items(),
                                                 columns=['UserId', 'EigenvectorCentrality'])

        merged_df = pd.merge(views_df, eigenvector_centrality_df, on='UserId')
        merged_df.UserId.nunique()

        print('--------------------{}-------------------'.format(names[i]))
        print(spearmanr(merged_df.Views.values, merged_df.EigenvectorCentrality.values))


def total_degree_centrality(t='mathoverflow', degree_type='in'):
    if degree_type == 'in':
        print('\n----------In-Degree Centrality - Reputation----------\n')
    else:
        print('\n----------Out-Degree Centrality - Reputation----------\n')
    G_degrees = []
    G = nx.read_gpickle('pickles/graphs/mathoverflow/total_2_1_3.gpickle')
    if degree_type == 'in':
        d = G.in_degree(weight='weight')
        s = len(list(d)) - 1
        for i, v in G.in_degree(weight='weight'):
            G_degrees.append([i, v / s])
    else:
        d = G.out_degree(weight='weight')
        s = len(list(d)) - 1
        for i, v in G.out_degree(weight='weight'):
            G_degrees.append([i, v / s])
    G_degrees.sort(key=itemgetter(1), reverse=True)
    for i, v in enumerate(G_degrees):
        G_degrees[i] = [v[0], v[1], i + 1]

    df = pd.read_csv('data/mathoverflow/mathoverflow_dataset.csv')
    reputation_dict = dict(zip(df.UserId, df.Reputation))

    reputation_list = [[k, v] for k, v in reputation_dict.items()]
    reputation_list.sort(key=itemgetter(1), reverse=True)
    for i, v in enumerate(reputation_list):
        reputation_list[i] = [v[0], v[1], i + 1]

    G_degrees = {int(r[0]): float(r[1]) for r in G_degrees}

    reputation_dict = {int(r[0]): float(r[1]) for r in reputation_list}

    temp_reputation_dict = {k: v for k, v in reputation_dict.items() if k in G_degrees}
    reputation_df = pd.DataFrame(temp_reputation_dict.items(), columns=['UserId', 'Reputation'])

    degree_values_dict = {k: v for k, v in G_degrees.items() if k in temp_reputation_dict}
    degree_values_df = pd.DataFrame(degree_values_dict.items(), columns=['UserId', 'Degree'])

    merged_df = pd.merge(reputation_df, degree_values_df, on='UserId')
    merged_df.UserId.nunique()

    print('--------------------TOTAL-------------------')
    print(spearmanr(merged_df.Reputation.values, merged_df.Degree.values))


def total_closeness_centrality(t='mathoverflow', cc_type='in'):
    if cc_type == 'in':
        print('\n----------IN Closeness Centrality - UpVotes----------\n')
    else:
        print('\n----------OUT Closeness Centrality - UpVotes----------\n')
    closeness_centrality = []
    if cc_type == 'in':
        with open('centralities/closeness/mathoverflow_total_in_cc.pickle', 'rb') as handle:
            cc = pickle.load(handle)
    else:
        with open('centralities/closeness/mathoverflow_total_out_cc.pickle', 'rb') as handle:
            cc = pickle.load(handle)
    for i, v in cc.items():
        closeness_centrality.append([i, v])
    closeness_centrality.sort(key=itemgetter(1), reverse=True)
    for i, v in enumerate(closeness_centrality):
        closeness_centrality[i] = [v[0], v[1], i + 1]

    df = pd.read_csv('data/mathoverflow/mathoverflow_dataset.csv')
    upvotes_dict = dict(zip(df.UserId, df.UpVotes))

    upvotes_list = [[k, v] for k, v in upvotes_dict.items()]
    upvotes_list.sort(key=itemgetter(1), reverse=True)
    for i, v in enumerate(upvotes_list):
        upvotes_list[i] = [v[0], v[1], i + 1]

    upvotes_dict = {int(r[0]): float(r[1]) for r in upvotes_list}

    closeness_centrality = {int(r[0]): float(r[1]) for r in closeness_centrality}

    temp_upvotes_dict = {k: v for k, v in upvotes_dict.items() if k in closeness_centrality}
    upvotes_df = pd.DataFrame(temp_upvotes_dict.items(), columns=['UserId', 'UpVotes'])

    closeness_centrality_dict = {k: v for k, v in closeness_centrality.items() if k in temp_upvotes_dict}
    closeness_centrality_df = pd.DataFrame(closeness_centrality_dict.items(),
                                           columns=['UserId', 'ClosenessCentrality'])

    merged_df = pd.merge(upvotes_df, closeness_centrality_df, on='UserId')
    merged_df.UserId.nunique()

    print('------------------TOTAL---------------------')
    print(spearmanr(merged_df.UpVotes.values, merged_df.ClosenessCentrality.values))


def total_eigenvector_centrality(t='mathoverflow', ec_type='in'):
    if ec_type == 'in':
        print('\n----------IN EigenVector Centrality - Views----------\n')
    else:
        print('\n----------OUT EigenVector Centrality - Views----------\n')

    eigenvector_centrality = []
    G = nx.read_gpickle('pickles/graphs/mathoverflow/total_1_1_1.gpickle')
    if ec_type == 'out':
        ec = nx.eigenvector_centrality(G.reverse(), weight='weight')
    else:
        ec = nx.eigenvector_centrality(G, weight='weight')
    for i, v in ec.items():
        eigenvector_centrality.append([i, v])
    eigenvector_centrality.sort(key=itemgetter(1), reverse=True)
    for i, v in enumerate(eigenvector_centrality):
        eigenvector_centrality[i] = [v[0], v[1], i + 1]

    df = pd.read_csv('data/mathoverflow/mathoverflow_dataset.csv')
    views_dict = dict(zip(df.UserId, df.ViewCount))

    views_list = [[k, v] for k, v in views_dict.items()]
    views_list.sort(key=itemgetter(1), reverse=True)
    for i, v in enumerate(views_list):
        views_list[i] = [v[0], v[1], i + 1]

    views_dict = {int(r[0]): float(r[1]) for r in views_list}

    eigenvector_centrality = {int(r[0]): float(r[1]) for r in eigenvector_centrality}

    temp_views_dict = {k: v for k, v in views_dict.items() if k in eigenvector_centrality}
    views_df = pd.DataFrame(temp_views_dict.items(), columns=['UserId', 'Views'])

    eigenvector_centrality_dict = {k: v for k, v in eigenvector_centrality.items() if k in temp_views_dict}
    eigenvector_centrality_df = pd.DataFrame(eigenvector_centrality_dict.items(),
                                             columns=['UserId', 'EigenvectorCentrality'])

    merged_df = pd.merge(views_df, eigenvector_centrality_df, on='UserId')
    merged_df.UserId.nunique()

    print('--------------------TOTAL-------------------')
    print(spearmanr(merged_df.Views.values, merged_df.EigenvectorCentrality.values))


def get_degree_centrality(t='mathoverflow', degree_type='in'):
    """
    Returns the nodes of the network ranked according to their out-degree
    centrality, for each of the 3 interactions.
    :param t: Network's name. Default is MathOverflow
    :param ec_type: Type of the degree centrality, in-link or out-link
    :return: Nodes ranked according to closeness centrality.
    Output form: {'a2q': [(UserId, Out-Degree centrality, ranking), ...], 'c2q': ...}
    """
    G_degrees = {}
    for j in range(1, 5):
        G_degrees[names[j - 1]] = []
        if j == 4:
            G = nx.read_gpickle('pickles/graphs/mathoverflow/total_1_1_1.gpickle')
        else:
            G = nx.read_gpickle('pickles/graphs/{0}/{1}.gpickle'.format(t, names[j - 1]))
        if degree_type == 'out':
            d = G.out_degree(weight='weight')
            s = len(list(d)) - 1
            for i, v in G.out_degree(weight='weight'):
                G_degrees[names[j - 1]].append((i, v / s))
        else:
            d = G.in_degree(weight='weight')
            s = len(list(d)) - 1
            for i, v in G.in_degree(weight='weight'):
                G_degrees[names[j - 1]].append((i, v / s))
        G_degrees[names[j - 1]].sort(key=itemgetter(1), reverse=True)
        for i, v in enumerate(G_degrees[names[j - 1]]):
            G_degrees[names[j - 1]][i] = (v[0], v[1], i + 1)
    return G_degrees


def get_closeness_centrality(t='mathoverflow', cc_type='in'):
    """
    Returns the nodes of the network ranked according to their closeness
    centrality, for each of the 3 interactions.
    :param t: Network's name. Default is MathOverflow
    :param cc_type: Type of the closeness centrality, for incoming or outward distance
    :return: Nodes ranked according to closeness centrality.
    Output form: {'a2q': [(UserId, Closeness centrality, ranking), ...], 'c2q': ...}
    """
    G_cc = {}
    for j in range(1, 5):
        G_cc[names[j - 1]] = []
        if j == 4:
            with open('centralities/closeness/mathoverflow_total_{}_cc.pickle'.format(cc_type), 'rb') as handle:
                cc = pickle.load(handle)
        else:
            with open('centralities/closeness/{0}_{1}_{2}_cc.pickle'.format(t, names[j - 1], cc_type), 'rb') as handle:
                cc = pickle.load(handle)
        for i, v in cc.items():
            G_cc[names[j - 1]].append((i, v))
        G_cc[names[j - 1]].sort(key=itemgetter(1), reverse=True)
        for i, v in enumerate(G_cc[names[j - 1]]):
            G_cc[names[j - 1]][i] = (v[0], v[1], i + 1)
    return G_cc


def get_eigenvector_centrality(t='mathoverflow', ec_type='in'):
    """
    Returns the nodes of the network ranked according to their eigenvector
    centrality, for each of the 3 interactions.
    :param t: Network's name. Default is MathOverflow
    :param ec_type: Type of the eigenvector centrality, left(in-edges) or right (out-edges)
    :return: Nodes ranked according to closeness centrality.
    Output form: {'a2q': [(UserId, Out-Degree centrality, ranking), ...], 'c2q': ...}
    """
    G_ec = {}
    for j in range(1, 5):
        G_ec[names[j - 1]] = []
        if j == 4:
            G = nx.read_gpickle('pickles/graphs/mathoverflow/total_1_1_1.gpickle')
        else:
            G = nx.read_gpickle('pickles/graphs/{0}/{1}.gpickle'.format(t, names[j - 1]))
        if ec_type == 'out':
            ec = nx.eigenvector_centrality(G.reverse(), weight='weight')
        else:
            ec = nx.eigenvector_centrality(G, weight='weight')
        for i, v in ec.items():
            G_ec[names[j - 1]].append((i, v))
        G_ec[names[j - 1]].sort(key=itemgetter(1), reverse=True)
        for i, v in enumerate(G_ec[names[j - 1]]):
            G_ec[names[j - 1]][i] = (v[0], v[1], i + 1)
    return G_ec


def create_weighted_total_graph():
    a2q = nx.read_gpickle('pickles/graphs/mathoverflow/a2q.gpickle')
    c2q = nx.read_gpickle('pickles/graphs/mathoverflow/c2q.gpickle')
    c2a = nx.read_gpickle('pickles/graphs/mathoverflow/c2a.gpickle')
    a2q_weight, c2q_weight, c2a_weight = 2, 1, 3
    G = fn.generate_weighted_total_graph(a2q, a2q_weight, c2q, c2q_weight, c2a, c2a_weight)
    with open('pickles/graphs/mathoverflow/total_{0}_{1}_{2}.gpickle'.format(str(a2q_weight), str(c2q_weight),
                                                                             str(c2a_weight)), 'wb') as handle:
        pickle.dump(G, handle, protocol=pickle.HIGHEST_PROTOCOL)


degree_centrality("mathoverflow", degree_type='in')
degree_centrality("mathoverflow", degree_type='out')
eigenvector_centrality("mathoverflow", 'in')
eigenvector_centrality("mathoverflow", 'out')
closeness_centrality("mathoverflow", cc_type='in')
closeness_centrality("mathoverflow", cc_type='out')
create_weighted_total_graph()
total_degree_centrality(degree_type='in')
total_degree_centrality(degree_type='out')
total_closeness_centrality(cc_type='in')
total_closeness_centrality(cc_type='out')
total_eigenvector_centrality(ec_type='in')
total_eigenvector_centrality(ec_type='out')
a = get_degree_centrality(degree_type='in')
b = get_degree_centrality(degree_type='out')
c = get_closeness_centrality(cc_type='in')
d = get_closeness_centrality(cc_type='out')