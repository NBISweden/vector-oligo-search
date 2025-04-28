import pytest
from .PbHiT_Tagging_Vectors_NBIS import (
    get_sequence_list as original_get_tag_sequence
)
from ..oligo_search import (
    TagSearchContext,
    REQUIRED_UNIQUE_SEGMENTS
)
from .tag_gene_ids import gene_ids
from ..annotations import Annotations as anno


@pytest.mark.parametrize('gene_id', list(gene_ids))
def test_compare_tag_algorithms(gene_id):
    search_context = TagSearchContext()
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


@pytest.mark.parametrize('gene_id', list(gene_ids))
def test_overlapping_tag_segments(gene_id):
    # NOTE: A number of these tests are expected to fail at the moment and may be fixed later

    search_context = TagSearchContext()
    system_result = search_context.get_sequence_list([gene_id])

    correct_status = tuple(
        (segment_id, 1)
        for segment_id in REQUIRED_UNIQUE_SEGMENTS
    )

    for i, row_status in enumerate(system_result['status']):
        status = tuple(
            (segment_id, row_status[segment_id])
            for segment_id in REQUIRED_UNIQUE_SEGMENTS
        )
        assert correct_status == status, (
            f"all segments occur only once in sequence for {gene_id} on row {i}"
        )
