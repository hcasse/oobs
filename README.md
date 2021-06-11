# OObs
OTAWA observer of abstract interpretation results

## Command

__Oobs__ is able to navigate in the CFG and in the state produced by an
abstract interpretation performed in [OTAWA](http://www.otawa.fr).
To get an input file for __oobs__, you have to run an OTAWA analysis
passing a property enablong the output of a trace. For example,
in the example below, we ask the analysis `otawa::clp::Analysis` to
generate its analysis trace:
```
$ operform BINARY process:otawa::clp::Analysis --add-prop otawa::clp::TRACE=true
```

The generated file(s) depends on the performed analysis. For
`otawa::clp::Analysis`, a unique file named `clp-trace.json` is created.
To run __oobs__ on it, one has just to type:
```
$ oobs.py clp-trace.json
```
And the commande line user interface is started.

To let __oobs__ display also graphically the CFG (using `otawa-xdot.py`),
the option `-x` can be used:
```
$ oobs.py clp-trace.json -x
```

## Display

The basic interface provided by __oops__ is displayed below:
```
[BB - id] [BB - id]		% predecessors
BB [id] (generation/max generation)
IN: state
CODE
OUT: state
[BB - id] [BB - id]		% successors
> to type command here
```

To get the list of commands, type 'h' or '?'.

To leave, type 'q', "crtl-d" or "ctrl-c".

