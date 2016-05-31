#!/usr/bin/env python
"""Library for calling variants
"""
import sys
import os
import glob
from random import shuffle
from serviceCourse.parsers import read_fasta
from serviceCourse.sequenceTools import reverse_complement


def randomly_select_alignments(path_to_alignments, max_alignments_to_use):
    alignments = [x for x in glob.glob(path_to_alignments) if os.stat(x).st_size != 0]
    if len(alignments) == 0:
        print("[error] Didn't find any alignment files here {}".format(path_to_alignments))
        sys.exit(1)

    shuffle(alignments)

    if len(alignments) < max_alignments_to_use:
        return alignments
    else:
        return alignments[:max_alignments_to_use]


def get_forward_mask(list_of_alignments, suffix):
    mask = []
    for alignment in list_of_alignments:
        if alignment.endswith(".backward.tsv{}".format(suffix)):
            mask.append(False)
        else:
            mask.append(True)
    return mask


def get_alignments_labels_and_mask(path_to_alignments, max, suffix=""):
    alignments = randomly_select_alignments(path_to_alignments, max)
    mask = get_forward_mask(alignments, suffix)
    return alignments, mask


def get_reference_sequence(path_to_fasta):
    seqs = []

    for header, comment, sequence in read_fasta(path_to_fasta):
        seqs.append(sequence)

    assert len(seqs) > 0, "Didn't find any sequences in the reference file"

    if len(seqs) > 1:
        print("[NOTICE] Found more than one sequence in the reference file, using the first one")

    return seqs[0]


def make_degenerate_reference(input_fasta, start, forward_sequence_path, backward_sequence_path,
                              block_size=1, step=6):
    """
    input_sequence: string, input nucleotide sequence
    out_path: string, path to directory to put new sequences with substituted degenerate characters
    block_size: not implemented
    step: number of bases between degenerate characters
    :return (subbed sequence, complement subbed sequence)
    """

    input_sequence = ""
    for header, comment, sequence in read_fasta(input_fasta):
        input_sequence += sequence
        break

    complement_sequence = reverse_complement(dna=input_sequence, reverse=False, complement=True)

    t_seq = list(input_sequence)
    c_seq = list(complement_sequence)

    positions = xrange(start, len(input_sequence), step)
    for position in positions:
        t_seq[position] = "X"
        c_seq[position] = "X"

    t_seq = ''.join(t_seq)
    c_seq = ''.join(c_seq)

    sequence_length = len(t_seq)

    with open(forward_sequence_path, 'w') as f:
        f.write("{seq}".format(seq=t_seq))
    with open(backward_sequence_path, 'w') as f:
        f.write("{seq}".format(seq=c_seq))

    return True, sequence_length
