# How the Corpus is Created

## Tag Format

Given an machine translated sentence and a source sentence, the corpus consists
of two sets of tags. 

* Target-side tags which have `2*N+1` entries for a machine translated sentence of `N` words.

* Source-side tags, one for each word in the sentence

Target side tags aim at addressing fluency errors, including omission errors.
To account for one or more words missing between the existing machine
translated words, gaps are considered after each word and at the beginning of
the sentence. This accounts for the `N+1` extra slots.

Source side tags aim at addressing adequacy errors by highlighting words in the
source that are related to inconsistencies on the target side.

## How the tags are computed

Similarly to past WMT editions, post-edited text is taken as reference, and
edit distance alignment (tercom) is used to align machine translated text with
post edited text. From the alignments, insertions and substitutions on MT are
marked as BAD tags over the words. Deletions are marked as BAD tags over the
gaps. 

Using alignments between MT and PE (tercom) and source PE (SimAlign), target
side BAD tags are propagated back to the source to signal words that are
related to the error. Three version were considered in this freest version of
the corpus. These can be selected inside of the `get_tags*` scripts using the
variable `$fluency_rule`.

- `normal` all BAD tokens are propagated to their aligned words
- `ignore-shift-set` if a BAD token appears also in PE do not propagate to source
- `missing-only` only propagate for missing words (deletions)

Default setting used was `normal`.


