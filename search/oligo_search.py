from Bio import SeqIO
import pandas as pd
from .annotations import Annotations as anno
from .search import SearchError, SearchResult
import logging
import io
import zipfile
from functools import lru_cache


logger = logging.getLogger(__name__)


# Set standard elements of the gRNA oligo into items
BbsI = 'GAAGACggTATT'
Scaffold = (
    'GTTTTAGAGCTAGAAATAGCAAGTTAAAATAAG'
    'GCTAGTCCGTTATCAACTTGAAAAAGTGGCACCGAGTCGGTGC'
)
AvrII = 'CCTAGG'
PstI = 'CTGCAG'


@lru_cache
def load_ko_data():
    logger.info("Loading KO data")
    # Read gRNA excel files as table
    # this file has top 3 gRNAs for each gene,
    # read only until column C 'Total_score'
    gRNA_EuPaGDT_top = pd.read_excel(
        "./resources/ko/selected_gRNA.PbHIT_KO_Test.xlsx",
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

    # Load table with Genes, HR1, HR2
    pHIT_KO_HR = pHIT_KO_HR = pd.read_excel("./resources/ko/PbHiT_KO_Vector_HR_List_April16_RE.xlsx")

    logger.info("KO data loaded")
    return [
        pHIT_KO_HR,
        gRNA_EuPaGDT_top
    ]


def get_ko_sequence(input_gene):
    [
        pHIT_KO_HR,
        gRNA_EuPaGDT_top
    ] = load_ko_data()
    gene_gRNA = gRNA_EuPaGDT_top[gRNA_EuPaGDT_top['GENE ID'] == input_gene]
    if gene_gRNA.empty:
        raise SearchError(f'No KO construct found:No gRNA found for: {input_gene}')

    gene_HR = pHIT_KO_HR[pHIT_KO_HR['GENE ID'] == input_gene]
    if gene_HR.empty:
        raise SearchError(f'No KO construct found: No gene found for: {input_gene}')

    gene_gRNA_top2 = gene_gRNA.iloc[:3]

    strand = gene_HR['strand_x'].to_list()[0]
    sequence_order = (
        anno.OLIGO_SEQUENCE_KO_ORDER_FW
        if strand == '+'
        else anno.OLIGO_SEQUENCE_KO_ORDER_REV
    )
    hr_variant = (
        "Fw"
        if strand == '+'
        else "Rev"
    )

    PbHOT_KO_Vector_List = pd.DataFrame({
        'Oligo sequence': "",
        'GENE ID': input_gene,
        anno.BBS_I: BbsI,
        anno.GRNA: gene_gRNA_top2['gRNA_sequence'],
        anno.SCAFFOLD: Scaffold,
        anno.HR2: gene_HR[f'HR2 Sequence {hr_variant}'].tolist()[0],
        anno.AVR_II: AvrII,
        anno.HR1: gene_HR[f'HR1 Sequence {hr_variant}'].tolist()[0],
        anno.PST_I: PstI,
        'Strand': strand,
    })

    for annotation in sequence_order:
        PbHOT_KO_Vector_List['Oligo sequence'] = (
            PbHOT_KO_Vector_List['Oligo sequence']
            + PbHOT_KO_Vector_List[annotation]
        )

    return PbHOT_KO_Vector_List


@lru_cache
def load_tag_data():
    logger.info("Loading TAG data")
    # Read gRNA excel files as table

    # this file has top 3 gRNAs for each gene,
    # read only until column C 'Total_score'
    gRNA_EuPaGDT_tag_top = pd.read_excel(
        "./resources/tag/selected_gRNA.CRISPR_tagging.xlsx",
        index_col=None,
        na_values=['NA'],
        usecols="A:C"
    )
    gRNA_EuPaGDT_tag_top[['GENE ID', 'gRNA ID', 'directionality']] = (
        gRNA_EuPaGDT_tag_top.gRNA_id.str.split("_", expand=True)
    )
    gRNA_EuPaGDT_tag_top['GENE ID'] = (
        gRNA_EuPaGDT_tag_top['GENE ID'].replace(
            'PBANKA',
            'PBANKA_',
            regex=True
        )
    )

    # Create a DataFrame that has the Gene ID, HR1, and HR2

    # Read HR1 FASTA file
    (genes, HR1_seq) = _parse_HR_fasta(
        "./resources/tag/PbHiT_Tagging_HR1_Final.fasta"
    )

    # Read HR2 FASTA file
    (genes, HR2_seq) = _parse_HR_fasta(
        "./resources/tag/PbHiT_Tagging_HR2_Final.fasta"
    )

    # Read HR1_rev FASTA file
    (genes, HR1_seq_rev) = _parse_HR_fasta(
        "./resources/tag/PbHiT_Tagging_HR1_Final_rev_comp.fasta"
    )

    # Read HR2_rev FASTA file
    (genes, HR2_seq_rev) = _parse_HR_fasta(
        "./resources/tag/PbHiT_Tagging_HR2_Final_rev_comp.fasta"
    )

    # Generate table with Genes, HR1, HR2
    pHIT_Tag_HR = pd.DataFrame({
        "GENE ID": genes,
        "HR1 Sequence": HR1_seq,
        "HR2 Sequence": HR2_seq,
        "HR1 Sequence Rev": HR1_seq_rev,
        "HR2 Sequence Rev": HR2_seq_rev,
    })

    # Create data frame with HR1 HR2 and gRNA merged
    merged_df = pd.merge(
        pHIT_Tag_HR,
        gRNA_EuPaGDT_tag_top,
        on='GENE ID',
        how='inner'
    )
    PbHiT_Tagging_Merge = pd.DataFrame(merged_df)

    # Use apply to perform the search and extract operation
    PbHiT_Tagging_Merge['Extracted_Sequence'] = PbHiT_Tagging_Merge.apply(
        _extract_sequence,
        axis=1,
        search_column='gRNA_sequence',
        target_column='HR1 Sequence'
    )
    PbHiT_HR1_Final_Fw = PbHiT_Tagging_Merge.copy()

    # Use apply to perform the search and extract operation
    PbHiT_Tagging_Merge['Extracted_Sequence'] = PbHiT_Tagging_Merge.apply(
        _extract_sequence_before,
        axis=1,
        search_column='gRNA_sequence',
        target_column='HR1 Sequence Rev'
    )
    PbHiT_HR1_Final_Rev = PbHiT_Tagging_Merge.copy()

    # Merge the two DataFrames on two common
    # columns (e.g., 'column1' and 'column2')
    PbHiT_HR1_merge = pd.merge(
        PbHiT_HR1_Final_Fw,
        PbHiT_HR1_Final_Rev,
        on=[
            'GENE ID',
            'HR1 Sequence',
            'HR2 Sequence',
            'HR1 Sequence Rev',
            'HR2 Sequence Rev',
            'gRNA_id',
            'gRNA_sequence',
            'Total_score',
            'gRNA ID',
            'directionality'
        ],
        how='inner'
    )

    # Concatenate the Extracted sequence column
    PbHiT_HR1_merge['HR1_Tag'] = (
        PbHiT_HR1_merge['Extracted_Sequence_x'].fillna('') +
        PbHiT_HR1_merge['Extracted_Sequence_y']
    )
    logger.info("TAG data loaded")
    return [PbHiT_HR1_merge]


def _parse_HR_fasta(file_path):
    # Parse a fasta file to a string list and extract gene list
    entries = [
        (seq_record.id, str(seq_record.seq))
        for seq_record in SeqIO.parse(file_path, 'fasta')
    ]
    (genes, sequence) = zip(*entries)
    return (
        list(genes),
        list(sequence)
    )


def _extract_sequence(row, search_column, target_column, extract_length=100):
    # Extract HR1 sequence in data frame forward sequences
    search_pattern = row[search_column]
    target_sequence = row[target_column]

    # Find the position of the search pattern in the target sequence
    position = target_sequence.find(search_pattern)

    if position != -1:
        # Extract 100 characters after the search pattern
        start_position = position + 6 + len(search_pattern)
        return target_sequence[start_position:start_position + extract_length]

    else:
        return ''  # Return an empty string if the pattern is not found


def _extract_sequence_before(
    row,
    search_column,
    target_column,
    extract_length=100
):
    # Extract HR1 Sequence in data frame reverse sequences
    search_pattern = row[search_column]
    target_sequence = row[target_column]

    # Find the position of the search pattern in the target sequence
    position = target_sequence.find(search_pattern)

    if position != -1:
        # Extract 100 characters before the search pattern
        start_position = max(0, position - extract_length)
        return target_sequence[start_position:position]

    else:
        return ''  # Return an empty string if the pattern is not found


def get_tag_sequence(input_gene):
    [PbHiT_HR1_merge] = load_tag_data()
    gene_gRNA = PbHiT_HR1_merge[PbHiT_HR1_merge['GENE ID'] == input_gene]

    if gene_gRNA.empty:
        raise SearchError(f'No tagging construct found: No gRNA found for: {input_gene}')

    PbHiT_Tag_Vector_List = pd.DataFrame({
        'Oligo sequence': "",
        'GENE ID': input_gene,
        anno.BBS_I: BbsI,
        anno.GRNA: gene_gRNA['gRNA_sequence'],
        anno.SCAFFOLD: Scaffold,
        anno.HR1: gene_gRNA['HR1_Tag'],
        anno.AVR_II: AvrII,
        anno.HR2: gene_gRNA['HR2 Sequence'],
        anno.PST_I: PstI
    })

    for annotation in anno.OLIGO_SEQUENCE_TAG_ORDER:
        PbHiT_Tag_Vector_List['Oligo sequence'] = (
            PbHiT_Tag_Vector_List['Oligo sequence']
            + PbHiT_Tag_Vector_List[annotation]
        )

    return PbHiT_Tag_Vector_List


class KOSearchContext:
    def get_sequence_list(self, gene_ids):
        return get_sequence_list(gene_ids, get_ko_sequence)

    def get_rows(self, result):
        row_parser = KOSearchContext.get_ko_row_parser()
        return SearchResult.from_df(
            result,
            row_parser
        )

    @staticmethod
    def get_ko_row_parser():
        forward_row_parser = SearchResult.get_key_row_parser(
            anno.OLIGO_SEQUENCE_KO_ORDER_FW
        )
        reverse_row_parser = SearchResult.get_key_row_parser(
            anno.OLIGO_SEQUENCE_KO_ORDER_REV
        )

        def _parse_row(row):
            strand = row['Strand']
            return (
                forward_row_parser(row)
                if strand == '+'
                else reverse_row_parser(row)
            )

        return _parse_row


class TagSearchContext:
    def get_sequence_list(self, gene_ids):
        return get_sequence_list(gene_ids, get_tag_sequence)

    def get_rows(self, result):
        row_parser = SearchResult.get_key_row_parser(
            anno.OLIGO_SEQUENCE_TAG_ORDER
        )
        return SearchResult.from_df(
            result,
            row_parser
        )


def df_to_file(df, output_format="csv", file_basename="oligo-vector-sequence"):
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
                f"{file_basename}.csv",
                csv_output.getvalue().decode("utf-8")
            )
        mimetype = "application/zip"
    elif output_format == "xlsx":
        output_data.to_excel(output)
        mimetype = (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    return output.getvalue(), mimetype


def df_to_search_result(
    df,
    parse_row
):
    return SearchResult.from_df(
        df,
        parse_row
    )


def get_sequence_list(gene_ids, seq_func=get_ko_sequence):
    return pd.concat(
        [
            seq_func(gene_id)
            for gene_id in gene_ids
        ]
    )
