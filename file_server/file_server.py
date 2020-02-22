from flask import Flask, request, abort
import sys, os
app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello!"

@app.errorhandler(404)
def page_not_found(e):
    return "File Server: 404", 404

def nth_word():
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
    print(f"serving for URL path {url}...")
    app.add_url_rule(url, 'nth_word', view_func=nth_word)
    contents = open("file.txt", 'r').read().split(' ')
    app.run(host='0.0.0.0')
