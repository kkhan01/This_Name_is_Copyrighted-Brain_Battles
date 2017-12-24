from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')                                                                 
def root():
    return render_template('default.html')
@app.route('/login')                                                            
def login():
    return render_template('login.html')

@app.route('/dummy')                                                            
def dummy():
    return render_template('dummy.html')

@app.route('/simon')
def simon():
    return render_template('simon.html')

if __name__ == '__main__':
    app.debug = True
    app.run()
