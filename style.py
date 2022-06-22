"""
The code is from thea.codes
"""
from pygments.style import Style
from pygments.token import Keyword, Name, Comment, String, Error, Text, \
     Number, Operator, Generic, Whitespace, Punctuation, Other, Literal


LILAC = '#ceb1ff'
TORQUOISE = '#1bc5e0'


class themeStyle(Style):
    """
    This style is a vs theme 
    """

    background_color = "#ffffff"
    highlight_color = "#ffffcc"

    styles = {
        # No corresponding class for the following:
        Text:                      "",  # class:  ''
        Whitespace:                "",        # class: 'w'
        Error:                     "#FF0000",  # class: 'err'
        Other:                     "",        # class 'x'

        Comment:                   "#008000",  # class: 'c'
        Comment.Multiline:         "#008800",        # class: 'cm'
        Comment.Preproc:           "#0000ff",        # class: 'cp'
        Comment.Single:            "#008800",        # class: 'c1'
        Comment.Special:           "#008800",        # class: 'cs'

        Keyword:                   "#0000ff",  # class: 'k' italic?
        Keyword.Constant:          "#0000ff",        # class: 'kc'
        Keyword.Declaration:       "#0000ff",        # class: 'kd' italic?
        Keyword.Namespace:         "#0000ff",  # class: 'kn'
        Keyword.Pseudo:            "#0000ff",        # class: 'kp'
        Keyword.Reserved:          "#0000ff",        # class: 'kr'
        Keyword.Type:              "#2b91af",        # class: 'kt' italic?

        Operator:                  "",  # class: 'o'
        Operator.Word:             "#0000ff",        # class: 'ow' - like keywords

        Punctuation:               "",  # class: 'p'

        Name:                      "",  # class: 'n'
        Name.Attribute:            "",  # class: 'na'
        Name.Builtin:              "",        # class: 'nb'
        Name.Builtin.Pseudo:       "",        # class: 'bp'
        Name.Class:                "#2b91af",  # class: 'nc' italic underline?
        Name.Constant:             "",  # class: 'no'
        Name.Decorator:            "",  # class: 'nd' underline?
        Name.Entity:               "",        # class: 'ni'
        Name.Exception:            "",  # class: 'ne' underline?
        Name.Function:             "",  # class: 'nf'
        Name.Property:             "",        # class: 'py'
        Name.Label:                "",        # class: 'nl'
        Name.Namespace:            "",        # class: 'nn' - to be revised
        Name.Other:                "",  # class: 'nx'
        Name.Tag:                  "",  # class: 'nt' - like a keyword
        Name.Variable:             "",        # class: 'nv' - to be revised
        Name.Variable.Class:       "",        # class: 'vc' - to be revised
        Name.Variable.Global:      "",        # class: 'vg' - to be revised
        Name.Variable.Instance:    "",        # class: 'vi' - to be revised

        Number:                    "",  # class: 'm'
        Number.Float:              "",        # class: 'mf'
        Number.Hex:                "",        # class: 'mh'
        Number.Integer:            "",        # class: 'mi'
        Number.Integer.Long:       "",        # class: 'il'
        Number.Oct:                "",        # class: 'mo'

        Literal:                   "",  # class: 'l'
        Literal.Date:              "",  # class: 'ld'

        String:                    "#a31515",  # class: 's'
        String.Backtick:           "#a31515 ",        # class: 'sb'
        String.Char:               "#a31515",        # class: 'sc'
        String.Doc:                "#a31515",        # class: 'sd' - like a comment
        String.Double:             "#a31515",        # class: 's2'
        String.Escape:             "#a31515",  # class: 'se'
        String.Heredoc:            "#a31515",        # class: 'sh'
        String.Interpol:           "#a31515",        # class: 'si'
        String.Other:              "#a31515",        # class: 'sx'
        String.Regex:              "#a31515",        # class: 'sr'
        String.Single:             "#a31515",        # class: 's1'
        String.Symbol:             "#a31515",        # class: 'ss'

        Generic:                   "",        # class: 'g'
        Generic.Deleted:           "",  # class: 'gd',
        Generic.Emph:              "italic",  # class: 'ge'
        Generic.Error:             "",        # class: 'gr'
        Generic.Heading:           "bold",        # class: 'gh'
        Generic.Inserted:          "",  # class: 'gi'
        Generic.Output:            "",        # class: 'go'
        Generic.Prompt:            "bold",        # class: 'gp'
        Generic.Strong:            "bold",    # class: 'gs'
        Generic.Subheading:        "bold",  # class: 'gu'
        Generic.Traceback:         "bold",        # class: 'gt'
    }