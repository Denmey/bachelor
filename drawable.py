"""Module with drawable class and subclasses.
"""
import pyglet
from pyglet import gl
from gym_duckietown.graphics import bezier_draw
from gym_duckietown.simulator import get_agent_corners, get_dir_vec
import numpy as np

class Drawable:
    """Base class for drawable objects."""

    def __init__(self):
        pass

    def draw(self, env):
        """Draws something in environment using active framebuffer, viewport, matrices.
        Note: Shouldn't change framebuffer, viewport or projection matrix.
        """
        raise NotImplementedError("Method is not implemented")

class Tiles(Drawable):
    """Class that draws all tiles in environment."""

    def __init__(self):
        pass

    def draw(self, env):
        """
        Draws all tiles in environment.

        Args:
            env: environment.
        """
        gl.glEnable(gl.GL_TEXTURE_2D)
        for j in range(env.grid_height):
            for i in range(env.grid_width):
                # Get the tile type and angle
                tile = env._get_tile(i, j)

                if tile is None:
                    continue

                # kind = tile['kind']
                angle = tile['angle']
                color = tile['color']
                texture = tile['texture']

                gl.glColor3f(*color)

                gl.glPushMatrix()
                gl.glTranslatef((i + 0.5) * env.road_tile_size, 0, (j + 0.5) * env.road_tile_size)
                gl.glRotatef(angle * 90, 0, 1, 0)

                # Bind the appropriate texture
                texture.bind()

                env.road_vlist.draw(gl.GL_QUADS)
                gl.glPopMatrix()

                if env.draw_curve and tile['drivable']:
                    # Find curve with largest dotproduct with heading
                    curves = env._get_tile(i, j)['curves']
                    curve_headings = curves[:, -1, :] - curves[:, 0, :]
                    curve_headings = curve_headings / np.linalg.norm(curve_headings).reshape(1, -1)
                    dirVec = get_dir_vec(angle)
                    dot_prods = np.dot(curve_headings, dirVec)

                    # Current ("closest") curve drawn in Red
                    pts = curves[np.argmax(dot_prods)]
                    bezier_draw(pts, n=20, red=True)

                    pts = env._get_curve(i, j)
                    for idx, pt in enumerate(pts):
                        # Don't draw current curve in blue
                        if idx == np.argmax(dot_prods):
                            continue
                        bezier_draw(pt, n=20)

class Objects(Drawable):
    """Draws all tiles in environment.

    Args:
        draw_bbox (bool): should be bbox for each object to be drawn or not.
    """

    def __init__(self, draw_bbox = False):
        self.draw_bbox = draw_bbox

    def draw(self, env):
        """
        Draws all objects in environment.

        Args:
            env: environment.
        """
        for obj in env.objects:
            obj.render(self.draw_bbox)

class Bot(Drawable):
    """Draws bot in environment.

    Args:
        draw_bbox (bool): should be bbox for bot to be drawn or not.
    """

    def __init__(self, draw_bbox = False):
        self.draw_bbox = draw_bbox

    def draw(self, env):
        """
        Draws all objects in environment.

        Args:
            env: environment.
        """
        self._draw_bot(env)
        if self.draw_bbox:
            self._draw_bbox(env)

    def _draw_bot(self, env):
        """Auxiliary draw method for bot."""
        gl.glPushMatrix()
        gl.glTranslatef(*env.cur_pos)
        gl.glScalef(1, 1, 1)
        gl.glRotatef(env.cur_angle * 180 / np.pi, 0, 1, 0)
        env.mesh.render()
        gl.glPopMatrix()
        label = pyglet.text.Label("Test", x=20, y=20)
        label.draw()

    def _draw_bbox(self, env):
        """Auxiliary draw method for bot's bbox."""
        corners = get_agent_corners(env.cur_pos, env.cur_angle)
        gl.glColor3f(1, 0, 0)
        gl.glBegin(gl.GL_LINE_LOOP)
        gl.glVertex3f(corners[0, 0], 0.01, corners[0, 1])
        gl.glVertex3f(corners[1, 0], 0.01, corners[1, 1])
        gl.glVertex3f(corners[2, 0], 0.01, corners[2, 1])
        gl.glVertex3f(corners[3, 0], 0.01, corners[3, 1])
        gl.glEnd()

class Origin(Drawable):
    """Draws red point on world's origin."""

    def __init__(self):
        pass

    def draw(self, env):
        """
        Draws red point on world's origin.

        Args:
            env: environment.
        """
        gl.glColor3f(1, 0, 0)
        gl.glBegin(gl.GL_POINTS)
        gl.glVertex3f(0, 0, 0)
        gl.glEnd()

class Text(Drawable):
    """Drawable class for text.

    Args:
        pos (tuple): Coordinates of x and y in pixels where to draw text.
        info (Info): One of info objects with get_str method.

    Note: Should be passed to info_drawers param.
    """

    def __init__(self, pos, info, kwargs = {}):
        self.x, self.y = pos
        self.info = info
        self.label = None
        self.kwargs = kwargs

    def draw(self, env):
        """Draw text on active framebuffer.

        Args:
            env: environment
        """
        string = self.info.get_str()
        if self.label:
            self.label.text = string
        else:
            self.label = pyglet.text.Label(string, x=self.x, y=self.y, **self.kwargs)
        self.label.draw()

# TODO
class Path(Drawable):
    # TODO
    def __init__(self):
        self.points = []
        pass

    def draw(self, env):
        # Move, (x, y)
        # Teleport, (x, y)
        # history =

        raise NotImplementedError("Method is not implemented")
