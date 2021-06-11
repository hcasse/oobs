# OObs -- OTAWA Observer for Abstract Interpretation

## Input format

__oops__ supports as input a JSON file structured as:

```
{
	"program" : [ CFG* ],
	"analysis": [ STATE* ]
}
```
A CFG is defined by:
```
{
	"label": STR,
	"id": INT
	"blocks": [ BLOCK* ],
	"edges": [ EDGE* ]
}
```

A _BLOCK_ may have three forms. Entry, exit or call with unknown target:
```
{
	"id": INT,
	"title": STR
}
```
Notice the identifier `id` must be unique over the whole program.
A call _BLOCK_ with identifier target (the `to` field refer to CFG identifier):
```
{
	"id": INT,
	"title": STR,
	"to": ID
}
```
Finally, finally a basic _BLOCK_ supports also its code as a sequence of lines:
```
{
	"id": INT,
	"title": STR,
	"code": [ STR* ]
}
```

An _EDGE_ is described by:
```
{
	"src": INT,
	"snk": INT,
	"taken": BOOL
}
```
`src`and `snk` refers to _BLOCK_ identifiers.

A _STATE_ has very simple and versatile structure:
```
{
	"id": INT,
	"type": "in"|"out",
	"state": ANY
}
```
`id` is a _BLOCK_ identifier concerned by the state. `type` represents
an input or an output state. `state`is the state value ifself, that is
any JSON value.

It must be noted that the state must be listed in their order of computation:
this order is used to determine the generation of the states when a block
supports several states.
