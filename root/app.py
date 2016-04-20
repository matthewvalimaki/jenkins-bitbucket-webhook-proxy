from flask import Flask
from flask import request
from flask import make_response
from unirest import post

app = Flask(__name__)

@app.errorhandler(Exception)
def exception_handler(error):
    return "!!!!"  + repr(error)

@app.route('/build', methods = ['POST'])
def build():
  jenkins = request.args.get('jenkins')
  jenkins = jenkins if jenkins.startswith('http://') or jenkins.startswith('https://') else 'http://%s' % jenkins
  jenkins = jenkins[:-1] if jenkins.endswith('/') else jenkins
  job = request.args.get('job')
  token = request.args.get('token', None)
  dockerfiles = request.args.get('dockerfiles', None)
  query = '' if token is None else 'token=%s' % token
  
  if dockerfiles is not None:
    query += '&dockerfiles=' + dockerfiles

  json = request.json

  if 'push' in json:
    params = {'git_hash': json['push']['changes'][0]['new']['target']['hash']}
  else:
    params = {
      'git_hash': json['changesets']['values'][0]['toCommit']['displayId'],
      'slug': json['repository']['slug'],
      'project_key': json['repository']['project']['key']
    }

  # forward the request
  jenkins_url = '%s/job/%s/buildWithParameters?%s' % (jenkins, job, query)
  response = post(jenkins_url, params = params)

  if (response.code in range(400, 500)):
    return "Request error"
  elif (response.code >= 500):
    return "Server error"
  else:
    return make_response(response.raw_body, response.code, {})

@app.route('/', methods = ['GET'])
def index():
  return "OK"


if __name__ == '__main__':
    app.run(host = '0.0.0.0')
