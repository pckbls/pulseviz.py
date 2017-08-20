#version 300 es

precision highp float;
precision highp int;
precision highp sampler2D;

uniform vec3      iResolution;           // viewport resolution (in pixels)
uniform float     iTime;                 // shader playback time (in seconds)
uniform sampler2D iChannel0;             // input channel
uniform vec4      iMouse;                // mouse pixel coords. xy: current (if MLB down), zw: click
uniform vec2      ifFragCoordOffsetUniform;     // used for tiled based hq rendering

out vec4 glFragColor;





const float lineWidth = 0.09;

float plot(float uvy, float liney) {
	return smoothstep(uvy-lineWidth, uvy, liney) - smoothstep(uvy, uvy+lineWidth, liney);
}

void mainImage(out vec4 fragColor, in vec2 fragCoord)
{
	vec2 uv = fragCoord.xy / iResolution.xy;
    float timeDomain = texture(iChannel0, vec2(uv.x, 0.75)).x;
    float frequencyDomain = texture(iChannel0, vec2(uv.x, 0.25)).x;
    float t = plot(uv.y*2.0-1.0, timeDomain);
    float f = plot(uv.y*2.0, frequencyDomain);
 	fragColor = vec4(t, 0.0, f, 1.0);
}

void main() {
    mainImage(glFragColor, gl_FragCoord.xy + ifFragCoordOffsetUniform );
}


