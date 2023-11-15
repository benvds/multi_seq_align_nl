import constants.constants_basiscript as constants

"""
Gets the aligned target and original word as a string. 
It calculates the phonemes of the target word and aligns this with the target and original pcu's.
Output is a list, consisting of 1 list with the phonemens of the target word, 1 list with the target pcu's
and 1 list with the original pcu's. 
"""
def computePCUs(target_adapt, orignal_adapt, target_adapt_align, target_graph_align, zero_char):

    target = target_adapt.replace(zero_char, "").lower()

    target_phon_list = []
    target_pcu_list = []
    original_pcu_list = []

    # Get corresponding phonetic data from lexicon
    # try:
    # target_adapt_align = lexicon.loc[target, "graphemes_align"]
    # target_graph_align = lexicon.loc[target, "phonemes_align"]
    # except:
    #     target_adapt_align = ["NaN"]
    #     target_graph_align = ["NaN"]

    if len(target_adapt_align) == 0 or target_adapt_align[0] == "NaN":
        target_phon_list.append("NaN")
        target_pcu_list.append("NaN")
        original_pcu_list.append("NaN")

    # Align original with target graphemes and phonemes
    else:
        
        # Get indices of insertions of two phoneme strings
        indices_insertions = [i for i, x in enumerate(target_adapt) if x == zero_char]

        # Add insertions to target_adapt_align and target_graph_align
        for i in indices_insertions:
            target_adapt_align, target_graph_align = add_insertion_to_graph_align(target_adapt_align, target_graph_align, i, zero_char)

        indices_not_written_phonemes = []
        for i in range(len(target_adapt_align)):
            if target_adapt_align[i] == zero_char and target_graph_align[i] != zero_char:
                indices_not_written_phonemes.append(len("".join(target_adapt_align[:i])))

        # Map target_adapt_align boundaries onto the original
        spans = get_pcu_boundaries(target_adapt_align)
        original_graph_align, target_adapt_align, target_graph_align = set_pcu_boundaries(orignal_adapt, target_adapt_align, target_graph_align, spans, indices_not_written_phonemes, zero_char)

        # # For each insertion, determine whether it belongs to the PCU after it
        # mergeList = set()
        # length = min(len(target_adapt_align), len(original_graph_align))
        # for i in range(length):
        #     if target_adapt_align[i] in [zero_char, constants.place_holder_char] and original_graph_align[i] not in [zero_char, constants.place_holder_char]:
        #         pcu = original_graph_align[i].replace(zero_char, "")
        #         pcu_before = ""
        #         pcu_after = ""
                
        #         if i!= 0:
        #             pcu_before = original_graph_align[i-1].replace(zero_char, "")
                
        #         if i != len(original_graph_align)-1:
        #             pcu_after = original_graph_align[i+1].replace(zero_char, "")
                
        #         combination_before = pcu_before + pcu
        #         combination_after = pcu + pcu_after
        #         if combination_before != pcu and combination_before in constants.pcus:
        #             mergeList.update([(i-1, i)])
        #         if combination_after != pcu and combination_after in constants.pcus:
        #             mergeList.update([(i, i+1)])
        
        # mergeList = sorted(list(mergeList))

        # # For each insertion, apply merging if necessary
        # for i in reversed(range(len(mergeList))):
        #     original_graph_align = combine_pcus(original_graph_align, mergeList[i])
        #     target_adapt_align   = combine_pcus(target_adapt_align, mergeList[i])
        #     target_graph_align    = combine_pcus(target_graph_align, mergeList[i])

        # Remove "-" if necessary
        target_graph_align = [x.replace(zero_char, "") for x in target_graph_align]
        target_graph_align = [zero_char if x == "" else x for x in target_graph_align]
        target_graph_align = [x.replace(constants.place_holder_char, zero_char) for x in target_graph_align]
        target_graph_align = [x.replace(" ", zero_char) for x in target_graph_align]

        target_adapt_align = [x.replace(zero_char, "") for x in target_adapt_align]
        target_adapt_align = [x.replace(constants.place_holder_char, zero_char) for x in target_adapt_align]
        target_adapt_align = [zero_char if x == "" else x for x in target_adapt_align]

        original_graph_align = [x.replace(zero_char, "") for x in original_graph_align]
        original_graph_align = [zero_char if x == "" else x for x in original_graph_align]

        target_graph_align, target_adapt_align, original_graph_align  = remove_redundant_wordboundaries(target_graph_align, target_adapt_align, original_graph_align, zero_char)
        
        # Append outcomes to lists
        target_phon_list.append(target_graph_align)
        target_pcu_list.append(target_adapt_align)
        original_pcu_list.append(original_graph_align)

    return target_phon_list, target_pcu_list, original_pcu_list

"""
This function adds an insertion ("-") at a specific index in the list.
graphemes_align  Premilinary list of target constants.pcus
idx_char          Index for insertion
"""
def add_insertion_to_graph_align(graphemes_align, phonemes_align, idx_char, zero_char):
    if idx_char == 0:
        return [zero_char] + graphemes_align, [zero_char] + phonemes_align 
    
    total_l = 0

    for i in range(len(graphemes_align)):
        l = len(graphemes_align[i])
        total_l += l
    
        if total_l >= idx_char and i+1 == len(graphemes_align):
            before = graphemes_align[: i+1]
            before_phon = phonemes_align[: i+1]
            return before + [zero_char], before_phon + [zero_char]
        elif total_l >= idx_char and graphemes_align[i+1] != zero_char:
            before = graphemes_align[: i+1]
            after = graphemes_align[i+1:]
            before_phon = phonemes_align[: i+1]
            after_phon = phonemes_align[i+1:]
            return before + [zero_char] + after, before_phon + [zero_char] + after_phon
        elif total_l >= idx_char and graphemes_align[i+1] == zero_char and phonemes_align[i+1] == zero_char:
            before = graphemes_align[: i+1]
            after = graphemes_align[i+2:]
            before_phon = phonemes_align[: i+1]
            after_phon = phonemes_align[i+2:]
            return before + [constants.place_holder_char] + after, before_phon + [constants.place_holder_char] + after_phon
        elif total_l >= idx_char and graphemes_align[i+1] == zero_char and phonemes_align[i+1] != zero_char:
            before = graphemes_align[: i+1]
            after = graphemes_align[i+2:]
            before_phon = phonemes_align[: i+1]
            after_phon = phonemes_align[i+1:]
            return before + [constants.place_holder_char] + after, before_phon + after_phon
    return graphemes_align, phonemes_align

"""
This function obtains the preliminary pcu boundaries from the target.
graphemes_align  Premilinary list of target constants.pcus
"""
def get_pcu_boundaries(graphemes_align):
    begin = 0
    end = 0
    span_list = []
    for i in range(len(graphemes_align)):
        l = len(graphemes_align[i])
        end += l
        span = [begin, end]
        span_list.append(span)
        begin = end

    return span_list

"""
This function projects the target boundaries onto the original.
original               Original transcription
spans                  PCU indexes from target
phon_not_written_idxs  Indexes at which ("-") should be added (in case of not written phoneme)
"""
def set_pcu_boundaries(orignal_adapt, target_adapt, target_graph_align, spans, phon_not_written_idxs, zero_char):

    # Add "-" to original at phon_not_written idxs
    for i in phon_not_written_idxs:
        if i < len(orignal_adapt):
            if orignal_adapt[i] != zero_char:
                orignal_adapt = orignal_adapt[:i] + zero_char + orignal_adapt[i:]
        else: 
            orignal_adapt = orignal_adapt + zero_char

    # Split original into constants.pcus
    original_graph_align_list = []
    for span in spans:
        part = orignal_adapt[span[0]: span[1]]
        if part.replace(zero_char, '').lower() in constants.pcus:
            original_graph_align_list.append(part)
        
        # If the part is not a pcu, add its pieces to the list and add hyphens to the target lists to compensate for this
        else: 
            for character in part:
                original_graph_align_list.append(character)

            span_list = list(range(span[0], span[1]))
            for i in span_list[1:]:
                target_adapt = target_adapt[:i] + [zero_char] + target_adapt[i:]
                target_graph_align = target_graph_align[:i] + [zero_char] + target_graph_align[i:]
                
    return original_graph_align_list, target_adapt, target_graph_align


"""
This function pastes two constants.pcus together to form one pcu.
graph_align      Preliminary list of original/target constants.pcus
index_type_tuple Tuple containing type of paste and index of char to paste
"""
def combine_pcus(graph_align, index_tuple):
    index1 = index_tuple[0]
    index2 = index_tuple[1]

    before = graph_align[:index1]
    after = graph_align[index2+1:]
    new = [graph_align[index1]+graph_align[index2]]
    
    return before + new + after

"""
Remove wordboundary character (*) if it is inserted at the same index for all three variables
"""
def remove_redundant_wordboundaries(target_phonemes, target_graphemes, original_graphemes, zero_char):
    indices_to_remove = []
    length = min(len(target_phonemes), len(target_graphemes), len(original_graphemes))
    for i in range(length-1):
        if target_phonemes[i] == target_graphemes[i] == original_graphemes[i] == zero_char:
            indices_to_remove.append(i)

    for index in reversed(indices_to_remove):
        target_phonemes = target_phonemes[:index] + target_phonemes[index+1:]
        target_graphemes = target_graphemes[:index] + target_graphemes[index+1:]
        original_graphemes = original_graphemes[:index] + original_graphemes[index+1:]
    return target_phonemes, target_graphemes, original_graphemes