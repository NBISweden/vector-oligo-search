from typing import Literal
from dataclasses import dataclass, field
import logging
import base64


logger = logging.getLogger(__name__)


class SearchError(RuntimeError):
    pass


@dataclass
class Annotation:
    position: tuple[int, int]
    label: str


@dataclass
class ResultMessage:
    message: str
    type: Literal["info", "warning", "danger"] = "info"


@dataclass
class SearchResult:
    gene_id: str = None
    annotations: list[Annotation] = field(default_factory=list)
    sequence: str = ""
    messages: list[str] = field(default_factory=list)

    def concat(self, sub_sequence, annotation=None):
        if annotation is not None:
            start = len(self.sequence)
            end = start + len(sub_sequence)
            self.annotations.append(
                Annotation(
                    position=(start, end),
                    label=annotation
                )
            )
        self.sequence += sub_sequence

    def add_message(self, message: ResultMessage):
        self.messages.append(message)

    @staticmethod
    def from_df(df, parse_row):
        for (index, row) in df.iterrows():
            gene_id, items, status = parse_row(row)
            result = SearchResult(gene_id=gene_id)
            for key, value in items:
                if isinstance(value, str):
                    result.concat(
                        sub_sequence=value,
                        annotation=key
                    )
            for key, value in status.items():
                if value > 1:
                    result.add_message(
                        ResultMessage(
                            f"Multiple occurences ({value}) for {key} detected.",
                            type="danger"
                        )
                    )
            yield result

    @staticmethod
    def get_key_row_parser(keys):
        def _parse_row(row):
            gene_id = row['GENE ID']
            status = row['status']
            return (
                gene_id,
                [
                    (key, row[key])
                    for key in keys
                ],
                status
            )

        return _parse_row


def stream_to_base64_url(file_data, mime_type):
    data = base64.b64encode(file_data).decode("utf-8").strip()
    url = f"data:{mime_type};base64,{data}"
    return url
