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
    This style is a witchy theme 
    """

    background_color = "#f8f8f8"
    highlight_color = "#ffffcc"

    styles = {
        # No corresponding class for the following:
        Text:                      "",  # class:  ''
        Whitespace:                "#bbbbbb",        # class: 'w'
        Error:                     "#FF0000",  # class: 'err'
        Other:                     "",        # class 'x'

        Comment:                   "#008800",  # class: 'c'
        Comment.Multiline:         "#008800",        # class: 'cm'
        Comment.Preproc:           "#008800",        # class: 'cp'
        Comment.Single:            "#008800",        # class: 'c1'
        Comment.Special:           "#008800",        # class: 'cs'

        Keyword:                   "#aa22FF",  # class: 'k' italic?
        Keyword.Constant:          "",        # class: 'kc'
        Keyword.Declaration:       "",        # class: 'kd' italic?
        Keyword.Namespace:         "#aa22FF",  # class: 'kn'
        Keyword.Pseudo:            "",        # class: 'kp'
        Keyword.Reserved:          "",        # class: 'kr'
        Keyword.Type:              "",        # class: 'kt' italic?

        Operator:                  "#666666",  # class: 'o'
        Operator.Word:             "#AA22FF",        # class: 'ow' - like keywords

        Punctuation:               "",  # class: 'p'

        Name:                      "#B8860B",  # class: 'n'
        Name.Attribute:            "#BB4444",  # class: 'na'
        Name.Builtin:              "#AA22FF",        # class: 'nb'
        Name.Builtin.Pseudo:       "#AA22F",        # class: 'bp'
        Name.Class:                "#0000FF",  # class: 'nc' italic underline?
        Name.Constant:             "#880000",  # class: 'no'
        Name.Decorator:            "#AA22FF",  # class: 'nd' underline?
        Name.Entity:               "#999999",        # class: 'ni'
        Name.Exception:            "#D2413A",  # class: 'ne' underline?
        Name.Function:             "#00A000",  # class: 'nf'
        Name.Property:             "",        # class: 'py'
        Name.Label:                "#A0A000",        # class: 'nl'
        Name.Namespace:            "#0000FF",        # class: 'nn' - to be revised
        Name.Other:                "",  # class: 'nx'
        Name.Tag:                  "#008000",  # class: 'nt' - like a keyword
        Name.Variable:             "#B8860B",        # class: 'nv' - to be revised
        Name.Variable.Class:       "#B8860B",        # class: 'vc' - to be revised
        Name.Variable.Global:      "#B8860B",        # class: 'vg' - to be revised
        Name.Variable.Instance:    "#B8860B",        # class: 'vi' - to be revised

        Number:                    "#666666",  # class: 'm'
        Number.Float:              "#666666",        # class: 'mf'
        Number.Hex:                "#666666",        # class: 'mh'
        Number.Integer:            "#666666",        # class: 'mi'
        Number.Integer.Long:       "#666666",        # class: 'il'
        Number.Oct:                "#666666",        # class: 'mo'

        Literal:                   "#BB4444",  # class: 'l'
        Literal.Date:              "#BB4444",  # class: 'ld'

        String:                    "#BB4444",  # class: 's'
        String.Backtick:           "#BB4444",        # class: 'sb'
        String.Char:               "#BB4444",        # class: 'sc'
        String.Doc:                "BB4444",        # class: 'sd' - like a comment
        String.Double:             "BB4444",        # class: 's2'
        String.Escape:             "#BB6622",  # class: 'se'
        String.Heredoc:            "#BB4444",        # class: 'sh'
        String.Interpol:           "#BB6688",        # class: 'si'
        String.Other:              "#008000",        # class: 'sx'
        String.Regex:              "#BB6688",        # class: 'sr'
        String.Single:             "#BB4444",        # class: 's1'
        String.Symbol:             "#B8860B",        # class: 'ss'

        Generic:                   "",        # class: 'g'
        Generic.Deleted:           "#A00000",  # class: 'gd',
        Generic.Emph:              "italic",  # class: 'ge'
        Generic.Error:             "#FF0000",        # class: 'gr'
        Generic.Heading:           "#000080",        # class: 'gh'
        Generic.Inserted:          "#00A000",  # class: 'gi'
        Generic.Output:            "#888888",        # class: 'go'
        Generic.Prompt:            "#000080",        # class: 'gp'
        Generic.Strong:            "bold",    # class: 'gs'
        Generic.Subheading:        "#800080",  # class: 'gu'
        Generic.Traceback:         "#0044DD",        # class: 'gt'
    }