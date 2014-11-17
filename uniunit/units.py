# encoding=utf-8
from .uniunit import Prefix, Atom, UniUnit, United


one = Prefix("", 1)
K = Prefix("K", 10 ** 3)
M = Prefix("M", 10 ** 6)
m = Prefix("m", 10 ** -3)
u = Prefix("u", 10 ** -6)

Byte = Atom("Byte", "B")
Bit = Atom("Bit", "b")
Second = Atom("Second", "s")
Metre = Atom("Metre", "m")
Gram = Atom("Gram", "g")
Kilogram = Atom("Kilogram", "kg")

Kilogram = UniUnit(atom=Kilogram)
Mbps = M * Bit / Second
Kb = K * Bit
