import networkx as nx

from ...common.graphs import construct_infoflow_graph

def report(fn):
    def inner(*args, **kwargs):
        res = fn(*args, **kwargs)
        # wrap into a report
        obj = [{
            "detector": "UnusedVar",
            "result": True if len(res)>0 else False,
            "details": res
        }]
        return obj
    return inner

@report
def uvar_detector(arg_fun, arg_sum):
    fname = arg_fun.name
    edges = construct_infoflow_graph(arg_fun)
    G = nx.DiGraph()
    G.add_edges_from(edges)
    res = []
    for din in arg_sum["functions"][fname]["arguments"].keys():
        if din == "self.caller":
            # skip special variable
            continue
        is_used = False
        for dout in arg_sum["functions"][fname]["returns"].keys():
            if nx.has_path(G, din, dout):
                is_used = True
                break
        if not is_used:
            res.append(din)
    return res