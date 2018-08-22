import codecs
import os


def read_raw(file_path):
    with codecs.open(file_path, 'r', 'utf-8') as fid:
        sids = []
        source_sents = []
        mt_sents = []
        pe_sents = []
        ref_sents = []
        for line in fid.readlines():
            sid, source_sent, mt_sent, pe_sent, ref_sent = line.split('\t')[:5]
            # Append
            sids.append(sid)
            source_sents.append(source_sent)
            mt_sents.append(mt_sent)
            pe_sents.append(pe_sent)
            ref_sents.append(ref_sent)

    return sids, source_sents, mt_sents, pe_sents, ref_sents


def write_file(file_path, sentences):
    with codecs.open(file_path, 'w', 'utf-8') as fid:
        for sent in sentences:
            fid.write('%s\n' % sent)


def idsort(sentences, ids, target_ids):
    sents_by_id = {id: sent for id, sent in zip(ids, sentences)}
    return [sents_by_id[id] for id in target_ids]


def convert_corpus(raw_file, out_folder, label):
    sids, src_sents, mt_sents, pe_sents, ref_sents = read_raw(raw_file)
    save_corpus(out_folder, src_sents, mt_sents, pe_sents, ref_sents, label)


def save_corpus(out_folder, src_sents, mt_sents, pe_sents, ref_sents, label):
    # Create
    if not os.path.isdir(out_folder):
        os.makedirs(out_folder)
    # Write files
    write_file('%s/%s.src' % (out_folder, label), src_sents)
    write_file('%s/%s.mt' % (out_folder, label), mt_sents)
    write_file('%s/%s.pe' % (out_folder, label), pe_sents)
    write_file('%s/%s.ref' % (out_folder, label), ref_sents)
    print('%s -> %s' % (raw_file, out_folder))


if __name__ == '__main__':

    # Language_pair.engine used
    language_engines = [
        'de-en.smt', 'en-cs.smt', 'en-de.nmt', 'en-de.smt', 'en-lv.nmt',
        'en-lv.smt'
    ]

#    # Normal set
#    for sset in ['train', 'dev', 'test']:
#        for language_engine in language_engines:
#            # WMT2018/RAW/de-en.smt.test.pre-processed_final
#            raw_file = '../DATA/WMT2018/RAW/%s.%s.pre-processed_final' % (language_engine, sset)
#            out_folder = '../DATA/WMT2018/task2_%s_%s/' % (language_engine, sset)
#            convert_corpus(raw_file, out_folder, sset)

    # en-lv
    # Num normalized set
    # It is shuffled differently so we need to read all in a single block
    en_lv_corpus_by_id = {}
    for machine in ['nmt', 'smt']:

        # Collect all files with different normalization
        raw_file = '../DATA/WMT2018/NUM_PREPRO/RAW/en-lv.%s.fully-pre-processed' % machine
        items = read_raw(raw_file)
        for sid, src_sent, mt_sent, pe_sent, ref_sent in zip(*items):
            en_lv_corpus_by_id[sid] = [src_sent, mt_sent, pe_sent, ref_sent]
        raw_file = '../DATA/WMT2018/NUM_PREPRO/RAW/en-lv.%s.test.fully-pre-processed' % machine
        items = read_raw(raw_file)
        for sid, src_sent, mt_sent, pe_sent, ref_sent in zip(*items):
            en_lv_corpus_by_id[sid] = [src_sent, mt_sent, pe_sent, ref_sent]

        for sset in ['train', 'dev', 'test']:
            out_folder = '../DATA/WMT2018/NUM_PREPRO/task2_en-lv.%s_%s/' % (machine, sset)

            # Get ids for this file
            ref_ids = read_raw(
                '../DATA/WMT2018/RAW/en-lv.%s.%s.pre-processed_final' % (machine, sset)
            )[0]
            items = [en_lv_corpus_by_id[id] for id in ref_ids]
            src_sents, mt_sents, pe_sents, ref_sents = zip(*items)

            # Get the ids
            save_corpus(
                out_folder, src_sents, mt_sents, pe_sents, ref_sents, sset
            )
