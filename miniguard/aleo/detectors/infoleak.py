import networkx as nx

from ...common.graphs import construct_infoflow_graph

def report(fn):
    def inner(*args, **kwargs):
        res = fn(*args, **kwargs)
        # wrap into a report
        obj = [{
            "detector": "InfoLeak",
            "result": True if len(res)>0 else False,
            "details": res
        }]
        return obj
    return inner

@report
def infoleak_detector(arg_fun, arg_sum):
    fname = arg_fun.name
    # (note) connec_hash should be set to False, since hash doesn't flow information
    edges = construct_infoflow_graph(arg_fun, connect_hash=False)
    G = nx.DiGraph()
    G.add_edges_from(edges)
    res = []
    for din in arg_sum["functions"][fname]["arguments"].keys():
        if din == "self.caller":
            # skip special variable
            continue
        if arg_sum["functions"][fname]["arguments"][din]["visibility"] == "private":
            is_leaked = False
            for dout in arg_sum["functions"][fname]["returns"].keys():
                if arg_sum["functions"][fname]["returns"][dout]["visibility"] == "public":
                    if nx.has_path(G, din, dout):
                        is_leaked = True
                        break
                else:
                    # only focus on public output signals
                    continue
            if is_leaked:
                res.append(din)
        else:
            # only focus on private input signals
            continue
    return res