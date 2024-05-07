from flask import (
    Flask,
    request,
    render_template,
    json,
    redirect
)
import logging
from search.oligo_search import (
    get_sequence_list,
    df_to_file,
    df_to_search_result
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
app.secret_key = "myverysecretkey"
Compress(app)


@app.route('/')
def root():
    return redirect("page/home")


def parse_gene_ids(gene_id=None, gene_list=None):
    gene_list = ("" if gene_list is None else gene_list).strip()
    gene_ids = [] if gene_id is None else [gene_id]
    gene_ids = (
        gene_ids if len(gene_list) == 0
        else [g.strip().rstrip('\r\n') for g in gene_list.split("\n")]
    )
    return list(set(gene_id for gene_id in gene_ids if gene_id))


@app.route('/search', methods=['POST', 'GET'])
def form():
    gene_ids = []
    output = None
    error = None
    status_code = 200
    csv_data = None
    xlsx_data = None

    if request.method == 'POST':
        gene_ids = parse_gene_ids(
            request.form.get('gene-id'),
            request.form.get('gene-list')
        )

    if len(gene_ids) > 0:
        try:
            sequence_list_df = get_sequence_list(gene_ids)
            output = list(df_to_search_result(sequence_list_df))

            (csv, mimetype) = df_to_file(sequence_list_df, "csv")
            csv_data = stream_to_base64_url(csv, mimetype)

            (xlsx, mimetype) = df_to_file(sequence_list_df, "xlsx")
            xlsx_data = stream_to_base64_url(xlsx, mimetype)
        except SearchError as e:
            error = str(e)
            status_code = 404

    return render_template(
        'form.html',
        gene_ids=gene_ids,
        output=None if output is None else json.dumps(output),
        error=error,
        status_code=status_code,
        files=[
            {
                "name": "oligo-vector-sequence.xlsx",
                "data": xlsx_data,
                "type": "XLSX"
            },
            {
                "name": "oligo-vector-sequence.zip",
                "data": csv_data,
                "type": "CSV"
            }
        ]
    )


@app.route('/page/<page_id>', methods=['GET'])
def page(page_id):
    page_path = f'pages/{page_id}.md'
    try:
        with open(page_path, "r") as f:
            page_data = frontmatter.load(f)
            html = markdown.markdown(
                page_data.content,
                extensions=[TocExtension(baselevel=1)]
            )
            return render_template(
                'page.html',
                content=html,
                title=page_data.metadata.get('title', "Default title")
            )
    except FileNotFoundError:
        return render_template('404.html', url=f'page/{page_id}'), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
