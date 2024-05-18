from interpreter import run_pet
from pathlib import Path



def showhelp():
    print('===commands===')
    print("'help': shows this list")
    print("'run': runs a Plentran file")



def main():
    while True:
        inp = input('> ').strip()
        if inp.casefold() in ('exit', 'quit'): break

        elif inp.startswith('run '):
            path = inp.removeprefix('run ').strip()
            if not path.endswith('.pet'): path += '.pet'
            path = Path(path)
            if not path.exists(): print(f"file '{str(path)}' does not exist"); continue
            with open(path, 'rt') as f: fcontent = f.read()
            run_pet(fcontent)



if __name__ == '__main__':
    main()