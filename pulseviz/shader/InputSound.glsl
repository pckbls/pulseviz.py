// https://www.shadertoy.com/view/Xds3Rr
// Created by inigo quilez - iq/2013
// License Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License.

#version 300 es

precision highp float;
precision highp int;
precision highp sampler2D;

uniform vec3      iResolution;           // viewport resolution (in pixels)
uniform sampler2D iChannel0;             // input channel
uniform vec2      ifFragCoordOffsetUniform;     // used for tiled based hq rendering

out vec4 glFragColor;

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
    // create pixel coordinates
	vec2 uv = fragCoord.xy / iResolution.xy;

    // the sound texture is 512x2
    int tx = int(uv.x*512.0);
    
	// first row is frequency data (48Khz/4 in 512 texels, meaning 23 Hz per texel)
	float fft  = texelFetch( iChannel0, ivec2(tx,0), 0 ).x; 

    // second row is the sound wave, one texel is one mono sample
    float wave = texelFetch( iChannel0, ivec2(tx,1), 0 ).x;
	
	// convert frequency to colors
	vec3 col = vec3( fft, 4.0*fft*(1.0-fft), 1.0-fft ) * fft;

    // add wave form on top	
	col += 1.0 -  smoothstep( 0.0, 0.15, abs(wave - uv.y) );
	
	// output final color
	fragColor = vec4(col,1.0);
}

void main() {
    // mainImage(glFragColor, gl_FragCoord.xy + ifFragCoordOffsetUniform );
    glFragColor = vec4(1.0, 0.0, 1.0, 1.0);
}
