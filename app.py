from flask import (
    Flask,
    request,
    render_template,
    json,
    redirect,
    current_app,
)
import os
import logging
from search.oligo_search import (
    df_to_file,
    TagSearchContext,
    KOSearchContext
)
from search.search import SearchError, stream_to_base64_url
import frontmatter
import markdown
from markdown.extensions.toc import TocExtension
from flask_compress import Compress


logger = logging.getLogger(__name__)
app = Flask(
    __name__,
    static_folder="static"
)
app.secret_key = os.getenv("APP_SECRET_KEY", os.urandom(24).hex())
app.config["MESSAGE_ROOT"] = os.getenv("APP_MESSAGE_ROOT", "/home/vector_oligo_search")
Compress(app)


def load_markdown(path: str):
    with open(path, "r") as f:
        page_data = frontmatter.load(f)
        html = markdown.markdown(
            page_data.content,
            extensions=[TocExtension(baselevel=1)]
        )
        return (html, page_data)


def get_page(page_id: str):
    page_path = f'pages/{page_id}.md'
    return load_markdown(page_path)


def get_message(msg_id: str):
    try:
        message_root = current_app.config["MESSAGE_ROOT"]
        message_path = f'{message_root}/{msg_id}.md'
        (html, page_data) = load_markdown(message_path)
        return {
            'content': html,
            'type': page_data.get('type', 'warning')
        }
    except (KeyError, FileNotFoundError) as e:
        return None


@app.route('/')
def root():
    return redirect("search")


def parse_gene_ids(gene_id=None, gene_list=None):
    gene_list = ("" if gene_list is None else gene_list).strip()
    gene_ids = [] if gene_id is None else [gene_id]
    gene_ids = (
        gene_ids if len(gene_list) == 0
        else [g.strip().rstrip('\r\n') for g in gene_list.split("\n")]
    )
    return list(set(gene_id for gene_id in gene_ids if gene_id))


def parse_sequence_lookup_type(sequence_lookup=None):
    if not sequence_lookup or sequence_lookup == "KO":
        return "KO"
    else:
        return "TAG"


def get_sequence_lookup(lookup_type):
    if lookup_type == "TAG":
        return TagSearchContext()
    elif lookup_type == "KO":
        return KOSearchContext()
    else:
        raise SearchError(f"Invalid lookup type: {lookup_type}")


@app.route('/search', methods=['POST', 'GET'])
def form():
    gene_ids = []
    output = None
    error = None
    status_code = 200
    csv_data = None
    xlsx_data = None
    lookup_type = "KO"
    file_basename = "oligo-vector-sequence"

    message = get_message("search")

    if request.method == 'POST':
        gene_ids = parse_gene_ids(
            request.form.get('gene-id'),
            request.form.get('gene-list')
        )
        lookup_type = parse_sequence_lookup_type(
            request.form.get('lookup-type')
        )

    if len(gene_ids) > 0:
        try:
            search_context = get_sequence_lookup(lookup_type)
            sequence_list_df = search_context.get_sequence_list(gene_ids)
            output = list(search_context.get_rows(sequence_list_df))

            file_basename = f"{file_basename}-{lookup_type}"
            (csv, mimetype) = df_to_file(sequence_list_df, "csv", file_basename)
            csv_data = stream_to_base64_url(csv, mimetype)

            (xlsx, mimetype) = df_to_file(sequence_list_df, "xlsx", file_basename)
            xlsx_data = stream_to_base64_url(xlsx, mimetype)
        except SearchError as e:
            error = str(e)
            status_code = 404

    (html, page_data) = get_page("search")

    return render_template(
        'form.html',
        title=page_data.get('title', 'Search'),
        content=html,
        gene_ids=gene_ids,
        lookup_type=lookup_type,
        output=None if output is None else json.dumps(output),
        error=error,
        status_code=status_code,
        message=message,
        files=[
            {
                "name": f"{file_basename}.xlsx",
                "data": xlsx_data,
                "type": "XLSX"
            },
            {
                "name": f"{file_basename}.zip",
                "data": csv_data,
                "type": "CSV"
            }
        ]
    )


@app.route('/page/<page_id>', methods=['GET'])
def page(page_id):
    try:
        message = get_message(f'page/{page_id}')
        (html, page_data) = get_page(page_id)
        return render_template(
            'page.html',
            content=html,
            title=page_data.metadata.get('title', page_id),
            message=message,
        )

    except FileNotFoundError:
        return render_template('404.html', url=f'page/{page_id}'), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
