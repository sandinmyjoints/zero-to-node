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

Insert into deck/presentation.html.

"""

SECTION = """</section>
             <section class="slide">"""

notes_re = r"<p>Notes:</p>(.*?)<hr />"
hr_re    = r"<hr />"
body_open_re = r'(<body>)'
body_close_re  = r'(</body>)'
link_re  = r'http://(.*?)( |</li>)'

md = open("presentation.md").read()
pres = markdown.markdown(md)

pass1 = re.sub(notes_re, '<div class="notes">\\1</div><hr />', pres, flags=re.DOTALL)
pass2 = re.sub(hr_re, SECTION, pass1, flags=re.DOTALL)
pass3 = re.sub(link_re, '<a href="http://\\1">\\1</a> ', pass2)

slides = '<section class="slide">' + pass3 + '</section>'

existing_pres = open("./deck/presentation.html").read()

# insert into boilerplate

final = re.sub(r'(<body.*?>).*(<!-- Begin extension)', '\\1\n' + slides + '\n\\2', existing_pres, flags=re.DOTALL)
#print "\n\nwriting", final[-2500:-1000]

new_pres = open("./deck/presentation.html", "w")
new_pres.write(final)
new_pres.close()
