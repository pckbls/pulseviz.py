// https://www.shadertoy.com/view/Xds3Rr
// Created by inigo quilez - iq/2013
// License Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License.

#version 300 es

precision highp float;
precision highp int;
precision highp sampler2D;

uniform vec3      iResolution;           // viewport resolution (in pixels)
uniform sampler2D iChannel0;             // input channel
uniform float     iTime;                 // shader playback time (in seconds)
uniform vec2      ifFragCoordOffsetUniform;     // used for tiled based hq rendering

out vec4 glFragColor;


#define time iTime

float noise3D(vec3 p)
{
	return fract(sin(dot(p ,vec3(12.9898,78.233,12.7378))) * 43758.5453)*2.0-1.0;
}

vec3 mixc(vec3 col1, vec3 col2, float v)
{
    v = clamp(v,0.0,1.0);
    return col1+v*(col2-col1);
}

void mainImage( out vec4 fragColor, in vec2 fragCoord )
{
	vec2 uv = fragCoord.xy / iResolution.xy;
    vec2 p = uv*2.0-1.0;
    p.x*=iResolution.x/iResolution.y;
    p.y+=0.5;
    
    vec3 col = vec3(0.0);
    vec3 ref = vec3(0.0);
   
    float nBands = 64.0;
    float i = floor(uv.x*nBands);
    float f = fract(uv.x*nBands);
    float band = i/nBands;
    band *= band*band;
    band = band*0.995;
    band += 0.005;
    float s = texture( iChannel0, vec2(band,0.25) ).x;
    
    /* Gradient colors and amount here */
    const int nColors = 4;
    vec3 colors[nColors];  
    colors[0] = vec3(0.0,0.0,1.0);
    colors[1] = vec3(0.0,1.0,1.0);
    colors[2] = vec3(1.0,1.0,0.0);
    colors[3] = vec3(1.0,0.0,0.0);
    
    vec3 gradCol = colors[0];
    float n = float(nColors)-1.0;
    for(int i = 1; i < nColors; i++)
    {
		gradCol = mixc(gradCol,colors[i],(s-float(i-1)/n)*n);
    }
      
    col += vec3(1.0-smoothstep(0.0,0.01,p.y-s*1.5));
    col *= gradCol;

    ref += vec3(1.0-smoothstep(0.0,-0.01,p.y+s*1.5));
    ref*= gradCol*smoothstep(-0.5,0.5,p.y);
    
    col = mix(ref,col,smoothstep(-0.01,0.01,p.y));

    col *= smoothstep(0.125,0.375,f);
    col *= smoothstep(0.875,0.625,f);

    col = clamp(col, 0.0, 1.0);

    float dither = noise3D(vec3(p,time))*2.0/256.0;
    col += dither;
    
	fragColor = vec4(col,1.0);
}

void main() {
    mainImage(glFragColor, gl_FragCoord.xy + ifFragCoordOffsetUniform );
}

