# encoding=utf-8


class Prefix(object):
    CONS = {
        10 ** 12: "T",
        10 ** 9: "G",
        10 ** 6: "M",
        10 ** 3: "K",
        0: "",
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
        return "<Prefix {} {}>".format(self.literal, self.value)

    def __str__(self):
        return self.literal

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


class Atom(object):
    def __init__(self, literal, order=1):
        self.literal = literal
        self._order_key = order

    def __eq__(self, other):
        return isinstance(other, Atom) and self.literal == other.literal

    def __rmul__(self, other):
        if isinstance(other, Prefix):
            return UniUnit(prefix=other, fraction=([self], []))
        else:
            return NotImplemented

    def order_key(self):
        return self._order_key

    def __mul__(self, other):
        if isinstance(other, Atom):
            return UniUnit(fraction=([self, other], []))
        else:
            raise TypeError("Must be Unit.")

    def __truediv__(self, other):
        if isinstance(other, Atom):
            return UniUnit(fraction=([self], [other]))
        else:
            raise TypeError("Must be Unit.")

    def __repr__(self):
        return "<Atom {} {}>".format(self.literal, self._order_key)

    def __str__(self):
        return self.literal


Byte = Atom("B")
Bit = Atom("b")
Second = Atom("s")
Metre = Atom("m")
Gram = Atom("g")
one = Prefix("", 1)
K = Prefix("K", 10 ** 3)
M = Prefix("M", 10 ** 6)
m = Prefix("m", 10 ** -3)
u = Prefix("u", 10 ** -6)


class UniUnit(object):
    def __init__(self, prefix=None, atom=None, fraction=None):
        self.prefix = prefix if prefix is not None else one
        if atom:
            self.fraction = ([atom], [])
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


class United(object):
    def __init__(self, value, uunit):
        self.value = value
        self.uunit = uunit

    def __str__(self):
        return "{}{}".format(self.value, self.uunit)

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


Mbps = M * Bit / Second
Kb = K * Bit
if __name__ == '__main__':
    a = 4 * Kb
    b = 16 * Mbps
    print(a/b)
