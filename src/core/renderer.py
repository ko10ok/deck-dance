"""
Рендерер - ModernGL контекст и 3D отрисовка
"""

import moderngl
import numpy as np
from pyrr import Matrix44, Vector3
from typing import Tuple, Optional
import os
from src.config import SHADERS_DIR, PLANE_SIZE, CAMERA_DISTANCE


class Renderer:
    """Рендерер с поддержкой 3D и 2D отрисовки"""

    def __init__(self, ctx: moderngl.Context, window_size: Tuple[int, int]):
        self.ctx = ctx
        self.window_size = window_size

        # Загрузка шейдеров
        self.plane_program = self._load_shader("plane")
        self.circle_program = self._load_shader("circle")

        # Создание геометрии
        self._create_plane()
        self._create_circle_quad()

        # Матрицы камеры
        self._update_matrices()

    def _load_shader(self, name: str) -> moderngl.Program:
        """Загрузка шейдерной программы"""
        vert_path = os.path.join(SHADERS_DIR, f"{name}.vert")
        frag_path = os.path.join(SHADERS_DIR, f"{name}.frag")

        # Если файлы не существуют, используем встроенные шейдеры
        if os.path.exists(vert_path) and os.path.exists(frag_path):
            with open(vert_path, 'r', encoding='utf-8') as f:
                vert_src = f.read()
            with open(frag_path, 'r', encoding='utf-8') as f:
                frag_src = f.read()
        else:
            vert_src, frag_src = self._get_builtin_shader(name)

        return self.ctx.program(vertex_shader=vert_src, fragment_shader=frag_src)

    def _get_builtin_shader(self, name: str) -> Tuple[str, str]:
        """Встроенные шейдеры"""
        if name == "plane":
            return (
                """
                #version 330 core
                in vec3 in_position;
                in vec2 in_texcoord;
                out vec2 v_texcoord;
                uniform mat4 mvp;
                void main() {
                    gl_Position = mvp * vec4(in_position, 1.0);
                    v_texcoord = in_texcoord;
                }
                """,
                """
                #version 330 core
                in vec2 v_texcoord;
                out vec4 fragColor;
                uniform vec4 color;
                void main() {
                    // Сетка на плоскости
                    vec2 grid = abs(fract(v_texcoord * 10.0 - 0.5) - 0.5) / fwidth(v_texcoord * 10.0);
                    float line = min(grid.x, grid.y);
                    float gridAlpha = 1.0 - min(line, 1.0);
                    fragColor = mix(color, vec4(0.3, 0.3, 0.4, 1.0), gridAlpha * 0.3);
                }
                """
            )
        elif name == "circle":
            return (
                """
                #version 330 core
                in vec2 in_position;
                in vec2 in_texcoord;
                out vec2 v_texcoord;
                uniform vec2 center;
                uniform float radius;
                uniform vec2 screen_size;
                void main() {
                    vec2 pos = center + in_position * radius;
                    vec2 ndc = (pos / screen_size) * 2.0 - 1.0;
                    ndc.y = -ndc.y;  // Flip Y
                    gl_Position = vec4(ndc, 0.0, 1.0);
                    v_texcoord = in_texcoord;
                }
                """,
                """
                #version 330 core
                in vec2 v_texcoord;
                out vec4 fragColor;
                uniform float alpha;
                uniform vec4 color;
                uniform float ring_width;
                void main() {
                    float dist = length(v_texcoord - vec2(0.5));
                    float ring = smoothstep(0.5, 0.5 - ring_width, dist) - 
                                 smoothstep(0.5 - ring_width, 0.5 - ring_width * 2.0, dist);
                    fragColor = vec4(color.rgb, ring * alpha);
                }
                """
            )
        return ("", "")

    def _create_plane(self):
        """Создание 3D плоскости"""
        size = PLANE_SIZE
        vertices = np.array([
            # position (x, y, z), texcoord (u, v)
            -size, 0.0, -size,  0.0, 0.0,
             size, 0.0, -size,  1.0, 0.0,
             size, 0.0,  size,  1.0, 1.0,
            -size, 0.0,  size,  0.0, 1.0,
        ], dtype='f4')

        indices = np.array([0, 1, 2, 0, 2, 3], dtype='i4')

        self.plane_vbo = self.ctx.buffer(vertices.tobytes())
        self.plane_ibo = self.ctx.buffer(indices.tobytes())

        self.plane_vao = self.ctx.vertex_array(
            self.plane_program,
            [(self.plane_vbo, '3f 2f', 'in_position', 'in_texcoord')],
            self.plane_ibo
        )

    def _create_circle_quad(self):
        """Создание квада для отрисовки кругов"""
        vertices = np.array([
            # position (x, y), texcoord (u, v)
            -1.0, -1.0,  0.0, 0.0,
             1.0, -1.0,  1.0, 0.0,
             1.0,  1.0,  1.0, 1.0,
            -1.0,  1.0,  0.0, 1.0,
        ], dtype='f4')

        indices = np.array([0, 1, 2, 0, 2, 3], dtype='i4')

        self.circle_vbo = self.ctx.buffer(vertices.tobytes())
        self.circle_ibo = self.ctx.buffer(indices.tobytes())

        self.circle_vao = self.ctx.vertex_array(
            self.circle_program,
            [(self.circle_vbo, '2f 2f', 'in_position', 'in_texcoord')],
            self.circle_ibo
        )

    def _update_matrices(self):
        """Обновление матриц проекции и вида"""
        aspect = self.window_size[0] / self.window_size[1]

        self.projection = Matrix44.perspective_projection(
            45.0, aspect, 0.1, 100.0
        )

        self.view = Matrix44.look_at(
            Vector3([0.0, CAMERA_DISTANCE, CAMERA_DISTANCE]),  # eye
            Vector3([0.0, 0.0, 0.0]),  # target
            Vector3([0.0, 1.0, 0.0])   # up
        )

        self.model = Matrix44.identity()

    def resize(self, new_size: Tuple[int, int]):
        """Обновление размера окна"""
        self.window_size = new_size
        self.ctx.viewport = (0, 0, new_size[0], new_size[1])
        self._update_matrices()

    def render_plane(self, color: Tuple[float, float, float, float] = (0.2, 0.2, 0.3, 1.0)):
        """Отрисовка 3D плоскости"""
        mvp = self.projection * self.view * self.model

        self.plane_program['mvp'].write(mvp.astype('f4').tobytes())
        self.plane_program['color'].value = color

        self.plane_vao.render(moderngl.TRIANGLES)

    def render_circle(
        self,
        center: Tuple[float, float],
        radius: float,
        alpha: float = 1.0,
        color: Tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0),
        ring_width: float = 0.1
    ):
        """Отрисовка круга (кольца) в 2D"""
        self.circle_program['center'].value = center
        self.circle_program['radius'].value = radius
        self.circle_program['screen_size'].value = self.window_size
        self.circle_program['alpha'].value = alpha
        self.circle_program['color'].value = color
        self.circle_program['ring_width'].value = ring_width

        self.circle_vao.render(moderngl.TRIANGLES)

    def cleanup(self):
        """Очистка ресурсов"""
        self.plane_vao.release()
        self.plane_vbo.release()
        self.plane_ibo.release()
        self.circle_vao.release()
        self.circle_vbo.release()
        self.circle_ibo.release()


