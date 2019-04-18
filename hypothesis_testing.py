import pickle
import pandas as pd
import networkx as nx
from operator import itemgetter
from scipy.stats import spearmanr
import function as fn

names = ['a2q', 'c2q', 'c2a', 'total']


def closeness_centrality(t):
    print('\n----------Closeness Centrality - UpVotes----------\n')
    closeness_centrality = [[], [], []]
    for j in range(1, 4):
        with open('centralities/closeness/{0}_{1}_cc.pickle'.format(t, names[j - 1]), 'rb') as handle:
            cc = pickle.load(handle)
        # G = nx.read_gpickle('old_pickles/graphs/{0}/{1}.gpickle'.format(t, names[j - 1]))
        # with open('centralities/{0}_{1}_new_cc.pickle'.format(t, names[j - 1]), 'wb') as handle:
        #     cc = nx.closeness_centrality(G, distance='1/weight')
        #     pickle.dump(cc, handle, protocol=pickle.HIGHEST_PROTOCOL)
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
        reputation_df = pd.DataFrame(temp_reputation_dict.items(), columns=['UserId', 'Reputation'])

        degree_values_dict = {k: v for k, v in G_degrees[i].items() if k in temp_reputation_dict}
        degree_values_df = pd.DataFrame(degree_values_dict.items(), columns=['UserId', 'Degree'])

        merged_df = pd.merge(reputation_df, degree_values_df, on='UserId')
        merged_df.UserId.nunique()

        print('--------------------{}-------------------'.format(names[i]))
        print(spearmanr(merged_df.Reputation.values, merged_df.Degree.values))


def eigenvector_centrality(t):
    print('\n----------Eigenvector Centrality - Views----------\n')
    eigenvector_centrality = [[], [], []]
    for j in range(1, 4):
        with open('centralities/eigenvector/{0}_{1}_ec.pickle'.format(t, names[j - 1]), 'rb') as handle:
            ec = pickle.load(handle)
        # G = nx.read_gpickle('old_pickles/graphs/{0}/{1}.gpickle'.format(t, names[j - 1]))
        # with open('centralities/{0}_{1}_ec.pickle'.format(t, names[j - 1]), 'wb') as handle:
        #     ec = nx.eigenvector_centrality(G, weight='weight')
        #     pickle.dump(ec, handle, protocol=pickle.HIGHEST_PROTOCOL)
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
    G = nx.read_gpickle('pickles/graphs/mathoverflow/total_0.6666666666666666_1_1.gpickle')
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


def total_closeness_centrality(t='mathoverflow'):
    print('\n----------Closeness Centrality - UpVotes----------\n')
    closeness_centrality = []
    with open('centralities/closeness/mathoverflow_total_cc.pickle', 'rb') as handle:
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


def total_eigenvector_centrality(t='mathoverflow'):
    print('\n----------Eigenvector Centrality - Views----------\n')
    eigenvector_centrality = []
    with open('centralities/eigenvector/mathoverflow_total_ec.pickle', 'rb') as handle:
        ec = pickle.load(handle)
    # G = nx.read_gpickle('pickles/graphs/mathoverflow/total_1_1_1.gpickle')
    # with open('centralities/eigenvector/mathoverflow_total_ec.pickle', 'wb') as handle:
    #     ec = nx.eigenvector_centrality(G, weight='weight')
    #     pickle.dump(ec, handle, protocol=pickle.HIGHEST_PROTOCOL)
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


def get_degree_centrality(t='mathoverflow'):
    """
    Returns the nodes of the network ranked according to their out-degree
    centrality, for each of the 3 interactions.
    :param t: Network's name. Default is MathOverflow
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
        d = G.out_degree(weight='weight')
        s = len(list(d)) - 1
        for i, v in G.out_degree(weight='weight'):
            G_degrees[names[j - 1]].append((i, v / s))
        G_degrees[names[j - 1]].sort(key=itemgetter(1), reverse=True)
        for i, v in enumerate(G_degrees[names[j - 1]]):
            G_degrees[names[j - 1]][i] = (v[0], v[1], i + 1)
    return G_degrees


def get_closeness_centrality(t='mathoverflow'):
    """
    Returns the nodes of the network ranked according to their closeness
    centrality, for each of the 3 interactions.
    :param t: Network's name. Default is MathOverflow
    :return: Nodes ranked according to closeness centrality.
    Output form: {'a2q': [(UserId, Closeness centrality, ranking), ...], 'c2q': ...}
    """
    G_cc = {}
    for j in range(1, 5):
        G_cc[names[j - 1]] = []
        if j == 4:
            # G = nx.read_gpickle('pickles/graphs/mathoverflow/total_1_1_1.gpickle')
            # with open('centralities/closeness/mathoverflow_total_cc.pickle'.format(t, names[j - 1]), 'wb') as handle:
            #     cc = nx.closeness_centrality(G, distance='1/weight')
            #     pickle.dump(cc, handle, protocol=pickle.HIGHEST_PROTOCOL)
            with open('centralities/closeness/mathoverflow_total_cc.pickle', 'rb') as handle:
                cc = pickle.load(handle)
        else:
            with open('centralities/closeness/{0}_{1}_cc.pickle'.format(t, names[j - 1]), 'rb') as handle:
                cc = pickle.load(handle)
        for i, v in cc.items():
            G_cc[names[j - 1]].append((i, v))
        G_cc[names[j - 1]].sort(key=itemgetter(1), reverse=True)
        for i, v in enumerate(G_cc[names[j - 1]]):
            G_cc[names[j - 1]][i] = (v[0], v[1], i + 1)
    return G_cc


def create_weighted_total_graph():
    a2q = nx.read_gpickle('pickles/graphs/mathoverflow/a2q.gpickle')
    c2q = nx.read_gpickle('pickles/graphs/mathoverflow/c2q.gpickle')
    c2a = nx.read_gpickle('pickles/graphs/mathoverflow/c2a.gpickle')
    a2q_weight, c2q_weight, c2a_weight = 4 / 6, 1, 1
    G = fn.generate_weighted_total_graph(a2q, a2q_weight, c2q, c2q_weight, c2a, c2a_weight)
    with open('pickles/graphs/mathoverflow/total_{0}_{1}_{2}.gpickle'.format(str(a2q_weight), str(c2q_weight),
                                                                             str(c2a_weight)), 'wb') as handle:
        pickle.dump(G, handle, protocol=pickle.HIGHEST_PROTOCOL)


# degree_centrality("mathoverflow", degree_type='in')
# degree_centrality("mathoverflow", degree_type='out')
# eigenvector_centrality("mathoverflow")
# closeness_centrality("mathoverflow")
# create_weighted_total_graph()
# total_degree_centrality(degree_type='in')
# total_degree_centrality(degree_type='out')
# a = get_degree_centrality()
# b = get_closeness_centrality()
# total_closeness_centrality()
# total_eigenvector_centrality()
