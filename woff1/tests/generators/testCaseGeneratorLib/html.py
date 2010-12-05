"""
Test case HTML generator.
"""

import os
import codecs

# ------------------
# SFNT Display Tests
# ------------------

testPassCharacter = unichr(int("E000", 16))
testFailCharacter = unichr(int("E001", 16))
refPassCharacter = testPassCharacter

testCSS = """
@font-face {
	font-family: "WOFF Test";
	src: url("resources/%s.woff") format("woff");
}
body {
	font-family;
	font-size: 25px;
}
.test {
	font-family: "WOFF Test", "WOFF Test %s Fallback";
	font-size: 200px;
	margin-top: 50px;
}
""".strip()

refCSS = """
body {
	font-family;
	font-size: 25px;
}
.test {
	font-family: "WOFF Test %s Reference";
	font-size: 200px;
	margin-top: 50px;
}
""".strip()

def _generateSFNTDisplayTestHTML(
    css, bodyCharacter,
    fileName=None, flavor=None,
    title=None, specLink=None, assertion=None,
    credits=[], flags=[]
    ):
    assert flavor is not None
    assert title is not None
    assert specLink is not None
    assert assertion is not None
    html = [
        "<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.0 Strict//EN\" \"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd\">",
        "<html xmlns=\"http://www.w3.org/1999/xhtml\">"
    ]
    # head
    html.append("\t<head>")
    ## encoding
    s = "\t\t<meta http-equiv=\"content-type\" content=\"text/html;charset=UTF-8\"/>"
    html.append(s)
    ## title
    s = "\t\t<title>WOFF Test: %s</title>" % title
    html.append(s)
    ## author
    for credit in credits:
        role = credit.get("role")
        title = credit.get("title")
        link = credit.get("link")
        date = credit.get("date")
        s = "\t\t<link rel=\"%s\" title=\"%s\" href=\"%s\" />" % (role, title, link)
        if date:
            s += " <!-- %s -->" % date
        html.append(s)
    ## link
    s = "\t\t<link rel=\"help\" href=\"%s\" />" % specLink
    html.append(s)
    ## flags
    if flags:
        s = "\t\t<meta name=\"flags\" content=\"%s\" />" % " ".join(flags)
        html.append(s)
    ## assertion
    s = "\t\t<meta name=\"assert\" content=\"%s\" />" % assertion
    html.append(s)
    ## css
    html.append("\t\t<style type=\"text/css\"><![CDATA[")
    s = "\n".join(["\t\t\t" + line for line in css.splitlines()])
    html.append(s)
    html.append("\t\t]]></style>")
    ## close
    html.append("\t</head>")
    # body
    html.append("\t<body>")
    ## install fonts note
    s = "\t\t<p><a href=\"LINK_TO_TEST_FONTS\">Test fonts</a> must be installed for this test.</p>"
    ## note
    s = "\t\t<p>Test passes if the word PASS appears below.</p>"
    html.append(s)
    ## test case
    s = u"\t\t<div class=\"test\">%s</div>" % bodyCharacter
    html.append(s)
    ## close
    html.append("\t</body>")
    # close
    html.append("</html>")
    # finalize
    html = u"\n".join(html)
    return html

def generateSFNTDisplayTestHTML(fileName=None, directory=None, flavor=None, title=None, specLink=None, assertion=None, credits=[], flags=[], shouldDisplay=None):
    bodyCharacter = testFailCharacter
    if shouldDisplay:
        bodyCharacter = testPassCharacter
    css = testCSS % (fileName, flavor)
    html = _generateSFNTDisplayTestHTML(
        css, bodyCharacter,
        fileName=fileName, flavor=flavor,
        title=title, specLink=specLink, assertion=assertion,
        credits=credits, flags=flags
    )
    # write the file
    path = os.path.join(directory, fileName) + ".xht"
    f = codecs.open(path, "wb", encoding="utf8")
    f.write(html)
    f.close()

def generateSFNTDisplayRefHTML(fileName=None, directory=None, flavor=None, title=None, specLink=None, assertion=None, credits=[], flags=[], shouldDisplay=None):
    bodyCharacter = refPassCharacter
    css = refCSS % flavor
    html = _generateSFNTDisplayTestHTML(
        css, bodyCharacter,
        fileName=fileName, flavor=flavor,
        title=title, specLink=specLink, assertion=assertion,
        credits=credits, flags=flags
    )
    # write the file
    path = os.path.join(directory, fileName) + "-ref.xht"
    f = codecs.open(path, "wb", encoding="utf8")
    f.write(html)
    f.close()
