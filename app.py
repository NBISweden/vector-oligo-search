from flask import (
    Flask,
    request,
    render_template,
    Response,
    json,
    make_response,
    jsonify,
    redirect
)
import io
import csv
import logging
from itertools import chain
from search.oligo_search import search, search_to_file
from search.search import SearchError
import frontmatter
import markdown


logger = logging.getLogger(__name__)
app = Flask(__name__)


@app.route('/')
def root():
    return redirect("page/home")


@app.route('/search', methods=['POST', 'GET'])
def form():
    gene_ids = []
    output = None
    error = None
    status_code = 200

    if request.method == 'POST':
        try:
            gene_id = request.form['gene-id']
            gene_list = request.form.get('gene-list', "").strip()
            gene_ids = (
                [gene_id] if len(gene_list) == 0
                else [g.strip().rstrip('\r\n') for g in gene_list.split("\n")]
            )
            output = search(gene_ids)
        except SearchError as e:
            error = str(e)
            status_code = 404

    return render_template(
      'form.html',
      gene_ids=gene_ids,
      output=output,
      error=error,
      status_code=status_code,
    )


@app.route('/page/<page_id>', methods=['GET'])
def page(page_id):
    page_path = f'pages/{page_id}.md'
    try:
        with open(page_path, "r") as f:
            page_data = frontmatter.load(f)
            html = markdown.markdown(page_data.content)
            return render_template(
                'page.html',
                content=html,
                title=page_data.metadata.get('title', "Default title")
            )
    except FileNotFoundError:
        return render_template('404.html', url=f'page/{page_id}'), 404


@app.route('/oligo-search')
def oligo_search():
    gene_ids = request.args.getlist('gene-id')
    try:
        output = search(gene_ids)
        return jsonify(output)
    except SearchError as e:
        error = str(e)
        return make_response(jsonify({"error": error}), 404)

    
@app.route("/get")
def get_data():
    gene_ids = request.args.getlist('gene-id')
    format = request.args.get('format', 'csv')
    (output, ext) = search_to_file(
        gene_ids,
        output_format=format
    )
    return Response(
        output,
        mimetype="text/csv",
        headers={
            "Content-disposition":
                f"attachment; filename=oligo-sequences.{ext}"
            }
        )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
