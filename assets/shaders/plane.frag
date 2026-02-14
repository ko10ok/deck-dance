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

