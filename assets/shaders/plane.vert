#version 330 core

in vec3 in_position;
in vec2 in_texcoord;

out vec2 v_texcoord;

uniform mat4 mvp;

void main() {
    gl_Position = mvp * vec4(in_position, 1.0);
    v_texcoord = in_texcoord;
}

