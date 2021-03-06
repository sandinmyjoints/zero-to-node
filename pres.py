import re
import markdown
"""

Replace <hr /> with:
</section>
<section class="slide">

After body:
<section class="slide">

Before /body:
</section>

Insert into index.html.

"""

SECTION = """</section>
             <section class="slide">"""

notes_re = r"<p>Notes:</p>(.*?)<hr />"
hr_re    = r"<hr />"
link_re  = r'http://(.*?)($| |</)'

md = open("presentation.md").read()
pres = markdown.markdown(md)

pass1 = re.sub(notes_re, '<div class="notes">\\1</div><hr />', pres, flags=re.DOTALL)
pass2 = re.sub(hr_re, SECTION, pass1, flags=re.DOTALL)
pass3 = re.sub(link_re, '<a href="http://\\1">\\1</a>\\2', pass2)

slides = '<section class="slide">' + pass3 + '</section>'

existing_pres = open("./index.html").read()

final = re.sub(r'(<body.*?>).*(<!-- Begin extension)', '\\1\n' + slides + '\n\\2', existing_pres, flags=re.DOTALL)
#print "\n\nwriting", final

with open("./index.html", "w") as new_pres:
    new_pres.write(final)
