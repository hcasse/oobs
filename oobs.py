#!/usr/bin/python3

import argparse
import json
import os.path
import sys
import tempfile
import time
import shutil
import subprocess
import sys

class Block:

	def __init__(self, title, id, code = None, to = None):
		self.title = title
		self.id = id
		self.code = code
		self.to = to
		self.preds = []
		self.succs = []
		self.next = next
		self.cfg = None

class Edge:

	def __init__(self, src, snk, taken):
		self.src = src
		self.snk = snk
		self.taken = taken
		src.succs.append(self)
		snk.preds.append(self)

class CFG:

	def __init__(self, label, id):
		self.label = label
		self.id = id
		self.blocks = []
		self.program = None

	def add(self, block):
		block.cfg = self
		self.blocks.append(block)
		self.program.block_map[block.id] = block

class Program:

	def __init__(self):
		self.cfgs = []
		self.cfg_map = {}
		self.block_map = {}

	def add(self, g):
		self.cfgs.append(g)
		self.cfg_map[g.id] = g
		g.program = self

	def block(self, id):
		return self.block_map[id]

	def cfg(self, id):
		return self.cfg_map[id]


class State:

	def __init__(self, value, gen, next = None):
		self.value = value
		self.gen = gen
		self.next = next

	def __str__(self):
		return "%s" % self.value

	def count(self):
		cnt = 0
		cur = self
		while cur != None:
			cnt = cnt + 1
			cur = cur.next
		return cnt

	def closest(self, gen):
		bst = self
		dif = abs(self.gen - gen)
		cur = self.next
		while cur != None:
			ndif = abs(cur.gen - gen)
			if ndif < dif:
				bst = cur
		return bst

EMPTY_STATE = State(None, 0)


def load(file):
	"""Load a trace file. Return (program, state map)"""
	js = json.load(file)

	# load CFG
	program = Program()
	for jg in js["program"]:
		g = CFG(jg["label"], jg["id"])
		program.add(g)

		# load blocks
		for jv in jg["blocks"]:
			id = jv["id"]
			title = jv["title"]
			try:
				code = jv["code"]
			except KeyError:
				code = None
			try:
				to = jv["to"]
			except KeyError:
				to = None
			g.add(Block(title, id, code, to))

		# load edges
		for je in jg["edges"]:
			src = program.block(je["src"])
			snk = program.block(je["snk"])
			taken = je["taken"]
			Edge(src, snk, taken)

	# fix the "to" arguments
	for g in program.cfgs:
		for v in g.blocks:
			if v.to != None:
				v.to = program.cfg_map[v.to]

	# load the states
	states = { }
	gen = 0
	for jst in js["analysis"]:
		id = jst["id"]
		try:
			next = states[id]
		except KeyError:
			next = None
		states[(id, jst["type"])] = State(jst["state"], gen, next)
		gen = gen + 1

	# return result
	return (program, states)


def gen_dots(program):
	"""Generate .dot files for the CFG of the program.
	Return path of the initial CFG."""

	def escape(s):
		return s.translate(str.maketrans({
			"\"": "\\\"",
			"\\": "\\\\"
		}))

	def escape_code(s):
		return s.translate(str.maketrans({
			"{": "\\{",
			"}": "\\}",
			"\t": "    "
		}))

	dir = tempfile.mkdtemp("-oobs")
	init_path = None

	for g in program.cfgs:
		path = "%s/%s.dot" % (dir, g.label)
		if init_path == None:
			init_path = path
		out = open(path, "w")
		out.write("digraph \"%s\" {\n" % escape(g.label))
		out.write("node [margin=0];\n")

		# write the nodes
		for v in g.blocks:
			out.write("\"%d\" [" % v.id)
			if v.code == None:
				out.write("label=<%s [%d]>" % (escape(v.title), v.id))
				if v.to != None:
					out.write(", URL=\"%s.dot\"" % v.to.label)
			else:
				out.write("label=<<TABLE BORDER=\"0\"><TR><TD><B>%s [%d]</B></TD></TR><HR/><TR><TD ALIGN=\"left\">%s<BR ALIGN=\"left\"/></TD></TR></TABLE>>" % (
					v.title, v.id,
					"<BR ALIGN=\"left\"/>".join([escape_code(c) for c in v.code])
				))
				out.write(", shape=Mrecord")
			out.write("];\n")

		# write the edges
		for v in g.blocks:
			for e in v.succs:
				out.write("\"%d\" -> \"%d\"" % (e.src.id, e.snk.id))
				if not e.taken:
					out.write(" [style=dashed]")
				out.write(";\n");

		# file suffix
		out.write("}\n")
		out.close()

	# return initial .dot
	return init_path


class CLI:

	def quit(self, args):
		self.done = True
		self.out.write("Quit!\n")
		return False

	def help(self, args):
		self.out.write(
"""Commands:
d		Displayed detailed code.
gID		Change the current block.
h, ?	Display help message.
q		Quit.
""")
		return False

	def total(self, id, type):
		try:
			return self.states[(self.bb.id, type)].count()
		except KeyError:
			return 0

	def display(self):
		for e in self.bb.preds:
			self.out.write("[%s - %d] " % (e.src.title, e.src.id))
		self.out.write("\n")
		self.out.write("IN: %s\n" % self.istate)
		self.out.write("%s [%d] (%d/%d)\n" % (
			self.bb.title,
			self.bb.id,
			self.istate.count() - 1,
			self.total(self.bb.id, "in")
		))
		if self.bb.code != None:
			for c in self.bb.code:
				if not self.compact or not c.startswith("\t"):
					self.out.write("\t%s\n" % c)
		self.out.write("OUT: %s\n" % self.ostate)
		for e in self.bb.succs:
			self.out.write("[%s - %d] " % (e.snk.title, e.snk.id))
		self.out.write("\n")			

	def details(self, args):
		"""Display the code in details."""
		old = self.compact
		self.compact = False
		self.display()
		self.compact = old
		return False

	def set_bb(self, bb):
		"""Set the new current BB."""
		self.bb = bb
		try:
			self.istate = self.states[(bb.id, "in")].closest(self.istate.gen)
		except KeyError:
			self.istate = EMPTY_STATE
		try:
			self.ostate = self.states[(bb.id, "out")].closest(self.ostate.gen)
		except KeyError as e:
			self.ostate = EMPTY_STATE

	def go(self, args):
		"""Change the current block."""
		try:
			id = int(args)
			self.set_bb(self.program.block_map[id])
			return True
		except ValueError:
			self.out.write("ERROR: argument should be an ID!\n")
			return False
		except KeyError:
			self.out.write("ERROR: bad block ID: %s\n" % args)
			return False

	def __init__(self, program, states):
		self.cmds = {
			"d": self.details,
			"g": self.go,
			"h": self.help,
			"q": self.quit,
			"?": self.help
		}

		# initialization
		self.out = sys.stdout
		self.program = program
		self.states = states
		self.done = False
		self.bb = program.cfgs[0].blocks[1]
		self.istate = states[(self.bb.id, "in")]
		self.ostate = states[(self.bb.id, "out")]
		self.compact = True

		# main loop
		self.display()
		while not self.done:
			try:
				cmd = input("> ")
				if cmd == "":
					continue
				try:
					if self.cmds[cmd[0]](cmd[1:]):
						self.display()
				except KeyError:
					self.out.write("ERROR: unknown commande: %s\n" % cmd)
			except (KeyboardInterrupt, EOFError):
				self.quit("")


def main():

	# parse arguments
	parser = argparse.ArgumentParser(
		description="OTAWA Observer for Abstract Interpretation trace."
	)
	parser.add_argument('trace', type=open,
		help="trace path")
	parser.add_argument("-x", "--xdot", action="store_true",
		help="display the CFG with otawa-xdot")
	args = parser.parse_args()

	# load the trace
	(program, states) = load(args.trace)

	# display the CFGs
	if args.xdot:
		path = gen_dots(program)
		proc = subprocess.Popen(
			"otawa-xdot.py %s" % path,
			shell=True,
			stdout=subprocess.DEVNULL,
			stderr=subprocess.DEVNULL)

	# wait for command until interrupted
	CLI(program, states)

	# cleanup all
	if args.xdot:
		proc.terminate()
		d = os.path.dirname(path)
		shutil.rmtree(d)

if __name__ == "__main__":
	main()
