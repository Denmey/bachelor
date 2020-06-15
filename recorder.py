import cv2
import numpy as np
import os
from pyglet import gl
from ctypes import POINTER
from gym_duckietown.simulator import get_dir_vec, CAMERA_FORWARD_DIST

from . import drawable
from .framebuffer import Framebuffer
from .camera import CameraSettings
class RecorderSubFrame:
    #TODO
    def __init__(self, camera_settings,
        drawers = [drawable.Tiles(), drawable.Objects(), drawable.Bot()],
        info_drawers = [],
        clear_color = [0.45, 0.82, 1]
    ):
        self.drawers = drawers
        self.info_drawers = info_drawers
        self.camera_settings = camera_settings
        self.width  = camera_settings.width
        self.height = camera_settings.height
        self.clear_color = clear_color

    def draw(self, env):
        # Draw environment objects
        self.camera_settings.use(env)
        gl.glClearColor(*self.clear_color, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        for drawer in self.drawers:
            drawer.draw(env)

        # Draw info
        gl.glDisable(gl.GL_DEPTH_TEST)
        if len(self.info_drawers) > 0:
            _draw_info(env, self.info_drawers, self.camera_settings.width,
                self.camera_settings.height)
        gl.glEnable(gl.GL_DEPTH_TEST)

class RecorderBotViewSubFrame:
    def __init__(self, width, height, info_drawers = []):
        self.width = width
        self.height = height
        self.drawers = [drawable.Tiles(), drawable.Objects()]
        self.info_drawers = info_drawers
        self.warned = False

    def draw(self, env):
        if (env.camera_width != self.width or env.camera_height != self.height):
            if not self.warned:
                self.warned = True
                print("Warning: BotViewSubFrame dimensions ({}, {}) aren't equal to environment's camera dimensions ({}, {}). Result will be distorted."
                    .format(self.width, self.height, env.camera_width, env.camera_height))

        gl.glEnable(gl.GL_MULTISAMPLE)
        gl.glClearColor(*env.horizon_color, 1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.gluPerspective(
                env.cam_fov_y,
                env.camera_width / float(env.camera_height),
                0.04,
                100.0
        )
        pos = env.cur_pos
        angle = env.cur_angle
        if env.domain_rand:
            pos = pos + env.randomization_settings['camera_noise']

        pos = pos + env.cam_offset
        pos[1] += env.cam_height
        dir = get_dir_vec(angle)
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        gl.glRotatef(env.cam_angle[0], 1, 0, 0)
        gl.glRotatef(env.cam_angle[1], 0, 1, 0)
        gl.glRotatef(env.cam_angle[2], 0, 0, 1)
        gl.glTranslatef(0, 0, env._perturb(CAMERA_FORWARD_DIST))
        gl.gluLookAt(
                # Eye position
                *pos,
                # Target
                *(pos+dir),
                # Up vector
                0, 1.0, 0.0
        )

        # Draw the ground quad
        gl.glDisable(gl.GL_TEXTURE_2D)
        gl.glColor3f(*env.ground_color)
        gl.glPushMatrix()
        gl.glScalef(50, 1, 50)
        env.ground_vlist.draw(gl.GL_QUADS)
        gl.glPopMatrix()

        # Draw the ground/noise triangles
        env.tri_vlist.draw(gl.GL_TRIANGLES)

        # Draw remaining objects
        for drawer in self.drawers:
            drawer.draw(env)

        # Draw infos if neccessary
        gl.glDisable(gl.GL_DEPTH_TEST) # Otherwise wouldn't be drawn
        if len(self.info_drawers) > 0:
            _draw_info(env, self.info_drawers, self.width, self.height)
        gl.glEnable(gl.GL_DEPTH_TEST)

class RecorderInfoSubFrame(RecorderSubFrame):
    def __init__(self, width, height, drawers):
        settings = CameraSettings(width, height,
            None,
            None,
            None,
            projection = 'orthogonal'
        )
        super(RecorderInfoSubFrame, self).__init__(
            settings,
            drawers = drawers,
            clear_color = [0] * 3
        )

class Recorder:
    """Records experiment in videofile.

    Args:
        filename: Path of a videofile that will be written.
        shape: Rows and cols number of subframes.
        env: Environment object of simulation.
    """
    def __init__(self, file, shape, env):
        # TODO: Don't delete already existing files
        # TODO: Use crossplatform paths?
        self.context  = env.shadow_window
        self.context.switch_to()
        self.filepath = os.path.dirname(file)
        self.filename = os.path.basename(file)
        # print(self.filepath)
        # print(self.filename)
        self.shape  = shape
        self.ready  = False #
        self.fb = self.writer = None
        self.subframes  = [[None for x in range(self.shape[1])] for y in range(self.shape[0])]
        self.env    = env

    def set_subframe(self, row, column, subframe):
        """Sets subframe at specified row and column.
        
        Args:
            row: Row position.
            column: Column position.
            subframe: Subframe object to be set.

        Note:
            (0, 0) is top-bottom corner of frame.
        """
        # TODO: asserts or exceptions?
        # TODO: Print message along with an error
        assert not self.writer # Can't change subframes when recording
        assert row    <  self.shape[0]
        assert row    >= 0
        assert column <  self.shape[1]
        assert column >= 0

        self.subframes[row][column] = subframe

    def _init(self):
        """Figure out video's width and height required to fit all the subviews"""
        self.min_widths  = [-np.Inf]*self.shape[1] # For each column
        self.min_heights = [-np.Inf]*self.shape[0] # For each row

        for i, frameRow in enumerate(self.subframes):
            h = 0
            for j, subframe in enumerate(frameRow):
                h = max(h, subframe.height if subframe else 0)
            self.min_heights[i] = h

        for i, frameCol in enumerate(list(zip(*self.subframes))):
            w = 0
            for subframe in frameCol:
                w = max(w, subframe.width if subframe else 0)
            self.min_widths[i] = w

        self.width  = sum(self.min_widths)
        self.height = sum(self.min_heights)

        self._init_writer()

        if not self.fb:
            self.fb = Framebuffer(self.width, self.height)

        self.ready = True

    def _init_writer(self):
        if not os.path.exists(self.filepath):
            os.makedirs(self.filepath)
        # TODO: FPS is const and can be too fast or slow
        self.writer = cv2.VideoWriter(
                                      os.path.join(self.filepath, self.filename),
                                      cv2.VideoWriter_fourcc(*'mp4v'),
                                      15,
                                      (self.width, self.height)
                                     )

    def render(self):
        # TODO: docstring
        """Render video frame from all connected subframes.
        """
        self.context.switch_to()
        # Switch context before creating Framebuffer in _init

        if not self.ready:
            self._init()

        self.fb.use()

        # Render each subframe
        gl.glEnable(gl.GL_SCISSOR_TEST) # For restricting glClear to specific rectangle
        yorigin = xorigin = 0 # Starting corner of renderable subframe
        for row, frameRow in enumerate(self.subframes):
            xorigin = 0
            for col, subframe in enumerate(frameRow):
                if subframe is None:
                    continue
                gl.glViewport(xorigin, yorigin, subframe.width, subframe.height)
                gl.glScissor(xorigin, yorigin, subframe.width, subframe.height)
                subframe.draw(self.env) if subframe else None
                xorigin += self.min_widths[col]
            yorigin += self.min_heights[row]

        img = np.zeros(shape=(self.height, self.width, 3), dtype=np.uint8)

        gl.glReadPixels(0,0,
            self.width, self.height,
            gl.GL_BGR, # cv2 uses BGR format instead of RGB
            gl.GL_UNSIGNED_BYTE,
            img.ctypes.data_as(POINTER(gl.GLubyte)))
        gl.glDisable(gl.GL_SCISSOR_TEST)
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)

        self.writer.write(cv2.flip(img, 0))

        return img

    def close(self):
        # TODO: docstring
        if self.ready:
            self.writer.release()
            self.writer = None
            self.ready  = False

def _draw_info(env, drawers, width, height):
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glLoadIdentity()
    gl.glOrtho(0, width, 0, height, -1, 1)
    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glLoadIdentity()
    for drawer in drawers:
        drawer.draw(env)
