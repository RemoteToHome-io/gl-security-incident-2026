#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
"""Static decoder for the "ulogd.bin" Lua 5.1 bytecode loader found on compromised GL.iNet routers.

Usage:
    python3 -I decode_ulogd.py <ulogd.bin>            decoded strings and key parameters
    python3 -I decode_ulogd.py --json <ulogd.bin>     the same, as JSON
    python3 -I decode_ulogd.py --disasm <ulogd.bin>   annotated listing of every function
    python3 -I decode_ulogd.py --strings <ulogd.bin>  hidden strings in program order with their
                                                      users, then all plain string constants

Standard library only; run it with `python3 -I` so nothing is imported from the sample's directory.
Nothing in the sample is executed. The script parses the bytecode, then rebuilds the hidden strings
by reading the constant tables and the arithmetic the decoder functions apply, and reimplementing
that arithmetic in Python. It exits non-zero with a clear message on any input it cannot parse, and
contains no values specific to any one device, so it is safe to run on any captured sample.

Format notes
------------
The file is a Lua 5.1 binary chunk as produced by OpenWrt's patched Lua ("LNUM" patch). Two things
differ from stock Lua 5.1 and make stock tools (luac -l, unluac) refuse it:
  * header byte 11 (stock: "lua_Number is integral" flag) holds 4, the size of the integer type;
  * constants may have type tag 9, an integer stored as a 4-byte signed little-endian value, besides
    the stock tags 0 (nil), 1 (boolean), 3 (8-byte double) and 4 (string).
The instruction set is stock Lua 5.1 (38 opcodes, 6-bit op, 8-bit A, 9-bit B and C, 18-bit Bx).

String hiding
-------------
Each hidden string is returned by its own small function with no parameters. The function builds a
table of 4-element records {value, position, operation, key}, then for each record computes
    operation "add":  char = value - key
    operation "sub":  char = value + key
    operation "xor":  char = value XOR key      (bitwise, by a Lua helper function taking 2 args)
and stores string.char(char) at index `position` of an output table, which is joined with
table.concat. The operation name records how the value was encoded, so decoding applies the
inverse. Records may appear in any order; the position field orders the output.

One further function builds a hex string from 2-element records {value, position}: the operation is
chosen per position by an if-chain in the code (xor / subtract / add with a constant that sits in
the code, not in the record) and each result is formatted with "%02x" after "mod 256". In some
records `value` is itself computed while the table is built, as xor(a, b) of two constants.

This script does not assume the arithmetic: it reads, from each function's instructions, which
record field is the value, which is the position, which is the key, and which operation each branch
applies, and it refuses (exit status 2) any function whose shape it does not recognise.
"""

import hashlib
import json
import struct
import sys

OPNAMES = (
    "MOVE LOADK LOADBOOL LOADNIL GETUPVAL GETGLOBAL GETTABLE SETGLOBAL SETUPVAL SETTABLE NEWTABLE "
    "SELF ADD SUB MUL DIV MOD POW UNM NOT LEN CONCAT JMP EQ LT LE TEST TESTSET CALL TAILCALL RETURN "
    "FORLOOP FORPREP TFORLOOP SETLIST CLOSE CLOSURE VARARG"
).split()
OP = {name: i for i, name in enumerate(OPNAMES)}

# Header of a little-endian Lua 5.1 chunk from OpenWrt's LNUM-patched Lua: signature, version
# 0x51, format 0, little-endian, int 4, size_t 4, instruction 4, number 8, integer size 4.
EXPECTED_HEADER = bytes.fromhex("1b4c75615100010404040804")


class DecodeError(Exception):
    """Raised for any input this decoder does not fully understand."""


class LuaInt(int):
    """An integer constant (LNUM type tag 9), kept distinct from doubles for display."""


# --------------------------------------------------------------------------------------------
# Chunk parser
# --------------------------------------------------------------------------------------------

class Reader:
    def __init__(self, data):
        self.data = data
        self.pos = 0

    def take(self, n):
        if self.pos + n > len(self.data):
            raise DecodeError("truncated chunk at offset %d (need %d bytes)" % (self.pos, n))
        b = self.data[self.pos:self.pos + n]
        self.pos += n
        return b

    def u8(self):
        return self.take(1)[0]

    def i32(self):
        return struct.unpack("<i", self.take(4))[0]

    def u32(self):
        return struct.unpack("<I", self.take(4))[0]

    def f64(self):
        return struct.unpack("<d", self.take(8))[0]

    def string(self):
        n = self.u32()
        if n == 0:
            return None
        s = self.take(n)
        if s[-1:] != b"\0":
            raise DecodeError("string constant at offset %d not NUL-terminated" % (self.pos - n))
        return s[:-1]


class Proto:
    """One Lua function prototype. `path` is its position in the tree, e.g. "0.11"."""

    def __init__(self, path):
        self.path = path
        self.protos = []
        self.upvals = []   # filled by resolve_upvalues(): what each upvalue refers to


def parse_proto(r, path):
    p = Proto(path)
    p.offset = r.pos
    p.source = r.string()
    p.linedefined = r.i32()
    p.lastlinedefined = r.i32()
    p.nups = r.u8()
    p.numparams = r.u8()
    p.is_vararg = r.u8()
    p.maxstack = r.u8()
    n = r.u32()
    p.code_offset = r.pos
    p.code = [r.u32() for _ in range(n)]
    n = r.u32()
    p.k = []
    p.k_offsets = []
    for _ in range(n):
        p.k_offsets.append(r.pos)
        tag = r.u8()
        if tag == 0:
            p.k.append(None)
        elif tag == 1:
            p.k.append(bool(r.u8()))
        elif tag == 3:
            p.k.append(r.f64())
        elif tag == 4:
            p.k.append(r.string())
        elif tag == 9:
            p.k.append(LuaInt(r.i32()))
        else:
            raise DecodeError("unknown constant type %d at offset %d" % (tag, r.pos - 1))
    n = r.u32()
    for i in range(n):
        p.protos.append(parse_proto(r, "%s.%d" % (path, i)))
    p.lineinfo = [r.i32() for _ in range(r.u32())]
    p.locvars = [(r.string(), r.i32(), r.i32()) for _ in range(r.u32())]
    p.upvalnames = [r.string() for _ in range(r.u32())]
    return p


def parse_chunk(data):
    if data[:4] != b"\x1bLua":
        raise DecodeError("not a Lua binary chunk (bad signature)")
    if data[:12] != EXPECTED_HEADER:
        raise DecodeError("unsupported Lua chunk header %s (expected %s)"
                          % (data[:12].hex(), EXPECTED_HEADER.hex()))
    r = Reader(data)
    r.pos = 12
    main = parse_proto(r, "0")
    if r.pos != len(data):
        raise DecodeError("%d trailing bytes after the main function" % (len(data) - r.pos))
    return main


def fields(ins):
    """Split an instruction into (opname, A, B, C, Bx, sBx)."""
    op = ins & 0x3F
    if op >= len(OPNAMES):
        raise DecodeError("invalid opcode %d" % op)
    a = (ins >> 6) & 0xFF
    c = (ins >> 14) & 0x1FF
    b = (ins >> 23) & 0x1FF
    bx = ins >> 14
    return OPNAMES[op], a, b, c, bx, bx - 131071


def all_protos(p):
    yield p
    for c in p.protos:
        yield from all_protos(c)


# --------------------------------------------------------------------------------------------
# Upvalue resolution: after each CLOSURE come `nups` pseudo-instructions, MOVE 0 B (capture the
# parent's register B) or GETUPVAL 0 B (capture the parent's upvalue B). Tracking which closure
# each parent register holds tells us which function each child's upvalue refers to.
# --------------------------------------------------------------------------------------------

def resolve_upvalues(p, parent_upvals=()):
    regs = {}
    code = p.code
    pc = 0
    while pc < len(code):
        name, a, b, c, bx, sbx = fields(code[pc])
        if name == "CLOSURE":
            child = p.protos[bx]
            child.upvals = []
            for i in range(child.nups):
                pname, _, pb, _, _, _ = fields(code[pc + 1 + i])
                if pname == "MOVE":
                    child.upvals.append(regs.get(pb, ("reg", pb)))
                elif pname == "GETUPVAL":
                    child.upvals.append(parent_upvals[pb] if pb < len(parent_upvals)
                                        else ("upval", pb))
                else:
                    raise DecodeError("bad closure pseudo-instruction in %s at %d"
                                      % (p.path, pc + 1 + i))
            regs[a] = ("proto", child)
            pc += 1 + child.nups
            continue
        if name == "GETGLOBAL":
            regs[a] = ("global", p.k[bx].decode("latin-1"))
            pc += 1
            continue
        if name == "LOADK":
            regs[a] = ("const", p.k[bx])
            pc += 1
            continue
        if name == "CALL" and b == 2 and regs.get(a) == ("global", "require") \
                and regs.get(a + 1, ("",))[0] == "const":
            modname = regs[a + 1][1].decode("latin-1")
            for r in list(regs):
                if r >= a:
                    del regs[r]
            regs[a] = ("module", modname)
            pc += 1
            continue
        # Any other write to a register forgets what it held.
        if name in ("MOVE", "LOADK", "LOADBOOL", "GETUPVAL", "GETGLOBAL", "GETTABLE", "NEWTABLE",
                    "ADD", "SUB", "MUL", "DIV", "MOD", "POW", "UNM", "NOT", "LEN", "CONCAT",
                    "TESTSET"):
            regs.pop(a, None)
        elif name == "SELF":
            regs.pop(a, None)
            regs.pop(a + 1, None)
        elif name == "LOADNIL":
            for r in range(a, b + 1):
                regs.pop(r, None)
        elif name in ("CALL", "TFORLOOP", "VARARG"):
            for r in list(regs):
                if r >= a:
                    del regs[r]
        pc += 1
    for child in p.protos:
        resolve_upvalues(child, child.upvals)


# The bitwise-xor helper: function(a, b) that walks the bits of a and b with "% 2", "* 2" and
# math.floor(x / 2). Recognised by its exact opcode sequence and constants.
XOR_SHAPE = ("LOADK LOADK LT JMP LT JMP MOD MOD EQ JMP ADD MUL GETGLOBAL GETTABLE DIV CALL MOVE "
             "GETGLOBAL GETTABLE DIV CALL MOVE JMP RETURN RETURN").split()


def is_xor_helper(p):
    if p.numparams != 2 or p.nups != 0:
        return False
    if [fields(i)[0] for i in p.code] != XOR_SHAPE:
        return False
    return p.k == [0, 1, 2, b"math", b"floor"]


def lua_xor(a, b):
    """Bitwise xor exactly as the Lua helper computes it (non-negative integers)."""
    if a < 0 or b < 0 or a != int(a) or b != int(b):
        raise DecodeError("xor helper called with %r, %r (helper only defined for non-negative "
                          "integers)" % (a, b))
    return int(a) ^ int(b)


def upval_is_xor(p, idx):
    if idx >= len(p.upvals):
        return False
    u = p.upvals[idx]
    return u[0] == "proto" and is_xor_helper(u[1])


# --------------------------------------------------------------------------------------------
# Decoder-function recognition
# --------------------------------------------------------------------------------------------

def rk(p, regs, x):
    """Value of an RK operand during constant evaluation of the table-building prefix."""
    if x >= 256:
        return p.k[x - 256]
    if x not in regs:
        raise DecodeError("%s: register R%d read before it is known" % (p.path, x))
    return regs[x]


def eval_table_prefix(p):
    """Evaluate the straight-line prefix that builds the record table in register 0.

    Only NEWTABLE, LOADK, MOVE, SETLIST, and a call of the xor helper on two known values are
    accepted. Returns (records, pc of the first instruction after the prefix).
    """
    regs = {}
    pc = 0
    code = p.code
    while pc < len(code):
        name, a, b, c, bx, sbx = fields(code[pc])
        if name == "NEWTABLE":
            regs[a] = []
        elif name == "LOADK":
            regs[a] = p.k[bx]
        elif name == "MOVE":
            regs[a] = rk(p, regs, b)
        elif name == "GETUPVAL":
            if not upval_is_xor(p, b):
                raise DecodeError("%s: table prefix reads upvalue %d that is not the xor helper"
                                  % (p.path, b))
            regs[a] = "XOR"
        elif name == "CALL":
            if regs.get(a) != "XOR" or b != 3 or c != 2:
                raise DecodeError("%s: unexpected call in table prefix at pc %d" % (p.path, pc))
            regs[a] = lua_xor(rk(p, regs, a + 1), rk(p, regs, a + 2))
        elif name == "SETLIST":
            if c != 1 or b == 0:
                raise DecodeError("%s: unsupported SETLIST form at pc %d" % (p.path, pc))
            if not isinstance(regs.get(a), list) or regs[a]:
                raise DecodeError("%s: SETLIST into a non-empty or unknown table" % p.path)
            regs[a].extend(rk(p, regs, a + 1 + i) for i in range(b))
            if a == 0:
                pc += 1
                break
        else:
            break
        pc += 1
    if not isinstance(regs.get(0), list) or not regs[0]:
        raise DecodeError("%s: no record table built in R0" % p.path)
    return regs[0], pc


def parse_loop(p, start):
    """Parse `for _, rec in ipairs(R0) do ... end` that follows the table prefix.

    Returns (field_of_register, body_start, body_end, merge_pc, tail) where tail is "char" or
    "hex", and the branch list [(condition, expression)].
    """
    code = p.code
    seq = [fields(code[start + i]) for i in range(5)]
    names = [s[0] for s in seq]
    if names != ["NEWTABLE", "GETGLOBAL", "MOVE", "CALL", "JMP"] \
            or p.k[seq[1][4]] != b"ipairs" or seq[2][2] != 0:
        raise DecodeError("%s: expected `out = {}; for _, rec in ipairs(records)` at pc %d"
                          % (p.path, start))
    out_reg = seq[0][1]
    base = seq[1][1]
    loop_pc = start + 4 + 1 + seq[4][5]          # the TFORLOOP
    lname, la, _, lc, _, _ = fields(code[loop_pc])
    if lname != "TFORLOOP" or la != base or lc != 2:
        raise DecodeError("%s: expected TFORLOOP at pc %d" % (p.path, loop_pc))
    rec_reg = base + 4
    body = start + 5
    # Field loads: GETTABLE Rx = rec[K(i)]
    field_of = {}
    pc = body
    while True:
        name, a, b, c, bx, sbx = fields(code[pc])
        if name != "GETTABLE" or b != rec_reg or c < 256:
            break
        field_of[a] = int(p.k[c - 256])
        pc += 1
    name, a, b, c, _, _ = fields(code[pc])
    if name != "LOADNIL" or a != b:
        raise DecodeError("%s: expected `local r = nil` at pc %d" % (p.path, pc))
    res_reg = a
    pc += 1
    branches = []
    merge = None
    while True:
        name, a, b, c, bx, sbx = fields(code[pc])
        if name != "EQ" or a != 0 or b not in field_of or c < 256:
            break
        cond = (field_of[b], p.k[c - 256])
        jname, _, _, _, _, jsbx = fields(code[pc + 1])
        if jname != "JMP":
            raise DecodeError("%s: expected JMP after EQ at pc %d" % (p.path, pc + 1))
        next_test = pc + 2 + jsbx
        expr, end = parse_branch(p, pc + 2, field_of, res_reg)
        branches.append((cond, expr))
        if end is not None:
            if merge is None:
                merge = end
            elif merge != end:
                raise DecodeError("%s: branches do not rejoin at one point" % p.path)
        pc = next_test
        if merge is not None and pc == merge:
            break
    if not branches or merge is None:
        raise DecodeError("%s: no operation branches recognised" % p.path)
    # Tail: either string.char(r) or string.format("%02x", r % 256), stored at out[position].
    tail_names = [fields(code[merge + i])[0] for i in range(6)]
    if tail_names[:5] == ["GETGLOBAL", "GETTABLE", "MOVE", "CALL", "SETTABLE"] \
            and p.k[fields(code[merge + 1])[3] - 256] == b"char":
        tail, st = "char", merge + 4
    elif tail_names[:6] == ["GETGLOBAL", "GETTABLE", "LOADK", "MOD", "CALL", "SETTABLE"] \
            and p.k[fields(code[merge + 2])[4]] == b"%02x" \
            and p.k[fields(code[merge + 3])[3] - 256] == 256:
        tail, st = "hex", merge + 5
    else:
        raise DecodeError("%s: unrecognised output step at pc %d" % (p.path, merge))
    sname, sa, sb, _, _, _ = fields(code[st])
    if sa != out_reg or sb not in field_of:
        raise DecodeError("%s: output not stored at out[record field]" % p.path)
    pos_field = field_of[sb]
    if fields(code[st + 1])[0] != "TFORLOOP" or st + 1 != loop_pc:
        raise DecodeError("%s: loop body has unexpected extra code" % p.path)
    # After the loop: return table.concat(out)
    after = [fields(code[loop_pc + 2 + i]) for i in range(4)]
    if [x[0] for x in after] != ["GETGLOBAL", "GETTABLE", "MOVE", "TAILCALL"] \
            or p.k[after[1][3] - 256] != b"concat" or after[2][2] != out_reg:
        raise DecodeError("%s: function does not end with table.concat(out)" % p.path)
    return branches, pos_field, tail


def parse_branch(p, pc, field_of, res_reg):
    """One branch: returns (expression, pc it jumps to afterwards or None if it falls through).

    Expression forms: ("sub", x, y) meaning x - y, ("add", x, y), ("xor", x, y); each operand is
    ("field", i) or ("const", v).
    """
    code = p.code

    def operand(x):
        if x >= 256:
            return ("const", p.k[x - 256])
        if x in field_of:
            return ("field", field_of[x])
        raise DecodeError("%s: operand R%d is not a record field" % (p.path, x))

    name, a, b, c, bx, sbx = fields(code[pc])
    if name in ("SUB", "ADD") and a == res_reg:
        expr, nxt = (name.lower(), operand(b), operand(c)), pc + 1
    elif name == "GETUPVAL" and upval_is_xor(p, b):
        n2 = [fields(code[pc + i]) for i in range(1, 5)]
        if [x[0] for x in n2[:1]] != ["MOVE"] or n2[2][0] != "CALL" or n2[3][0] != "MOVE" \
                or n2[3][1] != res_reg or n2[3][2] != a:
            raise DecodeError("%s: unrecognised xor call at pc %d" % (p.path, pc))
        x = operand(n2[0][2])
        if n2[1][0] == "MOVE":
            y = operand(n2[1][2])
        elif n2[1][0] == "LOADK":
            y = ("const", p.k[n2[1][4]])
        else:
            raise DecodeError("%s: unrecognised xor operand at pc %d" % (p.path, pc + 2))
        expr, nxt = ("xor", x, y), pc + 5
    else:
        raise DecodeError("%s: unrecognised operation at pc %d (%s)" % (p.path, pc, name))
    jname, _, _, _, _, jsbx = fields(code[nxt])
    if jname == "JMP":
        return expr, nxt + 1 + jsbx
    return expr, nxt   # last branch falls through to the merge point


def evaluate(expr, rec):
    def val(o):
        if o[0] == "field":
            v = rec[o[1] - 1]
        else:
            v = o[1]
        if isinstance(v, bytes) or isinstance(v, bool) or v is None:
            raise DecodeError("non-numeric operand %r" % (v,))
        return v
    kind, x, y = expr
    if kind == "sub":
        return val(x) - val(y)
    if kind == "add":
        return val(x) + val(y)
    return lua_xor(val(x), val(y))


def decode_function(p):
    """Return (kind, value) for a recognised decoder function, or None if it is not one."""
    if p.numparams != 0 or not p.code or fields(p.code[0])[0] != "NEWTABLE" \
            or fields(p.code[0])[1] != 0:
        return None
    try:
        records, pc = eval_table_prefix(p)
    except DecodeError:
        return None
    if len(records) < 2 or not all(isinstance(r, list) for r in records):
        return None
    branches, pos_field, tail = parse_loop(p, pc)
    out = {}
    for rec in records:
        expr = None
        for (field, want), e in branches:
            if rec[field - 1] == want:
                expr = e
                break
        if expr is None:
            raise DecodeError("%s: record %r matches no branch (would be nil at run time)"
                              % (p.path, rec))
        v = evaluate(expr, rec)
        pos = rec[pos_field - 1]
        if pos in out:
            raise DecodeError("%s: duplicate position %r" % (p.path, pos))
        if tail == "char":
            if not 0 <= v <= 255 or v != int(v):
                raise DecodeError("%s: character value %r out of range" % (p.path, v))
            out[pos] = bytes([int(v)])
        else:
            out[pos] = ("%02x" % (int(v) % 256)).encode()
    if sorted(out) != list(range(1, len(out) + 1)):
        raise DecodeError("%s: positions are not 1..n" % p.path)
    text = b"".join(out[i] for i in range(1, len(out) + 1))
    ops = sorted({e[0] for _, e in branches})
    return {"kind": "string" if tail == "char" else "hexkey", "value": text,
            "records": len(records), "branch_ops": ops}


# --------------------------------------------------------------------------------------------
# Listing
# --------------------------------------------------------------------------------------------

def show(v):
    if isinstance(v, bytes):
        return json.dumps(v.decode("latin-1"))
    if isinstance(v, LuaInt):
        return str(int(v))
    if isinstance(v, float) and v == int(v):
        return "%d.0" % v
    return repr(v)


def upval_label(p, i, decoded):
    if i >= len(p.upvals):
        return "U%d" % i
    u = p.upvals[i]
    if u[0] == "proto":
        q = u[1]
        if q.path in decoded:
            return "U%d=fn%s()->%s" % (i, q.path, show(decoded[q.path]["value"]))
        if is_xor_helper(q):
            return "U%d=fn%s(xor)" % (i, q.path)
        return "U%d=fn%s" % (i, q.path)
    if u[0] == "module":
        return "U%d=require(%s)" % (i, json.dumps(u[1]))
    return "U%d" % i


def listing(p, decoded, out):
    out("function %s  params=%d upvalues=%d vararg=%d maxstack=%d  file offset 0x%x"
        % (p.path, p.numparams, p.nups, p.is_vararg, p.maxstack, p.offset))
    for i in range(p.nups):
        out("  upvalue %s" % upval_label(p, i, decoded))
    if p.path in decoded:
        out("  DECODER -> %s" % show(decoded[p.path]["value"]))
    for i, k in enumerate(p.k):
        out("  K%-3d @0x%05x %s" % (i, p.k_offsets[i], show(k)))

    def RK(x):
        return "K%d(%s)" % (x - 256, show(p.k[x - 256])) if x >= 256 else "R%d" % x

    pc = 0
    while pc < len(p.code):
        name, a, b, c, bx, sbx = fields(p.code[pc])
        if name == "LOADK":
            s = "R%d = %s" % (a, show(p.k[bx]))
        elif name in ("GETGLOBAL", "SETGLOBAL"):
            s = ("R%d = %s" if name == "GETGLOBAL" else "%s = R%d").replace(
                "%s", p.k[bx].decode()) % a
        elif name == "GETUPVAL":
            s = "R%d = %s" % (a, upval_label(p, b, decoded))
        elif name == "SETUPVAL":
            s = "U%d = R%d" % (b, a)
        elif name == "GETTABLE":
            s = "R%d = R%d[%s]" % (a, b, RK(c))
        elif name == "SETTABLE":
            s = "R%d[%s] = %s" % (a, RK(b), RK(c))
        elif name == "SELF":
            s = "R%d = R%d; R%d = R%d[%s]" % (a + 1, b, a, b, RK(c))
        elif name in ("ADD", "SUB", "MUL", "DIV", "MOD", "POW"):
            sym = {"ADD": "+", "SUB": "-", "MUL": "*", "DIV": "/", "MOD": "%", "POW": "^"}[name]
            s = "R%d = %s %s %s" % (a, RK(b), sym, RK(c))
        elif name in ("EQ", "LT", "LE"):
            sym = {"EQ": "==", "LT": "<", "LE": "<="}[name]
            s = "if (%s %s %s) ~= %d then skip next" % (RK(b), sym, RK(c), a)
        elif name in ("JMP", "FORPREP", "FORLOOP"):
            s = "A%d -> %d" % (a, pc + 1 + sbx)
        elif name == "TEST":
            s = "if not (R%d <=> %d) then skip next" % (a, c)
        elif name == "TESTSET":
            s = "if (R%d <=> %d) then R%d = R%d else skip next" % (b, c, a, b)
        elif name in ("CALL", "TAILCALL"):
            args = "" if b == 1 else ("R%d..top" % (a + 1) if b == 0 else
                                      ", ".join("R%d" % r for r in range(a + 1, a + b)))
            if name == "TAILCALL" or c == 0:
                res = "R%d..top = " % a
            elif c == 1:
                res = ""
            else:
                res = ", ".join("R%d" % r for r in range(a, a + c - 1)) + " = "
            s = "%sR%d(%s)" % (res, a, args)
        elif name == "CLOSURE":
            s = "R%d = closure fn%s" % (a, p.protos[bx].path)
        elif name == "CONCAT":
            s = "R%d = R%d .. ... .. R%d" % (a, b, c)
        elif name == "RETURN":
            s = "return R%d..R%d" % (a, a + b - 2) if b else "return R%d..top" % a
        elif name == "MOVE":
            s = "R%d = R%d" % (a, b)
        elif name == "LOADBOOL":
            s = "R%d = %s%s" % (a, bool(b), "; skip next" if c else "")
        elif name == "LOADNIL":
            s = "R%d..R%d = nil" % (a, b)
        else:
            s = "A=%d B=%d C=%d" % (a, b, c)
        out("  %4d  0x%05x  %-9s %s" % (pc, p.code_offset + 4 * pc, name, s))
        if name == "CLOSURE":
            for i in range(p.protos[bx].nups):
                pc += 1
                pn, _, pb, _, _, _ = fields(p.code[pc])
                out("  %4d  0x%05x  %-9s (captures %s %d)" % (
                    pc, p.code_offset + 4 * pc, pn, "R" if pn == "MOVE" else "U", pb))
        pc += 1
    out("")


# --------------------------------------------------------------------------------------------
# Report
# --------------------------------------------------------------------------------------------

def analyse(data):
    main = parse_chunk(data)
    resolve_upvalues(main)
    decoded = {}
    for p in all_protos(main):
        d = decode_function(p)
        if d is not None:
            decoded[p.path] = d
    if not decoded:
        raise DecodeError("no hidden-string functions recognised")
    # Refuse to report a partial result: any function that has the shape of a string builder
    # (no parameters, record table in R0, ipairs loop, join with table.concat) must have decoded.
    for p in all_protos(main):
        if p.path in decoded or p.numparams != 0 or not p.code:
            continue
        name, a = fields(p.code[0])[:2]
        if name == "NEWTABLE" and a == 0 and b"ipairs" in p.k and b"concat" in p.k \
                and (b"char" in p.k or b"%02x" in p.k):
            raise DecodeError("%s looks like a hidden-string function but was not decoded" % p.path)
    return main, decoded


def plain_strings(main):
    """Every string constant in the chunk, in function order, as (function, index, value)."""
    res = []
    for p in all_protos(main):
        for i, k in enumerate(p.k):
            if isinstance(k, bytes):
                res.append((p.path, i, k))
    return res


def users_of(main):
    """Map function path -> list of places that use it: captured as an upvalue, or called
    directly from a register that holds its closure."""
    users = {}
    for q in all_protos(main):
        for i, u in enumerate(q.upvals):
            if u[0] == "proto":
                users.setdefault(u[1].path, []).append("fn%s (upvalue U%d)" % (q.path, i))
        regs = {}
        pc = 0
        while pc < len(q.code):
            name, a, b, c, bx, sbx = fields(q.code[pc])
            if name == "CLOSURE":
                regs[a] = q.protos[bx]
                pc += 1 + q.protos[bx].nups
                continue
            if name == "MOVE":
                if b in regs:
                    regs[a] = regs[b]
                else:
                    regs.pop(a, None)
            elif name in ("CALL", "TAILCALL") and a in regs:
                tag = "fn%s (called directly at pc %d)" % (q.path, pc)
                users.setdefault(regs[a].path, []).append(tag)
                for r in list(regs):
                    if r >= a:
                        del regs[r]
            elif name not in ("JMP", "EQ", "LT", "LE", "TEST", "SETGLOBAL", "SETTABLE",
                              "SETUPVAL", "SETLIST", "RETURN", "FORLOOP", "FORPREP", "CLOSE"):
                regs.pop(a, None)
            pc += 1
    return users


def strings_listing(path, data, main, decoded, out):
    """Hidden strings in program order with their users, then every plain string constant."""
    users = users_of(main)
    out("# Decoded hidden strings of %s" % path)
    out("# size %d, sha256 %s" % (len(data), hashlib.sha256(data).hexdigest()))
    out("# One line per hidden-string function, in bytecode order (also the order main creates")
    out("# them). Columns: function, number of records, decoded value (JSON-quoted), where the")
    out("# function is used (captured as an upvalue, or called directly).")
    out("")
    for p in all_protos(main):
        if p.path in decoded:
            d = decoded[p.path]
            used = "; ".join(users.get(p.path, [])) or "not referenced: dead code"
            out("fn%-6s %4d  %-70s %s" % (p.path, d["records"], show(d["value"]), used))
    out("")
    out("# Plain (not hidden) string constants, function/constant index: value")
    out("")
    for f, i, v in plain_strings(main):
        if f in decoded:
            continue   # the decoder functions' own constants are only operation names
        out("fn%s/K%d  %s" % (f, i, show(v)))


def summary(data, main, decoded):
    strings = [d["value"].decode("latin-1") for d in decoded.values() if d["kind"] == "string"]
    keys = [d["value"].decode() for d in decoded.values() if d["kind"] == "hexkey"]
    urls = [s for s in strings if s.startswith(("http://", "https://"))]
    sleeps = [s for s in strings if s.startswith("sleep ")]
    plain = plain_strings(main)
    pv = [v.decode("latin-1") for _, _, v in plain]
    ids = sorted({v for v in pv if len(v) == 40 and all(ch in "0123456789abcdefABCDEF" for ch in v)})
    versions = sorted({v for v in pv if len(v) <= 12 and v[:1] == "v" and v[1:2].isdigit()})
    formats = [v for v in pv if "%s=%d&" in v or "%s=%s&" in v]
    return {
        "size": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "functions": sum(1 for _ in all_protos(main)),
        "hidden_strings": len(strings),
        "urls": urls,
        "sleep_commands": sleeps,
        "hex_keys": keys,
        "id_constants": ids,
        "version_constants": versions,
        "beacon_formats": formats,
        "decoded": [{"function": path, "kind": d["kind"], "records": d["records"],
                     "value": d["value"].decode("latin-1")} for path, d in decoded.items()],
        "plain_strings": [{"function": f, "k": i, "value": v.decode("latin-1")}
                          for f, i, v in plain],
    }


def main_cli(argv):
    mode = "text"
    args = list(argv[1:])
    if args and args[0] in ("--json", "--disasm", "--strings"):
        mode = args.pop(0)[2:]
    if len(args) != 1:
        sys.stderr.write(__doc__.split("\n\n")[1] + "\n")
        return 64
    path = args[0]
    try:
        with open(path, "rb") as fh:
            data = fh.read()
        main, decoded = analyse(data)
        s = summary(data, main, decoded)
    except (DecodeError, OSError, IndexError, struct.error) as e:
        sys.stderr.write("decode_ulogd: FAILED on %s: %s: %s\n" % (path, type(e).__name__, e))
        return 2
    if mode == "json":
        print(json.dumps(s, indent=1))
    elif mode == "disasm":
        for p in all_protos(main):
            listing(p, decoded, print)
    elif mode == "strings":
        strings_listing(path, data, main, decoded, print)
    else:
        print("file      %s" % path)
        print("size      %d" % s["size"])
        print("sha256    %s" % s["sha256"])
        print("functions %d, hidden strings %d" % (s["functions"], s["hidden_strings"]))
        for u in s["urls"]:
            print("url       %s" % u)
        for c in s["sleep_commands"]:
            print("sleep     %s" % c)
        for k in s["hex_keys"]:
            print("hex key   %s" % k)
        for k in s["id_constants"]:
            print("40-hex id %s" % k)
        for k in s["version_constants"]:
            print("version   %s" % k)
        for k in s["beacon_formats"]:
            print("format    %s" % k)
        print()
        print("hidden strings (function: value):")
        for d in s["decoded"]:
            print("  fn%-6s %s" % (d["function"], json.dumps(d["value"])))
        print()
        print("plain string constants (function/constant: value):")
        for d in s["plain_strings"]:
            print("  fn%s/K%d %s" % (d["function"], d["k"], json.dumps(d["value"])))
    return 0


if __name__ == "__main__":
    sys.exit(main_cli(sys.argv))
