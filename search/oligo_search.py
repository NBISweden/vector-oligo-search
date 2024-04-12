from Bio import SeqIO
import pandas as pd
from .annotations import Annotations as anno
from .search import SearchError, SearchResult
import logging
import io
import zipfile


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
# this file has top 3 gRNAs for each gene,
# read only until column C 'Total_score'
gRNA_EuPaGDT_top = pd.read_excel(
    "./resources/selected_gRNA.PbHIT_KO_Test.xlsx",
    index_col=None,
    na_values=['NA'],
    usecols="A:C"
)
gRNA_EuPaGDT_top[['GENE ID', 'gRNA ID', 'directionality']] = (
    gRNA_EuPaGDT_top.gRNA_id.str.split("_", expand=True)
)
gRNA_EuPaGDT_top['GENE ID'] = (
    gRNA_EuPaGDT_top['GENE ID'].replace('PBANKA', 'PBANKA_', regex=True)
)

# Create a DataFrame that has the Gene ID, HR1, and HR2
# Read HR1 FASTA file
HR1_fasta_rev = "./resources/HR1_rev_comp.fasta"
HR1_seq_rev = [i for i in SeqIO.parse(HR1_fasta_rev, 'fasta')]

# Store HR1 sequences into a string
genes = []
HR1_seq_rev = []
for seq_record in SeqIO.parse(HR1_fasta_rev, 'fasta'):
    genes.append(seq_record.id)
    HR1_seq_rev.append(str(seq_record.seq))

# Read HR2 FASTA file
HR2_fasta_rev = "./resources/HR2_rev_comp.fasta"
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


def get_sequence(input_gene):
    gene_gRNA = gRNA_EuPaGDT_top[gRNA_EuPaGDT_top['GENE ID'] == input_gene]
    if gene_gRNA.empty:
        raise SearchError(f'No gRNA found for: {input_gene}')

    gene_HR = pHIT_KO_HR[pHIT_KO_HR['GENE ID'] == input_gene]
    if gene_HR.empty:
        raise SearchError(f'No gene found for: {input_gene}')

    gene_gRNA_top2 = gene_gRNA.iloc[:3]

    PbHOT_KO_Vector_List = pd.DataFrame({
        'Oligo sequence': "",
        'GENE ID': input_gene,
        anno.BBS_I: BbsI,
        anno.GRNA: gene_gRNA_top2['gRNA_sequence'],
        anno.SCAFFOLD: Scaffold,
        anno.HR2: gene_HR['HR2 Sequence'].tolist()[0],
        anno.AVR_II: AvrII,
        anno.HR1: gene_HR['HR1 Sequence'].tolist()[0],
        anno.PST_I: PstI
    })

    for annotation in anno.OLIGO_SEQUENCE_ORDER:
        PbHOT_KO_Vector_List['Oligo sequence'] = (
            PbHOT_KO_Vector_List['Oligo sequence']
            + PbHOT_KO_Vector_List[annotation]
        )

    return PbHOT_KO_Vector_List


def df_to_file(df, output_format="csv"):
    output_data = pd.DataFrame(
        {
            'GENE ID': df['GENE ID'],
            'Oligo sequence': df['Oligo sequence'],
        }
    )
    mimetype = None
    output = io.BytesIO()
    if output_format == "csv":
        csv_output = io.BytesIO()
        output_data.to_csv(csv_output)

        with zipfile.ZipFile(
            output,
            "a",
            zipfile.ZIP_DEFLATED,
            False
        ) as csv_zip:
            csv_zip.writestr(
                "oligo-vecotry-sequences.csv",
                csv_output.getvalue().decode("utf-8")
            )
        mimetype = "application/zip"
    elif output_format == "xlsx":
        output_data.to_excel(output)
        mimetype = (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    return output.getvalue(), mimetype


def df_to_search_result(df):
    return SearchResult.from_df(
        df,
        anno.OLIGO_SEQUENCE_ORDER
    )


def get_sequence_list(gene_ids):
    return pd.concat(
        [
            get_sequence(gene_id)
            for gene_id in gene_ids
        ]
    )


def search_to_file(gene_ids, output_format="csv"):
    full_result = get_sequence_list(gene_ids)
    return df_to_file(full_result, output_format=output_format)
