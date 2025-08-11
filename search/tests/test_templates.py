import os
import tempfile
import contextlib
from html5validator import validator
from flask import (
    render_template,
)
from ..core import create_app, parse_markdown
from ..search import SearchResult, Annotation


html5validator = validator.Validator()


app = create_app(
    secret_key=os.getenv("APP_SECRET_KEY", os.urandom(24).hex()),
    message_root=os.getenv("APP_MESSAGE_ROOT", "/home/vector_oligo_search"),
)


markdown_content = (
    """
# Title A
Hello world!

## Title A.A

## Title A.B

# Title B
Hello world!

## Title B.A

## Title B.B

"""
)


output = [
    SearchResult(
        gene_id="A",
        annotations=[
            Annotation(position=(0, 3), label="a"),
            Annotation(position=(3, 6), label="b")
        ],
        sequence="ACGGCA",
    )
]


@contextlib.contextmanager
def html_output_directory_test():
    with app.app_context():
        with tempfile.TemporaryDirectory(prefix="html-test") as workdir:
            def _add_test_data(name: str, data: str):
                with open(os.path.join(workdir, f"{name}.html"), "w") as f:
                    f.write(data)
            yield _add_test_data
            number_of_errors = html5validator.validate(
                validator.all_files(workdir)
            )
            if number_of_errors > 0:
                raise RuntimeError("HTML was not valid")


def test_form():
    with html_output_directory_test() as add_test_data:
        content_html = parse_markdown(markdown_content)
        files = [
            {
                "name": "data.xlsx",
                "data": "",
                "type": "XLSX"
            },
            {
                "name": "data.zip",
                "data": "",
                "type": "CSV"
            }
        ]
        result_with_error = render_template(
            "form.html",
            title="Test form",
            content=content_html,
            gene_ids=[],
            lookup_type="KO",
            output=[],
            error="A basic error",
            message="A basic message",
            files=files
        )
        add_test_data("form_with_error", result_with_error)
        result = render_template(
            "form.html",
            title="Test form",
            content=content_html,
            gene_ids=[],
            lookup_type="KO",
            output=output,
            message="A basic message",
            files=files
        )
        add_test_data("form", result)


def test_page():
    with html_output_directory_test() as add_test_data:
        content_html = parse_markdown(markdown_content)
        result = render_template(
            "page.html",
            content=content_html,
            title="Test page",
            message="Test form",
        )
        add_test_data("page", result)


def test_404():
    with html_output_directory_test() as add_test_data:
        result = render_template(
            "404.html",
            url="test"
        )
        add_test_data("404", result)
