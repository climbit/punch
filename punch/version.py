# -*- coding: utf-8 -*-

import collections

from punch.helpers import import_file
from punch import version_part as vpart


class Version():
    def __init__(self):
        self.keys = []
        self.parts = {}

    def add_part(self, part):
        self.keys.append(part.name)
        self.parts[part.name] = part

    def create_part(self, name, value, cls=vpart.IntegerVersionPart, *args, **kwds):
        self.keys.append(name)
        self.parts[name] = cls(name, value, *args, **kwds)

    def add_part_from_dict(self, dic):
        vp = vpart.VersionPart.from_dict(dic)
        self.keys.append(vp.name)
        self.parts[vp.name] = vp

    def get_part(self, name):
        return self.parts[name]

    def inc(self, name):
        self.parts[name].inc()
        idx = self.keys.index(name)
        for key in self.keys[idx + 1:]:
            self.parts[key].reset()

    def copy(self):
        new = Version()
        for key in self.keys:
            new.add_part(self.parts[key].copy())

        return new

    def as_dict(self):
        return dict((key, part.value) for key, part in self.parts.items())

    def to_file(self, version_filepath):
        with open(version_filepath, 'w') as f:
            for key in self.keys:
                f.write("{0} = {1}\n".format(key, self.parts[key].value))

    @classmethod
    def from_file(cls, version_filepath, version_description):
        version_module = import_file(version_filepath)
        version = Version()

        for version_part in version_description:
            if isinstance(version_part, collections.Mapping):
                version_part_name = version_part['name']
                version_part['value'] = cls._get_version_part(version_module, version_part, version_part_name)
                version.add_part_from_dict(version_part)
            else:
                version_part_name = version_part
                version_part_value = cls._get_version_part(version_module, version_part, version_part_name)
                version.create_part(version_part_name, version_part_value)

        return version

    @classmethod
    def _get_version_part(cls, version_module, version_part, version_part_name):
        try:
            return getattr(version_module, version_part_name)
        except AttributeError:
            raise ValueError("Given version file is invalid: missing '{}' variable".format(version_part_name))
