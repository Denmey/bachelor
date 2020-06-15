from pyglet import gl

class CameraSettings:
    """Class for camera settings.

    Args:
        width, height: Width and height of a camera
        pos_getter, dir_getter, up_getter: Getters used for camera position and rotation. If none passed, identity matrix is used.
        projection(perspective/orthogonal): Projection to use in camera
        scale(float): Scaling factor used when rendering objects
    """
    def __init__(self, width, height, pos_getter, dir_getter, up_getter, projection = 'perspective', scale = 1.0):
        self.pos_getter = pos_getter
        self.dir_getter = dir_getter
        self.up_getter  = up_getter
        if projection != 'perspective' and projection != 'orthogonal':
            raise ValueError("Projection parameter is invalid.")
        self.projection = projection
        self.width  = width
        self.height = height
        assert scale > 0
        self.scale = scale

    def use(self, env, flip_vertically = False):
        """Load projection and view matrices for camera.

        Args:
            env: Environment used in pos, dir, up getters.
            flip_vertically: Should rendered image be flipped vertically or not.

        Note: If identity matrix (see constructor) is used then flip_vertically doesn't change anything.
        """
        # Projection matrix:
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        if self.projection == 'perspective':
            gl.gluPerspective(
                45.0,
                self.width / float(self.height),
                0.04,
                100.0
            )
        elif self.projection == 'orthogonal':
            width = self.width
            height = self.height
            gl.glOrtho(-width/2, width/2, -height/2, height/2, -1, 10)
        gl.glScalef(self.scale, self.scale, 1)

        # View matrix:
        gl.glMatrixMode(gl.GL_MODELVIEW)
        gl.glLoadIdentity()
        if self.pos_getter and self.dir_getter and self.up_getter:
            pos = self.pos_getter(env)
            dir = self.dir_getter(env)
            tgt = list([pos+dir for (pos, dir) in zip(pos, dir)])
            # Invert up to flip image because OpenCV and OpenGL y-origins are
            #   in opposite corners
            if flip_vertically:
                up  = list([-val for val in self.up_getter(env)])
            else:
                up  = self.up_getter(env)
            gl.gluLookAt(
                *pos, # Eye position
                *tgt, # Target
                *up # Up vector
            )