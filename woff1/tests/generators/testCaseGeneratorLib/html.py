"""
Test case HTML generator.
"""

import os
import cgi

# ------------------
# SFNT Display Tests
# ------------------

testPassCharacter = "P"
testFailCharacter = "F"
refPassCharacter = testPassCharacter

testCSS = """
@font-face {
	font-family: "WOFF Test";
	src: url("resources/%s.woff") format("woff");
}
body {
	font-family;
	font-size: 20px;
}
pre {
	font-size: 12px;
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
	font-size: 20px;
}
pre {
	font-size: 12px;
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
    credits=[], flags=[],
    metadataIsValid=None,
    metadataToDisplay=None,
    extraSFNTNotes=[],
    extraMetadataNotes=[]
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
    s = "\t\t<p><a href=\"../FontsToInstall\">Test fonts</a> must be installed for this test. The WOFF being tested will be loaded over the network so please wait until the download is complete before determing the success of this test.</p>"
    html.append(s)
    ## note
    s = "\t\t<p>Test passes if the word PASS appears below.</p>"
    html.append(s)
    for note in extraSFNTNotes:
        s = "\t\t<p>%s</p>" % note
        html.append(s)
    ## test case
    s = "\t\t<div class=\"test\">%s</div>" % bodyCharacter
    html.append(s)
    ## show metadata statement
    if metadataIsValid is not None:
        if metadataIsValid:
            s = "\t\t<p>The Extended Metadata Block is valid and may be displayed to the user upon request.</p>"
        else:
            s = "\t\t<p>The Extended Metadata Block is not valid and must not be displayed.</p>"
        html.append(s)
    for note in extraMetadataNotes:
        s = "\t\t<p>%s</p>" % note
        html.append(s)
    if metadataToDisplay:
        s = "\t\t<p>The XML contained in the Extended Metadata Block is below.</p>"
        html.append(s)
        html.append("\t\t<pre>")
        html.append(cgi.escape(metadataToDisplay))
        html.append("\t\t</pre>")
    ## close
    html.append("\t</body>")
    # close
    html.append("</html>")
    # finalize
    html = "\n".join(html)
    return html

def generateSFNTDisplayTestHTML(fileName=None, directory=None, flavor=None, title=None, specLink=None, assertion=None, credits=[], flags=[], shouldDisplay=None, metadataIsValid=None, metadataToDisplay=None, extraSFNTNotes=[], extraMetadataNotes=[]):
    bodyCharacter = testFailCharacter
    if shouldDisplay:
        bodyCharacter = testPassCharacter
    css = testCSS % (fileName, flavor)
    html = _generateSFNTDisplayTestHTML(
        css, bodyCharacter,
        fileName=fileName, flavor=flavor,
        title=title, specLink=specLink, assertion=assertion,
        credits=credits, flags=flags,
        metadataIsValid=metadataIsValid,
        metadataToDisplay=metadataToDisplay,
        extraSFNTNotes=extraSFNTNotes,
        extraMetadataNotes=extraMetadataNotes
    )
    # write the file
    path = os.path.join(directory, fileName) + ".xht"
    f = open(path, "wb")
    f.write(html)
    f.close()

def generateSFNTDisplayRefHTML(fileName=None, directory=None, flavor=None, title=None, specLink=None, assertion=None, credits=[], flags=[], shouldDisplay=None, metadataIsValid=None, metadataToDisplay=None, extraSFNTNotes=[], extraMetadataNotes=[]):
    bodyCharacter = refPassCharacter
    css = refCSS % flavor
    html = _generateSFNTDisplayTestHTML(
        css, bodyCharacter,
        fileName=fileName, flavor=flavor,
        title=title, specLink=specLink, assertion=assertion,
        credits=credits, flags=flags,
        metadataIsValid=metadataIsValid,
        metadataToDisplay=metadataToDisplay,
        extraSFNTNotes=extraSFNTNotes,
        extraMetadataNotes=extraMetadataNotes
    )
    # write the file
    path = os.path.join(directory, fileName) + "-ref.xht"
    f = open(path, "wb")
    f.write(html)
    f.close()

def generateSFNTDisplayIndexHTML(directory=None, testCases=[]):
    print "...need to properly link to CSS!"
    testCount = sum([len(group["testCases"]) for group in testCases])
    html = [
        "<!DOCTYPE html PUBLIC \"-//W3C//DTD XHTML 1.1//EN\" \"http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd\">",
        "<html xmlns=\"http://www.w3.org/1999/xhtml\">",
        "\t<head>",
        "\t\t<title>WOFF: User Agent Test Suite</title>",
        "\t\t<style type=\"text/css\">",
        "\t\t\t@import \"http://www.w3.org/StyleSheets/TR/base.css\";",
        "\t\t\t/* XXX THIS SHOULD NOT IMPORT FROM A COMPLETELY DIFFERENT PROJECT! */",
        "\t\t\t/* XXX THIS IS A TEMPORARY CONVENIENCE! */",
        "\t\t\t@import \"http://test.csswg.org/suites/css2.1/20101027/indices.css\";",
        "\t\t</style>",
        "\t</head>",
        "\t<body>",
        "\t\t<h1>WOFF: User Agent Test Suite (%d tests)</h1>" % testCount,
        "\t\t<p>All of these tests require special fonts to be installed. The fonts can be obtained <a href=\"../FontsToInstall\">here</a>.</p>"
        "\t\t<table width=\"100%\">",
        "\t\t\t<col id=\"test-column\"></col>",
        "\t\t\t<col id=\"flags-column\"></col>",
        "\t\t\t<col id=\"info-column\"></col>",
        "\t\t\t<thead>",
        "\t\t\t\t<tr>",
        "\t\t\t\t\t<th>Test</th>",
        "\t\t\t\t\t<th><abbr title=\"Rendering References\">Refs</abbr></th>",
        "\t\t\t\t\t<th>Flags</th>",
        "\t\t\t\t\t<th>Info</th>",
        "\t\t\t\t</tr>",
        "\t\t\t</thead>",
    ]
    # add the test groups
    for group in testCases:
        title = group["title"]
        url = group["url"]
        id = title.replace(" ", "")
        # start a new body section
        html.append("\t\t\t<tbody id=\"%s\">" % id)
        # write the group header
        html.append("\t\t\t\t<tr><th colspan=\"4\" scope=\"rowgroup\">")
        html.append("\t\t\t\t\t<a href=\"#%s\">+</a>" % id)
        if url is None:
            html.append("\t\t\t\t\t%s" % title)
        else:
            html.append("\t\t\t\t\t<a href=\"%s\">%s</a>" % (url, title))
        html.append("\t\t\t\t</th></tr>")
        # write the individual test cases
        for test in group["testCases"]:
            identifier = test["identifier"]
            flags = test["flags"]
            title = test["title"]
            assertion = test["assertion"]
            # start the row
            html.append("\t\t\t\t<tr id=\"%s\" class=\"primary %s\">" % (identifier, " ".join(flags)))
            # identifier
            html.append("\t\t\t\t\t<td><strong><a href=\"%s.xht\">%s</a></strong></td>" % (identifier, identifier))
            # reference rendering
            html.append("\t\t\t\t\t<td><a href=\"%s-ref.xht\">=</a></td>" % identifier)
            # flags
            if not flags:
                html.append("\t\t\t\t\t<td></td>")
            else:
                line = ["\t\t\t\t\t<td>"]
                for flag in flags:
                    if flag == "font":
                        line.append("<abbr class=\"font\" title=\"Requires Special Font\">Font</abbr>")
                    else:
                        raise NotImplementedError("Unknown flag: %s" % flag)
                    line.append("</td>")
                html.append("".join(line))
            # assertion
            html.append("\t\t\t\t\t<td>%s<ul class=\"assert\"><li>%s</li></ul></td>" % (title, assertion))
            # end the row
            html.append("\t\t\t\t</tr>")
        html.append("\t\t\t</tbody>")
    # close the table
    html.append("\t\t</table>",)
    # close body
    html.append("\t</body>")
    # close html
    html.append("</html>")
    # finalize
    html = "\n".join(html)
    # write
    path = os.path.join(directory, "testcaseindex.xht")
    f = open(path, "wb")
    f.write(html)
    f.close()
