# this a Plentran Header file(PH)
# it's purpose is to specify exported variables and functions for a specific Plentran file

# single line comments only

# PH files don't have to be the same name as the Plentran file they're linked to,
# but they should be convention

# first you must say which Plentran file the header is linked to
%FILE%
./ph_example.pet
%ENDFILE%

# then you specify which functions and variables are public

# you can do '%ALL%' to make everything public

%PUBLIC%
publicVarTest_1
publicVarTest_2
%ENDPUBLIC%