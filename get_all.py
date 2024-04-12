from search.oligo_search import get_sequence_list
from search.tests.gene_ids import gene_ids
from search.search import SearchError, stream_to_base64_url
from search.oligo_search import get_sequence_list, df_to_file, df_to_search_result


sequence_list_df = get_sequence_list(gene_ids)
output = df_to_search_result(sequence_list_df)

(csv, ext) = df_to_file(sequence_list_df, "csv")
csv_data = stream_to_base64_url(csv, "text/csv")

(xlsx, ext) = df_to_file(sequence_list_df, "xlsx")
xlsx_data = stream_to_base64_url(xlsx, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")