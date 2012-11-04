
Zero to Node: Node.js in Production
===================================

* * * * *

## Goal
### Describe how we did a particular project in Node.

* Hopefully helpful to others who want to work with Node.

* * * * *

## The Problem

* Teaching a language means teaching pronunciation.

* Users want to learn how to pronounce arbitrary text.

* We have a command-line text-to-speech (TTS) application.

* But our legacy PHP app to generate audio is broken.

* * * * *

## The Solution

### A node.js app.

* Ryan and Chris assert: **Node.js can do this**.

<img src='deck/img/nodejs.png' style='width: 35%'>

* Me: OK.

* Thus was born **cicero**.

* * * * *

## Yikes!

* Lots of users!
* New stack and framework!
* Async!

* * * * *

## What's this app really doing?

* Taking in a string and:

    * serving audio from cache, or
    * generating audio, serving to user, and saving in cache

* In other words, **slinging data**. Node can do that really well.

* It needs to be quick and stable.

* It needs to serve ~500 requests/minute.

* * * * *

## Getting started

Install is easy. Check nodejs.org for instructions.

* On OS X, using Homebrew:

<pre>$ brew install node</pre>

Recommended: Install NVM (node version manager).

* Allows multiple versions of Node to be installed at once.

* * * * *

## Dependencies

Node has **lots** of third-party packages.

Here's what I started with in `package.json`:

    # [some boilerplate...]
    "dependencies": {
       "config": "0.4.15",
       "express": "3.x",
       "underscore": "1.3.3",
       "deep-extend": "0.2.2",
       "validator": "0.4.10",
       "winston": "0.6.2"
     },
     "devDependencies": {
       "coffee-script": "1.3.3",
       "jshint": "0.7.1",
       "coffeelint": "0.4.0"
     }

Then use Node package manager (NPM) to install them all:

    $ npm install

* * * * *

## Modules

`require` allows importing third-party packages into our code.

`require`'ing is dead simple.

    express = require "express"

Modules are just js files.

    utils = require "./common/utils"

* * * * *

## Dev Environment

* Coffeescript: a must (for me).

<pre><code class="javascript">// JavaScript               # CoffeeScript

fn = function (args) {      fn = (args) ->
  return args;                args
};

var obj = {                 obj =
  key: value                  key: value
};
</code>
</pre>

* Grunt: watch, test, server.

* REPL? Eh.

* * * * *

## Config


`node-config` provides per-environment config.

In `project_root/config`:

* `default.js`, `development.js`, `production.js`
* `node-config` chooses based on `NODE_ENV` environment variable.

Sample:

    module.exports =
      app:
        addr: "0.0.0.0"
        port: 8004
      tts:
        input:
          maxChars: 200
        languages:
          available: ["en", "es"]

* * * * *

## Connect and Express

Connect (middleware) and Express (HTTP framework) provide:

* Routes:

<pre><code class="coffeescript">app = express()
app.get '/audio', (req, res) ->
   # Do route callback.
</code></pre>

* Middleware:

<pre><code class="coffeescript">middle = (req, res, next) ->
   # Process req, res. Call next.
   next()
</code></pre>

* Very flexible flow of control.

* * * * *

## Structure and Decomposition

Really up to you. Here's our project layout:

    /cicero
       |-config
       |    |--default.js
       |    |--development.js
       |-docs
       |-lib
       |  |--server
       |      |--index.js
       |      |--tts.js
       |-node_modules ...
       |-src
          |-config
          |   |--default.coffee
          |   |--development.coffee
          |-server
              |--index.coffee
              |--tts.coffee


* * * * *

## Structure and Decomposition

**`index.(coffee|js)`**

* docstring
* requires
* logger config
* app creation and config
* routing

* * * * *

## Structure and Decomposition

**`tts.(coffee|js)`**

* config
* `TtsArgs`
* `TtsExec`
* `TtsCache`

* * * * *

## Structure and Decomposition

At bottom of `tts.(coffee|js)`, `Tts*` objects expose middleware: fns with
signature `(req, res, next)`:

<pre><code class="coffeescript">module.exports =
  parseArgs:   TtsArgs.parse
  searchCache: TtsCache.search
  exec:        TtsExec.exec
</code></pre>

In `index.(coffee|js)`:

<pre><code class="coffeescript">tts = require "./tts"
# ...

middle = [log, tts.parseArgs, tts.searchCache, tts.exec]

app.get "/audio", middle
</code></pre>

* * * * *

## Async

* I started doing fs operations with sync methods like `fs.openSync`.

* But why is that a problem?

* Node is single-threaded.

* Anything that blocks can halt the entire process.

* * * * *

## Callbacks

First async paradigm.

<pre><code class="coffeescript">fs.open path, 'r', (err, file) ->
  # In callback function with signature (err, file),
  # can do something with file now that it's ready, or
  # handle error if one occurred.
</code></pre>
* * * * *

## Events

Second async paradigam.

    # Create our process object.
    process = spawn 'tts_command', args, options

    # Listen for error event.
    stderr = ""
    process.stderr.on "data", (data) ->
      # Accumulate data.
      stderr += data

    # Listen for exit event.
    process.on "exit", (code) ->
      # Check errors, exit.
      if stderr or code isnt 0
        return new Error(stderr ? "TTS failed")

* * * * *

## Streams

* Streams are a powerful way of thinking about IO.
* Streams can be readable, writeable, or both.
* Can pipe readable into writeable.
* Streams emit events:

    * Readable: a bunch of `data` events and one `end` event.
    * Writeable: `drain`, `pipe`, `close` events.

### Why use streams?

* Avoid 'procrastination', i.e., buffering data in memory. Send it as
available/ready from the OS. Smooths out CPU and network load.
* Easy to reason about.

* * * * *

## Streams

Stream audio file to HTTP response (`res`) and S3 cache (`s3Stream`):

<pre><code class="coffeescript"># Get stream references to audio file and S3.
fileStream = fs.createReadStream tmpAudioFile
s3Stream = getCloudStream(res)

# Let the streaming begin!
fileStream.pipe(res)
tmpStream.pipe(s3Stream)

fileStream.on "error", errHandle
s3Stream.on "error", errHandle

fileStream.on "end", ->
  # Do cleanup (delete tmpAudioFile)
</code></pre>

* * * * *

## Logging

Gain visibility into what your app is doing.

* winston library
    * Allows multiple transports (e.g., console, filesystem, third-party service)
    * Logs JSON:
<pre><code>{
  "date": "2012-10-28T15:17:02.513Z",
  "level": "info",
  "env": "production",
  "type": "server",
  "serverHost": "inkling",
  "serverId": "m",
  "serverPid": 99632,
  "serverName": "prod-server",
  "addr": "0.0.0.0",
  "port": 2003,
  "vers": "v0.8.9",
  "deploy": "cicero",
  "message": "Server started on port 2003."
}
</code></pre>

* * * * *

## Provision and Deploy

* Many ways you could do this.
* We use Chef and AWS.
* Find Chef cookbooks online and customize when necessary.
* Time to deploy? Update version and Chef takes of the rest.

* * * * *

## Monitoring

* Again, many ways to do this.
* We use a service called Scout.
* Scans output from logging.

<img src='deck/img/scout.png'>

* * * * *

## Challenges

* Thinking async.
* Newness/rapid development.
* DIY / FIOY (figure it out yourself).
* Minimalism sometimes extends to docs!

* * * * *

## Links

#### Docs
* Node docs: http://nodejs.org/api (Make sure to get right version, Google is often behind!)
* Express docs: http://expressjs.com

#### Community
* Nodejitsu: http://docs.nodejitsu.com
* How to Node: http://howtonode.org

#### Coffee-script
* http://coffeescript.org/

#### Chef
* nodejs cookbook: http://community.opscode.com/cookbooks/nodejs
* node app cookbook: http://community.opscode.com/cookbooks/node

* * * * *

## Thanks!

@williamjohnbert

http://williamjohnbert.com

SpanishDict is hiring! http://spanishdict.com/careers
