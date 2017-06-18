#encoding=utf8
import sys
import random


format = """
<!DOCTYPE html>
<html>
  <head>
    <title>mxnet::engine survey</title>
    <meta charset="utf-8" />
    <script src="https://code.jquery.com/jquery-2.2.4.min.js"></script>
    <!-- <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.min.js"></script> -->

    <script>
      // this code is necessary only for showing source in example
      $(window).load(function() {
        // position source box in center
        $('#source').position({
          of: $('#slideshow')
        });

        // show source box
        $('.show-source > a, #overlay').click(function(e) {
          e.preventDefault();
          $('#overlay, #source').toggle(300);
        });

        // open source links in new tab/window
        $('.show-source > a').attr('target', '_blank');
      });
    </script>
<script src="https://cdn.rawgit.com/showdownjs/showdown/1.7.1/dist/showdown.min.js"></script>

    <style>
      @import url(https://fonts.googleapis.com/css?family=Droid+Serif);
      @import url(https://fonts.googleapis.com/css?family=Yanone+Kaffeesatz);

      body {
        font-family: 'Droid Serif';
        font-size: medium;
      }
      h1, h2, h3 {
        font-family: 'Yanone Kaffeesatz';
        font-weight: 400;
        margin-bottom: 0;
      }
      .small * {
        font-size: small !important;
      }
      code {
        border-radius: 5px;
      }
      .inverse {
        background: #272822;
        color: #777872;
        text-shadow: 0 0 20px #333;
      }
      .inverse h1, .inverse h2 {
        color: #f3f3f3;
        line-height: 0.8em;
      }
      .footnote {
        position: absolute;
        font-size: small;
        bottom: 3em;
        right: 3em;
      }
      /* styling only necessary for displaying source */
      #source {
        position: absolute;
        display: none;
        font-family: monospace;
        font-size: medium;
        background: #333333;
        color: white;
        padding: 10px;
        text-align: left;
        width: 65%;
        height: 70%;
        z-index: 1000;
      }
      #overlay {
        position: absolute;
        display: none;
        background: black;
        width: 100%;
        height: 100%;
        opacity: 0.2;
        z-index: 999;
      }
    </style>
  </head>
  <body>
    <textarea id="source" readonly>"""

format2 = """
</textarea>

    <script src="https://gnab.github.io/remark/downloads/remark-latest.min.js"></script>
    <script type="text/javascript">
      var hljs = remark.highlighter.engine;
    </script>
    <!-- <script src="terminal.language.js" type="text/javascript"></script> -->
    <script type="text/javascript">
      var slideshow = remark.create({
        highlightStyle: 'monokai',
        navigation: {
        scroll: false
        }
      });
      // extract the embedded styling from ansi spans
      $('code.terminal span.hljs-ansi').replaceWith(function(i, x) {
        return x.replace(/&lt;(\/?(\w+).*?)&gt;/g, '<$1>')
      });

      var converter = new showdown.Converter();
      converter.setOption('tables', true);

"""

format3 = """
    </script>

  </body>
</html>

<!--
  vim:filetype=markdown
-->
"""

content = open('mxnet-engine.md').read()

# parse scripts

in_script_flag = False
script_block_id = ''
scripts = []

# the common content
common_lines = content.split('\n')

latest_div_id = ''

for line_id, line in enumerate(common_lines):
    line = line.strip()
    if line.startswith('#+begin_script'):
        in_script_flag = True
        if len(line.split()) > 1:
            script_block_id = line.split()[1]
        common_lines[line_id] = ''
        scripts += [
            'var text = `',
        ]
        continue
    elif line.startswith('#+end_script'):
        in_script_flag = False
        scripts += [
            '`;',
            '$("#%s").append(converter.makeHtml(text));' % script_block_id,
        ]
        common_lines[line_id] = ''
        continue

    if '#+div' in line:
        class_id = line.strip().split()[-1]
        latest_div_id = 'div-%d' % line_id
        script_block_id = latest_div_id
        common_lines[line_id] = '<div id="%s" class="%s">' % (latest_div_id, class_id)
        continue

    if '#+/div' in line:
        common_lines[line_id] = '</div>'
        continue

    if in_script_flag:
        assert script_block_id
        scripts += [
            line,
        ]
        common_lines[line_id] = ''

content = '\n'.join(common_lines)

real = format + content + format2 + '\n'.join(scripts) + format3


print real
