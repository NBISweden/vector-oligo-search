from flask import Flask, request, render_template
from add import add

app = Flask(__name__)

@app.route('/')
def hello():
  return render_template('root.html')

@app.route('/form', methods=['POST', 'GET'])
def form():
    form_input = None
    a = 0
    b = 0

    if request.method == 'POST':
        form_input = request.form['userInput']
        a = int(request.form['a'])
        b = int(request.form['b'])
    math = add(a, b)
    return render_template('form.html',
      input=form_input,
      math=math)

if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8000)
