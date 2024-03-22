from flask import (
    Flask,
    request,
    render_template,
    Response,
    json,
    make_response,
    jsonify
)
import io
import csv
from itertools import chain
from search.oligo_search import search, search_to_file
from search.search import SearchError


app = Flask(__name__)

@app.route('/')
def root():
    return render_template('root.html')

@app.route('/search', methods=['POST', 'GET'])
def form():
    form_input = None
    output = None
    error = None
    status_code = 200

    if request.method == 'POST':
        try:
            form_input = request.form['gene-id']
            output = search([form_input])
        except SearchError as e:
            error = str(e)
            status_code = 404

    return render_template(
      'form.html',
      input=form_input,
      output=output,
      error=error,
      status_code=status_code,
    )


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
