# How the Corpus is Created

## Tag Format

Given an machine translated sentence and a source sentence, the corpus consists
of two sets of tags. 

* Target-side tags wich have `2*N+1` entries for a machine translated sentence of `N` words.

* Source-side tags, one for each word in the sentence

Target side tags aim at adressing fluency errors, including ommission errors.
To account for one or more words missing between the existing machine
translated words, gaps are considered after each word and at the begining of
the sentence. This accounts for the `N+1` extra slots.

Source side tags aim at adressing adequacy errors by higlighting words in the
source that are related to inconsistencies on the target side.


## How the tags are computed

Similarly to past WMT editions, post-edited text is taken as reference, and
edit distance alignment (tercom) is used to align machine translated text with
post edited text. From the alignments, insertions and substituions on MT are
marked as BAD tags over the words. Deletions are marked as BAD tags over the
gaps. 

Using alignments between MT and PE (tercom) and source PE (fast_align), BAD
tags are propagated back to the source. The only exception is if a word is
missing on the MT on the expected position (per tercom) but is present
otherwhere on the MT sentence. This is considered a fluency problem rather than
adequacy.

