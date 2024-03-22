from dataclasses import dataclass, field
import logging
import math


logger = logging.getLogger(__name__)


class SearchError(RuntimeError):
    pass


@dataclass
class Annotation:
    position: tuple[int, int]
    label: str


@dataclass
class SearchResult:
    gene_id: str = None
    annotations: list[Annotation] = field(default_factory=list)
    sequence: str = ""

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

    @staticmethod
    def from_df(gene_id, df, keys):
        result = SearchResult(gene_id=gene_id)
        for key in keys:
            value = df[key]
            logger.warning(f"{key}: {value}: {type(value)}")
            if type(value) == str:
                result.concat(
                    sub_sequence=value,
                    annotation=key
                )
        return result