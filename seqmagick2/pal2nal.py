#!/usr/bin/env python

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

CODON_TABLES = {
    1: {
        "B": "((U|T|C|Y|A)(U|T)G)",
        "L": "((C(U|T).)|((U|T)(U|T)(A|G|R)))",
        "R": "((CG.)|(AG(A|G|R)))",
        "S": "(((U|T)C.)|(AG(U|T|C|Y)))",
        "A": "(GC.)",
        "G": "(GG.)",
        "P": "(CC.)",
        "T": "(AC.)",
        "V": "(G(U|T).)",
        "I": "(A(U|T)(U|T|C|Y|A))",
        "_": "(((U|T)A(A|G|R))|((T|U)GA))",
        "*": "(((U|T)A(A|G|R))|((T|U)GA))",
        "C": "((U|T)G(U|T|C|Y))",
        "D": "(GA(U|T|C|Y))",
        "E": "(GA(A|G|R))",
        "F": "((U|T)(U|T)(U|T|C|Y))",
        "H": "(CA(U|T|C|Y))",
        "K": "(AA(A|G|R))",
        "N": "(AA(U|T|C|Y))",
        "Q": "(CA(A|G|R))",
        "Y": "((U|T)A(U|T|C|Y))",
        "M": "(A(U|T)G)",
        "W": "((U|T)GG)",
        "X": "...",
    },
    2: {
        "B": "((A(U|T).)|G(U|T)G)",
        "L": "((C(U|T).)|((U|T)(U|T)(A|G|R)))",
        "R": "(CG.)",
        "S": "(((U|T)C.)|(AG(U|T|C|Y)))",
        "A": "(GC.)",
        "G": "(GG.)",
        "P": "(CC.)",
        "T": "(AC.)",
        "V": "(G(U|T).)",
        "I": "(A(U|T)(U|T|C|Y))",
        "_": "(((U|T)A(A|G|R))|(AG(A|G|R)))",
        "*": "(((U|T)A(A|G|R))|(AG(A|G|R)))",
        "C": "((U|T)G(U|T|C|Y))",
        "D": "(GA(U|T|C|Y))",
        "E": "(GA(A|G|R))",
        "F": "((U|T)(U|T)(U|T|C|Y))",
        "H": "(CA(U|T|C|Y))",
        "K": "(AA(A|G|R))",
        "N": "(AA(U|T|C|Y))",
        "Q": "(CA(A|G|R))",
        "Y": "((U|T)A(U|T|C|Y))",
        "M": "(A(U|T)(A|G|R))",
        "W": "((U|T)G(A|G|R))",
        "X": "...",
    },
    3: {
        "B": "(A(U|T)(A|G|R))",
        "L": "((U|T)(U|T)(A|G|R))",
        "R": "((CG.)|(AG(A|G|R)))",
        "S": "(((U|T)C.)|(AG(U|T|C|Y)))",
        "A": "(GC.)",
        "G": "(GG.)",
        "P": "(CC.)",
        "T": "((AC.)|(C(U|T).))",
        "V": "(G(U|T).)",
        "I": "(A(U|T)(U|T|C|Y))",
        "_": "((U|T)A(A|G|R))",
        "*": "((U|T)A(A|G|R))",
        "C": "((U|T)G(U|T|C|Y))",
        "D": "(GA(U|T|C|Y))",
        "E": "(GA(A|G|R))",
        "F": "((U|T)(U|T)(U|T|C|Y))",
        "H": "(CA(U|T|C|Y))",
        "K": "(AA(A|G|R))",
        "N": "(AA(U|T|C|Y))",
        "Q": "(CA(A|G|R))",
        "Y": "((U|T)A(U|T|C|Y))",
        "M": "(A(U|T)(A|G|R))",
        "W": "((U|T)G(A|G|R))",
        "X": "...",
    },
    4: {
        "B": "((A(U|T).)|((U|T)(U|T)(A|G|R))|(C(U|T)G)|(G(U|T)G))",
        "L": "((C(U|T).)|((U|T)(U|T)(A|G|R)))",
        "R": "((CG.)|(AG(A|G|R)))",
        "S": "(((U|T)C.)|(AG(U|T|C|Y)))",
        "A": "(GC.)",
        "G": "(GG.)",
        "P": "(CC.)",
        "T": "(AC.)",
        "V": "(G(U|T).)",
        "I": "(A(U|T)(U|T|C|Y|A))",
        "_": "((U|T)A(A|G|R))",
        "*": "((U|T)A(A|G|R))",
        "C": "((U|T)G(U|T|C|Y))",
        "D": "(GA(U|T|C|Y))",
        "E": "(GA(A|G|R))",
        "F": "((U|T)(U|T)(U|T|C|Y))",
        "H": "(CA(U|T|C|Y))",
        "K": "(AA(A|G|R))",
        "N": "(AA(U|T|C|Y))",
        "Q": "(CA(A|G|R))",
        "Y": "((U|T)A(U|T|C|Y))",
        "M": "(A(U|T)G)",
        "W": "((U|T)G(A|G|R))",
        "X": "...",
    },
    5: {
        "B": "((A(U|T).)|((U|T|A|G|R)(U|T)G))",
        "L": "((C(U|T).)|((U|T)(U|T)(A|G|R)))",
        "R": "(CG.)",
        "S": "(((U|T)C.)|(AG.))",
        "A": "(GC.)",
        "G": "(GG.)",
        "P": "(CC.)",
        "T": "(AC.)",
        "V": "(G(U|T).)",
        "I": "(A(U|T)(U|T|C|Y))",
        "_": "((U|T)A(A|G|R))",
        "*": "((U|T)A(A|G|R))",
        "C": "((U|T)G(U|T|C|Y))",
        "D": "(GA(U|T|C|Y))",
        "E": "(GA(A|G|R))",
        "F": "((U|T)(U|T)(U|T|C|Y))",
        "H": "(CA(U|T|C|Y))",
        "K": "(AA(A|G|R))",
        "N": "(AA(U|T|C|Y))",
        "Q": "(CA(A|G|R))",
        "Y": "((U|T)A(U|T|C|Y))",
        "M": "(A(U|T)(A|G|R))",
        "W": "((U|T)G(A|G|R))",
        "X": "...",
    },
    6: {
        "B": "(A(U|T)G)",
        "L": "((C(U|T).)|((U|T)(U|T)(A|G|R)))",
        "R": "((CG.)|(AG(A|G|R)))",
        "S": "(((U|T)C.)|(AG(U|T|C|Y)))",
        "A": "(GC.)",
        "G": "(GG.)",
        "P": "(CC.)",
        "T": "(AC.)",
        "V": "(G(U|T).)",
        "I": "(A(U|T)(U|T|C|Y|A))",
        "_": "((T|U)GA)",
        "*": "((T|U)GA)",
        "C": "((U|T)G(U|T|C|Y))",
        "D": "(GA(U|T|C|Y))",
        "E": "(GA(A|G|R))",
        "F": "((U|T)(U|T)(U|T|C|Y))",
        "H": "(CA(U|T|C|Y))",
        "K": "(AA(A|G|R))",
        "N": "(AA(U|T|C|Y))",
        "Q": "((CA(A|G|R))|((U|T)A(A|G|R)))",
        "Y": "((U|T)A(U|T|C|Y))",
        "M": "(A(U|T)G)",
        "W": "((U|T)GG)",
        "X": "...",
    },
    9: {
        "B": "((A|G|R)(U|T)G)",
        "L": "((C(U|T).)|((U|T)(U|T)(A|G|R)))",
        "R": "(CG.)",
        "S": "(((U|T)C.)|(AG.))",
        "A": "(GC.)",
        "G": "(GG.)",
        "P": "(CC.)",
        "T": "(AC.)",
        "V": "(G(U|T).)",
        "I": "(A(U|T)(U|T|C|Y|A))",
        "_": "((U|T)A(A|G|R))",
        "*": "((U|T)A(A|G|R))",
        "C": "((U|T)G(U|T|C|Y))",
        "D": "(GA(U|T|C|Y))",
        "E": "(GA(A|G|R))",
        "F": "((U|T)(U|T)(U|T|C|Y))",
        "H": "(CA(U|T|C|Y))",
        "K": "(AAG)",
        "N": "(AA(U|T|C|Y|A))",
        "Q": "(CA(A|G|R))",
        "Y": "((U|T)A(U|T|C|Y))",
        "M": "(A(U|T)G)",
        "W": "((U|T)G(A|G|R))",
        "X": "...",
    },
    10: {
        "B": "(A(U|T)G)",
        "L": "((C(U|T).)|((U|T)(U|T)(A|G|R)))",
        "R": "((CG.)|(AG(A|G|R)))",
        "S": "(((U|T)C.)|(AG(U|T|C|Y)))",
        "A": "(GC.)",
        "G": "(GG.)",
        "P": "(CC.)",
        "T": "(AC.)",
        "V": "(G(U|T).)",
        "I": "(A(U|T)(U|T|C|Y|A))",
        "_": "(((U|T)A(A|G|R))|((T|U)GA))",
        "*": "(((U|T)A(A|G|R))|((T|U)GA))",
        "C": "((U|T)G(U|T|C|Y))",
        "D": "(GA(U|T|C|Y))",
        "E": "(GA(A|G|R))",
        "F": "((U|T)(U|T)(U|T|C|Y))",
        "H": "(CA(U|T|C|Y))",
        "K": "(AA(A|G|R))",
        "N": "(AA(U|T|C|Y))",
        "Q": "(CA(A|G|R))",
        "Y": "((U|T)A(U|T|C|Y))",
        "M": "(A(U|T)G)",
        "W": "((U|T)GG)",
        "X": "...",
    },
    11: {
        "B": "((A(U|T)G)|(.(U|T)G))",
        "L": "((C(U|T).)|((U|T)(U|T)(A|G|R)))",
        "R": "((CG.)|(AG(A|G|R)))",
        "S": "(((U|T)C.)|(AG(U|T|C|Y)))",
        "A": "(GC.)",
        "G": "(GG.)",
        "P": "(CC.)",
        "T": "(AC.)",
        "V": "(G(U|T).)",
        "I": "(A(U|T)(U|T|C|Y|A))",
        "_": "(((U|T)A(A|G|R))|((T|U)GA))",
        "*": "(((U|T)A(A|G|R))|((T|U)GA))",
        "C": "((U|T)G(U|T|C|Y))",
        "D": "(GA(U|T|C|Y))",
        "E": "(GA(A|G|R))",
        "F": "((U|T)(U|T)(U|T|C|Y))",
        "H": "(CA(U|T|C|Y))",
        "K": "(AA(A|G|R))",
        "N": "(AA(U|T|C|Y))",
        "Q": "(CA(A|G|R))",
        "Y": "((U|T)A(U|T|C|Y))",
        "M": "(A(U|T)G)",
        "W": "((U|T)GG)",
        "X": "...",
    },
    12: {
        "B": "((A|C)(U|T)G)",
        "L": "((C(U|T)(U|T|C|Y|A))|((U|T)(U|T)(A|G|R)))",
        "R": "((CG.)|(AG(A|G|R)))",
        "S": "(((U|T)C.)|(AG(U|T|C|Y))|(C(U|T)G))",
        "A": "(GC.)",
        "G": "(GG.)",
        "P": "(CC.)",
        "T": "(AC.)",
        "V": "(G(U|T).)",
        "I": "(A(U|T)(U|T|C|Y|A))",
        "_": "(((U|T)A(A|G|R))|((T|U)GA))",
        "*": "(((U|T)A(A|G|R))|((T|U)GA))",
        "C": "((U|T)G(U|T|C|Y))",
        "D": "(GA(U|T|C|Y))",
        "E": "(GA(A|G|R))",
        "F": "((U|T)(U|T)(U|T|C|Y))",
        "H": "(CA(U|T|C|Y))",
        "K": "(AA(A|G|R))",
        "N": "(AA(U|T|C|Y))",
        "Q": "(CA(A|G|R))",
        "Y": "((U|T)A(U|T|C|Y))",
        "M": "(A(U|T)G)",
        "W": "((U|T)GG)",
        "X": "...",
    },
    13: {
        "B": "((T|U|A|G|R)(U|T)G)",
        "L": "((C(U|T).)|((U|T)(U|T)(A|G|R)))",
        "R": "(CG.)",
        "S": "(((U|T)C.)|(AG(U|T|C|Y)))",
        "A": "(GC.)",
        "G": "((GG.)|(AG(A|G|R)))",
        "P": "(CC.)",
        "T": "(AC.)",
        "V": "(G(U|T).)",
        "I": "(A(U|T)(U|T|C|Y))",
        "_": "((U|T)A(A|G|R))",
        "*": "((U|T)A(A|G|R))",
        "C": "((U|T)G(U|T|C|Y))",
        "D": "(GA(U|T|C|Y))",
        "E": "(GA(A|G|R))",
        "F": "((U|T)(U|T)(U|T|C|Y))",
        "H": "(CA(U|T|C|Y))",
        "K": "(AA(A|G|R))",
        "N": "(AA(U|T|C|Y))",
        "Q": "(CA(A|G|R))",
        "Y": "((U|T)A(U|T|C|Y))",
        "M": "(A(U|T)(A|G|R))",
        "W": "((U|T)G(A|G|R))",
        "X": "...",
    },
    14: {
        "B": "(A(U|T)G)",
        "L": "((C(U|T).)|((U|T)(U|T)(A|G|R)))",
        "R": "(CG.)",
        "S": "(((U|T)C.)|(AG.))",
        "A": "(GC.)",
        "G": "(GG.)",
        "P": "(CC.)",
        "T": "(AC.)",
        "V": "(G(U|T).)",
        "I": "(A(U|T)(U|T|C|Y|A))",
        "_": "((U|T)AG)",
        "*": "((U|T)AG)",
        "C": "((U|T)G(U|T|C|Y))",
        "D": "(GA(U|T|C|Y))",
        "E": "(GA(A|G|R))",
        "F": "((U|T)(U|T)(U|T|C|Y))",
        "H": "(CA(U|T|C|Y))",
        "K": "(AAG)",
        "N": "(AA(U|T|C|Y|A))",
        "Q": "(CA(A|G|R))",
        "Y": "((U|T)A(U|T|C|Y|A))",
        "M": "(A(U|T)G)",
        "W": "((U|T)G(G|A|R))",
        "X": "...",
    },
    15: {
        "B": "(A(U|T)G)",
        "L": "((C(U|T).)|((U|T)(U|T)(A|G|R)))",
        "R": "((CG.)|(AG(A|G|R)))",
        "S": "(((U|T)C.)|(AG(U|T|C|Y)))",
        "A": "(GC.)",
        "G": "(GG.)",
        "P": "(CC.)",
        "T": "(AC.)",
        "V": "(G(U|T).)",
        "I": "(A(U|T)(U|T|C|Y|A))",
        "_": "(((U|T)AA)|((T|U)GA))",
        "*": "(((U|T)AA)|((T|U)GA))",
        "C": "((U|T)G(U|T|C|Y))",
        "D": "(GA(U|T|C|Y))",
        "E": "(GA(A|G|R))",
        "F": "((U|T)(U|T)(U|T|C|Y))",
        "H": "(CA(U|T|C|Y))",
        "K": "(AA(A|G|R))",
        "N": "(AA(U|T|C|Y))",
        "Q": "((CA(A|G|R))|((U|T)AG))",
        "Y": "((U|T)A(U|T|C|Y))",
        "M": "(A(U|T)G)",
        "W": "((U|T)GG)",
        "X": "...",
    },
    16: {
        "B": "(A(U|T)G)",
        "L": "((C(U|T).)|((U|T)(U|T)(A|G|R))|((U|T)AG))",
        "R": "((CG.)|(AG(A|G|R)))",
        "S": "(((U|T)C.)|(AG(U|T|C|Y)))",
        "A": "(GC.)",
        "G": "(GG.)",
        "P": "(CC.)",
        "T": "(AC.)",
        "V": "(G(U|T).)",
        "I": "(A(U|T)(U|T|C|Y|A))",
        "_": "(((U|T)AA)|((T|U)GA))",
        "*": "(((U|T)AA)|((T|U)GA))",
        "C": "((U|T)G(U|T|C|Y))",
        "D": "(GA(U|T|C|Y))",
        "E": "(GA(A|G|R))",
        "F": "((U|T)(U|T)(U|T|C|Y))",
        "H": "(CA(U|T|C|Y))",
        "K": "(AA(A|G|R))",
        "N": "(AA(U|T|C|Y))",
        "Q": "(CA(A|G|R))",
        "Y": "((U|T)A(U|T|C|Y))",
        "M": "(A(U|T)G)",
        "W": "((U|T)GG)",
        "X": "...",
    },
    21: {
        "B": "((A|G|R)(U|T)G)",
        "L": "((C(U|T).)|((U|T)(U|T)(A|G|R)))",
        "R": "(CG.)",
        "S": "(((U|T)C.)|(AG.))",
        "A": "(GC.)",
        "G": "(GG.)",
        "P": "(CC.)",
        "T": "(AC.)",
        "V": "(G(U|T).)",
        "I": "(A(U|T)(U|T|C|Y))",
        "_": "((U|T)A(A|G|R))",
        "*": "((U|T)A(A|G|R))",
        "C": "((U|T)G(U|T|C|Y))",
        "D": "(GA(U|T|C|Y))",
        "E": "(GA(A|G|R))",
        "F": "((U|T)(U|T)(U|T|C|Y))",
        "H": "(CA(U|T|C|Y))",
        "K": "(AAG)",
        "N": "(AA(U|T|C|Y|A))",
        "Q": "(CA(A|G|R))",
        "Y": "((U|T)A(U|T|C|Y))",
        "M": "(A(U|T)(A|G|R))",
        "W": "((U|T)G(A|G|R))",
        "X": "...",
    },
    22: {
        "B": "(A(U|T)G)",
        "L": "((C(U|T).)|((U|T)(U|T)(A|G|R))|((T|U)AG))",
        "R": "((CG.)|(AG(A|G|R)))",
        "S": "(((U|T)C(U|T|C|Y|G))|(AG(U|T|C|Y)))",
        "A": "(GC.)",
        "G": "(GG.)",
        "P": "(CC.)",
        "T": "(AC.)",
        "V": "(G(U|T).)",
        "I": "(A(U|T)(U|T|C|Y|A))",
        "_": "((U|T)(C|A|G|R)A)",
        "*": "((U|T)(C|A|G|R)A)",
        "C": "((U|T)G(U|T|C|Y))",
        "D": "(GA(U|T|C|Y))",
        "E": "(GA(A|G|R))",
        "F": "((U|T)(U|T)(U|T|C|Y))",
        "H": "(CA(U|T|C|Y))",
        "K": "(AA(A|G|R))",
        "N": "(AA(U|T|C|Y))",
        "Q": "(CA(A|G|R))",
        "Y": "((U|T)A(U|T|C|Y))",
        "M": "(A(U|T)G)",
        "W": "((U|T)GG)",
        "X": "...",
    },
    23: {
        "B": "(((A|G|R)(U|T)G)|(A(U|T)(U|T)))",
        "L": "((C(U|T).)|((U|T)(U|T)G))",
        "R": "((CG.)|(AG(A|G|R)))",
        "S": "(((U|T)C.)|(AG(U|T|C|Y)))",
        "A": "(GC.)",
        "G": "(GG.)",
        "P": "(CC.)",
        "T": "(AC.)",
        "V": "(G(U|T).)",
        "I": "(A(U|T)(U|T|C|Y|A))",
        "_": "(((U|T)A(A|G|R))|((T|U)GA)|((T|U)(T|U)A))",
        "*": "(((U|T)A(A|G|R))|((T|U)GA)|((T|U)(T|U)A))",
        "C": "((U|T)G(U|T|C|Y))",
        "D": "(GA(U|T|C|Y))",
        "E": "(GA(A|G|R))",
        "F": "((U|T)(U|T)(U|T|C|Y))",
        "H": "(CA(U|T|C|Y))",
        "K": "(AA(A|G|R))",
        "N": "(AA(U|T|C|Y))",
        "Q": "(CA(A|G|R))",
        "Y": "((U|T)A(U|T|C|Y))",
        "M": "(A(U|T)G)",
        "W": "((U|T)GG)",
        "X": "...",
    },
}

STOP_RE = re.compile(r"(((U|T)A(A|G|R))|((T|U)GA))", re.I)


def _normalize_newlines(text):
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _split_fixed(seq, width):
    return [seq[i:i + width] for i in range(0, len(seq), width)]


def _read_nuc_sequences(nuc_paths):
    nuc_ids = []
    id_to_seq = {}
    for path in nuc_paths:
        with open(path, "r", encoding="utf-8", errors="replace") as handle:
            data = _normalize_newlines(handle.read())
        current_id = None
        for line in data.split("\n"):
            if line.startswith("#") or not line.strip():
                continue
            if line.startswith(">"):
                current_id = line[1:].split()[0]
                nuc_ids.append(current_id)
                if current_id not in id_to_seq:
                    id_to_seq[current_id] = ""
            else:
                clean = re.sub(r"[^A-Za-z]", "", line)
                if current_id is not None:
                    id_to_seq[current_id] += clean
    return nuc_ids, id_to_seq


def _detect_alignment_type(lines):
    for line in lines:
        if line.startswith("#") or not line.strip():
            continue
        if line.startswith("CLUSTAL"):
            return "clustal"
        if line.startswith(">"):
            return "fasta"
        if line.startswith("Gblocks"):
            return "gblocks"
        return "clustal"
    return "clustal"


def _read_alignment(aln_path):
    with open(aln_path, "r", encoding="utf-8", errors="replace") as handle:
        data = _normalize_newlines(handle.read())
    lines = data.split("\n")
    aln_type = _detect_alignment_type(lines)

    aaid = []
    id2aaaln = {}
    aaidcnt = {}
    gblockseq = ""

    if aln_type == "clustal":
        getblock = False
        tmplen = 0
        idspc = 0
        subalnlen = 0
        for line in lines:
            if line.startswith("CLUSTAL") or line.startswith("#"):
                continue
            if line and not line[0].isspace():
                parts = line.rstrip().split()
                if len(parts) >= 2:
                    seq_id, seq_part = parts[0], parts[1]
                    aaidcnt[seq_id] = aaidcnt.get(seq_id, 0) + 1
                    if aaidcnt[seq_id] == 1:
                        aaid.append(seq_id)
                    seq_part = seq_part.upper()
                    id2aaaln[seq_id] = id2aaaln.get(seq_id, "") + seq_part
                    tmplen = len(line.rstrip())
                    idspc = len(re.match(r"^\S+\s+", line).group(0))
                    subalnlen = len(seq_part)
                    getblock = True
                else:
                    getblock = False
            elif getblock:
                padded = line + (" " * max(0, tmplen - len(line)))
                gblockseq += padded[idspc:idspc + subalnlen]
                getblock = False
    elif aln_type == "fasta":
        current_id = None
        for line in lines:
            if line.startswith(">"):
                current_id = line[1:].split()[0]
                aaid.append(current_id)
                id2aaaln[current_id] = ""
            else:
                if current_id is None:
                    continue
                seq_part = re.sub(r"\s+", "", line).upper()
                id2aaaln[current_id] += seq_part
    elif aln_type == "gblocks":
        getaln = False
        for line in lines:
            if re.match(r"^\s+=", line):
                getaln = True
                continue
            if line.startswith("Parameters"):
                getaln = False
                continue
            if not getaln:
                continue
            parts = line.split()
            if not parts:
                continue
            if line.startswith("Gblocks"):
                if len(parts) > 1:
                    gblockseq += parts[1]
            elif line and not line[0].isspace():
                seq_id, seq_part = parts[0], parts[1]
                aaidcnt[seq_id] = aaidcnt.get(seq_id, 0) + 1
                if aaidcnt[seq_id] == 1:
                    aaid.append(seq_id)
                seq_part = seq_part.upper()
                id2aaaln[seq_id] = id2aaaln.get(seq_id, "") + seq_part

    aaseq = [id2aaaln[seq_id] for seq_id in aaid]
    return aaid, aaseq, id2aaaln, gblockseq


def _apply_frameshift(aaseq):
    out = []
    for seq in aaseq:
        seq = seq.replace("\\", "1")
        seq = re.sub(r"/(-*)[A-Z\*]", lambda m: "-" + m.group(1) + "2", seq)
        out.append(seq)
    return out


def _pn2codon(pep, nuc, codontable):
    p2c = CODON_TABLES.get(codontable)
    if not p2c:
        raise ValueError("invalid codontable")

    retval = {"message": []}
    peplen = len(pep)
    qcodon = ""

    for i in range(peplen):
        peppos = i + 1
        tmpaa = pep[i]
        if re.match(r"[ACDEFGHIKLMNPQRSTVWY_\*XU]", tmpaa):
            if not re.search(r"\w", qcodon) and tmpaa == "M":
                qcodon += p2c["B"]
            else:
                qcodon += p2c[tmpaa]
        elif tmpaa.isdigit():
            qcodon += "." * int(tmpaa)
        elif tmpaa in "-.":
            pass
        else:
            retval["message"].append(
                f"pepAlnPos {peppos}: {tmpaa} unknown AA type. Taken as 'X'")
            qcodon += p2c["X"]

    match = re.search(qcodon, nuc, re.I)
    if match:
        retval["codonseq"] = match.group(0)
        retval["result"] = 1
        return retval

    preanchor = []
    tmpanc = ""
    nanc = 0
    for i in range(peplen):
        tmpaa = pep[i]
        tmpanc += tmpaa
        if tmpaa != "-":
            nanc += 1
        if nanc == 10 or i == peplen - 1:
            preanchor.append(tmpanc)
            tmpanc = ""
            nanc = 0

    anchor = []
    if preanchor:
        lastanchorlen = len(preanchor[-1])
        if lastanchorlen < 10:
            for i in range(len(preanchor) - 1):
                if i < len(preanchor) - 2:
                    anchor.append(preanchor[i])
                else:
                    anchor.append(preanchor[i] + preanchor[i + 1])
        else:
            anchor = preanchor

    wholecodon = ""
    for i, anc in enumerate(anchor):
        anclen = len(anc)
        qcodon = ""
        fncodon = ""
        for j in range(anclen):
            peppos = i * 10 + j + 1
            tmpaa = anc[j]
            if re.match(r"[ACDEFGHIKLMNPQRSTVWY_\*XU]", tmpaa):
                if i == 0 and not re.search(r"\w", qcodon) and tmpaa == "M":
                    qcodon += "((A|C|G|R)TG)"
                else:
                    qcodon += p2c[tmpaa]
                fncodon += p2c["X"]
            elif tmpaa.isdigit():
                qcodon += "." * int(tmpaa)
                fncodon += "." * int(tmpaa)
            elif tmpaa in "-.":
                pass
            else:
                qcodon += p2c["X"]
                fncodon += p2c["X"]
        if re.search(qcodon, nuc, re.I):
            wholecodon += qcodon
        else:
            wholecodon += fncodon

    match = re.search(wholecodon, nuc, re.I)
    if not match:
        retval["result"] = -1
        return retval

    codon = match.group(0)
    codonpos = 0
    tmpnaa = 0
    for i in range(peplen):
        peppos = i + 1
        tmpaa = pep[i]
        tmpcodon = ""
        if (not tmpaa.isdigit()) and tmpaa != "-":
            tmpnaa += 1
            tmpcodon = codon[codonpos:codonpos + 3]
            codonpos += 3
            if tmpnaa == 1 and tmpaa == "M":
                if not re.search(r"((A|C|G|R)TG)", tmpcodon, re.I):
                    retval["message"].append(
                        f"pepAlnPos {peppos}: {tmpaa} does not correspond to {tmpcodon}")
            elif not re.search(p2c[tmpaa], tmpcodon, re.I):
                retval["message"].append(
                    f"pepAlnPos {peppos}: {tmpaa} does not correspond to {tmpcodon}")
        elif tmpaa.isdigit():
            tmpcodon = codon[codonpos:codonpos + int(tmpaa)]
            codonpos += int(tmpaa)

    retval["codonseq"] = codon
    retval["result"] = 2
    return retval


def _render_colored(seq, mask):
    if "R" not in mask:
        return seq
    out = []
    for c, m in zip(seq, mask):
        if m == "R":
            out.append("<FONT color='red'>" + c + "</FONT>")
        else:
            out.append(c)
    return "".join(out)


def _print_error(message, out_handle, err_handle, html):
    if html:
        out_handle.write(message)
    else:
        err_handle.write(message)


def run(aln_path, nuc_paths, out_handle, err_handle, options):
    if options.html:
        out_handle.write("<pre>\n")

    if options.outform == "codon" and (options.blockonly or options.nogap or options.nomismatch):
        msg = "\nERROR:  \"-outform codon\" is not valid with -blockonly, -nogap, -nomismatch\n\n"
        _print_error(msg, out_handle, err_handle, options.html)
        raise SystemExit(1)

    nuc_ids, id2nucseq = _read_nuc_sequences(nuc_paths)
    aaid, aaseq, id2aaaln, gblockseq = _read_alignment(aln_path)
    aaseq = _apply_frameshift(aaseq)

    if len(aaid) != len(nuc_ids):
        naa = len(aaid)
        nnuc = len(nuc_ids)
        msg = f"\nERROR: number of input seqs differ (aa: {naa};  nuc: {nnuc})!!\n\n"
        if options.html:
            out_handle.write(msg)
        else:
            err_handle.write(msg)
            err_handle.write(f"   aa  '{' '.join(aaid)}'\n")
            err_handle.write(f"   nuc '{' '.join(nuc_ids)}'\n")
        raise SystemExit(1)

    common_ids = [nid for nid in nuc_ids if nid in set(aaid)]
    idcorrespondence = "sameID" if len(common_ids) == len(aaid) else "ordered"

    codonseq = []
    aaidpos2mismatch = {}
    outmessage = []

    for i, aaid_item in enumerate(aaid):
        if idcorrespondence == "sameID":
            tmpnucid = aaid_item
        elif idcorrespondence == "ordered":
            tmpnucid = nuc_ids[i]
        else:
            _print_error("\nERROR in ID correspondence.\n\n", out_handle, err_handle, options.html)
            raise SystemExit(1)

        codonout = _pn2codon(aaseq[i], id2nucseq.get(tmpnucid, ""), options.codontable)
        for message in codonout.get("message", []):
            outmessage.append(f"WARNING: {aaid_item} {message}")
            parts = message.split()
            if len(parts) >= 2:
                pos = parts[1].rstrip(":")
                aaidpos2mismatch[f"{aaid_item} {pos}"] = 1

        if codonout.get("result") in (1, 2):
            codonseq.append(codonout.get("codonseq", ""))
        else:
            erraa = aaseq[i].replace("-", "")
            erraafrags = _split_fixed(erraa, 60)
            erraa = "\n".join(erraafrags)

            errnuc = id2nucseq.get(tmpnucid, "").replace("-", "")
            errnucfrags = _split_fixed(errnuc, 60)
            errnuc = "\n".join(errnucfrags)

            if options.html:
                out_handle.write("</pre>\n")
                out_handle.write("<H1>ERROR in your input files!</H1>\n")
                out_handle.write("<pre>\n")
                out_handle.write("#---  ERROR: inconsistency between the following pep and nuc seqs  ---#\n")
                out_handle.write(f">{aaid_item}\n{erraa}\n")
                out_handle.write(f">{tmpnucid}\n{errnuc}\n")
                out_handle.write("</pre>\n")
            else:
                err_handle.write("#---  ERROR: inconsistency between the following pep and nuc seqs  ---#\n")
                err_handle.write(f">{aaid_item}\n{erraa}\n")
                err_handle.write(f">{tmpnucid}\n{errnuc}\n")

            if sys.platform.startswith("linux"):
                if shutil.which("bl2seq"):
                    if options.html:
                        erraafile = tempfile.mkstemp(prefix="erraafile.", text=True)[1]
                        errnucfile = tempfile.mkstemp(prefix="errnucfile.", text=True)[1]
                        tblnout = tempfile.mkstemp(prefix="tbln.out.", text=True)[1]
                    else:
                        erraafile = tempfile.mkstemp(prefix="erraafile.", text=True)[1]
                        errnucfile = tempfile.mkstemp(prefix="errnucfile.", text=True)[1]
                        tblnout = tempfile.mkstemp(prefix="tbln.out.", text=True)[1]

                    with open(erraafile, "w", encoding="utf-8") as fp:
                        fp.write(f">{aaid_item}\n{erraa}\n")
                    with open(errnucfile, "w", encoding="utf-8") as fp:
                        fp.write(f">{tmpnucid}\n{errnuc}\n")

                    subprocess.run(
                        ["bl2seq", "-p", "tblastn", "-F", "F", "-i", erraafile, "-j", errnucfile, "-o", tblnout],
                        check=False,
                    )

                    if options.html:
                        out_handle.write("<BR>\n<BR>\n")
                        out_handle.write("<H1>Check the following TBLASTN output.</H1><BR>\n<pre>\n")
                        out_handle.write("      your pep -> 'Query'\n")
                        out_handle.write("      your nuc -> 'Sbjct'\n<BR>\n")
                    else:
                        err_handle.write("\n\n")
                        err_handle.write("        ###-----   Check the following TBLASTN output:           -----###\n")
                        err_handle.write("        ###-----       your pep -> 'Query'                       -----###\n")
                        err_handle.write("        ###-----       your nuc -> 'Sbjct'                       -----###\n")
                        err_handle.write("\n")

                    with open(tblnout, "r", encoding="utf-8", errors="replace") as fp:
                        tblnoutdata = _normalize_newlines(fp.read())
                    for line in tblnoutdata.split("\n"):
                        if options.html:
                            out_handle.write(line + "\n")
                        else:
                            err_handle.write(line + "\n")

                    if options.html:
                        out_handle.write("</pre>\n")

                    for path in (erraafile, errnucfile, tblnout):
                        try:
                            os.unlink(path)
                        except OSError:
                            pass
                else:
                    msg = "\n\nRun bl2seq (-p tblastn) or GeneWise to see the inconsistency.\n\n"
                    _print_error(msg, out_handle, err_handle, options.html)
            else:
                msg = "\n\nRun bl2seq (-p tblastn) or GeneWise to see the inconsistency.\n\n"
                _print_error(msg, out_handle, err_handle, options.html)

            raise SystemExit(1)

    if gblockseq and "#" in gblockseq and options.blockonly:
        new_outmessage = []
        for msg in outmessage:
            parts = msg.split()
            if len(parts) >= 4:
                mpos = parts[3].rstrip(":")
                try:
                    idx = int(mpos) - 1
                except ValueError:
                    continue
                if idx >= 0 and idx < len(gblockseq) and gblockseq[idx] == "#":
                    new_outmessage.append(msg)
        outmessage = new_outmessage

    if options.codontable != 1:
        outmessage.insert(0, f"Codontable {options.codontable} is used")

    if not options.nostderr:
        for j, msg in enumerate(outmessage):
            if options.html:
                if j == 0 and not options.nomismatch:
                    out_handle.write("#------------------------------------------------------------------------#\n")
                if not options.nomismatch:
                    out_handle.write(f"#  {msg}\n")
                if j == len(outmessage) - 1 and not options.nomismatch:
                    out_handle.write("#------------------------------------------------------------------------#\n\n")
            else:
                if j == 0 and not options.nomismatch:
                    err_handle.write("#------------------------------------------------------------------------#\n")
                    err_handle.write(f"#  Input files:  {aln_path} {' '.join(nuc_paths)}\n")
                if not options.nomismatch:
                    err_handle.write(f"#  {msg}\n")
                if j == len(outmessage) - 1 and not options.nomismatch:
                    err_handle.write("#------------------------------------------------------------------------#\n\n")

    errorpos = {}
    for msg in outmessage:
        parts = msg.split()
        if len(parts) >= 4:
            tmperrpos = parts[3].rstrip(":")
            try:
                errorpos[int(tmperrpos) - 1] = 1
            except ValueError:
                continue

    tmppos = [0] * len(aaid)
    codonaln = ["" for _ in aaid]
    coloraln = ["" for _ in aaid]
    maskseq = ""

    aln_len = len(aaseq[0]) if aaseq else 0
    for i in range(aln_len):
        tmpmax = 0
        apos = i + 1

        putcodon = 1
        if gblockseq and "#" in gblockseq and i < len(gblockseq):
            if gblockseq[i] != "#" and options.blockonly:
                putcodon = 0
        if options.nomismatch and errorpos.get(i):
            putcodon = 0

        for seq in aaseq:
            tmpaa = seq[i]
            if not tmpaa.isdigit():
                tmplen = 3
            else:
                tmplen = (int((int(tmpaa) - 1) / 3) + 1) * 3
            if tmpmax < tmplen:
                tmpmax = tmplen

        for k, seq in enumerate(aaseq):
            tmpaa = seq[i]
            mismatch = aaidpos2mismatch.get(f"{aaid[k]} {apos}")
            if not tmpaa.isdigit():
                if tmpaa == "-":
                    if putcodon:
                        codonaln[k] += "-" * tmpmax
                        coloraln[k] += ("R" * tmpmax) if mismatch else ("-" * tmpmax)
                elif re.match(r"[A-Z\*]", tmpaa):
                    if putcodon:
                        codonaln[k] += codonseq[k][tmppos[k]:tmppos[k] + 3]
                        coloraln[k] += "RRR" if mismatch else "---"
                    tmppos[k] += 3
                    if putcodon:
                        pad = tmpmax - 3
                        if pad > 0:
                            codonaln[k] += "-" * pad
                            coloraln[k] += ("R" * pad) if mismatch else ("-" * pad)
            else:
                if putcodon:
                    codonaln[k] += codonseq[k][tmppos[k]:tmppos[k] + int(tmpaa)]
                    coloraln[k] += ("R" * int(tmpaa)) if mismatch else ("-" * int(tmpaa))
                tmppos[k] += int(tmpaa)
                if putcodon:
                    pad = tmpmax - int(tmpaa)
                    if pad > 0:
                        codonaln[k] += "-" * pad
                        coloraln[k] += ("R" * pad) if mismatch else ("-" * pad)

        if not options.blockonly and putcodon:
            if gblockseq and "#" in gblockseq and i < len(gblockseq) and gblockseq[i] == "#":
                maskseq += "#" * tmpmax
            else:
                maskseq += " " * tmpmax

    if options.nogap:
        alilen = len(codonaln[0]) if codonaln else 0
        tmppos = 0
        nogapaln = ["" for _ in codonaln]
        nogapcoloraln = ["" for _ in codonaln]
        nogapmaskseq = ""
        while tmppos < alilen:
            outok = 1
            for row in codonaln:
                tmpcodon = row[tmppos:tmppos + 3]
                if "-" in tmpcodon:
                    outok = 0
                if STOP_RE.search(tmpcodon):
                    outok = 0
            if outok:
                for i in range(len(codonaln)):
                    tmpcodon = codonaln[i][tmppos:tmppos + 3]
                    nogapaln[i] += tmpcodon
                    tmpcolor = coloraln[i][tmppos:tmppos + 3]
                    nogapcoloraln[i] += tmpcolor
                nogapmaskseq += maskseq[tmppos:tmppos + 3]
            tmppos += 3
        codonaln = nogapaln
        coloraln = nogapcoloraln
        maskseq = nogapmaskseq

    maxn = max([len(x) for x in aaid] + [10])
    alilen = len(codonaln[0]) if codonaln else 0

    aaid2codonarr = {seq_id: _split_fixed(codonaln[i], 60) for i, seq_id in enumerate(aaid)}
    aaid2colorarr = {seq_id: _split_fixed(coloraln[i], 60) for i, seq_id in enumerate(aaid)}
    maskarr = _split_fixed(maskseq, 60)

    if options.outform == "clustal":
        out_handle.write("CLUSTAL W multiple sequence alignment\n\n")
        output1 = aaid2codonarr[aaid[0]] if aaid else []
        for i in range(len(output1)):
            for seq_id in aaid:
                out_handle.write(f"{seq_id:<{maxn}}    ")
                outf = aaid2codonarr[seq_id][i]
                outr = aaid2colorarr[seq_id][i]
                if options.html:
                    out_handle.write(_render_colored(outf, outr) + "\n")
                else:
                    out_handle.write(outf + "\n")
            if not options.blockonly and gblockseq and "#" in gblockseq:
                outmask = maskarr[i] if i < len(maskarr) else ""
                out_handle.write(f"{'':<{maxn}}    {outmask}\n")
            out_handle.write("\n")

    elif options.outform == "codon":
        outaa = []
        withn = any(re.search(r"\d", seq) for seq in aaseq)
        if withn:
            alnlen = len(aaseq[0]) if aaseq else 0
            for i in range(alnlen):
                maxaan = 0
                for seq in aaseq:
                    tmpaa = seq[i]
                    if tmpaa.isdigit() and int(tmpaa) > maxaan:
                        maxaan = int(tmpaa)
                if maxaan >= 4:
                    tmplen = int((maxaan - 1) / 3) + 1
                else:
                    tmplen = 1
                for j, seq in enumerate(aaseq):
                    if len(outaa) <= j:
                        outaa.append("")
                    pushaa = "-" * tmplen
                    tmpaa = seq[i]
                    pushaa = tmpaa + pushaa[1:]
                    outaa[j] += pushaa
        else:
            outaa = list(aaseq)

        aaid2aaarr = {seq_id: _split_fixed(outaa[i], 20) for i, seq_id in enumerate(aaid)}
        output1 = aaid2codonarr[aaid[0]] if aaid else []
        for i in range(len(output1)):
            for seq_id in aaid:
                out_handle.write(f"{'':<{maxn}}    ")
                outa = aaid2aaarr[seq_id][i]
                outa = "   ".join(_split_fixed(outa, 1))

                outf = aaid2codonarr[seq_id][i]
                outf = " ".join(_split_fixed(outf, 3))

                outr = aaid2colorarr[seq_id][i]
                outr = " ".join(_split_fixed(outr, 3))

                if options.html:
                    if "R" in outr:
                        rlen = len(outf)
                        line = []
                        for l in range(rlen):
                            tmppep = outa[l]
                            tmpr = outr[l]
                            if tmpr == "R":
                                line.append("<FONT color='red'>" + tmppep + "</FONT>")
                            else:
                                line.append(tmppep)
                        out_handle.write("".join(line) + "\n")
                        out_handle.write(f"{seq_id:<{maxn}}    ")
                        line = []
                        for l in range(rlen):
                            tmpnuc = outf[l]
                            tmpr = outr[l]
                            if tmpr == "R":
                                line.append("<FONT color='red'>" + tmpnuc + "</FONT>")
                            else:
                                line.append(tmpnuc)
                        out_handle.write("".join(line) + "\n")
                    else:
                        out_handle.write(outa + "\n")
                        out_handle.write(f"{seq_id:<{maxn}}    {outf}\n")
                else:
                    out_handle.write(outa + "\n")
                    out_handle.write(f"{seq_id:<{maxn}}    {outf}\n")

            if not options.blockonly and gblockseq and "#" in gblockseq:
                outmask = maskarr[i] if i < len(maskarr) else ""
                outmask = outmask.replace(" ", "-")
                outmask = " ".join(_split_fixed(outmask, 3))
                outmask = outmask.replace("-", " ")
                out_handle.write(f"{'':<{maxn}}    {outmask}\n")
            out_handle.write("\n")

    elif options.outform == "paml":
        nseq = len(aaid)
        out_handle.write(f" {nseq:3d} {alilen:6d}\n")
        for seq_id in aaid:
            out_handle.write(f"{seq_id}\n")
            if options.html:
                for outf, outr in zip(aaid2codonarr[seq_id], aaid2colorarr[seq_id]):
                    out_handle.write(_render_colored(outf, outr) + "\n")
            else:
                out_handle.write("\n".join(aaid2codonarr[seq_id]) + "\n")

    elif options.outform == "fasta":
        for seq_id in aaid:
            out_handle.write(f">{seq_id}\n")
            if options.html:
                for outf, outr in zip(aaid2codonarr[seq_id], aaid2colorarr[seq_id]):
                    out_handle.write(_render_colored(outf, outr) + "\n")
            else:
                out_handle.write("\n".join(aaid2codonarr[seq_id]) + "\n")

    if options.html:
        out_handle.write("</pre>\n")


def build_parser():
    parser = argparse.ArgumentParser(
        description="pal2nal - Convert a protein alignment and nucleotide sequences into a codon alignment",
        add_help=False,
    )
    parser.add_argument("pep_aln")
    parser.add_argument("nuc_fasta", nargs="+")
    parser.add_argument("-h", action="help", help="Show help")
    parser.add_argument("-output", dest="outform", choices=["clustal", "paml", "fasta", "codon"],
                        default="clustal", help="Output format; default = clustal")
    parser.add_argument("-blockonly", action="store_true", help="Show only user specified blocks")
    parser.add_argument("-nogap", action="store_true", help="Remove columns with gaps and inframe stop codons")
    parser.add_argument("-nomismatch", action="store_true", help="Remove mismatched codons")
    parser.add_argument("-codontable", type=int, choices=sorted(CODON_TABLES.keys()), default=1,
                        help="Codon table number")
    parser.add_argument("-html", action="store_true", help="HTML output")
    parser.add_argument("-nostderr", action="store_true", help="No STDERR messages")
    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    run(args.pep_aln, args.nuc_fasta, sys.stdout, sys.stderr, args)


if __name__ == "__main__":
    main()
