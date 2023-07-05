from llvmlite.binding.module import ModuleRef
from llvmlite.binding.value import ValueRef

from ...common.utils import regularize_name as rn

def report(fn):
    def inner(*args, **kwargs):
        res = fn(*args, **kwargs)
        # wrap into a report
        obj = [{
            "detector": "Underflow",
            "result": True if len(res)>0 else False,
            "details": res
        }]
        return obj
    return inner

@report
def underflow_detector(arg_fun):
    ptr_map = []
    # all `gte a b into c` operations, in the form of (a, b, c)
    gte_ops = []
    # all `assert.eq a b` operations, in the form of (a, b)
    eq_ops = []
    
    res = []
    for dblock in arg_fun.blocks:
        if isinstance(dblock, ValueRef) and dblock.is_block:
            # iterate on instructions
            for dinst in dblock.instructions:
                if isinstance(dinst, ValueRef) and dinst.is_instruction:
                    if dinst.opcode == "icmp":
                        # check which icmp operation it is
                        str_pred = str(dinst).split(" ")
                        icmp_op = list(filter(lambda x: x != "", str_pred))[3]
                        if icmp_op == "sge":
                            operands = list(dinst.operands)
                            gte_ops.append((
                                rn(operands[0]), rn(operands[1]), rn(dinst)
                            ))
                    elif dinst.opcode == "call":
                        operands = list(dinst.operands)
                        if str.find(str(dinst), "aleo.assert.eq") != -1:
                            eq_ops.append((
                                rn(operands[0]), rn(operands[1])
                            ))
                    elif dinst.opcode == "sub":
                        # check if the operands are safe
                        operands = list(dinst.operands)
                        assert len(operands) == 2, f"sub has unexpected number of operands, got: {dinst}"
                        def find_ptr(dest):
                            for ptr in ptr_map:
                                if ptr[1] == dest:
                                    return ptr[0]
                            return None
                        # get all the values represented by the operands
                        op1 = rn(operands[0])
                        op2 = rn(operands[1])
                        op1_ptr = find_ptr(op1)
                        op2_ptr = find_ptr(op2)
                        safe = False
                        if op1_ptr is not None and op2_ptr is not None:
                            # check if the result is used in an eq_op
                            for eq_op in eq_ops:
                                op1_values = list(map(lambda x: x[1], filter(lambda x: x[0] == op1_ptr, ptr_map)))
                                op2_values = list(map(lambda x: x[1], filter(lambda x: x[0] == op2_ptr, ptr_map)))
                                for gte_op in gte_ops:
                                    if gte_op[0] in op1_values and gte_op[1] in op2_values:
                                        for eq_op in eq_ops:
                                            assert_op1 = eq_op[0]
                                            assert_op2 = gte_op[2]
                                            assert_op1_ptr = find_ptr(assert_op1)
                                            assert_op2_ptr = find_ptr(assert_op2)
                                            if assert_op1_ptr is not None and assert_op2_ptr is not None:
                                                if assert_op1_ptr == assert_op2_ptr:
                                                    if eq_op[1] == 'i1 true':
                                                        safe = True
                        if not safe:
                            res.append(rn(dinst))
                    # taint the gte_ops
                    elif dinst.opcode == "zext":
                        operands = list(dinst.operands)
                        for gte_op in gte_ops:
                            if gte_op[2] == rn(operands[0]):
                                gte_ops.append((
                                    gte_op[0], gte_op[1], rn(dinst)
                                ))
                    elif dinst.opcode == "store":
                        operands = list(dinst.operands)
                        ptr_map.append((
                            rn(operands[1]), rn(operands[0])
                        ))
                    elif dinst.opcode == "load":
                        operands = list(dinst.operands)
                        ptr_map.append((
                            rn(operands[0]), rn(dinst)
                        ))
                else:
                    raise Exception("dinst is not a ValueRef / instruction")
        else:
            raise Exception("dblock is not a ValueRef / block")
    return res