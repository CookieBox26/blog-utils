import blog_utils
import tinycss2
import io


def is_node(node, type_expected, value_expected):
    return node.type == type_expected and node.value == value_expected


def test_tinycss2():
    # https://doc.courtbouillon.org/tinycss2/stable/api_reference.html
    text = '''
    @charset "UTF-8";.alert{color:red;font-weight:bold}
    /* ----- 青い文字 ----- */
    div.blue  {color: blue}
    '''
    rules = tinycss2.parse_stylesheet(text, skip_whitespace=True)

    assert len(rules) == 4

    assert rules[0].type == 'at-rule'
    assert rules[0].at_keyword == 'charset'
    assert len(rules[0].prelude) == 2
    assert is_node(rules[0].prelude[0], 'whitespace', ' ')
    assert is_node(rules[0].prelude[1], 'string', 'UTF-8')
    assert rules[0].content is None

    assert rules[1].type == 'qualified-rule'
    assert len(rules[1].prelude) == 2
    assert is_node(rules[1].prelude[0], 'literal', '.')
    assert is_node(rules[1].prelude[1], 'ident', 'alert')
    assert len(rules[1].content) == 7
    assert is_node(rules[1].content[0], 'ident', 'color')
    assert is_node(rules[1].content[1], 'literal', ':')
    assert is_node(rules[1].content[2], 'ident', 'red')
    assert is_node(rules[1].content[3], 'literal', ';')
    assert is_node(rules[1].content[4], 'ident', 'font-weight')
    assert is_node(rules[1].content[5], 'literal', ':')
    assert is_node(rules[1].content[6], 'ident', 'bold')

    assert rules[2].type == 'comment'
    assert rules[2].value == ' ----- 青い文字 ----- '

    assert rules[3].type == 'qualified-rule'
    assert len(rules[3].prelude) == 4
    assert is_node(rules[3].prelude[0], 'ident', 'div')
    assert is_node(rules[3].prelude[1], 'literal', '.')
    assert is_node(rules[3].prelude[2], 'ident', 'blue')
    assert is_node(rules[3].prelude[3], 'whitespace', '  ')
    assert len(rules[3].content) == 4
    assert is_node(rules[3].content[0], 'ident', 'color')
    assert is_node(rules[3].content[1], 'literal', ':')
    assert is_node(rules[3].content[2], 'whitespace', ' ')
    assert is_node(rules[3].content[3], 'ident', 'blue')

    assert rules[0].serialize() == '@charset "UTF-8";'
    assert rules[1].serialize() == '.alert{color:red;font-weight:bold}'
    assert rules[2].serialize() == '/* ----- 青い文字 ----- */'
    assert rules[3].serialize() == 'div.blue  {color: blue}'

    buf = io.StringIO()
    tinycss2.serializer._serialize_to(rules[3].prelude[:2], buf.write)
    assert buf.getvalue() == 'div.'


def test_format_qs():
    org = '.alert{color:red;font-weight:bold}'
    expected = '''
    .alert {
      color: red;
      font-weight: bold;
    }
    '''.strip().replace('    ', '')
    assert blog_utils.format_qs(org) == expected

    org = '''
    .h5-margin-bottom-02 h5 {
      margin-bottom: 0.2em !important;
    }
    '''.strip().replace('    ', '')
    expected = '''
    .h5-margin-bottom-02 h5 {
      margin-bottom: 0.2em !important;
    }
    '''.strip().replace('    ', '')
    assert blog_utils.format_qs(org) == expected
