# encoding=utf-8
import operator
from functools import reduce
from itertools import repeat, chain


class Prefix(object):
    CONS = {
        10 ** 12: "T",
        10 ** 9: "G",
        10 ** 6: "M",
        10 ** 3: "K",
        1: "",
        10 ** -3: "m",
        10 ** -6: "u",
        10 ** -9: "n",
        10 ** -12: "p",
    }

    def __init__(self, literal, value):
        self.literal = literal
        self.value = value

    def __eq__(self, other):
        return isinstance(other, Prefix) and self.value == other.value

    def __repr__(self):
        return "Prefix({!r}, {!r})".format(self.literal, self.value)

    def __str__(self):
        return "<Prefix {} {}>".format(self.literal, self.value)

    def __truediv__(self, other):
        if not isinstance(other, Prefix):
            return NotImplemented
        value = self.value / other.value
        if value in Prefix.CONS:
            return Prefix(Prefix.CONS[value], value)
        return Prefix("?", value)

    def __mul__(self, other):
        if not isinstance(other, Prefix):
            return NotImplemented
        value = self.value * other.value
        if value in Prefix.CONS:
            return Prefix(Prefix.CONS[value], value)
        return Prefix("?", value)

    def __pow__(self, power, modulo=None):
        if not isinstance(power, int) or modulo:
            return NotImplemented
        new_value = self.value ** power
        return Prefix(Prefix.CONS.get(new_value, "?"), new_value)

one = Prefix("", 1)


class Atom(object):
    def __init__(self, atom_id, literal, order=1):
        self.id = atom_id
        self.literal = literal
        self._order_key = order

    def order_key(self):
        return self._order_key

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return isinstance(other, Atom) and self.id == other.id

    def __rmul__(self, other):
        if isinstance(other, Prefix):
            return UniUnit(prefix=other, fraction=([self], []))
        else:
            return NotImplemented

    def __mul__(self, other):
        if isinstance(other, Atom):
            return UniUnit(fraction=([self, other], []))
        elif isinstance(other, UniUnit):
            return UniUnit(prefix=other.prefix,
                           fraction=(other.fraction[0] + [self],
                                     other.fraction[1]))
        else:
            raise TypeError("Must be Unit.")

    def __truediv__(self, other):
        if isinstance(other, Atom):
            return UniUnit(fraction=([self], [other]))
        elif isinstance(other, UniUnit):
            return UniUnit(prefix=other.prefix,
                           fraction=(other.fraction[1] + [self],
                                     other.fraction[0]))
        else:
            return NotImplemented

    def __pow__(self, power, modulo=None):
        if not isinstance(power, int) or modulo:
            return NotImplemented
        return reduce(operator.mul, repeat(self, power))

    def __repr__(self):
        return "Atom({!r}, {!r}, order={!r})".format(self.id, self.literal, self._order_key)

    def __str__(self):
        return self.literal


class UniUnit(object):
    def __init__(self, prefix=None, atom=None, fraction=None):
        self.prefix = prefix if prefix is not None else one
        if atom:
            self.fraction = ([atom], [])
        if fraction:
            self.fraction = fraction
        self.justify()

    def justify(self):
        numerator, denominator = self.fraction
        numerator.sort(key=lambda x: x.order_key())
        denominator.sort(key=lambda x: x.order_key())
        for _, n in enumerate(tuple(numerator)):
            if n in denominator:
                denominator.remove(n)
                numerator.remove(n)
        self.fraction = numerator, denominator

    def order_key(self):
        numerator = sum(map(lambda x: x.order_key(), self.fraction[0]))
        denominator = sum(map(lambda x: x.order_key(), self.fraction[1]))
        if denominator is 0:
            return numerator
        else:
            return numerator / denominator

    def mul_by(self, other):
        return UniUnit(fraction=(self.fraction[0] + other.fraction[0],
                                 self.fraction[1] + other.fraction[1]),
                       prefix=self.prefix * other.prefix)

    def div_by(self, other):
        return UniUnit(fraction=(self.fraction[0] + other.fraction[1],
                                 self.fraction[1] + other.fraction[0]),
                       prefix=self.prefix / other.prefix)

    def __eq__(self, other):
        return isinstance(other, UniUnit) and self.fraction == other.fraction

    def __mul__(self, other):
        if isinstance(other, UniUnit):
            return self.mul_by(other)
        elif isinstance(other, Atom):
            return UniUnit(prefix=self.prefix,
                           fraction=(self.fraction[0] + [other],
                                     self.fraction[1]))
        else:
            raise TypeError("Must be Unit.")

    def __truediv__(self, other):
        if isinstance(other, UniUnit):
            return self.div_by(other)
        elif isinstance(other, Atom):
            return UniUnit(fraction=(self.fraction[0],
                                     self.fraction[1] + [other]),
                           prefix=self.prefix)
        else:
            raise TypeError("Must be Unit.")

    def __rmul__(self, other):
        if not isinstance(other, (int, float, complex)):
            return NotImplemented
        else:
            return United(other, self)

    def __pow__(self, power, modulo=None):
        if not isinstance(power, int) or modulo:
            return NotImplemented
        return UniUnit(prefix=self.prefix ** power,
                       fraction=(self.fraction[0] * power,
                                 self.fraction[1] * power))

    @staticmethod
    def format_pair(pair):
        atom_, e = pair
        if e == 1:
            return str(atom_)
        return "{}^{}".format(*pair)

    @classmethod
    def _dump_atom_lists(cls, *args):
        retvals = []
        for arg in args:
            n, _rec = [], []
            for i in arg:
                if i not in _rec:
                    _rec.append(i)
                    n.append((i, arg.count(i)))
            retvals.append(n)
        return retvals

    def full_exp(self):
        en_, ed_ = self._dump_atom_lists(*self.fraction)
        ed_ = [(a_, -c_) for a_, c_ in ed_]
        return "".join(map(self.format_pair, chain(en_, ed_)))

    def with_exp(self):
        dumped_atoms = self._dump_atom_lists(*self.fraction)
        formater_ = lambda x: ''.join(map(self.format_pair, x))
        return "/".join(map(formater_, dumped_atoms))

    def __str__(self):
        numerator, denominator = self.fraction
        if not numerator and not denominator:
            return ''
        if self.prefix:
            ps = self.prefix.literal
        else:
            ps = ''
        if denominator:
            vs = "{}/{}".format(''.join(map(str, numerator)),
                                ''.join(map(str, denominator)))
        else:
            vs = ''.join(map(str, numerator))
        return ps + vs

    def __repr__(self):
        tpl = "UniUnit(prefix={!r}, fraction={!r})"
        return tpl.format(self.prefix, self.fraction)


class United(object):
    def __init__(self, value, uunit):
        self.value = value
        self.uunit = uunit

    def __str__(self):
        return "{}{}".format(self.value, self.uunit)

    def __repr__(self):
        return "United({!r}, {!r})".format(self.value, self.uunit)

    def __add__(self, other):
        if isinstance(other, United):
            pass
        else:
            return NotImplemented

    def __sub__(self, other):
        if isinstance(other, United):
            pass
        else:
            return NotImplemented

    def __mul__(self, other):
        if isinstance(other, United):
            new_uuint = self.uunit * other.uunit
            new_value = self.value * other.value
            if new_uuint is 1:
                return self.value * other.value
            else:
                return United(new_value, new_uuint)
        elif isinstance(other, (int, float)):
            return United(self.value * other, self.uunit)
        else:
            return NotImplemented

    def __truediv__(self, other):
        if isinstance(other, United):
            new_uuint = self.uunit / other.uunit
            new_value = self.value / other.value
            if new_uuint is 1:
                return self.value * other.value
            else:
                return United(new_value, new_uuint)
        elif isinstance(other, (int, float)):
            return United(self.value / other, self.uunit)
        else:
            return NotImplemented

    def __eq__(self, other):
        return all((isinstance(other, United),
                    self.value == other.value,
                    self.uunit == other.uunit))

