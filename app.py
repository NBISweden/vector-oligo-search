from flask import Flask, request, render_template, Response
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
            output = search(form_input)
        except SearchError as e:
            error = str(e)

    return render_template(
      'form.html',
      input=form_input,
      output=output,
      error=error
    )

@app.route("/get")
def get_csv():
    genome_id = request.args.get('id')
    csv = search(genome_id)
    return Response(
        csv,
        mimetype="text/csv",
        headers={
            "Content-disposition":
                f"attachment; filename={genome_id}.csv"
            }
        )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
