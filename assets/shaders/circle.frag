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

