
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

Recommended: Install NVM (Node version manager).

* Allows multiple versions of Node to be installed at once.
* Useful for trying out new versions (which are released often).

* * * * *

## Dependencies

* Node has **lots** of third-party packages.

* Available via Node package manager (NPM).

* First, specify dependencies in `package.json`:

<pre><code class="javascript">"dependencies": {
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
</code></pre>

* Then NPM will install into `node_modules`:

<pre><code>$ npm install</code></pre>

* * * * *

## Modules

`require` allows importing third-party packages into our code.

`require`'ing is very simple:

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

## Configuration

`node-config` provides per-environment config.

Place config files In `cicero/config` directory:

* `default`
* `development`
* `production`

`node-config` chooses based on `NODE_ENV` environment variable.

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

## Express and Connect

Express (HTTP framework) and Connect (middleware) and provide:

* Routes:

<pre><code class="coffeescript">express = require 'express'
app = express()
app.get '/audio', (req, res) ->
  # Process request...
  # When finished, send response:
  res.send 200, responseData
</code></pre>

* Middleware:

<pre><code class="coffeescript">middle = (req, res, next) ->
   # Process request...
   # When finished, move on to next middleware:
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

**`index.coffee`**

* docstring
* requires
* logger config
* app creation and config
* routing

* * * * *

## Structure and Decomposition

**`tts.coffee`**

* config
* `TtsArgs`
* `TtsExec`
* `TtsCache`

* * * * *

## Structure and Decomposition

`tts.coffee` exposes middleware functions (signature is `(req, res,
next)`):

<pre><code class="coffeescript">module.exports =
  parseArgs:   TtsArgs.parse
  searchCache: TtsCache.search
  exec:        TtsExec.exec
</code></pre>

In `index.coffee`:

<pre><code class="coffeescript">tts = require "./tts"
# ...

middle = [log, tts.parseArgs, tts.searchCache, tts.exec]

app.get "/audio", middle
</code></pre>

* * * * *

## Async

* I started cicero doing filesystem operations with sync methods like
  `fs.openSync`.

* But why is that a problem?

* Node is single-threaded.

* Anything that blocks can halt the entire process.

* * * * *

## Callbacks

First async paradigm.

<pre><code class="coffeescript">fs.open path, 'r', (err, file) ->
  # In callback function.
  
  # Handle error if err is non-null:
  handleError err if err

  # Otherwise, everything went ok, and we can do something
  # with file now that it's ready...
</code></pre>
* * * * *

## Events

Second async paradigam.

    # Create our process object.
    ttsProcess = spawn 'tts_command', args, options

    # Listen for error event.
    stderr = ""
    ttsProcess.stderr.on "data", (data) ->
      # Accumulate data from stderr.
      stderr += data

    # Listen for exit event.
    ttsProcess.on "exit", (code) ->
      # Check errors, exit.
      if stderr or code isnt 0
        return new Error(stderr ? "TTS failed")

* * * * *

## Streams

* Streams are a powerful way of thinking about IO.
* Send output of something directly as input to something else (like pipes in
  Unix).
* Streams can be readable, writeable, or both.
* Can pipe readable into writeable.

### Why use streams?

* Avoid 'procrastination', i.e., buffering data in memory. Send it as
available/ready from the OS. Smooths out CPU and network load.
* Easy to reason about.

* * * * *

## Streams

Stream audio file to HTTP response (`res`) and S3 cache (`s3Stream`):

<pre><code class="coffeescript"># Get readable stream reference to audio file.
fileStream = fs.createReadStream tmpAudioFile

# res is our HTTP response object, and it's a writeable stream.
# s3Stream is our writeable stream to Amazon S3.
# Let the streaming begin!
fileStream.pipe(res)
fileStream.pipe(s3Stream)

# Listen for error events.
fileStream.on "error", errHandle
s3Stream.on "error", errHandle

# Cleanup on end event.
fileStream.on "end", ->
  # Do cleanup (delete tmpAudioFile)
</code></pre>

* * * * *

## Logging

Gain visibility into what your app is doing.

* Winston library
    * Allows multiple transports (e.g., console, filesystem, third-party service)
    * Logs JSON:
<pre><code>{
  "date": "2012-10-28T15:17:02.513Z",
  "level": "info",
  "env": "production",
  "type": "server",
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
* We use Chef and Amazon Web Services (AWS).
* Find Chef cookbooks online and customize when necessary.
* Time to deploy? Update version and Chef takes of the rest.

* * * * *

## Monitoring

* Again, many ways to do this.
* We use a service called Scout.
* Scans output from logging.

<img src='deck/img/scout.png'>

* * * * *

## Summing Up

### Results

* Cicero meets our needs

### Node Challenges

* Thinking async.
* Newness/rapid development.
* DIY / FIOY (figure it out yourself).
* Minimalist aesthetic sometimes extends to docs.

* * * * *

## Links

#### Docs
* Node docs: http://nodejs.org/api (Make sure to get right version, Google is often behind!)
* Express docs: http://expressjs.com

#### Community
* Nodejitsu: http://docs.nodejitsu.com
* How to Node: http://howtonode.org

#### Coffee-script
* http://coffeescript.org

#### Chef
* nodejs cookbook: http://community.opscode.com/cookbooks/nodejs
* node app cookbook: http://community.opscode.com/cookbooks/node

* * * * *

## Thanks!

@williamjohnbert

http://williamjohnbert.com

SpanishDict is hiring! http://spanishdict.com/careers
