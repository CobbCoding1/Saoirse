# This file is:
# src/python/saoirse_base.py

import os, logging
from enum import Enum

logger = logging.getLogger("saoirse")
#class Logger():
#    class LogLevels(Enum):
#        LOG_LEVEL_INFO="info"
#        LOG_LEVEL_WARN="warn"
#        LOG_LEVEL_ERROR="error"
#
#    def log_msg(sender="Nobody", msg="This is a test message, please ignore it!", level=LogLevels.LOG_LEVEL_INFO, should_print=True):
#        formatted_msg = f"Log: Sender = {sender}: Level = {level}: Message =\n{msg}\n"
#        if should_print:
#            print(formatted_msg)
#        return formatted_msg


#class VarHolder():
#    def __init__(self):
#        pass


class Identifier():
    def __init__(self, path="", delimiter="/"):
        self.set_delimiter(delimiter)
        self.set_path(path)

    def set_path(self, new_path_in, update_self=True):
        new_path = new_path_in
        if isinstance(new_path_in, list):
            for i, part in enumerate(new_path):
                if isinstance(part, str):
                    if self.get_delimiter() in part:
                        fixed = part.split(self.get_delimiter())
                        new_path.pop(i)
                        fixed.reverse()
                        for fixed_part in fixed:
                            new_path.insert(i, fixed_part)
        elif isinstance(new_path_in, str):
            new_path = new_path_in.split(self.get_delimiter())

        if update_self:
            self.path = new_path
            return self
        return Identifier(new_path)

    def set_delimiter(self, new_delimiter_in, update_self=True):
        if isinstance(new_delimiter_in, str):
            new_delimiter = new_delimiter_in
        else:
            new_delimiter = "/"

        if update_self:
            self.delimiter = new_delimiter
            return self
        return Identifier(delimiter=new_delimiter)

    def get_path(self):
        return self.path

    def get_delimiter(self):
        return self.delimiter

    def get_path_str(self):
        return self.get_delimiter().join(self.get_path())

    def __str__(self):
        return self.get_path_str()

    def is_equal(self, other_in):
        return isinstance(other_in, Identifier) and other_in.get_path() == self.get_path()

    def append(self, other_path_in, update_self=True):
        new_path = self.path.copy()
        if isinstance(other_path_in, list):
            new_path.extend(other_path_in)
        elif isinstance(other_path_in, str):
            new_path.append(other_path_in)
        else:
            logger.warning(f"Failed to append invalid path {str(other_path_in)} to identifier {str(self)} as it is not of type list or str!")
        if update_self:
            self.set_path(new_path)
            return self
        return Identifier(new_path)

    def extend(self, other_in, update_self=True):
        if isinstance(other_in, Identifier):
                new_path = self.path.copy()
                new_path.extend(other_in.get_path())
                if update_self:
                    self.set_path(new_path)
                    return self
                return Identifier(new_path)

    def copy(self):
        return Identifier(self.get_path(), self.get_delimiter())

    def get_file_path(self):
        return os.path.join(*self.get_path())

    def get_id_from_str_list_or_id(ide):
        if isinstance(ide, str) or isinstance(ide, list):
            return Identifier(ide)
        elif isinstance(ide, Identifier):
            return ide
        return None


class IdentifierEnum(Enum):
    def get_base_ide(self):
        return Identifier()

    def get_value(self):
        return self.get_base_ide().extend(Identifier.get_id_from_str_list_or_id(self.value), False)


class IdentifierObjGetterPair():
    def __init__(self, obj_in=None, id_in=Identifier()):
        self.obj = obj_in
        self.set_id(id_in)

    def is_equal(self, other_in):
        return isinstance(other_in, IdentifierObjGetterPair) and self.get_id().is_equal(other_in.get_id()) and self.get_obj() == other_in.get_obj()

    def copy(self):
        return IdentifierObjGetterPair(self.get_obj(), self.get_id().copy())

    def set_id(self, id_in):
        self.ide = Identifier.get_id_from_str_list_or_id(id_in)

    def get_id(self):
        return self.ide

    def get_obj(self, *args, **kwargs):
        obj = self.obj(*args, **kwargs)
        if hasattr(obj, "set_id"):
            obj.set_id(self.get_id())
        return obj

    def __str__(self):
        return f"{str(self.get_id())} : {str(self.obj)}"


class BaseRegistry():
    def __init__(self):
        self.entries = {}

    def get_entries_dict(self):
        return self.entries

    def get_entries(self):
        return self.entries.values()

    def get_entry(self, id_in):
        ide = Identifier.get_id_from_str_list_or_id(id_in)

        if self.contains_id(ide):
            return self.entries[ide.get_path_str()]
        return None

    def get_entries_under_category(self, category_id):
        category_entries = {}
        category_key = category_id.get_path_str()
        for key, obj in self.get_entries_dict().items():
            if key.startswith(category_key):
                category_entries[key] = obj
        return category_entries

    def contains_id(self, id_in):
        ide = Identifier.get_id_from_str_list_or_id(id_in)
        return ide.get_path_str() in self.get_entries_dict().keys()

    def register_id_obj(self, obj_in, id_in):
        if isinstance(id_in, Identifier):
            self.register_id_obj_pair(IdentifierObjGetterPair(obj_in, id_in), id_in)

    def register_id_obj_pair(self, id_obj_pair, ide = None):
        if isinstance(id_obj_pair, IdentifierObjGetterPair):
            if ide is None:
                ide = id_obj_pair.get_id()
            if isinstance(ide, Identifier):
                id_str = ide.get_path_str()
                if id_str in self.get_entries_dict().keys():
                    logger.warning(msg=f"Failed to register {str(id_obj_pair)} as its id of {id_str} is alread registered!")
                else:
                    id_obj_pair.set_id(ide)
                    self.entries[id_str] = id_obj_pair
            else:
                logger.warning(msg=f"Failed to register {str(id_obj_pair)} as its id of {str(ide)} is not an Identifier!")
        else:
            logger.warning(msg=f"Failed to register {str(id_obj_pair)} as it is not an IdentifierObjectPair!")


class ThreeDimensionalPosition():
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

    def get_origin():
        return ThreeDimensionalPosition()

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def get_z(self):
        return self.z

    def get_distance_from_other(self, other):
        return ((self.get_x() + other.get_x())**2 + (self.get_y() + other.get_y())**2 + (self.get_z() + other.get_z())**2)**0.5

    def get_distance_two_1d_points(primary, secondary):
        return secondary - primary

    def get_distance_from_other_x(self, other):
        return ThreeDimensionalPosition.get_distance_two_1d_points(self.get_x(), other.get_x())

    def get_distance_from_other_y(self, other):
        return ThreeDimensionalPosition.get_distance_two_1d_points(self.get_y(), other.get_y())

    def get_distance_from_other_z(self, other):
        return ThreeDimensionalPosition.get_distance_two_1d_points(self.get_z(), other.get_z())

    class Direction(Enum):
        def of_index(i=1):
            if i < -6 or i > 6:
                i %= 6
            if i == 0:
                i = 6
            return getattr(ThreeDimensionalPosition.Direction, abs(i))

        def get_opposite(self):
            if self == ThreeDimensionalPosition.Direction.UP:
                return ThreeDimensionalPosition.Direction.DOWN
            elif self == ThreeDimensionalPosition.Direction.DOWN:
                return ThreeDimensionalPosition.Direction.UP
            elif self == ThreeDimensionalPosition.Direction.FRONT:
                return ThreeDimensionalPosition.Direction.BACK
            elif self == ThreeDimensionalPosition.Direction.BACK:
                return ThreeDimensionalPosition.Direction.FRONT
            elif self == ThreeDimensionalPosition.Direction.LEFT:
                return ThreeDimensionalPosition.Direction.RIGHT
            return ThreeDimensionalPosition.Direction.LEFT

        def get_relative(self, front, up):
            if front == up or front.get_opposite() == up:
                return None
            dist_front = ThreeDimensionalPosition.Direction.FRONT.value - self.value
            dist_up = ThreeDimensionalPosition.Direction.UP.value - self.value
            for d in ThreeDimensionalPosition.Direction:
                if front.value - d.value == dist_front and up.value - d.value == dist_up:
                    return d
            return None

        FRONT = 1
        LEFT = 2
        BACK = 3
        UP = 4
        RIGHT = 5
        DOWN = 6

    def offset(self, direction, distance):
        if direction == ThreeDimensionalPosition.Direction.UP:
            return ThreeDimensionalPosition(self.get_x(), self.get_y() + distance, self.get_z())

        if direction == ThreeDimensionalPosition.Direction.DOWN:
            return ThreeDimensionalPosition(self.get_x(), self.get_y() - distance, self.get_z())

        if direction == ThreeDimensionalPosition.Direction.FRONT:
            return ThreeDimensionalPosition(self.get_x() + distance, self.get_y(), self.get_z())

        if direction == ThreeDimensionalPosition.Direction.BACK:
            return ThreeDimensionalPosition(self.get_x() - distance, self.get_y(), self.get_z())

        if direction == ThreeDimensionalPosition.Direction.RIGHT:
            return ThreeDimensionalPosition(self.get_x(), self.get_y(), self.get_z() + distance)

        if direction == ThreeDimensionalPosition.Direction.LEFT:
            return ThreeDimensionalPosition(self.get_x(), self.get_y(), self.get_z() - distance)

        return self

    def get_nearest_direction_to_other_pos(self, other):
        dist_x = self.get_distance_from_other_x(other)
        dist_y = self.get_distance_from_other_y(other)
        dist_z = self.get_distance_from_other_z(other)

        dist_farthest = max(abs(dist_x), abs(dist_y), abs(dist_z))
        if dist_farthest == abs(dist_x):
            if dist_x < 0:
                return ThreeDimensionalPosition.Direction.LEFT
            return ThreeDimensionalPosition.Direction.RIGHT
        elif dist_farthest == abs(dist_y):
            if dist_y < 0:
                return ThreeDimensionalPosition.Direction.DOWN
            return ThreeDimensionalPosition.Direction.UP
        else:
            if dist_z < 0:
                return ThreeDimensionalPosition.Direction.BACK
            return ThreeDimensionalPosition.Direction.FRONT

    class Axies(Enum):
        X = "x"
        Y = "y"
        Z = "z"

    def to_dict(self):
        return {ThreeDimensionalPosition.Axies.X.value: self.get_x(), ThreeDimensionalPosition.Axies.Y.value: self.get_y(), ThreeDimensionalPosition.Axies.Z.value: self.get_z()}

    def to_str(self):
        return str(self.to_dict())

    def of_dict(pos_dict):
        return ThreeDimensionalPosition(pos_dict.get(ThreeDimensionalPosition.Axies.X, 0), pos_dict.get(ThreeDimensionalPosition.Axies.Y, 0), pos_dict.get(ThreeDimensionalPosition.Axies.Z, 0))

    def of_str(pos_str):
        return ThreeDimensionalPosition.of_dict(dict(pos_str))

    def __str__(self):
        return self.to_str()

    def __eq__(self, other):
        return self.get_x() == other.get_x() and self.get_y() == other.get_y() and self.get_z() == other.get_z()


class ActionIds(Enum):
    MAIN = "main"
    SECONDARY = "secondary"


class TickableObject():
    def tick(self):
        pass

    def get_ticks_per_second(self):
        return 64


class InteractableObject():
    def get_action_by_id(self, ide, actor):
        return None

    def get_main_action(self, actor):
        return self.get_action_by_id(ActionIds.MAIN, actor)

    def get_secondary_action(self, actor):
        return self.get_action_by_id(ActionIds.SECONDARY, actor)


class MainGameObject(TickableObject, InteractableObject):
    persist_data_key = "persist_data"
    def __init__(self, ide, server):
        self.persist_data = {}
        self.ide = ide
        self.server = server
        self.on_created()

    def set_removed(self, removed=True):
        self.removed = removed
        return self

    def on_created(self):
        self.set_removed(False)
        return self

    def on_removed(self):
        return self.set_removed(True)

    def get_server(self):
        return self.server

    def get_id(self):
        return self.ide

    def set_persist_data(self, data):
        self.persist_data = data
        return self

    def get_persist_data(self):
        return self.persist_data

    def set_data(self, data):
        if self.persist_data_key in data.keys():
            self.set_persist_data(data.get(self.persist_data_key))
        return self

    def get_data(self):
        return {self.persist_data_key: self.get_persist_data()}


class SpaceGameObject(MainGameObject):
    def __init__(self, ide, server, pos=ThreeDimensionalPosition.get_origin(), three_dimensional_space=None):
        super().__init__(ide, server)

        self.set_pos(pos)
        self.set_three_dimensional_space(three_dimensional_space)

    def set_pos(self, pos):
        self.pos = pos
        return self

    def get_pos(self):
        return self.pos

    def set_three_dimensional_space(self, three_dimensional_space):
        self.three_dimensional_space = three_dimensional_space
        return self

    def get_three_dimensional_space(self):
        return self.three_dimensional_space

    def has_gravity(self):
        return True

    def get_mass(self):
        return 1


class Item(SpaceGameObject):
    def __init__(self, ide, server, pos=ThreeDimensionalPosition.get_origin(), three_dimensional_space=None):
        super().__init__(ide, server, pos, three_dimensional_space)


class Tile(SpaceGameObject):
    def __init__(self, ide, server, pos=ThreeDimensionalPosition.get_origin(), three_dimensional_space=None):
        super().__init__(ide, server, pos, three_dimensional_space)


class Fluid(SpaceGameObject):
    def __init__(self, ide, server, pos=ThreeDimensionalPosition.get_origin(), three_dimensional_space=None):
        super().__init__(ide, server, pos, three_dimensional_space)


class Entity(SpaceGameObject):
    def __init__(self, ide, server, pos=ThreeDimensionalPosition.get_origin(), three_dimensional_space=None):
        super().__init__(ide, server, pos, three_dimensional_space)

    def get_agenda(self):
        return []


class ThreeDimensionalSpace(SpaceGameObject):
    def __init__(self, ide, server, three_dimensional_space=None):
        super().__init__(ide, server, three_dimensional_space)

        self.space_game_objects = {}

    def get_server(self):
        return self.server

    def get_space_game_objects_dict(self):
        return self.space_game_objects

    def get_objects(self):
        return self.get_space_game_objects_dict().values()

    def get_g_constant(self):
        return 6.67 * (10**-11)

    def get_gravity_speed(self, m1, m2, distance):
        return ((self.get_g_constant() * m1 * m2) / (distance**2)) / self.get_server().get_ticks_per_second()

    def add_space_game_object_at_pos(self, pos, space_game_object):
        space_game_object.set_pos(pos)
        space_game_object.set_three_dimensional_space(self)
        pos_str = pos.to_str()
        existing_objects = self.space_game_objects.get(pos_str, [])
        existing_objects.append(space_game_object)
        self.space_game_objects[pos_str] = existing_objects
        return self

    def remove_space_game_object_at_pos(self, pos, check_space_game_object=None):
        for space_game_object in self.get_space_game_objects_at_pos(pos, check_space_game_object):
            self.space_game_objects.pop(space_game_object)
        return self

    def replace_space_game_object_at_pos(self, pos, old_space_game_object, new_space_game_object):
        self.remove_space_game_object_at_pos(pos, old_space_game_object)
        self.add_space_game_object_at_pos(pos, new_space_game_object)
        return self

    def get_space_game_objects_at_pos(self, pos, check_space_game_object=None):
        if check_space_game_object is None:
            return self.get_space_game_objects_dict().get(pos.to_str(), [])
        space_game_objects = []
        for space_game_object in self.get_objects():
            if space_game_object.get_pos() == pos and (check_space_game_object == space_game_object or check_space_game_object is None):
                space_game_objects.append(space_game_object)
        return space_game_objects

    def get_nearest_obj_to_pos(self, pos, exclusions=[]):
        if len(self.get_objects()) > 0:
            nearest = self.get_objects()[0]
            if len(self.get_objects()) > 1:
                for obj in self.get_objects()[1:]:
                    if obj not in exclusions and obj.get_pos().get_distance_from_other(pos) < nearest.get_pos().get_distance_from_other(pos):
                        nearest = obj
            if nearest not in exclusions:
                return nearest
        return None

    def tick_space_game_object_gravity(self, space_game_object):
        if len(self.get_objects()) > 1 and space_game_object.has_gravity():
            nearest = self.get_nearest_obj_to_pos(space_game_object.get_pos(), [space_game_object])
            space_game_object.set_pos(space_game_object.get_pos().offset(space_game_object.get_pos().get_nearest_direction_to_other_pos(nearest.get_pos()), self.get_gravity_speed(space_game_object.get_mass(), nearest.get_mass(), nearest.get_pos().get_distance_from_other(space_game_object.get_pos()))))
        return self

    def tick(self):
        for space_game_object_set in self.get_objects():
            for space_game_object in space_game_object_set:
                space_game_object.tick()
                self.tick_space_game_object_gravity(space_game_object)
        return self

    class SaveDataKeys(Enum):
        IDE = "ide"
        POS = "pos"
        DATA = "data"
        OBJECTS = "objects"

    def set_data(self, data):
        if ThreeDimensionalSpace.SaveDataKeys.OBJECTS.value in data.keys():
            objects_data = data.get(ThreeDimensionalSpace.SaveDataKeys.OBJECTS.value)
            for space_game_object_set_data in objects_data.values():
                for space_game_object_data in space_game_object_set_data:
                    if ThreeDimensionalSpace.SaveDataKeys.IDE.value in space_game_object_data.keys() and ThreeDimensionalSpace.SaveDataKeys.POS.value in space_game_object_data.keys():
                        ide = Identifier(space_game_object_data[ThreeDimensionalSpace.SaveDataKeys.IDE.value])
                        space_game_object_pair = self.get_server().get_registry().get_entry(ide)
                        if space_game_object_pair is not None:
                            space_game_object = space_game_object_pair.get_obj()
                            if space_game_object is not None:
                                pos = ThreeDimensionalPosition.of_dict(space_game_object_data[ThreeDimensionalSpace.SaveDataKeys.POS.value])
                                space_game_object.set_pos(pos)
                                space_game_object.set_data(space_game_object_data.get(ThreeDimensionalSpace.SaveDataKeys.DATA.value))
                                self.add_space_game_object_at_pos(pos, space_game_object)

    def get_data(self):
        data = super().get_data()
        objects_data = {}
        for i, space_game_object_set in self.get_space_game_objects_dict().items():
            space_game_object_set_data = []
            for i1, space_game_object in enumerate(space_game_object_set):
                if space_game_object is not None:
                    ide_path = space_game_object.get_id().get_path()
                    pos_dict = space_game_object.get_pos().to_dict()
                    saved_data = space_game_object.get_data()
                    space_game_object_data = {}
                    space_game_object_data[ThreeDimensionalSpace.SaveDataKeys.IDE.value] = ide_path
                    space_game_object_data[ThreeDimensionalSpace.SaveDataKeys.POS.value] = pos_dict
                    space_game_object_data[ThreeDimensionalSpace.SaveDataKeys.DATA.value] = saved_data
                    space_game_object_set_data.append(space_game_object_data)
            objects_data[str(i)] = space_game_object_set_data
        data[ThreeDimensionalSpace.SaveDataKeys.OBJECTS.value] = objects_data
        return data


class BaseServer(MainGameObject):
    spaces_key = "spaces"

    def __init__(self, ide, registry):
        super().__init__(ide, self)

        self.registry = registry
        self.registry.server = self
        self.spaces = {}

    def get_registry(self):
        return self.registry

    def get_spaces(self):
        return self.spaces

    def add_three_dimensional_space(self, three_dimensional_space):
        self.spaces[three_dimensional_space.get_id().get_path_str()] = three_dimensional_space
        return self

    def get_three_dimensional_space(self, ide):
        return self.spaces.get(ide.get_path_str(), None)

    def tick(self):
        for space in self.get_spaces().values():
            space.tick()
        return self

    def get_data(self):
        spaces_data = {}
        for space in self.get_spaces().values():
            spaces_data[space.get_id().get_path_str()] = space.get_data()
        return {self.spaces_key: spaces_data}

    def set_data(self, data):
        if self.spaces_key in data.keys():
            spaces_data = data.get(self.spaces_key)
            for space_key in spaces_data.keys():
                space_ide = Identifier(space_key)
                if space_key not in self.get_spaces().keys():
                    self.add_three_dimensional_space(ThreeDimensionalSpace(space_ide, self))
                self.get_three_dimensional_space(space_ide).set_data(spaces_data.get(space_key))
        return self
