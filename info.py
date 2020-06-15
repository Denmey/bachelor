from gym_duckietown.simulator import NotInLane
from math import pi
import numpy as np

class Info:
    #TODO comments
    """Base class for objects"""
    def __init__(self, env, prefix = ""):
        raise NotImplementedError("Class is not implemented")

    def __call__(self, env = None):
        raise NotImplementedError("Method is not implemented")

    def get_str(self):
        raise NotImplementedError("Method is not implemented")

class BotPos(Info):
    #TODO
    def __init__(self, env, prefix = ""):
        self.env = env
        self.prefix = prefix

    def __call__(self, env = None):
        if env == None:
            ret = self.env.cur_pos
        else:
            ret = env.cur_pos
        return np.array(ret)

    def get_str(self):
        string = self.prefix + str([round(val, 2) for val in self.env.cur_pos])
        return string

class BotSpeed(Info):
    #TODO
    def __init__(self, env, prefix = ""):
        self.env = env
        self.prefix = prefix

    def __call__(self, env = None):
        if env == None:
            ret = self.env.speed
        else:
            ret = env.speed
        return ret

    def get_str(self):
        string = self.prefix + str(round(self(), 2))
        return string

class Step(Info):
        #TODO
        def __init__(self, env, prefix = ""):
            self.env = env
            self.prefix = prefix

        def __call__(self, env = None):
            if env == None:
                ret = self.env.step_count
            else:
                ret = env.step_count
            return ret

        def get_str(self):
            string = self.prefix + str([round(val, 2) for val in self.env.cur_pos])
            return string


class BotAngle(Info):
    """Class used to get info on bot's angle.

    Args:
        env: Environment to get info from.
        prefix (string): Prefix concatenated to stringified value when get_str called.
    """
    def __init__(self, env, prefix = ""):
        self.env = env
        self.prefix = prefix

    def __call__(self, env = None):
        """Returns angle of a bot in radians.

        Args:
            env: environment to get bot's angle. If not passed, environment passed to constructor is used.
        """
        if env == None:
            ret = self.env.cur_angle
        else:
            ret = env.cur_angle
        return ret

    def get_str(self):
        """Returns string of angle of a bot in environment in degrees.

        Note: Returns concatenation with prefix that was passed to constructor.
        """
        angle_rads = self()
        angle = int(angle_rads * 180 / pi)
        return self.prefix + str(angle)

class BotDirection(Info):
    #TODO
    def __init__(self, env, prefix = ""):
        self.env = env
        self.prefix = prefix

    def __call__(self, env = None):
        if env == None:
            ret = self.env.get_dir_vec()
        else:
            ret = env.get_dir_vec()
        return np.array(ret)

    def get_str(self):
        return self.prefix + str([round(val, 2) for val in self()])

class WorldUp(Info):
    #TODO
    def __init__(self, env = None, prefix = ""):
        self.env = env
        self.prefix = prefix

    def __call__(self, env = None):
        return np.array([0, 1, 0])

    def get_str(self):
        return self.prefix + str(self())

class Distance(Info):
    #TODO
    def __init__(self, env, prefix = ""):
        self.env = env
        self.prefix = prefix
        raise NotImplementedError("Class is not implemented")

    def __call__(self, env = None):
        pass

    def get_str(self):
        pass

class IsInLane(Info):
    #TODO
    def __init__(self, env, prefix = ""):
        self.env = env
        self.prefix = prefix

    def __call__(self, env = None):
        if (env == None):
            t_env = self.env
        else:
            t_env = env
        try:
            t_env.get_lane_pos2(t_env.cur_pos, t_env.cur_angle)
            return True
        except NotInLane:
            return False

    def get_str(self):
        return self.prefix + str(self())

class TimeOutOfLane(Info):
    #TODO
    def __init__(self, env, prefix = ""):
        self.env = env
        self.prefix = prefix
        raise NotImplementedError("Class is not implemented")

    def __call__(self, env = None):
        pass

    def get_str(self):
        pass

class TimeInactive(Info):
    #TODO
    def __init__(self, env, prefix = ""):
        self.env = env
        self.prefix = prefix
        raise NotImplementedError("Class is not implemented")

    def __call__(self, env = None):
        pass

    def get_str(self):
        pass
