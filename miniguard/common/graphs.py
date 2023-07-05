from llvmlite.binding.module import ModuleRef
from llvmlite.binding.value import ValueRef

from .utils import regularize_name as rn

def collect_infoflow_pairs(arg_obj, connect_hash=True):
    """
    Construct pairs of information flow graph.
    - connect_hash: add information flow edge between each input-output pair of a hash call
                    when doing taint analysis, this should be set to False, otherwise True
    """
    pairs = []
    # FIXME: "call" opcode could lead to inter-component analysis
    SKIPPED_OPCODES = set(["alloca", "br", "ret"])
    HASH_CALLS = set([
        "aleo.hash.bhp256.i128",
        "aleo.hash.psd2.i128",
        "aleo.commit.bhp256.i128.i128",
    ])
    if isinstance(arg_obj, ValueRef) and arg_obj.is_instruction:
        if arg_obj.opcode in SKIPPED_OPCODES:
            # skip
            pass
        elif arg_obj.opcode == "call":
            # the last operand is the name of the callled function
            fname = list(arg_obj.operands)[-1].name
            if fname in HASH_CALLS:
                if connect_hash:
                    operands = list(arg_obj.operands)[:-1]
                    for p in operands:
                        pairs.append((
                            rn(p), rn(arg_obj)
                        ))
                else:
                    # do an inter-component analysis
                    # TODO
                    pass
            else:
                # do an inter-component analysis
                # TODO
                pass
        elif arg_obj.opcode == "store":
            # e.g.,
            #   store i128 %a, i128* %b, align 4
            # will generate
            #   a -> b
            operands = list(arg_obj.operands)
            assert len(operands) == 2, f"store has unexpected number of operands, got: {arg_obj}"
            pairs.append((
                rn(operands[0]), rn(operands[1])
            ))
        elif arg_obj.opcode == "load":
            # e.g.,
            #   %b = load i32, i32* %a, align 4
            # will generate
            #   a -> b
            operands = list(arg_obj.operands)
            assert len(operands) == 1, f"load has unexpected number of operands, got: {arg_obj}"
            pairs.append((
                rn(operands[0]), rn(arg_obj)
            ))
        elif arg_obj.opcode == "add":
            # e.g.
            #   %c = add i32 %a, %b
            # will generate
            #   a -> c, b -> c
            operands = list(arg_obj.operands)
            assert len(operands) == 2, f"add has unexpected number of operands, got: {arg_obj}"
            pairs.append((
                rn(operands[0]), rn(arg_obj)
            ))
            pairs.append((
                rn(operands[1]), rn(arg_obj)
            ))
        elif arg_obj.opcode == "icmp":
            # e.g.
            #   %c = add i32 %a, %b
            # will generate
            #   a -> c, b -> c
            operands = list(arg_obj.operands)
            assert len(operands) == 2, f"icmp has unexpected number of operands, got: {arg_obj}"
            pairs.append((
                rn(operands[0]), rn(arg_obj)
            ))
            pairs.append((
                rn(operands[1]), rn(arg_obj)
            ))
        elif arg_obj.opcode == "select":
            # e.g.
            #   %d = select i1 %a, i1 b, i1 c
            # will generate
            #   a -> d, b -> d, c -> d
            operands = list(arg_obj.operands)
            assert len(operands) == 3, f"select has unexpected number of operands, got: {arg_obj}"
            pairs.append((
                rn(operands[0]), rn(arg_obj)
            ))
            pairs.append((
                rn(operands[1]), rn(arg_obj)
            ))
            pairs.append((
                rn(operands[2]), rn(arg_obj)
            ))
        elif arg_obj.opcode == "getelementptr":
            # e.g.
            #   %d = getelementptr inbounds %token, %token* %a, i32 %b, i32 %c
            # will generate
            #   a -> d, b -> d, c -> d
            operands = list(arg_obj.operands)
            assert len(operands) == 3, f"getelementptr has unexpected number of operands, got: {arg_obj}"
            pairs.append((
                rn(operands[0]), rn(arg_obj)
            ))
            pairs.append((
                rn(operands[1]), rn(arg_obj)
            ))
            pairs.append((
                rn(operands[2]), rn(arg_obj)
            ))
        elif arg_obj.opcode == "zext":
            # e.g.
            #   %d = zext i1 %a to i32
            # will generate
            #   a -> d
            operands = list(arg_obj.operands)
            assert len(operands) == 1, f"zext has unexpected number of operands, got: {arg_obj}"
            pairs.append((
                rn(operands[0]), rn(arg_obj)
            ))
        elif arg_obj.opcode == "mul":
            # e.g.
            #   %d = mul i32 %a, %b
            # will generate
            #   a -> d, b -> d
            operands = list(arg_obj.operands)
            assert len(operands) == 2, f"mul has unexpected number of operands, got: {arg_obj}"
            pairs.append((
                rn(operands[0]), rn(arg_obj)
            ))
            pairs.append((
                rn(operands[1]), rn(arg_obj)
            ))
        elif arg_obj.opcode == "sdiv":
            # e.g.
            #   %d = sdiv i32 %a, %b
            # will generate
            #   a -> d, b -> d
            operands = list(arg_obj.operands)
            assert len(operands) == 2, f"sdiv has unexpected number of operands, got: {arg_obj}"
            pairs.append((
                rn(operands[0]), rn(arg_obj)
            ))
            pairs.append((
                rn(operands[1]), rn(arg_obj)
            ))
        elif arg_obj.opcode == "sub":
            # e.g.
            #   %d = sub i32 %a, %b
            # will generate
            #   a -> d, b -> d
            operands = list(arg_obj.operands)
            assert len(operands) == 2, f"sub has unexpected number of operands, got: {arg_obj}"
            pairs.append((
                rn(operands[0]), rn(arg_obj)
            ))
            pairs.append((
                rn(operands[1]), rn(arg_obj)
            ))
        else:
            raise Exception(f"unsupported instruction type, got: {arg_obj}")
    else:
        raise Exception("unsupported arg_obj in dependence pair collection")
    return pairs

def construct_infoflow_graph(arg_fun, connect_hash=True):
    edges = []
    # iterate on blocks
    for dblock in arg_fun.blocks:
        if isinstance(dblock, ValueRef) and dblock.is_block:
            # iterate on instructions
            for dinst in dblock.instructions:
                if isinstance(dinst, ValueRef) and dinst.is_instruction:
                    edges += collect_infoflow_pairs(dinst, connect_hash=connect_hash)
                else:
                    raise Exception("dinst is not a ValueRef / instruction")
        else:
            raise Exception("dblock is not a ValueRef / block")
    return edges