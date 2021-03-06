from typing import Callable, SupportsInt, SupportsFloat, SupportsRound, SupportsComplex, SupportsAbs, SupportsBytes

from observable_primitives.observables.numeric_base import ObservableNumeric


class ObservableInteger(ObservableNumeric, SupportsInt, SupportsFloat, SupportsRound, SupportsComplex, SupportsAbs,
                        SupportsBytes):
    def __init__(self, val=0, final_value=None, incorrect_type_handler="round"):
        """
        An integer which is observable.
        All methods and operations that work on integer should work on this class and have identical behavior.
        The only exception are the augmented arithmetic assignments, these all call the observers:
            +=, -=, *=, /=, //=, %=, **=, <<=, >>=, &=, ^=, |=
        :param val: Anything that can be cast to an int.
        :param str | Callable incorrect_type_handler:
        """
        super().__init__(val=int(val))
        self._incorrect_type_policy = incorrect_type_handler
        self.final_value = final_value

    # Unary

    def __index__(self):  # For indexing in list etc.
        return self._val

    def __invert__(self):
        return ~self._val

    # Arithmetics

    def __pow__(self, power, modulo=None):
        return pow(self._val, power, modulo)

    def __rpow__(self, power, modulo=None):
        return pow(power, self._val, modulo)

    # Arithmetics: Divisions and Modulo

    def __floordiv__(self, other):
        return self._val // other

    def __rfloordiv__(self, other):
        return other // self._val

    def __mod__(self, other):
        return self._val % other

    def __rmod__(self, other):
        return other % self._val

    def __divmod__(self, other):
        return divmod(self._val, other)

    def __rdivmod__(self, other):
        return divmod(other, self._val)

    # Arithmetics: Binary

    def __lshift__(self, other):
        return self._val << other

    def __rlshift__(self, other):
        return other << self._val

    def __rshift__(self, other):
        return self._val >> other

    def __rrshift__(self, other):
        return other >> self._val

    # Boolean

    def __and__(self, other):
        return self._val & other

    def __rand__(self, other):
        return other & self._val

    def __or__(self, other):
        return self._val | other

    def __ror__(self, other):
        return other | self._val

    def __xor__(self, other):
        return self._val ^ other

    def __rxor__(self, other):
        return other ^ self._val

    # Representation

    def __bytes__(self) -> bytes:
        return bytes(self._val)

    # Conversions

    def __complex__(self) -> complex:
        return complex(self._val)

    def __int__(self) -> int:
        return int(self._val)

    def __float__(self) -> float:
        return float(self._val)

    def __round__(self, n=None) -> round:
        return round(self._val, n)

    # Augmented arithmetics

    def __ilshift__(self, other):
        previous = self._val
        self._val <<= other
        return self._ireturn(method="__ilshift__", other=other, previous=previous)

    def __irshift__(self, other):
        previous = self._val
        self._val >>= other
        return self._ireturn(method="__irshift__", other=other, previous=previous)

    def __iand__(self, other):
        previous = self._val
        self._val &= other
        return self._ireturn(method="__iand__", other=other, previous=previous)

    def __ixor__(self, other):
        previous = self._val
        self._val ^= other
        return self._ireturn(method="__ixor__", other=other, previous=previous)

    def __ior__(self, other):
        previous = self._val
        self._val |= other
        return self._ireturn(method="__ior__", other=other, previous=previous)

    def __imod__(self, other):
        previous = self._val
        self._val %= other
        return self._ireturn(method="__imod__", other=other, previous=previous)

    def __ipow__(self, other, modulo=None):
        previous = self._val
        self._val = pow(self._val, other, modulo)
        return self._ireturn(method="__ipow__", other=other, modulo=modulo, previous=previous)

    # Observation method

    def _ireturn(self, *, method, other, **kwargs):
        # Check if incorrect type
        if not isinstance(self._val, int):
            name = type(self).__name__

            # String keyword policies
            if isinstance(self._incorrect_type_policy, str):
                if self._incorrect_type_policy.lower() == "round":
                    self._val = round(self._val)
                elif self._incorrect_type_policy.lower() == "int":
                    self._val = int(self._val)
                else:
                    raise ValueError(f"Value of {name} is not an integer. Instead it is {type(self._val)}.")

            # Check for callable policy
            elif isinstance(self._incorrect_type_policy, Callable):
                self._val = self._incorrect_type_policy(self._val)

            # Raise error
            else:
                raise ValueError(f"Value of {name} is not an integer. Instead it is {type(self._val)}.")

        # Notify observers
        self.update_observers(method=method, other=other, new_val=self._val, **kwargs)

        return self

    # Class specifics
    @property
    def imag(self):
        return 0

    @property
    def real(self):
        return self._val

    def conjugate(self):
        return complex(self._val, 0)

    def bit_length(self):
        return self._val.bit_length()

    def from_bytes(self, bytes, byteorder, *, signed):
        return self._val.from_bytes(bytes=bytes, byteorder=byteorder, signed=signed)

    def to_bytes(self, length, byteorder, *, signed):
        return self._val.to_bytes(length=length, byteorder=byteorder, signed=signed)

    # Added specials

    def range(self, *args):
        if len(args) == 1:
            self.final_value = args[0] - 1
        else:
            self.final_value = args[1] - 1
        for i in range(*args):
            yield self.set(i, method="range")
