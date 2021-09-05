import pygments
import pygments.lexers
import pygments.formatters
from html.parser import unescape

import html
import re

_LANG_ALIASES  = {
    'java' : 'java',
    'python' : 'python3'
}

def highlight(content: str) -> str:
    """Syntax-highlights HTML-rendered Markdown.
    Plucks sections to highlight that conform the the GitHub fenced code info
    string as defined at https://github.github.com/gfm/#info-string.
    Args:
        html (str): The rendered HTML.
    Returns:
        str: The HTML with Pygments syntax highlighting applied to all code
            blocks.
    """

    formatter = pygments.formatters.HtmlFormatter(nowrap=True)

    code_expr = re.compile(
        r'<pre><code class="language-(?P<lang>.+?)">(?P<code>.+?)'
        r'</code></pre>', re.DOTALL)

    def replacer(match):
        try:
            lang = match.group('lang')
            lang = _LANG_ALIASES.get(lang, lang)
            lexer = pygments.lexers.get_lexer_by_name(lang)
        except ValueError:
            lexer = pygments.lexers.TextLexer()

        code = match.group('code')

        # Decode html entities in the code. cmark tries to be helpful and
        # translate '"' to '&quot;', but it confuses pygments. Pygments will
        # escape any html entities when re-writing the code, and we run
        # everything through bleach after.
        code = unescape(code)

        highlighted = pygments.highlight(code, lexer, formatter)

        return '<pre class="lang-{}">{}</pre>'.format(lang, highlighted)

    result = code_expr.sub(replacer, content)

    return result

def get_style_css(style):
    """Returns the CSS for the given Pygments style."""
    formatter = pygments.formatters.HtmlFormatter(
        style=style)
    return formatter.get_style_defs('pre')