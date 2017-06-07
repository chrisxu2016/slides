#encoding=utf8
import sys


format = """
<!DOCTYPE html>
<html>
  <head>
    <title>mxnet::engine survey</title>
    <meta charset="utf-8" />

    <script src="https://code.jquery.com/jquery-2.2.4.min.js"></script>
    <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.min.js"></script>

    <script>
      // this code is necessary only for showing source in example
      $(window).load(function() {
        // position source box in center
        $('#source').position({
          of: \$('#slideshow')
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
    <script src="terminal.language.js" type="text/javascript"></script>
    <script type="text/javascript">
      var slideshow = remark.create({
        highlightStyle: 'monokai'
      });
      // extract the embedded styling from ansi spans
      $('code.terminal span.hljs-ansi').replaceWith(function(i, x) {
        return x.replace(/&lt;(\/?(\w+).*?)&gt;/g, '<$1>')
      });
    </script>

  </body>
</html>

<!--
  vim:filetype=markdown
-->
"""

content = open('slide.md').read()

real = format + content + format2

print real
