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

    background_color = "#f7f7f8"
   # highlight_color = "#ffffcc"

    styles = {
        # No corresponding class for the following:
        Text:                      "",  # class:  ''
        Whitespace:                "#bbbbbb",        # class: 'w'
        Error:                     "#FF0000",  # class: 'err'
        Other:                     "",        # class 'x'

        Comment:                   "#3D7B7B",  # class: 'c'
        Comment.Multiline:         "#3D7B7B",        # class: 'cm'
        Comment.Preproc:           "#9C6500",        # class: 'cp'
        Comment.Single:            "#3D7B7B",        # class: 'c1'
        Comment.Special:           "#3D7B7B",        # class: 'cs'

        Keyword:                   "#008000",  # class: 'k' italic?
        Keyword.Constant:          "#008000",        # class: 'kc'
        Keyword.Declaration:       "#008000",        # class: 'kd' italic?
        Keyword.Namespace:         "#008000",  # class: 'kn'
        Keyword.Pseudo:            "#008000",        # class: 'kp'
        Keyword.Reserved:          "#008000",        # class: 'kr'
        Keyword.Type:              "#B00040",        # class: 'kt' italic?

        Operator:                  "#666666",  # class: 'o'
        Operator.Word:             "#AA22FF",        # class: 'ow' - like keywords

        Punctuation:               "",  # class: 'p'

        Name:                      "",  # class: 'n'
        Name.Attribute:            "#687822",  # class: 'na'
        Name.Builtin:              "#008000",        # class: 'nb'
        Name.Builtin.Pseudo:       "#008000",        # class: 'bp'
        Name.Class:                "#0000FF",  # class: 'nc' italic underline?
        Name.Constant:             "#880000",  # class: 'no'
        Name.Decorator:            "#AA22FF",  # class: 'nd' underline?
        Name.Entity:               "#717171",        # class: 'ni'
        Name.Exception:            "#CB3F38",  # class: 'ne' underline?
        Name.Function:             "#0000FF",  # class: 'nf'
        Name.Property:             "#0000FF",        # class: 'py'
        Name.Label:                "#767600",        # class: 'nl'
        Name.Namespace:            "#0000FF",        # class: 'nn' - to be revised
        Name.Other:                "#767600",  # class: 'nx'
        Name.Tag:                  "#008000",  # class: 'nt' - like a keyword
        Name.Variable:             "#19177C",        # class: 'nv' - to be revised
        Name.Variable.Class:       "#19177C",        # class: 'vc' - to be revised
        Name.Variable.Global:      "#19177C",        # class: 'vg' - to be revised
        Name.Variable.Instance:    "#19177C",        # class: 'vi' - to be revised

        Number:                    "#666666",  # class: 'm'
        Number.Float:              "#666666",        # class: 'mf'
        Number.Hex:                "#666666",        # class: 'mh'
        Number.Integer:            "#666666",        # class: 'mi'
        Number.Integer.Long:       "#666666",        # class: 'il'
        Number.Oct:                "#666666",        # class: 'mo'

        Literal:                   "",  # class: 'l'
        Literal.Date:              "",  # class: 'ld'

        String:                    "#BA2121",  # class: 's'
        String.Backtick:           "#BA2121",        # class: 'sb'
        String.Char:               "#BA2121",        # class: 'sc'
        String.Doc:                "#BA2121",        # class: 'sd' - like a comment
        String.Double:             "#BA2121",        # class: 's2'
        String.Escape:             "#AA5D1F",  # class: 'se'
        String.Heredoc:            "#BA2121",        # class: 'sh'
        String.Interpol:           "#A45A77",        # class: 'si'
        String.Other:              "#008000",        # class: 'sx'
        String.Regex:              "#A45A77",        # class: 'sr'
        String.Single:             "#BA2121",        # class: 's1'
        String.Symbol:             "#19177C",        # class: 'ss'

        Generic:                   "",        # class: 'g'
        Generic.Deleted:           "#A00000",  # class: 'gd',
        Generic.Emph:              "italic",  # class: 'ge'
        Generic.Error:             "#E40000",        # class: 'gr'
        Generic.Heading:           "#000080",        # class: 'gh'
        Generic.Inserted:          "#008400",  # class: 'gi'
        Generic.Output:            "#717171",        # class: 'go'
        Generic.Prompt:            "#000080",        # class: 'gp'
        Generic.Strong:            "bold",    # class: 'gs'
        Generic.Subheading:        "#800080",  # class: 'gu'
        Generic.Traceback:         "#0044DD",        # class: 'gt'
    }