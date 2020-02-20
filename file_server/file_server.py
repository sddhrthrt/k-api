from flask import Flask, request, abort
import sys, os
app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello!"

def test():
    word = request.args.get('index')
    try:
        word = int(word)
        return contents[word]
    except ValueError as v:
        abort(400)
    except IndexError as i:
        abort(400)

if __name__ == "__main__":
    url = '/test'
    if len(sys.argv) > 1:
        url = os.path.join('/', sys.argv[1])
    app.add_url_rule(url, 'test', view_func=test)
    contents = open("file.txt", 'r').read().split(' ')
    app.run(host='0.0.0.0')
