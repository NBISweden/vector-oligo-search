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
from search.oligo_search import search
from search.search import SearchError


app = Flask(__name__)

@app.route('/')
def root():
    return render_template('root.html')

@app.route('/form', methods=['POST', 'GET'])
def form():
    form_input = None
    output = None
    error = None

    if request.method == 'POST':
        try:
            form_input = request.form['gene-id']
            output = json.dumps(search([form_input]))
        except SearchError as e:
            error = str(e)
            make_response(jsonify(message), status_code)

    return render_template(
      'form.html',
      input=form_input,
      output=output,
      error=error
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
    fieldnames = ['GENE ID', 'Oligo sequence']
    csv_io = io.StringIO()
    writer = csv.DictWriter(csv_io, fieldnames=fieldnames)
    writer.writeheader()
    results = search(gene_ids)
    for item in results:
        writer.writerow(
            {
                'GENE ID': item.gene_id,
                'Oligo sequence': item.sequence
            }
        )

    output = csv_io.getvalue()
    return Response(
        output,
        mimetype="text/csv",
        headers={
            "Content-disposition":
                "attachment; filename=oligo-sequences.csv"
            }
        )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
