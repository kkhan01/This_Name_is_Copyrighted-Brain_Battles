from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')                                                                 
def root():
    return render_template('default.html')

@app.route('/dummy')                                                            
def dummy():
    return render_template('dummy.html')

if __name__ == '__main__':
    app.debug = True
    app.run()
