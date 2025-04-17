from .PbHiT_Tagging_Vectors_NBIS import (
    get_sequence_list as original_get_tag_sequence
)
from ..oligo_search import (
    TagSearchContext,
)
from .tag_gene_ids import gene_ids


def test_compare_tag_algorithms():
    search_context = TagSearchContext()
    for gene_id in gene_ids:
        print(gene_id)
        original_result = original_get_tag_sequence([gene_id])
        original_sequences = list(original_result['Oligo Sequence'])

        system_result = search_context.get_sequence_list([gene_id])
        system_sequences = list(system_result['Oligo sequence'])

        assert original_sequences == system_sequences, (
            f"the resulting vectors for {gene_id} are all the same"
        )

        rows = search_context.get_rows(system_result)
        annotated_sequences = [
            row.sequence
            for row in rows
        ]

        assert original_sequences == annotated_sequences, (
            f"the resulting vectors for {gene_id} are all the same"
        )
