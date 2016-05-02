# -*- coding: utf-8 -*-

import sys

class VersionPart(object):
    @classmethod
    def from_dict(cls, dic):
        try:
            part_type = dic.pop('type')
        except KeyError:
            part_type = 'integer'

        class_name = part_type.title().replace("_", "") + 'VersionPart'
        part_class = getattr(sys.modules[__name__], class_name)

        return part_class(**dic)


class IntegerVersionPart(VersionPart):
    def __init__(self, name, value):
        self.name = name

        if value is None:
            self.value = 0
        else:
            self.value = int(value)

    def inc(self):
        self.value = self.value + 1

    def reset(self):
        self.value = 0


class ValueListVersionPart(VersionPart):
    def __init__(self, name, value, allowed_values):
        self.name = name

        if value is None:
            self.value = allowed_values[0]
        else:
            if value not in allowed_values:
                raise ValueError("The given value {} is not allowed, the list of possible values is {}", value,
                                 allowed_values)
            self.value = value

        self.values = allowed_values

    def inc(self):
        idx = self.values.index(self.value)
        self.value = self.values[(idx + 1) % len(self.values)]

    def reset(self):
        self.value = self.values[0]
