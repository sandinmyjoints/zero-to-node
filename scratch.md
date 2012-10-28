SpanishDict recently deployed a new text-to-speech service
powered by Node. This service can generate audio files on
the fly for arbitrary Spanish and English texts with rapid
response times. The presentation will walk through the
design, development, testing, monitoring, and deployment
process for the new application. We will cover topics like
how to structure an Express app, testing and debugging,
learning to think in streams and pipes, writing a Chef
cookbook to deploy to AWS, and monitoring the application
for high performance. The lead engineer on the project,
William Bert, will also talk about his experiences
transitioning from a Python background to Node and some of
the key insights he had about writing in Node while
developing the application.


# Ryan's presentation

http://ryan-roemer.github.com/novanode-cloud-talk/




Design, write, test, and deploy a node app in a high-traffic
production setting serving one specific task.


* * * * *

Notes:

So we'll write a node app. We use a lot of node here. We use
it for making user input suggestions, providing
translations, connecting to the database. It has worked well
for us so far. Plus, Ryan did all those, and now he's got a
new guy who needs to get up to speed. So the new guy can do
it.

What's it do? Sling data. Take in a string and return an
mp3.


* * * * *


X Add to head:

<script src="extensions/markdown/Markdown.Converter.js"></script>
<script src="extensions/markdown/deck.markdown.js"></script>

Each time:

Markdown export C-c C-c e to generate html



Replace <p>Notes: to <hr /> with:
<div class="notes">
$1
</div>

Replace <hr /> with:
</section>
<section class="slide">

After body:
<section class="slide">

Before /body:
</section>

Insert into deck/presentation.html.
