#!flask/bin/python
from werkzeug.contrib.profiler import ProfilerMiddleware
from app import app

app.config['PROFILE'] = True
app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])
app.run(debug = True)
#ncalls: number of times this function was called.
#tottime: total time spent inside this function.
#percall: this is tottime divided by ncalls.
#cumtime: total time spent inside this function and any functions called from it.
#percall: cumtime divided by ncalls.
#filename:lineno(function): the function name and location.