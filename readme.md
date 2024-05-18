# Plentran
I like the look of Fortran, an english only language is an interesting idea, and Python's pattern matching makes all of this really easy<br>
Hence, Plain english translation system(Plentran) was born

<br>

"hello world" example:
```
;; create variable 'x' with a string value
define x as "Hello, Catdog!"

;; print variable 'x' to console
send x to @OUT
```
for more examples, check the [examples](./examples/) folder

<br>

Here's a cool fun fact:<br>
This repo's interpreter doesn't use a lexer or a parser!<br>
Instead, it uses an incredibly cursed(but suprisingly organized) series of splits and recursion to do stuff!<br>
What is this monstrosity I've created?

<br>
<br>

**This repository is licensed under the Apache Version 2.0 license**