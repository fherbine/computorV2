Computer V2
===========

A 42 project which is basically a reproduction of `bc`. Final grade **124/100**


How to install
-----------

- Make sure that you've installed `requirements.txt` with `pip`
- Run the program with: `python3 main.py`
- Type `help` after prompt for usage.
- Or see [pdf(EN)](computorv2.en.pdf) or [pdf(FR)](computor.fr.pdf) for usage.

How to run Unittests:
--------------------

- Please install `pytest` with pip
- Then run `python -m pytest .` at the root of the repository


Todos:
------

**MANDATORY**
- [x] Lexer
- [x] Parser
    - [x] variables handling
    - [x] functions handling
    - [x] complex handling
    - [x] matrix handling
- [x] Math lib

**Bonus**
- [ ] Documentation
- [x] Unittests
- [x] Function curve display (Kivy)
- [x] Added usual functions
- [ ] Radian computation for angles
- [ ] Function composition
- [ ] Norm computation
- [ ] History of commands w/results
- [ ] Matrix inversion
- [ ] An extension of the matrix computation applied to vector computation
- [x] Integer divs (floordivs)
- [x] Others (cmds: quit, help, stored vars, ...)
    - [x] quit
    - [x] vars
    - [x] funcs
    - [x] draw
    **BEWARE:** `draw` is not compatible w/MacOSX
