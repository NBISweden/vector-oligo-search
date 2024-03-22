from Bio import SeqIO
import pandas as pd
from .search import SearchError, SearchResult
from itertools import chain
import logging


logger = logging.getLogger(__name__)

# Set standard elements of the gRNA oligo into items
BbsI = 'GAAGACggTATT'
Scaffold = (
    'GTTTTAGAGCTAGAAATAGCAAGTTAAAATAAG'
    'GCTAGTCCGTTATCAACTTGAAAAAGTGGCACCGAGTCGGTGC'
)
AvrII = 'CCTAGG'
PstI = 'CTGCAG'


# Read gRNA excel files as table
# this file has top 3 gRNAs for each gene, read only until column C 'Total_score'
gRNA_EuPaGDT_top = pd.read_excel("selected_gRNA.PbHIT_KO_Test.xlsx", index_col=None, na_values=['NA'], usecols="A:C")
gRNA_EuPaGDT_top[['GENE ID', 'gRNA ID', 'directionality']] = gRNA_EuPaGDT_top.gRNA_id.str.split("_", expand=True)
gRNA_EuPaGDT_top['GENE ID'] = gRNA_EuPaGDT_top['GENE ID'].replace('PBANKA', 'PBANKA_', regex=True)

# Create a DataFrame that has the Gene ID, HR1, and HR2
# Read HR1 FASTA file
HR1_fasta_rev = "HR1_rev_comp.fasta"
HR1_seq_rev = [i for i in SeqIO.parse(HR1_fasta_rev, 'fasta')]

# Store HR1 sequences into a string
genes = []
HR1_seq_rev = []
for seq_record in SeqIO.parse(HR1_fasta_rev, 'fasta'):
    genes.append(seq_record.id)
    HR1_seq_rev.append(str(seq_record.seq))

# to see items in a FASTA file
# PBANKA1 = HR1_seq[0]
# print (PBANKA1)

# Read HR2 FASTA file
HR2_fasta_rev = "HR2_rev_comp.fasta"
HR2_seq_rev = [i for i in SeqIO.parse(HR2_fasta_rev, 'fasta')]

# Store HR2 sequences into a string
genes = []
HR2_seq_rev = []

for seq_record in SeqIO.parse(HR2_fasta_rev, 'fasta'):
    genes.append(seq_record.id)
    HR2_seq_rev.append(str(seq_record.seq))

# Generate table with Genes, HR1, HR2
pHIT_KO_HR = pd.DataFrame({
    "GENE ID": genes,
    "HR1 Sequence": HR1_seq_rev,
    "HR2 Sequence": HR2_seq_rev
})


def get_gene_list(input_gene):
    gene_gRNA = gRNA_EuPaGDT_top[gRNA_EuPaGDT_top['GENE ID'] == input_gene]
    if not gene_gRNA.empty:
        Result1 = BbsI + gene_gRNA['gRNA_sequence']
    else:
        raise SearchError('No gRNA')

    # Store Results in a data frame
    pHIT_KO_BbsI_gRNA = pd.DataFrame({
        "GENE ID": input_gene,
        "Sequence": Result1
    })

    pHIT_KO_BbsI_gRNA_top2 = pHIT_KO_BbsI_gRNA.iloc[:3]
    logger.warning(pHIT_KO_BbsI_gRNA_top2.to_csv())
    gene_HR = pHIT_KO_HR[pHIT_KO_HR['GENE ID'] == input_gene]

    sub_sequences = {
        "Sequence": pHIT_KO_BbsI_gRNA_top2['Sequence'],
        "Scaffold": Scaffold,
        "HR2 Sequence": gene_HR['HR2 Sequence'],
        "AvrII": AvrII,
        "HR1 Sequence": gene_HR['HR1 Sequence'],
        "PstI": PstI
    }
    PbHOT_KO_Vector_List = pd.DataFrame(
        columns=[
            'GENE ID',
            *[cid for cid in sub_sequences.keys()]
        ]
    )
    if not gene_HR.empty:
        for (annotation, sub_sequence) in sub_sequences.items():
            PbHOT_KO_Vector_List[annotation] = sub_sequence
        logger.warning(PbHOT_KO_Vector_List.to_csv())
    else:
        raise SearchError('Gene Cannot be Found')

    PbHOT_KO_Vector_List['GENE ID'] = pHIT_KO_BbsI_gRNA_top2['GENE ID']
    PbHOT_KO_Vector_List['Oligo sequence'] = (
        PbHOT_KO_Vector_List['Sequence']
        + PbHOT_KO_Vector_List['Scaffold']
        + PbHOT_KO_Vector_List['HR2 Sequence']
        + PbHOT_KO_Vector_List['AvrII']
        + PbHOT_KO_Vector_List['HR1 Sequence']
        + PbHOT_KO_Vector_List['PstI']
     )

    return [
        SearchResult.from_df(
            row['GENE ID'],
            row,
            sub_sequences.keys()
        )
        for (index, row) in PbHOT_KO_Vector_List.iterrows()
    ]


def search(gene_ids):
    return list(chain(
        *[
            get_gene_list(gene_id)
            for gene_id in gene_ids
        ]
    ))

