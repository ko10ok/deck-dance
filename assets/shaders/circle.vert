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

