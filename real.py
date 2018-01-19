import math

# TODO remove and replace with Real
LOG_10_2 = math.log10(2)

class InvalidOperationError(Exception):
    def __init__(self, msg):
        self.msg = msg
    
    def __repr__(self):
        return 'InvalidOperationError({!r})'.format(self.msg)
    
    def __str__(self):
        return self.msg

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
        '''
        Sets the precision of this real and normalizes it to the new precision
        '''
        self.precision = int(precision)
        self.normalize()
    
    def normalize(self):
        '''
        'Normalizes' this real by right shifting the coefficient until it is no
        larger (in bits) than the specified precision. Adds the amount of the
        shift to the exponent so that the approximate value does not change.
        This operation will sometimes drop bits (changing the exact value)
        '''
        bit_diff = self.coefficient.bit_length() - self.precision
        if bit_diff > 0:
            self.coefficient >>= bit_diff
            self.exponent += bit_diff
    
    def next(self):
        '''
        Returns the 'next' real: the smallest of all real numbers larger than
        this one with the same precision.
        '''
        amount = self.precision - self.coefficient.bit_length()
        coef = (self.coefficient << amount) + 1
        return Real(coef, self.exponent, precision=self.precision)
    
    def prev(self):
        '''
        Returns the 'previous' real: the largest of all real numbers smaller
        than this one with the same precision.
        '''
        bits = self.coefficient.bit_length()
        amount = self.precision - bits
        coef = (self.coefficient << amount) - 1
        if self.coefficient & bitmask(bits) != 0:
            return Real(coef, self.exponent, precision=self.precision)
        else:
            return Real((coef <<) + 1, self.exponent, precision=self.precision)
    
    def is_int(self):
        '''
        Returns true if this real represents an integer
        '''
        # TODO
    
    
    
    # Comparison Operators
    
    def __eq__(self, other):
        if isinstance(other, Real):
            return compare(self, other) == 0
        else:
            raise NotImplementedError()
    
    def __ne__(self, other):
        if isinstance(other, Real):
            return compare(self, other) != 0
        else:
            raise NotImplementedError()
    
    def __gt__(self, other):
        if isinstance(other, Real):
            return compare(self, other) > 0
        else:
            raise NotImplementedError()
    
    def __ge__(self, other):
        if isinstance(other, Real):
            return compare(self, other) >= 0
        else:
            raise NotImplementedError()
    
    def __lt__(self, other):
        if isinstance(other, Real):
            return compare(self, other) < 0
        else:
            raise NotImplementedError()
    
    def __le__(self, other):
        if isinstance(other, Real):
            return compare(self, other) <= 0
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



########################
# Conversion Functions #
########################

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
    # TODO

def str_from_real(x):
    '''
    If this real represents 0, return '0'. Otherwise, return an approximate
    scientific notation representation of it.
    '''
    if x.coefficient == 0:
        return '0'
    
    # TODO minimize floating point errors in string representation
    
    # Calculate base 10 exponent and coefficient
    c, a = unshift(x.coefficient)
    v = (x.exponent + a) * LOG_10_2 # FIXME float errors likely occur here
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

def compare(x, y):
    '''
    Compares two reals x and y and returns 1 if x is greater than y, 0 if x is
    equal to y, and -1 if x is less than y.
    '''
    
    # Negate y
    y.coefficient = -y.coefficient
    
    # Rename reals based on the size of their exponents
    if x.exponent > y.exponent:
        x, y = y, x
    
    # Calculate the new coefficient
    c = x.coefficient + (y.coefficient << (y.exponent - x.exponent))
    
    #
    if c > 0:
        return 1
    elif c < 0:
        return -1
    else:
        return 0

def neg(x):
    return Real(-x.coefficient, x.exponent, precision=x.precision)

# Called _abs to differentate with builtin abs
def _abs(x):
    return Real(abs(x.coefficient), x.exponent, precision=x.precision)

def round_zero(x):
    '''
    Rounds a real toward zero
    '''
    # TODO

def round_inf(x):
    '''
    Rounds a real toward infinity (away from zero)
    '''
    # TODO

# Called _round to differentate with builtin round
def _round(x):
    if x.exponent >= 0:
        return Real(x.coefficient << x.exponent)
    
    exp = -x.exponent
    x = x.coefficient >> (exp - 1)
    if x % 2 == 1:
        x += 1
    
    return Real(x >> 1)

def floor(x):
    if x.exponent >= 0:
        return Real(x.coefficient << x.exponent)
    
    if x.coefficient < 0:
        return -ceil(-x)
    
    exp = -x.exponent
    return Real(x.coefficient >> exp)

def ceil(x):
    if x.exponent >= 0:
        return Real(x.coefficient << x.exponent)
    
    if x.coefficient < 0:
        return -floor(-x)
    
    exp = -x.exponent
    if (x.coefficient & bitmask(exp)) != 0:
        return Real((x.coefficient >> exp) + 1)
    else:
        return Real(x.coefficient >> exp)

def add(x, y):
    # Rename reals based on the size of their exponents
    if x.exponent > y.exponent:
        x, y = y, x
    
    # Calculate the new coefficient, exponent, and precision
    coefficient = x.coefficient + (y.coefficient << (y.exponent - x.exponent))
    exponent = x.exponent
    precision = min(x.precision, y.precision)
    
    return Real(coefficient, exponent, precision=precision)

def sub(x, y):
    # Negate y
    y.coefficient = -y.coefficient
    
    res = add(x, y)
    
    # Reset sign of y
    y.coefficient = -y.coefficient
    
    return res

def mul(x, y):
    # Calculate the new coefficient, exponent, and precision
    coefficient = x.coefficient * y.coefficient
    exponent = x.exponent + y.exponent
    precision = min(x.precision, y.precision)
    
    return Real(coefficient, exponent, precision=precision)

def div(x, y):
    if y.coefficient == 0:
        raise InvalidOperationError('Cannot divide a Real by 0')
    
    k = 2 * max(x.precision, y.precision) + 1
    
    # Calculate the new coefficient, exponent, and precision
    coefficient = (x.coefficient << k) // y.coefficient
    exponent = x.exponent - y.exponent - k
    precision = min(x.precision, y.precision)
    
    return Real(coefficient, exponent, precision=precision)

# Called _pow to differentate with builtin pow
def _pow(x, y):
    # TODO
    if y.coefficient == 0:
        return Real(1)
        
    elif x.coefficient == 0:
        return x
        
    elif y.isint():
        pass
        
    elif x > 0:
        return exp(y * log(x))
        
    else:
        raise InvalidOperationError('Cannot evalute an exponential with a negative base')

def exp(x):
    raise NotImplementedError()

def log(x):
    # ln(x)
    #       = ln(c * 2^x)
    #       = ln(c / 2^p * 2^p * 2^x)
    #       = ln(c / 2^p) + ln(2^(p + x))
    #       = ln(c / 2^p) + (p + x) * ln(2)
    
    # ln(1 + x)
    #       = x + x^2/2 + x^3/3 + x^4/4 + x^5/5 ...
    
    # ln(2) = 1/(1 * 2) + 1/(2 * 4) + 1/(3 * 8) + .... + 1/(k * 2^k) + ...
    # ln(10) =
    
    raise NotImplementedError()

def sqrt(x):
    # babylonian method
    raise NotImplementedError()

def sin(x):
    raise NotImplementedError()
    xsqr = x * x
    num = x
    den = Real(1, precision=x.precision)
    i = 0
    while True: # TODO
        i += 2
        num *= xsqr
        den *= Real(i * (i + 1))
        x += num / den
    return x

def cos(x):
    raise NotImplementedError()

def root(x, n):
    raise NotImplementedError()



#########################
# Real-Valued Constants #
#########################

###
### Use iterative methods for
### computing constants to avoid
### accumulating error over time
###

class Ln2:
    def get(precision):
        pass

class Ln10:
    def get(precision):
        pass

class E:
    def get(precision):
        pass

class Pi:
    def get(precision):
        pass
