## Prep
* Audio sample to play: fantastico, java script

## Slide 1 - Title

* Hi, thanks for coming. 
* I'm William Bert, a software engineer at SpanishDict. I joined in August.
* My talk is titled Zero to Node. It's a case study of deploying node.js in
  production based on a project I worked on in my first month here.

## Slide 2 - Goal

* My goal is to describe what it was like to begin with node, and get a service
into production
* I hope to help others who are interested in Node to do something similar.
* My background: I worked mostly with Python and Django previously, though this
  presentation should hopefully be generally applicable to anyone interested in
  node.
* A quick disclaimer: I'm not a node expert. I'm still learning. My experience
  is fairly limited.
* If you're looking for expert advice, I might not be able to help, but the
  internet is your best bet.

## Slide 3 - The Problem

* SpanishDict.com is an English-Spanish language learning website. Part of
teaching language is teaching pronunciation. Pronunciation is taught by hearing
words pronounced correctly.
* Users are arbitrary--they want to hear how to pronounce whatever words they
  want to learn!
* We have a text to speech (TTS) product that actually does a pretty good job of
pronouncing arbitrary Spanish and English text (play samples).
* The TTS application is enterprise software that only runs on the command line,
but our old PHP app is not working well and not worth repairing.

## Slide 4 - The Solution

* The solution is (you may have guessed) a node app.
* Ryan and Chris assert it can do this. I say, OK.
* The team has experience with Node. We use a lot of node here:
* We use it for making user input suggestions, providing translations,
connecting to the database backend. It has worked well for us so far.
* Ryan did all those, and now he's got a new guy who needs to get up to
speed. So the new guy--me--can do it.
* Thus is born Cicero, the name we gave to our application.

## Slide 5 - Yikes!

* This is my internal reaction.
* Lots of users!
* New stack and framework!
* Async!
* New to server-side Node! Learning curve. 
* Where to start? Hopefully my experience can help you.

## Slide 6 - What's this app really doing

* Taking in a string and

    * serving audio from cache, or
    * generating audio, serving to user, and caching
    
* In other words, **slinging data**. Node can do that really well.
* We need to serve the audio quickly (very quickly) and efficiently.
* This isn't a core service, but a nice add-on.
* We just want to forget about it. We want stability, relatively low resources,
simplicity so easy to maintain.
* We'll serve ~500 requests/minute.
* So now the problem is well understood.

## Slide 7 - Getting started

* Install is easy on any platform. Here's how to do it on OS X with Homebrew
  (see slide).
* We installed `nvm`, node version manager, which allows you to have
  multiple node versions installed at once. This is useful because node is
  updated all the time.
* This way, you can try out new versions and switch when ready. Different apps
  can use different versions.
* We're going into production, so there's a little more to installation than
  just this.

## Slide 8 - Dependencies

* Node has **lots** of third-party packages.
* We used Node package manager (npm) to install some packages out of the gate
  to get the most out of node. We'll talk about what they do in a minute.
* Npm is dead simple. 
* Put a list of packages and versions in `package.json` (see docs for
  boilerplate).
* Do `npm install`.
* Npm installs everything and their dependencies into `node_modules`.

## Slide 9 - Modules

* Now that our third-party packages are installed, how do we use them in our
  code? We require them in as modules.
* Node uses a specification called Common JS that allows us to import Javascript
  files as modules.
* Require'ing is dead simple. Since modules are just js files, we can import,
  for example, `express` like this.
* Since they're just just js files, we can import our own code too (see slide).

## Slide 10 - Dev Env

* I'll briefly describe my dev environment.
* Coffescript is "a little language that compiles to Javascript."
* Coffescript looks better, more readable, significant whitespace. It reminds me
  of Python. Also hear it's like Ruby.
* Coffescript is really "the best parts of Javascript". Protects you from
  tripping on some gotchas like global variables, semicolon insertion, weird
  type coercion.
* Quick CS explanation (see slide)
* My examples are in CS. Ask if anything is unclear about it.
* Grunt: Command line dev tool. Very useful for tasks: watch, test, server. Like
  Rake in Ruby.

## Slide 11 - Config

* So let's get started with our application. First, handling configuration.
* `node-config` is one of the modules we installed above.
* It provides runtime configuration control for node deployments.
* Define config files per environment. (see slide)

## Slide 12 - Connect and Express

* Express is a node HTTP framework built on Connect, which is a middleware
  framework.
* They're so much part of my node experience that I almost forget they are their own
  things because they provide essentials: routes and middleware (see slide).
* Deceivingly simple, extremely flexible.
* Think mostly in terms of middleware. Pass requests through chain of
  middleware. Middleware are functions that take req, res, do something, and
  call the next middleware function.
* Example: logging. You get a request to '/audio', pass to log middleware first,
  it logs the request, then passes to next, which parses the query string
  parameters, then next, etc.
* We can send some routes through some middleware, like auth, but others will go
  through different middleware.

## Slide 13 - Structure and Decomposition - Project layout

* Node is ripe for structuring. It's entirely up to you, unlike Django or RoR.
* So here's what we did for Cicero:
* First, directory structure. It's slightly more complicated because we used
  Coffee-script.
* I'm going to skip down to the source directory  (see slide)
* index.coffee and tts.coffee are the main source code files.
* grunt compiles from src/server into lib, from src/config into config.

## Slide 14 - S and D - Index

* Now, structure within the code modules.
* At first I put all my code in one file. It worked. 
* It wasn't a terribly long file, but it's better to structure for long-term
  readability and maintenance.
* But how? In Django, you have resuable apps that have models.py and urls.py and
  views.py, etc. None of that here!
* Everything is so flexible, so it's up to you. It's preferences, not dictated.
* Ryan sat me down and we broke them up. 
* First: index. Index holds mostly sort of boilerplate-y stuff (see slide).
* But it's important: it ensures you'll get logging and your routes will work.
* Separate from app logic.

## Slide 15 - S and D  - Tts

* config: Read runtime config from files
* Then structure by function: it's all exposed as middleware. We're free to
  break up within the code as we see fit
* For these, we used Coffescript classes basically as namespaces, just js
  objects that encapsulate related code. 
* TtsArgs: Process the arguments from query string params to command line flags
* TtsExec: Spawn the process and get its results
* TtsCache: Look for audio mp3 for some particular user input in cache. Serve it
  if it's there, otherwise store it.

## Slide 16 - S and D - How to use as middleware

* How to use middleware? Middleware is just a function that takes `(req, res,
  next)`, does something, and calls next, possibly passing an error.
* Every request goes through this chain:
  * process args
  * search cache, return if found
  * exec tts if not in cache, store in cache

## Slide 17 - Async

* So now that we've laid out the app structure, I'm going to discuss one of the
  techniques used within the app: async control flow.
* I looked at some early commits and found sync methods.
* Sync is a problem because Node is single-threaded, so one blocking call can
halt everything in the entire Node process, or if not halt, then slow down.
* Node is designed for async, everything in the std lib and the ecosystem
  supports async, and async works well in practice for web apps, so I wanted to
  be sure to use it.
* Async: I understood it in theory, but had limited exposure in practice.

## Slide 18 - Callbacks

* First async paradigm: callback functions.
* They are functions that are called once something is ready. In other words,
  they are deferred execution.
* They are kind of the building blocks of Node async.
* This example shows how to open a file.
* The flow is fairly straightfoward: start this operation, keep going with
  whatever comes next, but when this operation is done, execute this code.

## Slide 19 - Events

* Events are the next async paradigm I encountered.
* Events are like arbitrary callbacks--an event emitter object can emit them
  whenever some condition occurs, like receiving data, or encountering an error.
* (see slide) We create the process object, init stderr, and register the event
  handlers, all synchronously within one 'tick'.
* A 'tick' is one trip around the event loop. Node is continuously running this
  event loop, and on each trip around event loop: node asks, is it time to fire
  this callback? execute this event handler? etc.
* So on subsequent ticks, if our process has triggered 'data' or 'exit' events,
  the cbs execute (synchronously inside each)
* Using this event loop/async event paradigm mean node effectively never blocks;
  it only executes code when the condition that code is supposed to handle has
  occurred. This is especially useful for I/O bound applications like HTTP
  servers: we don't block for network input or filesystem operations while
  complete; they can run and node is free to keep serving requests.

## Slide 20 - Streams

* So I got comfortable with callbacks first. And events. Then Ryan says to
  switch to streams.
* Streams are another async paradigm. Powerful abstraction for IO.
* Streams are like pipes in unix. Send output of something directly as input to
  something else.
* Can be readable, writeable, both. Can pipe readable into writeable.
* Why use streams?
* Avoid buffering data in memory. Send it as available/ready from the
OS. Smooths out CPU and network load. Users see faster response.
* Easy to reason about.

## Slide 21 - Stream example

* Here's an example use of streams to return audio data (see slide).
* Note that one readable stream is piping to two totally separate writeable
  streams simultaneously. Node and the OS handle all that for us.
* Listen for events. Handle end and error events, particularly.
* Ideal would be to stream directly from the TTS application without touching the
filesystem, but the application is picky and uncooperative.

## Slide 22 - Logging 

* Now that we have our app working, let's start thinking about operations and
  maintenance.
* Logging allows you visibility into what your app is doing.
* This is very important for production deployment so you know the app is
  working correctly, or if it breaks, you know what is going wrong.
* We use a library called Winston for logging.
* Configure multiple transports: 
* log to console in dev.
* log to filesystem and a service (e.g., Loggly) in production.
* It outputs JSON instead of a big string blob.
* We can data mine these logs later for diagnosing any problems, or also for
  business value, say, what kinds of words or phrases do people tend to want to
  pronounce?

## Slide 23 - Provisioning and Deployment

* There are many ways you could do this. It's a big topic.
* We use Chef for provisioning and deployment. Chef is "an open-source systems
  integration framework built specifically for automating the cloud."
* That means we can control our servers through code. 
* We write cookbooks that describe how to configure machines, then Chef executes
  those cookbooks and actually configures machines.
* AWS is our IAAS provider. They give us raw machines to use. Chef is how we
  control them.
* A lot of kinds of Chef cookbooks are available online. You can use the off the
  shelf or customize them fairly easily.
* Ryan wrote our general node webapp cookbook.
* I wrote a tts webapp cookbook which extends that for cicero.
* Once the cookbook is written, we can use Chef to start, stop, and deploy our
  app with one or two commands. Quick and convenient.

## Slide 24 - Monitoring

* In production, you can't read the voluminous logs, so monitoring aggregates
  the logs and gives even better visibility into your app's operation.
* Again, there are many ways to do this.
* We use a service called Scout.
* It simple scans output from logging, and produces realtime charts like this.
* We configure alerts so that if the number of requests drops below a threshold,
  or the amount of memory used goes above a threshold, we get emails or texts.

<img src='deck/img/scout.png'>


## Slide 25 - Challenges

* Async means wrapping your head around a new kind of flow control if you're
  used to sync. Debug is a little messier, but tolerable.
* Newness and rapid development mean best practices aren't always well known,
  and change frequently. Need to keep up with the community.
* Seems to be a DIY/FIOY attitude, which you may like or not, depending on your
  temperment, your task, and your deadlines.
* Minimalism of node/express sometimes extends to docs. Aesthetically pleasing,
  but frustrating when you're trying to understand something. Always good to
  look at source.

## Slide 25 - Links

* Official
    * Node docs -- make sure to get right version, Google is behind
    * Express
* Community
    * Nodejitsu is a PAAS provider that has a good community site.
    * How to Node
* Other
    * Coffee-script

## Slide 26 - Thanks and Questions

* Thanks!
* I will put slides online at my website.
* Quick note: If this sounded interesting, SpanishDict is hiring. Talk to me,
  Chris, or Ryan.
* Questions?
