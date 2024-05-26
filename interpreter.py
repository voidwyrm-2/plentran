import enum
import sys
from typing import Any, SupportsIndex, Type
from pathlib import Path
from random import randint


####### CONTROL TAGS #######
# "@IN": user input
# "@OUT": stdout
# "@FILE": the current file
# "@RUN:[function]": used before a function identifier to call that function
# "@RAND:[min]:[max]": returns a random number between 'min' and 'max'
# "@LIST": creates a new linked list
# "@ARRAY:[length]:[type?]: creates a new array with the given length and an optional type constraint"
# "@LEN:[variable/object]": returns the length of the given variable/object/etc
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



class PlentranFunction:
    def __init__(self, name: str, code: list[str]):
        self.__name = name
        self.__code = code
    
    def run(self): return run_pet(self.__code, is_function=True)



class Array:
    
    '''
    A statically sized array that can optionally have a type constraint
    '''
    class __NoType:
        def __repr__(self): return 'NoType'
    def __init__(self, size: int = None, typeof: Type = __NoType, *inital_values: Any):
        if size: self.__size: int = size
        else:
            if inital_values: self.__arr = list(inital_values); self.__size: int = len(self.__arr)
            else: self.__size: int = 10
        self.__typeof = typeof
        self.__arr: list[Any] = [self.__typeof() for _ in range(self.__size)]
    
    def len(self):
        'Returns the amount of currently assigned indexes'
        return len(self.__arr)

    def size(self):
        'Returns the maximum size of the array'
        return self.__size

    def index(self, value: Any, start: SupportsIndex = 0, stop: SupportsIndex = sys.maxsize):
        'Return first index of value.\n\nRaises ValueError if the value is not present.'
        return self.__arr.index(value, start, stop)
    
    def get(self, index: int):
        'Return item at given index.\n\nRaises IndexError if the index is out of bounds.\n\nIf the item at index is not assigned and the array has a type constraint,\n\nthen the zero value of that type is returned;\n\notherwise raises IndexError.'
        if index > self.__size: raise IndexError(f"{index} is outside the bounds of the array")
        if index > len(self.__arr):
            if self.__typeof != self.__NoType: return self.__typeof()
            else: raise IndexError(f"{index} is outside the bounds of the assigned indexes")
        return self.__arr[index]
    
    def set(self, index: int, value: Any):
        '''Set item at given index.\n
        Raises IndexError if the index is out of bounds.\n
        If the item at index is not assigned and the array has a type constraint,\n
        then the zero value of that type is returned;\n
        otherwise raises IndexError.\n
        If the array has a type constraint and the given value isn't of that type, raises ValueError'''
        if index > self.__size: raise IndexError(f"{index} is outside the bounds of the array")
        if index > len(self.__arr):
            if self.__typeof != self.__NoType: return self.__typeof()
            else: raise IndexError(f"{index} is outside the bounds of the assigned indexes")
        if self.__typeof != self.__NoType and not isinstance(value, self.__typeof):
            raise ValueError(f"can not assign type of '{type(value).__name__}' to an array with a type constraint of '{self.__typeof.__name__}'")
        self.__arr[index] = value
    
    def copy(self, new_arr_size: int = None, new_array_type_constraint: Type = __NoType):
        '''
        Returns a shallow copy of the array.\n
        If `new_array_type_constraint` is `None`, then it uses the old array's type constraint.
        '''
        if new_arr_size == None: new_arr_size = self.__size
        if not new_array_type_constraint: new_array_type_constraint = self.__typeof
        return Array(new_arr_size, new_array_type_constraint, *self.__arr)

    def __repr__(self):
        arr = []
        for i in self.__arr:
            if isinstance(i, self.__NoType): arr.append('[NoType]')
            else: arr.append(f"{type(i).__name__}({i})")
        out = ', '.join(arr)
        if self.__typeof != self.__NoType: out += f'({self.__typeof.__name__})'
        out = f'Array({self.__size})[' + out + ']'
        return out


class Stack:
    def __init__(self, *initial_values: Any) -> None:
        self.__stack = []
        #self.__size = size # , size: int = -1
        if len(initial_values): self.__stack = list(initial_values)
    
    def pop(self):
        if not len(self.__stack): raise IndexError('Can not pop value as stack is empty')
        return self.__stack.pop()

    def push(self, value: Any): self.__stack.append(value)

    def peek(self):
        if not len(self.__stack): raise IndexError('Can not pop value as stack is empty')
        return self.__stack[-1]



class Nil:
    def __repr__(self): return 'Nil'

    def __eq__(self, value: object) -> bool: return None == value

    def __ne__(self, value: object) -> bool: return None != value

#### END CLASSES ####



#### GETTERS ####

def get_control_tag(vars: dict[str, Any], funcs: dict[str, PlentranFunction], tag: str, ln: int, program: str) -> tuple[Any, Error | None]:

    if tag == '@IN': return input('input wanted\n'), None

    if tag == '@FILE': return __file__, None

    if tag == '@LIST': return [], None

    if tag.startswith('@LEN:'):
        o = tag.removeprefix('@LEN:')
        o_converted, o_err = get_value(vars, o, ln, program)
        if o_err: return None, o_err
        try:
            return len(o_converted), None
        except TypeError:
            return None, Error('InvalidValueError', f"invalid value '{o_converted}' for control tag 'LEN'", ln, program)

    if tag.startswith('@RAND:') and tag.count(':') == 2:
        r_min, r_max = tag.removeprefix('@RAND:').split(':')

        min_converted, min_err = get_value(vars, r_min, ln, program)
        if min_err: return None, min_err

        max_converted, max_err = get_value(vars, r_max, ln, program)
        if max_err: return None, max_err

        if not isinstance(min_converted, int): return None, Error('InvalidValueError', f"invalid value '{min_converted}' for control tag 'RAND', minimum must be an int", ln, program)
        if not isinstance(max_converted, int): return None, Error('InvalidValueError', f"invalid value '{max_converted}' for control tag 'RAND', maximum must be an int", ln, program)

        if min_converted > max_converted: return None, Error('InvalidValueError', f"minimum range cannot be greater than maximum range", ln, program)

        return randint(min_converted, max_converted), None
    
    if tag.startswith('@ARRAY:'): pass

    if tag.startswith('@RUN:'):
        funcname = tag.removeprefix('@RUN:').strip()
        if funcname not in list(funcs):
            return None, Error('UnknownFunctionError', f"unknown function '{funcname}'", ln, program)
        funcs[funcname].run()
        

    return None, Error('InvalidControlTagError', f"invalid control tag '{tag}'", ln, program)


def get_value(vars: dict[str, Any], value: str, ln: int, program: str) -> tuple[str | float | int | Path | Nil | None, Error | None]:
    if value.startswith('"') and value.endswith('"'):
        return value.removeprefix('"').removesuffix('"'), None
    
    elif value.isdigit():
        if '.' in value: return float(value), None
        return int(value), None
    
    elif value == 'false': return False, None

    elif value == 'true': return True, None
    
    elif value == '~': return Nil(), None

    elif value.startswith('@'):
        tagval, err = get_control_tag(vars, value, ln, program)
        if err: return None, err
        return tagval, None
    
    elif value.startswith('f#'): return Path(value.removeprefix('f#')), None

    elif value in list(vars): return vars[value], None

    elif ' == ' in value:
        r, l = value.split(' == ', 1)
        expr_res, expr_err = process_expression(vars, r, '==', l, ln, program)
        if expr_err: return None, expr_err
        return expr_res, None
    
    elif ' != ' in value:
        r, l = value.split(' != ', 1)
        expr_res, expr_err = process_expression(vars, r, '!=', l, ln, program)
        if expr_err: return None, expr_err
        return expr_res, None
    
    elif 'not ' in value:
        l = value.split('not ', 1)
        expr_res, expr_err = process_expression(vars, '~', 'not', l, ln, program)
        if expr_err: return None, expr_err
        return expr_res, None
    
    elif ' and ' in value:
        r, l = value.split(' and ', 1)
        expr_res, expr_err = process_expression(vars, r, 'and', l, ln, program)
        if expr_err: return None, expr_err
        return expr_res, None
    
    elif ' or ' in value:
        r, l = value.split(' or ', 1)
        expr_res, expr_err = process_expression(vars, r, 'or', l, ln, program)
        if expr_err: return None, expr_err
        return expr_res, None
    
    elif ' < ' in value:
        r, l = value.split(' < ', 1)
        expr_res, expr_err = process_expression(vars, r, '<', l, ln, program)
        if expr_err: return None, expr_err
        return expr_res, None
    
    elif ' > ' in value:
        r, l = value.split(' > ', 1)
        expr_res, expr_err = process_expression(vars, r, '>', l, ln, program)
        if expr_err: return None, expr_err
        return expr_res, None
    
    elif ' ^ ' in value:
        r, l = value.split(' ^ ', 1)
        expr_res, expr_err = process_expression(vars, r, '^', l, ln, program)
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
    
    elif ' % ' in value:
        r, l = value.split(' % ', 1)
        expr_res, expr_err = process_expression(vars, r, '%', l, ln, program)
        if expr_err: return None, expr_err
        return expr_res, None
    
    elif ' // ' in value:
        r, l = value.split(' // ', 1)
        expr_res, expr_err = process_expression(vars, r, '//', l, ln, program)
        if expr_err: return None, expr_err
        return expr_res, None
    
    elif ' * ' in value:
        r, l = value.split(' * ', 1)
        expr_res, expr_err = process_expression(vars, r, '*', l, ln, program)
        if expr_err: return None, expr_err
        return expr_res, None
    
    elif ' - ' in value:
        r, l = value.split(' - ', 1)
        expr_res, expr_err = process_expression(vars, r, '-', l, ln, program)
        if expr_err: return None, expr_err
        return expr_res, None
    
    elif ' + ' in value:
        r, l = value.split(' + ', 1)
        expr_res, expr_err = process_expression(vars, r, '+', l, ln, program)
        if expr_err: return None, expr_err
        return expr_res, None
    
    else: return None, Error('UnknownValueError', f"unknown value '{value}'", ln, program)

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

            # boolean operations
            case 'and': return right_converted and left_converted, None
            case 'or': return right_converted or left_converted, None
            case 'not': return not left_converted, None
            case '==': return right_converted == left_converted, None
            case '!=': return right_converted != left_converted, None
            case '>': return right_converted > left_converted, None
            case '<': return right_converted < left_converted, None
    except ValueError as e: return None, Error('ExpressionError', e, ln, program)


def create_variable(vars: dict[str, Any], varname: str, value: str, ln: int, program: str) -> Error | None:
    if varname in list(vars):
        return Error('AlreadyDefinedVariableError', f"variable '{varname}' has already been defined", ln, program)
    elif varname == '': return Error('InvalidIdentifierError', "variable identifier can't be empty", ln, program)
    
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


def delete_variable(vars: dict[str, Any], funcs: dict[str, PlentranFunction], varname: str, ln: int, program: str) -> Error | None:
    if varname not in list(vars):
        if varname not in list(funcs):
            return Error('UndefinedVariableError', f"variable '{varname}' has not been defined", ln, program)
        else:
            del funcs[varname]
    else:
        del vars[varname]

    return None


def return_value(vars: dict[str, Any], funcs: dict[str, PlentranFunction], value: str, ln: int, program: str) -> tuple[Any, Error | None]:
    converted, err = get_value(vars, value, ln, program)
    if err: return None, err
    return converted, None


def process_if(vars: dict[str, Any], statement: str, ln: int, program: str) -> tuple[bool, Error | None]:
    statement_res, err = get_value(vars, statement, ln, program)
    if err: return False, err
    if statement_res == True: return True, None
    else: return False, None

#### END OPERATIONS ####



#### MAIN ####

def process_line(vars: dict[str, Any], funcs: dict[str, PlentranFunction], pub_vars_set: set[str], line: str, ln: int, cprog: str, all_programs: list[str]) -> tuple[str, int, Error | None]:
    if_statement_cache = None
    if line.startswith('if ') and line.endswith(' then'):
        if_statement_cache = line.removeprefix('if ').removesuffix(' then')
    
    while_loop_cache = None
    if line.startswith('while ') and line.endswith(' do'):
        while_loop_cache = line.removeprefix('while ').removesuffix(' do')

    if not if_statement_cache and not while_loop_cache:
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

    if if_statement_cache:
        l = ['if', if_statement_cache, 'then']
    elif while_loop_cache:
        l = ['while', while_loop_cache, 'do']
    else: l = line.split(' ') # split line by spaces

    if not if_statement_cache and not while_loop_cache:
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
            if l[1] == '': return '', 0, Error('InvalidIdentifierError', "program identifier can't be empty", ln, cprog)
            if l[1] == all_programs[0]: return '', 0, Error('InvalidProgramNameError', "program name can't be '<main>'", ln, cprog)
            if l[1] in all_programs: return '', 0, Error('ProgramAlreadyCreatedError', f"program '{l[1]}' has already been created", ln, cprog)
            return l[1], 1, None
        
        case ('#endprogram', progname):
            if l[1] == '': return '', 0, Error('InvalidIdentifierError', "program identifier can't be empty", ln, cprog)
            if l[1] == all_programs[0]: return '', 0, Error('InvalidProgramNameError', "program name can't be '<main>'", ln, cprog)
            if l[1] != cprog: return '', 0, Error('InvalidProgramError', f"program '{l[1]}' is not the current program", ln, cprog)
            return l[1], -1, None

        #case ('return', val):
        #    err = return_value(vars, l[1], ln, cprog)
        #    if err: return '', 0, err
        #    valid = True

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
            err = delete_variable(vars, funcs, l[1], ln, cprog)
            if err: return '', 0, err
            valid = True
        
        case ('if', statement, 'then'):
            if_res, err = process_if(vars, if_statement_cache, ln, cprog)
            if err: return '', 0, err
            if if_res: return '', 3, None
            return '', 2, None
            #valid = True
        
        case ('while', statement, 'do'):
            while_res, err = process_if(vars, while_loop_cache, ln, cprog)
            if err: return '', 0, err
            if while_res: return '', 0, None
            return '', 4, None

        #case ('createf', filename):
        #    err = delete_var(vars, l[1])
        #    if err: return '', 0, err
        #    valid = True

        #case ('flushf', filename):
        #    err = delete_var(vars, l[1])
        #    if err: return '', 0, err
        #    valid = True
    
    # other cases
    #if len(l) >= 2 and not valid:
    #    if l[0] == '@RUN' and l[1] in list(funcs):
    #        err = run_function(vars, l[1], ' '.join([i for n, i in enumerate(l) if n > 2]), ln, cprog)
    #        if err: return '', 0, err
    #        valid = True
    
    if len(l) >= 4 and not valid:
        if l[0] == 'define' and l[2] == 'as':
            err = create_variable(vars, l[1], ' '.join([i for n, i in enumerate(l) if n > 2]), ln, cprog)
            if err: return '', 0, err
            valid = True
        elif l[0] == 'assign' and l[2] == 'with':
            err = assign_variable(vars, l[1], ' '.join([i for n, i in enumerate(l) if n > 2]), ln, cprog)
            if err: return '', 0, err
            valid = True
    
    if not valid: return '', 0, Error('UnkownPatternError', f'unkown pattern ({', '.join(["'" + i + "'" for i in l])})', ln, cprog)
    return '', 0, None



def run_pet(text: str, is_function: bool = False, is_imported: bool = False, main_program_name: str = '<main>', injected_vars: dict[str, Any] = None, injected_funcs: dict[str, PlentranFunction] = None) -> None | dict[str, Any]:
    #lines = [l.split(';;')[0].strip() for l in text.split('\n') if not l.startswith(';;') and l.strip() != '']
    #lines = [l for l in lines if l != '']

    

    lines = [l.split(';;')[0].strip() for l in text.split('\n')]

    if_to_else = {}
    if_to_endif = {}
    else_to_endif = {}

    while_to_endwhile = {}
    breakwhile_to_endwhile = {}
    endwhile_to_while = {}

    # get if-else-endif and while-endwhile positions
    else_index_stack: list[int] = []
    if_index_stack: list[list[int, bool]] = []

    while_index_stack: list[int] = []
    breakwhile_index_stack: list[int] = []

    for ln, l in enumerate(lines):
        if l.startswith('if ') and l.endswith(' then'):
            if_index_stack.append([ln, False])
        elif l == 'else do':
            else_index_stack.append(ln)
            if_index_stack[-1][1] = True
        elif l == 'endif' and len(if_index_stack):
            if_idx, has_else = if_index_stack.pop()
            if_to_endif[if_idx] = ln
            if has_else:
                else_idx = else_index_stack.pop()
                if_to_else[if_idx] = else_idx
                else_to_endif[else_idx] = ln
        elif l.startswith('while ') and l.endswith(' do'):
            while_index_stack.append(ln)
        elif l == 'breakwhile' and len(while_index_stack): pass
        elif l == 'endwhile' and len(while_index_stack):
            while_idx = while_index_stack.pop()
            while_to_endwhile[while_idx] = ln
            endwhile_to_while[ln] = while_idx


    all_programs = [main_program_name]

    programs = [main_program_name]
 
    public_vars_set: set[str] = set()

    vars: dict[str, Any] = injected_vars if injected_vars else {}

    funcs: dict[str, PlentranFunction] = injected_funcs if injected_funcs else {}

    #collect_lines = False
    #collected_lines = []

    # if statement booleans
    should_jump_to_endif_from_else = False
    ignore_next_endif = False

    # while loop booleans
    jump_back_to_while_from_endwhile = True

    to_be_returned: Nil | Error | Any = Nil()

    # if ln not in list(if_to_else): print(Error('IfStatementError', f"could not index ", ln, programs[-1]).error()); return

    ln = 0
    while ln < len(lines):
        l = lines[ln]
        #print(ln, l)
        if l == '' or l.startswith(';;'): ln += 1; continue

        if l == 'endif' and ignore_next_endif: ignore_next_endif = False; ln += 1; continue

        if l == 'else do' and should_jump_to_endif_from_else:
            if ln not in list(else_to_endif): print(Error('IfStatementError', f"could not index of 'else->end'", ln, programs[-1]).error()); return
            should_jump_to_endif_from_else = False
            ln = else_to_endif[ln] + 1; continue
        
        if l == 'endwhile' and jump_back_to_while_from_endwhile: ln = endwhile_to_while[ln]; continue

        common_line_output, exitcode, err = process_line(vars, funcs, public_vars_set, l, ln+1, programs[-1], all_programs)
        if err: print(err.error()); return

        if exitcode == 1:
            programs.append(common_line_output)
            all_programs.append(common_line_output)

        elif exitcode == -1: programs.pop()

        elif exitcode == 2:
            if ln not in list(if_to_else):
                if ln not in list(if_to_endif): print(Error('IfStatementError', f"could not index 'if->else' nor 'if->endif'", ln, programs[-1]).error()); return
                else: ln = if_to_endif[ln]
            else: ln = if_to_else[ln]; ignore_next_endif = True

        elif exitcode == 3:
            if ln in list(if_to_else): should_jump_to_endif_from_else = True
            else: ignore_next_endif = True

        elif exitcode == 4:
            if ln not in list(while_to_endwhile): print(Error('WhileLoopError', f"could not index 'while->endwhile'", ln, programs[-1]).error()); return
            ln = while_to_endwhile[ln]

        elif exitcode != 0: print(Error('InterpreterError', f"program exit code should be in range -1 to 2(inclusive), but it was '{exitcode}' instead", ln, programs[-1]).error()); return
        
        ln += 1

    ### exit codes ###
    # * -1: pop latest program
    # * 0: do nothing
    # * 1: push new program
    # * 2: jump to 'else' from 'if'
    # * 3: jump to 'endif' from 'else'
    # * 4: jump to 'endwhile' from 'while'
    # * 5: get 
    ##################

    if is_function:
        return to_be_returned
    if is_imported:
        return {varname: vars[varname] for varname in vars if varname in public_vars_set}

#### END MAIN ####



#### PLENTRAN HEADER FILE STUFF ####

def load_plentran_header(filepath: str, ln: int, program: str) -> tuple[set[str], Error | None]:
    if not Path(filepath).exists(): return [], Error('FileNotFoundError', f"file at path '{str(filepath)}' does not exist", ln, program)
    with open(filepath, 'rt') as file: fcontent = file.read()


#### END PLENTRAN HEADER STUFF ####




test_array = Array(10)

print(test_array)

test_array.set(0, '*')
test_array.set(1, '<<<<->>>>')

print(test_array)