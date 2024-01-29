from flask import Flask, request, render_template, Response
from add import add
from placeholder import VectorOligoSearch

app = Flask(__name__)

@app.route('/')
def hello():
  return render_template('root.html')

@app.route('/form', methods=['POST', 'GET'])
# Sample form POST to get input and render result
def form():
    form_input = None
    output = None

    if request.method == 'POST':
        form_input = request.form['userInput']
        output = VectorOligoSearch(form_input)

    return render_template('form.html',
      input=form_input,
      output=output)

# Sample download generated CSV
@app.route("/get")
def getPlotCSV():
    genome_id = request.args.get('id')
    csv = VectorOligoSearch(genome_id)
    return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-disposition":
                 f"attachment; filename={genome_id}.csv"})

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8000)
