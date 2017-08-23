from observable_primitives.observers.condition_observer_base import ConditionObserver


class IntegerConditionObserver(ConditionObserver):
    def __init__(self, name=None, observable=None,
                 divisible_by=None,
                 if_less_than=None, if_more_than=None,
                 at_specific_value=None
                 ):
        """
        Watches an observable integer for various conditions.
        Silently keeps its internal status and provides it if needed.

        :param ObservableInteger observable: Observable integers to watch.
        :param int | list[int] divisible_by:
        :param int if_less_than:
        :param int if_more_than:
        :param int | list[int] at_specific_value:
        """
        super().__init__(name=name, default=False, observables=observable)
        self.divisible_by = divisible_by if (isinstance(divisible_by, list) or divisible_by is None) \
            else [divisible_by]
        self.if_less_than = if_less_than
        self.if_more_than = if_more_than
        self.at_specific_value = at_specific_value if isinstance(at_specific_value, list) \
            else [at_specific_value]

        # Initialize
        self._initialize(observable=observable)

    def _initialize(self, observable):
        self._update_status(new_val=observable.val, method="ObserverInitialize", other=None, previous=None)

    def _update_status(self, *, new_val, method, other, previous):
        # Specific iteration
        if self.at_specific_value is not None:
            if new_val in self.at_specific_value:
                self._reason = f"Specifically chosen value {new_val}"
                self._status = True
                return

        # Select iteration at specified iteration interval
        if self.divisible_by is not None:
            for div_val in self.divisible_by:
                if (new_val % div_val) == 0:
                    self._reason = f"Value {new_val} divisible by {div_val}"
                    self._status = True
                    return

        # Check for lower limit
        if self.if_less_than is not None and new_val < self.if_less_than:
            self._reason = f"Value {new_val} < {self.if_less_than}"
            self._status = True
            return

        # Check for upper limit
        if self.if_more_than is not None and new_val > self.if_more_than:
            self._reason = f"Value {new_val} > {self.if_more_than}"
            self._status = True
            return

        # Don't select iteration
        self._reason = None
        self._status = False


class CounterConditionObserver(IntegerConditionObserver):
    def __init__(self, name=None, observable=None,
                 at_every=None, at_relative=None,
                 if_first_count=False, last_value=None,
                 if_less_than=None, if_more_than=None,
                 at_specific_value=None,
                 first_val=0):
        self.at_relative = at_relative if isinstance(at_relative, float) else 1. / float(at_relative)
        self.if_first_iteration = if_first_count
        self.last_value = last_value
        self.first_val = first_val
        super().__init__(name=name, observable=observable, divisible_by=at_every, if_less_than=if_less_than,
                         if_more_than=if_more_than, at_specific_value=at_specific_value)

    def _update_status(self, *, new_val, method, other, previous):
        # Standard integer conditions
        super()._update_status(new_val=new_val, method=method, other=other, previous=previous)

        # First iteration
        if self.if_first_iteration and new_val == self.first_val:
            self._reason = f"First count."
            self._status = True
            return

        # Last iteration
        if self.last_value is not None and new_val == self.last_value:
            self._reason = f"Last count."
            self._status = True
            return

        # Relative
        if self.last_value is not None and self.at_relative is not None:
            step = round(self.last_value * self.at_relative)
            if (new_val % step) == 0:
                self._reason = f"Iteration divisible by {step} " \
                               + f"(increase by {self.at_relative:%} of total iterations)"
                return True


if __name__ == "__main__":
    from observable_primitives import ObservableInteger

    obs_int = ObservableInteger(-2)
    int_condition = CounterConditionObserver(observable=obs_int,
                                             at_every=[3, 7],
                                             if_less_than=-1,
                                             if_more_than=9,
                                             at_specific_value=[2, 6],
                                             if_first_count=True,
                                             last_value=10,
                                             at_relative=.5)

    print(f"Counter {obs_int:3d}, condition {bool(int_condition)!r:5s}, reason {int_condition._reason}")
    for _ in range(12):
        obs_int += 1
        print(f"Counter {obs_int:3d}, condition {bool(int_condition)!r:5s}, reason {int_condition._reason}")
