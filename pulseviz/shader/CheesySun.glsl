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




//Author : Antoine Pazat
// Description : Cheesy audioreactive sunset
#pragma input iChannel0 audio

float circle(vec2 uv, vec2 pos, float radius){
return smoothstep(0.0,0.2,radius-length(uv + pos));
}

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
	vec2 uv = -1.+2.*fragCoord.xy / iResolution.xy;
	uv.x *= iResolution.x/iResolution.y;


	float fft  = texture( iChannel0, vec2(-uv.y,0.25) ).x;
	float wave = texture( iChannel0, vec2(uv.x,0.75) ).x;



	vec3 color = vec3(1.0,fft,fft-.4)*circle(uv,vec2(0.,0.),fft); // add fft
	color += vec3(.7,0.1,.0)+.25*((.4-length(uv))*vec3(1.,1.,0.));
	color += step(uv.y,0.)*vec3(-.1,-.1,.1);
	color *= vec3(2.*distance(fft, 0.));

	fragColor = vec4(color,1.0);
}


void main() {
    mainImage(glFragColor, gl_FragCoord.xy + ifFragCoordOffsetUniform );
}

