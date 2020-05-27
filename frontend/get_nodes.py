# Group 66 Swear Words Analysis
# Xinshu Li 875109
# Dongting Hu 960886
# Qinwei Yuan 1006223
# Ansheng Dong  989973
# Tonghao Wang 1039694
def get_ip(node_name):
    with open('../nodes.txt', 'r') as f:
        line = f.readlines()
        i = nodes_dict[node_name]
        node_ip = line[i][:-1] 
    return node_ip

nodes_dict={'nginx':0,'master':1,'slave1':2,'slave2':3}
