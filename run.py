import argparse
import pandas as pd
import os
import glob
import re

# ADAPT
import alignment_adapt.run_adapt as run_adapt
import alignment_adapt.cgn2_adapt_map as cgn2_adapt_map
import alignment_adapt.deduce_pcus_orig_phon as deduce_pcus

#ADAGT
import alignment_adagt.adagt as adagt
import alignment_adagt.deduce_pcus_orig_graph as deduce_pcus_graph

# APGA 
import alignment_graph_phon.graph_phon_alignment as gpa


def run(args):

    # Get alignment type
    alignmentType = args.type
    assert alignmentType in ['adapt', 'adagt', 'apga', 'multi_phon', 'multi_graph'], "choose for the variable \'type\' from the values \'adapt\', \'adagt\', \'apga\'or \'multi\'" 

    target_graph = args.target_graphemes
    target_phon = args.target_phonemes
    realised_graph = args.realised_graphemes
    realised_phon = args.realised_phonemes

    print("INPUTS")
    print("target_graphemes: ", target_graph)
    print("target_phonemes: ", target_phon)
    print("realised_graphemes: ", realised_graph)
    print("realised_phonemes: ", realised_phon)

    if(alignmentType == 'adapt'):

        assert target_graph != None and realised_graph != None, "To use type \"adapt\" both \"target_graph\" and \"realised_graph\" need to be specified."

        # ADAPT uses '-' for ins/del
        align_target_phon_cgn2, align_realised_phon_cgn2, align_target_phon_adapt, align_realised_phon_adapt = run_adapt.reverse_align_two_phone_strings(target_phon, realised_phon)
        
        print("OUTPUTS in CGN2 CPA")
        print(align_target_phon_cgn2)
        print(align_realised_phon_cgn2)

        print("OUTPUTS in ADAPT CPA")
        print(align_target_phon_adapt)
        print(align_realised_phon_adapt)

    elif(alignmentType == 'adagt'):

        assert target_phon != None and realised_phon != None, "To use type \"adapt\" both \"target_phonemes\" and \"realised_phonemes\" need to be specified."
    
        align_target_graph, align_realised_graph = adagt.align(target_phon, realised_phon)
        
        print("OUTPUTS")
        print(align_target_graph)
        print(align_realised_graph)

    elif(alignmentType == 'apga'):

        assert target_graph != None and target_phon != None, "To use type \"apga\" both \"target_graph\" and \"target_phon\" need to be specified."

        pcu_target_graph, pcu_target_phon = gpa.align_word_and_phon_trans(target_graph, target_phon)

        print(pcu_target_graph, pcu_target_phon)

    elif(alignmentType == 'multi_graph'):

        assert target_graph != None and realised_graph != None and target_phon != None, "To use type \"multi\" both \"target_graph\", \"realised_graph\" and \"target_phon\" need to be specified."

        # ADAGT
        align_target_graph, align_realised_graph = adagt.align(target_graph, realised_graph)

        # APGA
        pcu_target_graph, pcu_target_phon = gpa.align_word_and_phon_trans(target_graph, target_phon)

        # Combine output alignments from ADAGT and APGA
        multi_target_phon, multi_target_graph, multi_realised_graph = deduce_pcus_graph.computePCUs(align_target_graph, align_realised_graph, pcu_target_graph, pcu_target_phon, '*')

        print(multi_target_phon, multi_target_graph, multi_realised_graph)
        
    elif(alignmentType == 'multi_phon'):

        assert target_graph != None and target_phon != None, "To use type \"multi\" both \"target_graph\", \"realised_graph\" and \"target_phon\" need to be specified."

        # ADAPT alignment
        align_target_phon_cgn2, align_realised_phon_cgn2, align_target_phon_adapt, align_realised_phon_adapt = run_adapt.reverse_align_two_phone_strings(target_phon, realised_phon)

        # APGA alignment
        pcu_target_graph, pcu_target_phon = gpa.align_word_and_phon_trans(target_graph, target_phon)

        # Combine output alignments from ADAPT and APGA
        multi_target_graph, multi_target_phon_adapt, multi_realised_phon_adapt = deduce_pcus.computePCUs(align_target_phon_adapt, align_realised_phon_adapt, pcu_target_graph, pcu_target_phon, '-')

        # Postprocess
        multi_target_phon_cgn2 = [cgn2_adapt_map.adapt_to_cgn2_dict[phone] for phone in multi_target_phon_adapt[0]]
        multi_realised_phon_cgn2 = [cgn2_adapt_map.adapt_to_cgn2_dict[phone] for phone in multi_realised_phon_adapt[0]]

        print(multi_target_graph, multi_target_phon_cgn2, multi_realised_phon_cgn2)


def main():
    parser = argparse.ArgumentParser("Message")
    parser.add_argument("--type", type=str, help = "Choose your type of alignment: adapt, adagt, apga or multi")
    parser.add_argument("--target_graphemes", type=str, help = "A string containing the target (correct) transcription. This is a grapheme string.")
    parser.add_argument("--target_phonemes", type=str, help = "A string containing the CGN2 phonetic transcription of the grapheme transcription of the target, specified in \'target_graphemes\', e.g. \"k EI k @\" ")
    parser.add_argument("--realised_graphemes", type=str, help = "A string containing The realised (incorrect) grapheme transcription. This is a grapheme string.")
    parser.add_argument("--realised_phonemes", type=str, help = "A string containing the CGN2 phonetic transcription of the (incorrect) realised transcription. ")
    parser.set_defaults(func=run)
    args = parser.parse_args()
    args.func(args)   

if __name__ == "__main__": 
    main()