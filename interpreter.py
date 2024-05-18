from typing import Any
from pathlib import Path
from random import randint



####### CONTROL TAGS #######
# "@IN": user input
# "@OUT": stdout
# "@FILE": the current file
############################



#### FUNCTIONS ####

def strsub(string: str, start: int, end_at: int = None) -> str:
    if not end_at: end_at = len(string)
    else: end_at = start+end_at
    #if start > len(string) or end_at > len(string): return string
    return string[start:end_at]

def revstrsub(string: str, start: int, end_at: int = None, return_as_tuple: bool = False) -> str | tuple[str, str]:
    if not end_at: end_at = len(string)
    else: end_at = start+end_at
    if start > len(string) or end_at > len(string):
        if return_as_tuple: return string, ''
        return string
    if return_as_tuple: return string[0:start], string[end_at:len(string)]
    return string[0:start] + string[end_at:len(string)]


def append_file(filename: str | Path, data: Any):
    with open(filename, 'at') as f:
        f.write(str(data))

def write_file(filename: str | Path, data: Any):
    with open(filename, 'wt') as f: f.write(str(data))

### END FUNCTIONS ####



#### CLASSES ####

class Error:
    def __init__(self, type: str, details: str = None, ln: int = None, program: str = None):
        self.__type = type
        self.__details = details
        self.__ln = ln
        self.__program = program
    
    def error(self):
        out = self.__type
        if self.__details: out += ': ' + self.__details
        if self.__program:
            out += f"; program '{self.__program}'"
        if self.__ln:
            if self.__program: out += f', on line {self.__ln}'
            else: out += f'; line {self.__ln}'
        return out


class Nil:
    def __repr__(self): return 'Nil'

#### END CLASSES ####



#### GETTERS ####

def get_control_tag(tag: str, ln: int, program: str) -> tuple[Any, Error | None]:
    match tag:
        case '@IN': return input('input wanted\n'), None
        case '@FILE': return __file__, None
        #case '@OUT': return None, None
    return None, Error('InvalidControlTagError', f"invalid control tag '{tag}'", ln, program)


def get_value(vars: dict[str, Any], value: str, ln: int, program: str) -> tuple[str | float | int | Path | Nil | None, Error | None]:
    if value.startswith('"') and value.endswith('"'):
        return value.removeprefix('"').removesuffix('"'), None
    elif value.isdigit():
        if '.' in value: return float(value), None
        return int(value), None
    elif value == '~': return Nil(), None
    elif value.startswith('@'):
        tagval, err = get_control_tag(value, ln, program)
        if err: return None, err
        return tagval, None
    elif value.startswith('f#'): return Path(value.removeprefix('f#')), None
    elif value in list(vars): return vars[value], None
    elif ' + ' in value:
        r, l = value.split(' + ', 1)
        expr_res, expr_err = process_expression(vars, r, '+', l, ln, program)
        if expr_err: return None, expr_err
        return expr_res, None
    elif ' - ' in value:
        r, l = value.split(' - ', 1)
        expr_res, expr_err = process_expression(vars, r, '-', l, ln, program)
        if expr_err: return None, expr_err
        return expr_res, None
    elif ' * ' in value:
        r, l = value.split(' * ', 1)
        expr_res, expr_err = process_expression(vars, r, '*', l, ln, program)
        if expr_err: return None, expr_err
        return expr_res, None
    elif ' ** ' in value:
        r, l = value.split(' ** ', 1)
        expr_res, expr_err = process_expression(vars, r, '**', l, ln, program)
        if expr_err: return None, expr_err
        return expr_res, None
    elif ' / ' in value:
        r, l = value.split(' / ', 1)
        expr_res, expr_err = process_expression(vars, r, '/', l, ln, program)
        if expr_err: return None, expr_err
        return expr_res, None
    elif ' // ' in value:
        r, l = value.split(' // ', 1)
        expr_res, expr_err = process_expression(vars, r, '//', l, ln, program)
        if expr_err: return None, expr_err
        return expr_res, None
    elif ' % ' in value:
        r, l = value.split(' % ', 1)
        expr_res, expr_err = process_expression(vars, r, '%', l, ln, program)
        if expr_err: return None, expr_err
        return expr_res, None
    elif ' & ' in value:
        r, l = value.split(' & ', 1)
        expr_res, expr_err = process_expression(vars, r, '&', l, ln, program)
        if expr_err: return None, expr_err
        return expr_res, None
    elif ' | ' in value:
        r, l = value.split(' | ', 1)
        expr_res, expr_err = process_expression(vars, r, '|', l, ln, program)
        if expr_err: return None, expr_err
        return expr_res, None
    elif ' ^ ' in value:
        r, l = value.split(' ^ ', 1)
        expr_res, expr_err = process_expression(vars, r, '^', l, ln, program)
        if expr_err: return None, expr_err
        return expr_res, None
    else: return None, Error('UnkownValueError', f"unknown value '{value}'", ln, program)

#### END GETTERS ####



#### OPERATIONS ####

def process_expression(vars: dict[str, Any], right: str, op: str, left: str, ln: int, program: str) -> tuple[Any, Error | None]:
    right_converted, right_err = get_value(vars, right, ln, program)
    if right_err: return None, right_err

    left_converted, left_err = get_value(vars, left, ln, program)
    if left_err: return None, left_err

    try:
        match op:
            case '+': return right_converted + left_converted, None
            case '-': return right_converted - left_converted, None
            case '*': return right_converted * left_converted, None
            case '**': return right_converted ** left_converted, None
            case '/': return right_converted / left_converted, None
            case '//': return right_converted // left_converted, None
            case '%': return right_converted % left_converted, None
            # binary operations
            case '&': return right_converted & left_converted, None
            case '|': return right_converted | left_converted, None
            case '^': return right_converted ^ left_converted, None
    except ValueError as e: return None, Error('ExpressionError', e, ln, program)

def create_variable(vars: dict[str, Any], varname: str, value: str, ln: int, program: str) -> Error | None:
    if varname in list(vars):
        return Error('AlreadyDefinedVariableError', f"variable '{varname}' has already been defined", ln, program)
    elif varname == '': return Error('InvalidIdentifier', "variable identifier can't be empty", ln, program)
    
    converted, err = get_value(vars, value, ln, program)
    if err: return err

    vars[varname] = converted
    return None


def assign_variable(vars: dict[str, Any], varname: str, value: str, ln: int, program: str) -> Error | None:
    if varname not in list(vars):
        return Error('UndefinedVariableError', f"variable '{varname}' has not been defined", ln, program)
    
    converted, err = get_value(vars, value, ln, program)
    if err: return err

    vars[varname] = converted
    return None


def send_value_to(vars: dict[str, Any], val: str, out: str, ln: int, program: str) -> Error | None:
    val_converted, val_err = get_value(vars, val, ln, program)
    if val_err: return val_err

    if out == '@OUT': print(str(val_converted)); return None

    out_converted, out_err = get_value(vars, out, ln, program)
    if out_err: return out_err

    if isinstance(out_converted, str): out_converted = Path(out_converted)

    if isinstance(out_converted, Path):
        if not out_converted.exists():
            return Error('FileNotFoundError', f"file at path '{str(out_converted)}' does not exist", ln, program)
        append_file(out_converted, val_converted)
        return None
    else: return Error('InvalidValueError', f"invalid value '{out_converted}' for send-to operation", ln, program)
    #return Error('GotToEndOfFunctionError', "got to end of function 'send_value_to'", ln, program)


def delete_var(vars: dict[str, Any], varname: str, ln: int, program: str) -> Error | None:
    if varname not in list(vars):
        return Error('UndefinedVariableError', f"variable '{varname}' has not been defined", ln, program)
    
    del vars[varname]

    return None


def process_if(vars: dict[str, Any], statement: str, ln: int, program: str) -> tuple[bool, Error | None]:
    pass

#### END OPERATIONS ####



#### MAIN ####

def process_line(vars: dict, line: str, ln: int, cprog: str, all_programs: list[str]) -> tuple[str, int, Error | None]:
    repcode = '{' + f'{randint(0, 9)}{randint(0, 9)}{randint(0, 9)}{randint(0, 9)}{randint(0, 9)}' + '}'
    # get all starts and ends of all strings in the line
    spos = []
    pcache = None
    ignore_next = False
    for i, c in enumerate(line):
        if c == '"':
            if ignore_next: ignore_next = False; continue
            if pcache:
                spos.append((pcache, (i-pcache)+1))
                pcache = None
            else: pcache = i
        elif c == '\\': ignore_next = True
        elif ignore_next: ignore_next = False
    
    # isolate strings from line before strings
    strings = []
    for p in spos:
        start, end = p
        strings.append(strsub(line, start, end))
        t = revstrsub(line, start, end, True)
        line = t[0] + repcode + t[1]
    
    if_statement_cache = None
    if line.startswith('if '):
        if_statement_cache = line.removeprefix('if ')

    # split line by spaces
    l = line.split(' ')
    if if_statement_cache:
        l == 'if', if_statement_cache

    # re-add strings to split line
    idx = 0
    for i, il in enumerate(l):
        if il == repcode:
            l[i] = strings[idx]
            idx += 1
    
    # remove any trailing or leading whitespace that may be left over from something
    for i in range(len(l)): l[i] = l[i].strip()

    # line pattern match
    valid = False
    match l:
        case ('#program', progname):
            if l[1] == '': return '', 0, Error('InvalidIdentifier', "program identifier can't be empty", ln, cprog)
            if l[1] == '<main>': return '', 0, Error('InvalidProgramNameError', "program name can't be '<main>'", ln, cprog)
            if l[1] in all_programs: return '', 0, Error('ProgramAlreadyCreatedError', f"program '{l[1]}' has already been created", ln, cprog)
            return l[1], 1, None
        
        case ('#endprogram', progname):
            if l[1] == '': return '', 0, Error('InvalidIdentifier', "program identifier can't be empty", ln, cprog)
            if l[1] == '<main>': return '', 0, Error('InvalidProgramNameError', "program name can't be '<main>'", ln, cprog)
            if l[1] != cprog: return '', 0, Error('InvalidProgramError', f"program '{l[1]}' is not the current program", ln, cprog)
            return l[1], -1, None

        case ('define', var):
            err = create_variable(vars, l[1], '~', ln, cprog)
            if err: return '', 0, err
            valid = True

        case ('define', var, 'as', val):
            err = create_variable(vars, l[1], l[3], ln, cprog)
            if err: return '', 0, err
            valid = True
        
        case ('assign', var, 'with', val):
            err = assign_variable(vars, l[1], l[3], ln, cprog)
            if err: return '', 0, err
            valid = True

        case ('send', val, 'to', out):
            err = send_value_to(vars, l[1], l[3], ln, cprog)
            if err: return '', 0, err
            valid = True

        case ('delete', var):
            err = delete_var(vars, l[1], ln, cprog)
            if err: return '', 0, err
            valid = True
        
        case ('if', statement):
            pass

        #case ('createf', filename):
        #    err = delete_var(vars, l[1])
        #    if err: return '', 0, err
        #    valid = True

        #case ('flushf', filename):
        #    err = delete_var(vars, l[1])
        #    if err: return '', 0, err
        #    valid = True
    
    if len(l) >= 4 and not valid:
        if l[0] == 'define' and l[2] == 'as':
            err = create_variable(vars, l[1], ' '.join([i for n, i in enumerate(l) if n > 2]), ln, cprog)
            if err: return '', 0, err
            valid = True
        elif l[0] == 'assign' and l[2] == 'with':
            err = assign_variable(vars, l[1], ' '.join([i for n, i in enumerate(l) if n > 2]), ln, cprog)
            if err: return '', 0, err
            valid = True
    
    if not valid: return '', 0, Error('UnkownPatternError', f'unkown pattern [{','.join(["'" + i + "'" for i in l])}]', ln, cprog)
    return '', 0, None



def run_pet(text: str):
    #lines = [l.split(';;')[0].strip() for l in text.split('\n') if not l.startswith(';;') and l.strip() != '']
    #lines = [l for l in lines if l != '']

   # print(lines)

    all_programs = ['<main>']

    programs = ['<main>']

    vars = {}

    lines = [l.split(';;')[0].strip() for l in text.split('\n')]

    for ln, l in enumerate(lines):
        print(vars)
        print(programs)
        if l == '' or l.startswith(';;'): continue
        progname, mode, err = process_line(vars, l, ln+1, programs[-1], all_programs)
        if err: print(err.error()); return
        if mode == 1:
            programs.append(progname)
            all_programs.append(progname)
        elif mode == -1: programs.pop()
        elif mode != 0: print(Error('InterpreterError', f"program mode should be '-1', '0', or '1', but it was '{mode}' instead", ln, programs[-1]).error()); return

#### END MAIN ####