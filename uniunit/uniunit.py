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
            return UniUnit(prefix=other, rate=([self], []))
        else:
            return NotImplemented

    def order_key(self):
        return self._order_key

    def __mul__(self, other):
        if isinstance(other, Atom):
            return UniUnit.make_rate([self, other], [])
        else:
            raise TypeError("Must be Unit.")

    def __truediv__(self, other):
        if isinstance(other, Atom):
            return UniUnit.make_rate([self], [other])
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
one = Prefix("", 1)
K = Prefix("K", 10 ** 3)
M = Prefix("M", 10 ** 6)
m = Prefix("m", 10 ** -3)
u = Prefix("u", 10 ** -6)


class UniUnit(object):
    def __init__(self, prefix=None, atom=None, rate=None, product=None):
        self.prefix = prefix if prefix is not None else one
        self.atom = atom
        self.rate = rate
        self.product = product
        self._is_atom = False
        self._is_rate = False
        self._is_product = False
        if atom is not None:
            self._is_atom = True
            self.rate = ([atom], [])
        if product is not None:
            self._is_product = True
            self.rate = (product, [])
        if product is not None:
            self._is_product = True
        if rate is not None:
            self._is_rate = True
        self.justify()

    @classmethod
    def make_rate(cls, m, n, prefix=None):
        return UniUnit(rate=(m, n), prefix=prefix)

    @classmethod
    def make_product(cls, product):
        return UniUnit(product=product)

    def justify(self):
        numerator, denominator = self.rate
        numerator.sort(key=lambda x: x.order_key())
        denominator.sort(key=lambda x: x.order_key())
        for _, n in enumerate(tuple(numerator)):
            if n in denominator:
                denominator.remove(n)
                numerator.remove(n)
        self.rate = numerator, denominator

    def order_key(self):
        numerator = sum(map(lambda x: x.order_key(), self.rate[0]))
        denominator = sum(map(lambda x: x.order_key(), self.rate[1]))
        if denominator is 0:
            return numerator
        else:
            return numerator / denominator

    def without_prefix(self):
        return UniUnit(rate=self.rate)

    def div_by(self, other):
        sp, op = self.prefix, other.prefix
        self.prefix, other.prefix = one, one
        new_uu = UniUnit.make_rate(self.rate[0] + other.rate[1], self.rate[1] + other.rate[0])
        new_uu.prefix = sp / op
        return new_uu

    def mul_by(self, other):
        sp, op = self.prefix, other.prefix
        self.prefix, other.prefix = one, one
        new_uu = UniUnit.make_rate(self.rate[0] + other.rate[0], self.rate[1] + other.rate[1])
        new_uu.prefix = sp * op
        return new_uu

    def __eq__(self, other):
        return isinstance(other, UniUnit) and self.atom == other.atom

    def __mul__(self, other):
        if isinstance(other, UniUnit):
            return self.mul_by(other)
        elif isinstance(other, Atom):
            return UniUnit.make_rate(self.rate[0]+[other], self.rate[1], prefix=self.prefix)
        else:
            raise TypeError("Must be Unit.")

    def __truediv__(self, other):
        if isinstance(other, UniUnit):
            return self.div_by(other)
        elif isinstance(other, Atom):
            return UniUnit.make_rate(self.rate[0], self.rate[1] + [other], prefix=self.prefix)
        else:
            raise TypeError("Must be Unit.")

    def __str__(self):
        if self._is_product:
            us = ''.join(map(str, self.rate[0]))
        elif self._is_rate:
            numerator, denominator = self.rate
            ns = ''.join(map(str, numerator))
            ds = ''.join(map(str, denominator))
            us = '{}/{}'.format(ns, ds)
        elif self._is_atom:
            us = self.atom.literal
        else:
            numerator = self.rate[0]
            us = ''.join(map(str, numerator))
        if self.prefix:
            return self.prefix.literal + us
        else:
            return us


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


class Constructor(object):
    def __init__(self, uunit):
        self.uunit = uunit

    def __rmul__(self, other):
        return United(other, self.uunit)

    def __str__(self):
        return str(self.uunit)


Mbps = Constructor(M * Bit / Second)
Kb = Constructor(K * Bit)

if __name__ == '__main__':
    a = 4 * Kb
    b = 16 * Mbps
    c = a / b
    print(Mbps)
    print(c)
    print(K * K)
    print(M / K)
    t = (M * Bit / Second) * Second
    print(t)
