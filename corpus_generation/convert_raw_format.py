import codecs
import os


def read_raw(file_path):
    with codecs.open(file_path, 'r', 'utf-8') as fid:
        source_sents = []
        mt_sents = []
        pe_sents = []
        ref_sents = []
        for line in fid.readlines():
            source_sent, mt_sent, pe_sent, ref_sent = line.split('\t')[1:5]
            # append
            source_sents.append(source_sent)
            mt_sents.append(mt_sent)
            pe_sents.append(pe_sent)
            ref_sents.append(ref_sent)

    return source_sents, mt_sents, pe_sents, ref_sents


def write_file(file_path, sentences):
    with codecs.open(file_path, 'w', 'utf-8') as fid:
        for sent in sentences:
            fid.write('%s\n' % sent)


def convert_corpus(raw_file, out_folder, label):
    if not os.path.isdir(out_folder):
        os.mkdir(out_folder)
    src_sents, mt_sents, pe_sents, ref_sents = read_raw(raw_file)
    write_file('%s/%s.src' % (out_folder, label), src_sents)
    write_file('%s/%s.mt' % (out_folder, label), mt_sents)
    write_file('%s/%s.pe' % (out_folder, label), pe_sents)
    write_file('%s/%s.ref' % (out_folder, label), ref_sents)
    print('%s -> %s' % (raw_file, out_folder))


if __name__ == '__main__':

    for sset in ['en-lv.nmt', 'en-lv.nmt', 'en-cs.smt']:

        # Train
        raw_file = '../DATA/WMT2018/RAW/%s.pre-processed' % sset
        out_folder = '../DATA/WMT2018/task2_%s_training/' % sset
        convert_corpus(raw_file, out_folder, 'train')

        # Test
        raw_file = '../DATA/WMT2018/RAW/%s.test.pre-processed' % sset
        out_folder = '../DATA/WMT2018/task2_%s_test/' % sset
        convert_corpus(raw_file, out_folder, 'test')
