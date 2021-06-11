# OObs -- OTAWA Observer for Abstract Interpretation

## Display

[a - BB] [b - BB]		% predecessors
BB [age]
STATE BEFORE
CODE
STATE AFTER
[c - BB] [d - BB]		% successors

Keys:
	a, b, c, ... -- display predecessor, successor
	A, B, C, ... -- move to successor, predecessor
	ctrl-c, ctrl-d -- stop
	<, > -- younger/older age of state
	(, ) -- youngest/oldest age of state
	^ -- states of predecessors (same or younger age)
	$ -- states of successors (same or younger age)
	. -- redisplay current block
	! NUM -- goto BB
