import psutil
from flask import Flask, request, abort

app = Flask(__name__)


@app.route('/')
def index():
    return '''
    <p>Endpoints:</p><br/>
    <ul>
        <li><li><a href="/processes">/processes</a> - list of all system processes, 
        to filter results use `mem-above` and/or `threads-above` query string arguments, 
        e.g. <a href="/processes?mem-above=5">/processes?mem-above=5</a> returns processes 
        that consume more than 5% of system memory, 
        <a href="/processes?mem-above=5&threads-above=25">/processes?mem-above=5&threads-above=25</a> 
        returns all processes that consume more than 5% of system memory and have more than 25 threads running</li>
        <li><a href="/processes/<pid>">/processes/&lt;pid&gt;</a>, 
        e.g. <a href="/processes/0">/processes/0</a> - info of a process with a &lt;pid&gt;</li>
        <li>POST <a href="/processes/<pid>/kill">/processes/&lt;pid&gt;/kill</a>, 
        e.g. <a href="/processes/0/kill">/processes/0/kill</a> - terminate process with a &lt;pid&gt;</li>
    </ul>
    '''


@app.route('/processes')
def processes():
    response = {}
    mem_above = request.args.get('mem-above')
    threads_above = request.args.get('threads-above')
    for proc in psutil.process_iter():
        if mem_above and proc.memory_percent() <= float(mem_above):
            continue
        if threads_above and proc.num_threads() <= float(threads_above):
            continue
        response[proc.pid] = proc.as_dict(
            attrs=['pid', 'name', 'memory_percent', 'num_threads']
        )

    return response


@app.route('/processes/<pid>')
def process(pid):
    try:
        return psutil.Process(int(pid)).as_dict(
            attrs=['pid', 'name', 'memory_percent', 'num_threads']
        )
    except (psutil.NoSuchProcess, ValueError):
        abort(404)


@app.route('/processes/<pid>/kill', methods=['GET', 'POST'])
def kill(pid):
    try:
        proc = psutil.Process(int(pid))
    except (psutil.NoSuchProcess, ValueError):
        abort(404)

    if request.method == 'POST':
        try:
            proc.terminate()
            return f'Process {pid} killed successfully'
        except psutil.AccessDenied:
            return f'Insufficient permissions to kill process {pid}'
    else:
        return 'Use POST request to kill the process'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
