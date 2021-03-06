#!/usr/bin/env python
import os
import sys
import math
import pandas
import argparse
import sqlite3
import yaml
import json
import subprocess


def clean_db(db_file):
    conn = sqlite3.connect(db_file)
    c = conn.cursor()
    print('Cleaning database ... ')
    c.execute("DELETE FROM main_experimenthasintron")
    c.execute("UPDATE SQLITE_SEQUENCE SET SEQ=0 WHERE NAME='main_experimenthasintron'")

    c.execute("DELETE FROM main_experiment")
    c.execute("UPDATE SQLITE_SEQUENCE SET SEQ=0 WHERE NAME='main_experiment'")

    c.execute("DELETE FROM main_sample_condition")
    c.execute("UPDATE SQLITE_SEQUENCE SET SEQ=0 WHERE NAME='main_sample_condition'")

    c.execute("DELETE FROM main_sample")
    c.execute("UPDATE SQLITE_SEQUENCE SET SEQ=0 WHERE NAME='main_sample'")

    c.execute("DELETE FROM main_condition")
    c.execute("UPDATE SQLITE_SEQUENCE SET SEQ=0 WHERE NAME='main_condition'")

    c.execute("DELETE FROM main_project")
    c.execute("UPDATE SQLITE_SEQUENCE SET SEQ=0 WHERE NAME='main_project'")

    c.execute("DELETE FROM main_intron")
    c.execute("UPDATE SQLITE_SEQUENCE SET SEQ=0 WHERE NAME='main_intron'")

    c.execute("DELETE FROM main_gene")
    c.execute("UPDATE SQLITE_SEQUENCE SET SEQ=0 WHERE NAME='main_gene'")

    c.execute("DELETE FROM main_chromosome")
    c.execute("UPDATE SQLITE_SEQUENCE SET SEQ=0 WHERE NAME='main_chromosome'")

    conn.commit()
    conn.close()
    print('Database empty')


def loading_introns(conn, gene_id):
    i_c = conn.cursor()
    introns = {}
    for row in i_c.execute("SELECT id,start,end FROM main_intron WHERE gene_id = " + str(gene_id)):
        introns[row[1]] = {}
        introns[row[1]]['ID'] = row[0]
        introns[row[1]]['end'] = row[2]
    return introns


def loading_genes(conn, chr_id):
    g_c = conn.cursor()
    genes = {}
    for row in g_c.execute("SELECT id,name FROM main_gene WHERE chr_id = " + str(chr_id)):
        genes[row[1]] = {}
        genes[row[1]]['ID'] = row[0]
        genes[row[1]]['introns'] = loading_introns(conn, row[0])
    return genes


def loading_chromosomes(conn):
    c_c = conn.cursor()
    chr = {}
    for row in c_c.execute("SELECT id,name,refseqacc  FROM main_chromosome"):
        chr[row[1]] = {}
        chr[row[1]]['ID'] = row[0]
        chr[row[1]]['refseqacc'] = row[2]
        chr[row[1]]['genes'] = loading_genes(conn, row[0])
    return chr


def loading_chromosomes_from_assembly(conn, assembly_report):
    data = pandas.read_csv(assembly_report, sep='\t', comment='#', header=None)
    chr = loading_chromosomes(conn)
    c = conn.cursor()
    for index, row in data.loc[data[6].str.startswith('NC_')].iterrows():
        if row[9] not in chr:
            chr[row[9]] = {}
            chr[row[9]]['refseqacc'] = row[6]
            c.execute("INSERT INTO main_chromosome (name,refseqacc) VALUES ('" + row[9] + "','" + row[6] + "')")
        elif chr[row[9]]['refseqacc'] != row[6]:
            print('Chromosome: ' + row[9] + ' is already inserted with another Assembly Report.')
            print('This is system is designed to host experiments using the same Human Genome')
            sys.exit(-1)
    conn.commit()
    return loading_chromosomes(conn)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Clean SNPdata table')
    parser.add_argument('-d', help='SQLite database', required=True)
    parser.add_argument('-c', help='Clean database', required=False, action='store_true')
    parser.add_argument('--yaml', help='Data file in Yaml format', required=False)
    parser.add_argument('--samtools_out',
                        help='Write out an script to run in a queue system to create introns BAM files', required=True)

    args = parser.parse_args()
    db_file = args.d
    if args.c:
        clean_db(db_file)

    if args.yaml:
        with open(args.yaml, 'r') as stream:
            yaml_data = yaml.load(stream)
            print(json.dumps(yaml_data, sort_keys=True, indent=4))

            print('Loading data to the database')
            conn = sqlite3.connect(db_file)
            c = conn.cursor()

            print('Project: ' + yaml_data['PROJECT_NAME'])
            print('Description: ' + yaml_data['PROJECT_DESCR'])
            c.execute("INSERT INTO main_project (name, description) VALUES (?,?)",
                      (yaml_data['PROJECT_NAME'], yaml_data['PROJECT_DESCR']))
            prj_id = c.lastrowid
            print('Project ID: ' + str(prj_id))

            print('Loading samples data')
            samples = []
            sample_data = pandas.read_csv(yaml_data['SAMPLE_FILE'], sep='\t')
            for index, row in sample_data.iterrows():
                samples.append((row[yaml_data['SAMPLE_NAME_COLUMN']],))

            print('Inserting samples')
            c.executemany("INSERT INTO main_sample (name) VALUES (?)", samples)
            samples = {}
            for row in c.execute("SELECT id, name FROM main_sample"):
                samples[row[1]] = row[0]

            print('Inserting conditions')
            conditions = {}
            condition_samples = []
            for cond in yaml_data['CONDITIONS']:
                c.execute("INSERT INTO main_condition (name, description, prj_id) VALUES (?,?, ?)",
                          (cond['NAME'], cond['DESCR'], prj_id))
                conditions[cond['NAME']] = c.lastrowid

                if 'not' in cond['SAMPLE_TYPE']:
                    type = cond['SAMPLE_TYPE'].split(' ')[1]
                    data = sample_data.loc[sample_data[yaml_data['SAMPLE_TYPE_COLUMN']] != type]
                else:
                    data = sample_data.loc[sample_data[yaml_data['SAMPLE_TYPE_COLUMN']] == cond['SAMPLE_TYPE']]
                for index, row in data.iterrows():
                    if row[yaml_data['SAMPLE_NAME_COLUMN']] in samples:
                        condition_samples.append(
                            (samples[row[yaml_data['SAMPLE_NAME_COLUMN']]], conditions[cond['NAME']]))

            c.executemany("INSERT INTO main_sample_condition (sample_id, condition_id) VALUES (?,?)", condition_samples)

            chr = loading_chromosomes_from_assembly(conn, yaml_data['ASSEMBLY_REPORT'])

            print('Inserting experiments')
            for exp in yaml_data['EXPERIMENTS']:
                if exp['COND1'] in conditions and exp['COND2'] in conditions:
                    print('\tExperiment: ' + exp['NAME'])
                    exps = (exp['NAME'], exp['DESCR'], conditions[exp['COND1']], conditions[exp['COND2']],
                            exp['TPMRATIONCUTOFF'], exp['PVALUECUTOFF'], exp['RCUTOFF'])
                    c.execute(
                        "INSERT INTO main_experiment (name, description, condition1_id, condition2_id, TPMRatio_cutoff, pvalue_cutoff, r_cutoff) VALUES (?,?,?,?,?,?,?)",
                        exps)
                    exp_id = c.lastrowid

                    diffexpir = pandas.read_csv(exp['DIFFEXPIR'], sep='\t')

                    load_again = False
                    for g, l in diffexpir.groupby('GeneId'):
                        for i, r in l.iterrows():
                            if r['Chr'] not in chr:
                                print('Chromosome: ' + r['Chr'] + ' is not inserted in the database.')
                                print('This is system is designed to host experiments using the same Human Genome')
                                sys.exit(-1)
                            if g not in chr[r['Chr']]['genes']:
                                load_again = True
                                c.execute("INSERT INTO main_gene (name, chr_id) VALUES ('" + g + "'," + str(
                                    chr[r['Chr']]['ID']) + ")")
                                chr[r['Chr']]['genes'][g] = {'ID': c.lastrowid, 'introns': {}}
                            if r['Intron_Start'] not in chr[r['Chr']]['genes'][g]['introns']:
                                load_again = True
                                c.execute("INSERT INTO main_intron (start, end, gene_id) VALUES (" + str(
                                    r['Intron_Start']) + "," + str(r['Intron_End']) + "," + str(
                                    chr[r['Chr']]['genes'][g]['ID']) + ")")
                                chr[r['Chr']]['genes'][g]['introns'][r['Intron_Start']] = {'ID': c.lastrowid}
                            c.executemany(
                                "INSERT INTO main_experimenthasintron (exp_id, intron_id, pvalue, TPM1, TPM2, fc, r1, r2, chr, gene, start, end) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                                [(exp_id, chr[r['Chr']]['genes'][g]['introns'][r['Intron_Start']]['ID'], r['PValue'],
                                  r['TPM_1'], r['TPM_2'], math.log2(r['TPM_1'] / r['TPM_2']),
                                  r['RValue_1'], r['RValue_2'], r['Chr'], g, r['Intron_Start'], r['Intron_End'])])
                    if load_again:
                        conn.commit()
                        chr = loading_chromosomes(conn)
            conn.commit()

            print('Creating BAM files for inserted introns')
            print('Using files in ' + yaml_data['BAM_FILES'] + ' directory')
            print('Loading samples data')
            samples = []
            sample_data = pandas.read_csv(yaml_data['SAMPLE_FILE'], sep='\t')
            for index, row in sample_data.iterrows():
                samples.append(row[yaml_data['SAMPLE_NAME_COLUMN']])
            files = [name for root, dirs, files in os.walk(yaml_data['BAM_FILES']) for name in files if
                     name.endswith(".bam")]
            if not os.path.exists(yaml_data['BAM_FILES_INTRON']):
                os.mkdir(yaml_data['BAM_FILES_INTRON'])
            os.chdir(yaml_data['BAM_FILES_INTRON'])
            print('Working on ' + yaml_data['BAM_FILES_INTRON'])
            chr = loading_chromosomes(conn)
            with open(args.samtools_out, 'w') as f_out:
                for f in files:
                    sample = ''
                    for s in samples:
                        if s in f:
                            sample = s
                            break

                    if sample:
                        if not os.path.exists(sample):
                            os.mkdir(sample)
                        print('Processing BAM file:' + f)
                        for c in chr:
                            for g in chr[c]['genes']:
                                for i in chr[c]['genes'][g]['introns']:
                                    f_out.write(
                                        yaml_data['PROJECT_BIM_DIR'] + '/samtools.sh '
                                        + yaml_data['BAM_FILES'] + '/' + f
                                        + ' ' + c + ':' + str(i) + '-' + str(chr[c]['genes'][g]['introns'][i]['end'])
                                        + ' ' + sample + '/' + str(chr[c]['genes'][g]['introns'][i]['ID']) + '.bam'
                                        + '\n'
                                    )
                                    print(c + ' ' + g + ' ' + str(chr[c]['genes'][g]['introns'][i]['ID']) + ' ' + str(i) + '-' + str(chr[c]['genes'][g]['introns'][i]['end']))
                                    # subprocess.call([yaml_data['PROJECT_BIM_DIR'] + '/samtools.sh', yaml_data['BAM_FILES'] + '/' + f, c + ':' + str(i) + '-' + str(chr[c]['genes'][g]['introns'][i]['end']), sample + '/' + str(chr[c]['genes'][g]['introns'][i]['ID'])+ '.bam'])
            conn.close()
