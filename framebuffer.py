from ctypes import byref # , POINTER
import pyglet
from pyglet import gl

class Framebuffer:
    """OpenGL Framebuffer wrapper class.

    Args:
        width:  Width of the framebuffer.
        height: Height of the framebuffer.
        context: (optional) OpenGL context to switch to when creating and using Framebuffer.
            If none passed - context is not switched by this class.
    """
    # http://www.opengl-tutorial.org/ru/intermediate-tutorials/tutorial-14-render-to-texture/
    # http://www.songho.ca/opengl/gl_fbo.html
    def __init__(self, width, height, context=None):
        if context:
            context.switch_to()
        self.context = context
        # global recorder_context
        # assert recorder_context or env
        # if not recorder_context:
        #     # recorder_context = pyglet.window.Window(width=1, height=1, visible=False)
        #     recorder_context = env.shadow_window
        # recorder_context.switch_to()

        id = gl.GLuint(0)
        # Generate framebuffer
        gl.glGenFramebuffers(1, byref(id))
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, id)
        # width = 80
        # height = 60
        self.fb_id = id
        self.width = width
        self.height = height

        # Generate texture for color buffer
        colorbuffer = gl.GLuint(0)
        gl.glGenTextures(1, byref(colorbuffer))
        gl.glBindTexture(gl.GL_TEXTURE_2D, colorbuffer)
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGBA, width, height, 0, gl.GL_RGBA, gl.GL_FLOAT, None)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
        gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
        self.colorbuffer_id = colorbuffer

        # Generate depth buffer
        depthbuffer = gl.GLuint(0)
        gl.glGenRenderbuffers(1, byref(depthbuffer))
        gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, depthbuffer)
        gl.glRenderbufferStorage(gl.GL_RENDERBUFFER, gl.GL_DEPTH_COMPONENT, width, height)
        self.depthbuffer_id = depthbuffer

        # Set texture and depth buffer to the framebuffer
        gl.glFramebufferTexture2D(gl.GL_FRAMEBUFFER, gl.GL_COLOR_ATTACHMENT0,
            gl.GL_TEXTURE_2D, colorbuffer, 0)
        gl.glFramebufferRenderbuffer(gl.GL_FRAMEBUFFER, gl.GL_DEPTH_ATTACHMENT, gl.GL_RENDERBUFFER, depthbuffer)

        if pyglet.options['debug_gl']:
          res = gl.glCheckFramebufferStatus(gl.GL_FRAMEBUFFER)
          assert res == gl.GL_FRAMEBUFFER_COMPLETE

        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, 0)

    def use(self):
        if self.context:
            self.context.switch_to()
        gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, self.fb_id)
        gl.glViewport(0, 0, self.width, self.height)
