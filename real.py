import math

# TODO remove and replace with Real
LOG_10_2 = math.log10(2)

class Real:
    '''
    Represents arbitrary precision floating point numbers.
    
    Internally, values are stored as (coefficient * 2 ^ exponent) where
    coefficient and exponent are arbitrary length integers. Each Real also
    stores its precision which determines the maximum number of bits in the
    coefficient. If an operation results in a coefficient with more bits than
    the value of precision, the lower bits of coefficient will be dropped.
    
    When an operation (+, -, *, /, //) occurs between two Real objects, the
    precision of the result is set to the minimum of the precision of each
    argument. This mimicks the idea behind significant figures.
    '''
    
    # Used for comparing Reals
    epsilon = 4
    
    # The default precision for new Reals
    default_precision = 256
    
    def __init__(self, arg1, arg2=None, **kwargs):
        if arg2 is None:
            if isinstance(arg1, int):
                coefficient, exponent = real_from_int(arg1)
            elif isinstance(arg1, float):
                coefficient, exponent = real_from_float(arg1)
            elif isinstance(arg1, str):
                coefficient, exponent = real_from_str(arg1)
            else:
                raise ValueError('Cannot construct a Real from {!r}'.format(type(arg1)))
        else:
            coefficient, exponent = arg1, arg2
        
        precision = kwargs.get('precision', Real.default_precision)
        if not isinstance(precision, int) or precision <= 0:
            raise ValueError('Real precision must be a positive integer')
        
        self.coefficient = coefficient
        self.exponent = exponent
        self.precision = precision
        
        self.normalize()
    
    def __repr__(self):
        return 'Real({}, precision={})'.format(str(self), self.precision)
    
    def __str__(self):
        return str_from_real(self)
    
    def clone(self):
        return Real(self.coefficient, self.exponent, precision=self.precision)
    
    def set_precision(self, precision):
        self.precision = int(precision)
        self.normalize()
    
    def normalize(self):
        '''
        Modifies this real so that all
        '''
        bit_diff = self.coefficient.bit_length() - self.precision
        if bit_diff > 0:
            self.coefficient >>= bit_diff
            self.exponent += bit_diff
        elif bit_diff < 0:
            self.coefficient <<= -bit_diff
            self.exponent += bit_diff
    
    def next(self):
        return Real(self.coefficient + 1, self.exponent, precision=self.precision)
    
    def prev(self):
        # TODO fails when coefficient is a power of 2
        return Real(self.coefficient - 1, self.exponent, precision=self.precision)
    
    
    
    # Comparison Operators
    
    def __eq__(self, other):
        if isinstance(other, Real):
            # TODO show that this does or does not fail in general
            return abs((self - other).coefficient) <= Real.epsilon
        else:
            raise NotImplementedError()
    
    def __ne__(self, other):
        if isinstance(other, Real):
            return abs((self - other).coefficient) > Real.epsilon
        else:
            raise NotImplementedError()
    
    def __gt__(self, other):
        if isinstance(other, Real):
            return (self - other).coefficient > Real.epsilon
        else:
            raise NotImplementedError()
    
    def __ge__(self, other):
        if isinstance(other, Real):
            return (self - other).coefficient >= -Real.epsilon
        else:
            raise NotImplementedError()
    
    def __lt__(self, other):
        if isinstance(other, Real):
            return (self - other).coefficient < -Real.epsilon
        else:
            raise NotImplementedError()
    
    def __le__(self, other):
        if isinstance(other, Real):
            return (self - other).coefficient <= Real.epsilon
        else:
            raise NotImplementedError()
    
    
    
    # Unary Operators
    
    def __pos__(self):
        return self
    
    def __neg__(self):
        return neg(self)
    
    def __abs__(self):
        return _abs(self)
    
    def __round__(self):
        return _round(self)
    
    def __ceil__(self):
        return ceil(self)
    
    def __floor__(self):
        return floor(self)
    
    
    
    # Arithmetic Operators
    
    def __add__(self, other):
        if isinstance(other, Real):
            return add(self, other)
        else:
            return add(self, Real(other))
    
    def __sub__(self, other):
        if isinstance(other, Real):
            return sub(self, other)
        else:
            return sub(self, Real(other))
    
    def __mul__(self, other):
        if isinstance(other, Real):
            return mul(self, other)
        else:
            return mul(self, Real(other))
    
    def __truediv__(self, other):
        if isinstance(other, Real):
            return div(self, other)
        else:
            return div(self, Real(other))
    
    def __floordiv__(self, other):
        if isinstance(other, Real):
            return floor(div(self, other))
        else:
            return floor(div(self, Real(other)))
    
    def __pow__(self, other):
        if isinstance(other, Real):
            return _pow(self, other)
        else:
            return _pow(self, Real(other))



#######################
# Auxiliary Functions #
#######################

def real_from_int(i):
    '''
    Returns the (coefficient, exponent) tuple which represents the int i.
    '''
    return i, 0

def real_from_float(f):
    '''
    Returns the (coefficient, exponent) tuple which represents the float f.
    '''
    coefficient, exponent = math.frexp(f)
    while math.floor(coefficient) != coefficient:
        coefficient *= 2
        exponent -= 1
    return int(coefficient), int(exponent)

def real_from_str(s):
    '''
    Returns the (coefficient, exponent) tuple which represents the str s.
    '''
    pass # TODO

def bitmask(k):
    return (1 << k) - 1

def unshift(k):
    half = k.bit_length()
    shift = 0
    while k % 2 == 0:
        half = (half + 1) // 2
        if k & bitmask(half) == 0:
            k >>= half
            shift += half
    return k, shift

def str_from_real(n):
    '''
    If this real represents 0, return '0'. Otherwise, return an approximate
    scientific notation representation of it.
    '''
    if n.coefficient == 0:
        return '0'
    
    # TODO minimize floating point errors in string representation
    
    # Calculate base 10 exponent and coefficient
    c, a = unshift(n.coefficient)
    v = (n.exponent + a) * LOG_10_2 # FIXME float errors likely occur here
    exponent = int(v)
    coefficient = int(c * 10 ** (v - exponent))
    
    # Build strings for each piece
    sign = '-' if coefficient < 0 else ''
    digits = str(abs(coefficient))
    head, tail = digits[0], digits[1:]
    
    # Correct exponent to match the decimal shift of coefficient
    exp = exponent + len(tail)
    
    # Strip trailing zeros
    tail = tail.rstrip('0')
    
    if len(tail) == 0:
        return '{}{}e{:+}'.format(sign, head, exp)
    else:
        return '{}{}.{}e{:+}'.format(sign, head, tail, exp)




##############
# Arithmetic #
##############

def neg(n):
    return Real(-n.coefficient, n.exponent, precision=n.precision)

# Called _abs to differentate with builtin abs
def _abs(n):
    return Real(abs(n.coefficient), n.exponent, precision=n.precision)

# Called _round to differentate with builtin round
def _round(n):
    if n.exponent >= 0:
        return Real(n.coefficient << n.exponent)
    
    x = n.coefficient >> (-n.exponent - 1)
    if x % 2 == 1:
        x += 1
    
    return Real(x >> 1)

def floor(n):
    if n.exponent >= 0:
        return Real(n.coefficient << n.exponent)
    
    if n.coefficient < 0:
        return -ceil(-n)
    
    return Real(n.coefficient >> -n.exponent)

def ceil(n):
    if n.exponent >= 0:
        return Real(n.coefficient << n.exponent)
    
    if n.coefficient < 0:
        return -floor(-n)
    
    mask = (1 << -n.exponent) - 1
    if (n.coefficient & mask) != 0:
        return Real((n.coefficient >> -n.exponent) + 1)
    else:
        return Real(n.coefficient >> -n.exponent)

def add(n1, n2):
    # Rename Reals based on the size of their exponents
    if n1.exponent > n2.exponent:
        n1, n2 = n2, n1
    
    # Calculate the new coefficient, exponent, and precision
    coefficient = n1.coefficient + (n2.coefficient << (n2.exponent - n1.exponent))
    exponent = n1.exponent
    precision = min(n1.precision, n2.precision)
    
    return Real(coefficient, exponent, precision=precision)

def sub(n1, n2):
    # Negate n2
    n2.coefficient = -n2.coefficient
    
    # Rename Reals based on the size of their exponents
    if n1.exponent > n2.exponent:
        n1, n2 = n2, n1
    
    # Calculate the new coefficient, exponent, and precision
    coefficient = n1.coefficient + (n2.coefficient << (n2.exponent - n1.exponent))
    exponent = n1.exponent
    precision = min(n1.precision, n2.precision)
    
    # Reset sign of n2
    n2.coefficient = -n2.coefficient
    
    return Real(coefficient, exponent, precision=precision)

def mul(n1, n2):
    # Calculate the new coefficient, exponent, and precision
    coefficient = n1.coefficient * n2.coefficient
    exponent = n1.exponent + n2.exponent
    precision = min(n1.precision, n2.precision)
    
    return Real(coefficient, exponent, precision=precision)

def div(n1, n2):
    k = 2 * max(n1.precision, n2.precision) + 1
    
    # Calculate the new coefficient, exponent, and precision
    coefficient = (n1.coefficient << k) // n2.coefficient
    exponent = n1.exponent - n2.exponent - k
    precision = min(n1.precision, n2.precision)
    
    return Real(coefficient, exponent, precision=precision)

# Called _pow to differentate with builtin pow
def _pow(n1, n2):
    raise NotImplementedError()

def exp(n):
    raise NotImplementedError()

def log(n):
    raise NotImplementedError()

def sqrt(n):
    raise NotImplementedError()
