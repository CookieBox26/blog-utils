from pathlib import Path
import tinycss2
import re
pattern_q = re.compile(r'([^{}]+)\{([^{}]+)\}')
pattern_bad_ws = re.compile(r' {2,}')
pattern_bad_comma = re.compile(r',(?![ \n])')
pattern_newline_ws = re.compile(r'\n *')
import argparse
import difflib
from colorama import Fore
import logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')


def color_diff(diff):
    color = {'@': Fore.CYAN + '@'}
    for line in diff:
        yield color.get(line[0], line[0]) + line[1:] + Fore.RESET
        if line[0] == '@':
            color.update({'-': Fore.RED + '-', '+': Fore.GREEN + '+'})


def print_diff(lines_0, lines_1):
    for line in color_diff(difflib.unified_diff(
        lines_0, lines_1, fromfile='Before', tofile='After', lineterm='',
    )):
        print(line)


def parse_qs(qs):
    m = pattern_q.match(qs)
    return m.group(1), m.group(2)


def format_qs(qs):
    qs = pattern_bad_ws.sub(' ', qs)
    pre, con = parse_qs(qs)
    pre = pattern_bad_comma.sub(', ', pre)
    pre = pre.strip() + ' '
    props = []
    for c in con.split(';'):
        if not c.strip():
            continue
        pair = c.strip().split(':', 1)
        if len(pair) == 1:
            print(pair)
        prop, value = c.strip().split(':', 1)
        prop = prop.strip()
        value = pattern_newline_ws.sub('\n    ', value).rstrip()
        if value[0] != ' ' and value[0] != '\n':
            value = ' ' + value
        c = '  ' + prop + ':' + value + ';'
        props.append(c)
    return pre + '{\n' + '\n'.join(props) + '\n}'


def format(style, overwrite, style_bak):
    path = Path(style)
    path_bak = Path(style_bak)
    text_org = path.read_text('utf8')
    path_bak.write_text(text_org, newline='\n', encoding='utf8')
    rules = tinycss2.parse_stylesheet(text_org, skip_whitespace=True)
    text = ''
    n_comment = 0
    for rule in rules:
        if rule.type == 'comment':
            n_comment += 1
            if n_comment == 2:
                text += '\n'
        if rule.type in ['at-rule', 'comment']:
            text += rule.serialize() + '\n'
        elif rule.type == 'qualified-rule':
            if n_comment < 2:
                text += rule.serialize()
            else:
                qs = rule.serialize()
                if 'data:image' in qs:
                    text += qs + '\n'
                else:
                    text += format_qs(qs) + '\n'
        else:
            raise NotImplementedError('Unsupported: ' + rule.type)
    if text != text_org:
        print_diff(text_org.splitlines(), text.splitlines())
        if overwrite:
            path.write_text(text, newline='\n', encoding='utf8')
            logging.info('Updated the stylesheet.')
    else:
        logging.info('No updates to the stylesheet.')


def search_ident(style, ident):
    logging.info('Search for: ' + ident)
    text_org = Path(style).read_text('utf8')
    rules = tinycss2.parse_stylesheet(text_org, skip_whitespace=True)
    for rule in rules:
        if rule.type == 'qualified-rule':
            idents = [p.value for p in rule.prelude if p.type == 'ident']
            idents += ['#' + p.value for p in rule.prelude if p.type == 'hash']
            if ident in idents:
                print(rule.prelude[0].source_line)
                print(rule.serialize())


def search_prelude(style, prelude):
    logging.info('Search for: ' + prelude)
    text_org = Path(style).read_text('utf8')
    rules = tinycss2.parse_stylesheet(text_org, skip_whitespace=True)
    for rule in rules:
        if rule.type == 'qualified-rule':
            pre, _ = parse_qs(format_qs(rule.serialize()))
            if prelude in pre:
                print(rule.prelude[0].source_line)
                print(rule.serialize())


def find_duplicate(style):
    text_org = Path(style).read_text('utf8')
    rules = tinycss2.parse_stylesheet(text_org, skip_whitespace=True)
    d = {}
    for rule in rules:
        if rule.type == 'qualified-rule':
            pre, _ = parse_qs(format_qs(rule.serialize()))
            if pre not in d:
                d[pre] = []
            d[pre].append((rule.prelude[0].source_line, rule))
    for k, v in d.items():
        if len(v) > 1:
            print('---------------\n' + k + '\n---------------')
            for pair in v:
                print(pair[0])
                print(pair[1].serialize())


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-f', '--format', action='store_true')
    group.add_argument('-i', '--ident')
    group.add_argument('-p', '--prelude')
    group.add_argument('-d', '--duplicate', action='store_true')
    parser.add_argument('--style', default='style.css')
    parser.add_argument('-o', '--overwrite', action='store_true')
    parser.add_argument('--style_bak', default='style.bak.css')
    args = parser.parse_args()

    if args.format:
        format(args.style, args.overwrite, args.style_bak)
    if args.ident:
        search_ident(args.style, args.ident)
    if args.prelude:
        search_prelude(args.style, args.prelude)
    if args.duplicate:
        find_duplicate(args.style)
