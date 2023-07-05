import sys
import json
import argparse
import logging
import networkx as nx
from pathlib import Path
from llvmlite.binding import parse_assembly

from miniguard.common.utils import summary_conversion, locate_function
from miniguard.common.graphs import construct_infoflow_graph

from miniguard.aleo.detectors.divrd import divrd_detector
from miniguard.aleo.detectors.underflow import underflow_detector
from miniguard.aleo.detectors.uvar import uvar_detector
from miniguard.aleo.detectors.infoleak import infoleak_detector

logging.getLogger().setLevel(logging.INFO)
logging.basicConfig(format='[%(levelname)s] %(message)s')

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("-p", "--project", help="path to aleo project folder", required=True)
    ap.add_argument("-d", "--detector", help="detectors to use, choose from: DivRD, Underflow, UnusedVar, InfoLeak, GraphGen, GraphGenTaint", required=True)
    ap.add_argument("-f", "--function", help="target function to analyze", required=True)
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    target_detector = args.detector
    target_path = args.project
    target_function_name = args.function
    
    target_ll = Path(target_path) / "main.ll"
    with open(target_ll, "r") as f:
        raw_ll = f.read()

    target_summary = Path(target_path) / "main.json"
    with open(target_summary, "r") as f:
        sum0 = json.load(f)
    sum0 = summary_conversion(sum0)
    
    # FIXME: we assume obj0 is a module here
    obj0 = parse_assembly(raw_ll)
    fun0 = locate_function(obj0, target_function_name)

    res = {
        "src": str(target_ll.resolve()),
        "summary": str(target_summary.resolve()),
        "report": []
    }

    if target_detector == "GraphGen":
        if args.verbose: logging.info(f"Generating information flow graph...")
        edges = construct_infoflow_graph(fun0)
        G = nx.DiGraph()
        G.add_edges_from(edges)
        A = nx.nx_agraph.to_agraph(G)
        A.draw(Path(target_path) / f"{target_function_name}.png", prog="dot")
        A.write(Path(target_path) / f"{target_function_name}.dot")
        if args.verbose: logging.info(f"Output: {target_function_name}.png")
        if args.verbose: logging.info(f"Output: {target_function_name}.dot")
    elif target_detector == "GraphGenTaint":
        logging.info(f"Generating information flow graph for taint analysis...")
        edges = construct_infoflow_graph(fun0, connect_hash=False)
        G = nx.DiGraph()
        G.add_edges_from(edges)
        A = nx.nx_agraph.to_agraph(G)
        A.draw(Path(target_path) / "main.png", prog="dot")
        A.write(Path(target_path) / "main.dot")
        if args.verbose: logging.info(f"Output: {target_function_name}.png")
        if args.verbose: logging.info(f"Output: {target_function_name}.dot")
    elif target_detector == "DivRD":
        res["report"] += divrd_detector(fun0)
    elif target_detector == "Underflow":
        res["report"] += underflow_detector(fun0)
    elif target_detector == "UnusedVar":
        res["report"] += uvar_detector(fun0, sum0)
    elif target_detector == "InfoLeak":
        res["report"] += infoleak_detector(fun0, sum0)
    else:
        raise Exception(f"unrecognized detector: {target_detector}")

    # output the report
    print(json.dumps(res, indent=4))