precision mediump float;
uniform float time_ms;
uniform vec2 mouse;
uniform vec2 resolution;

void main( void ) {
        float mouse_charge = 10.;
        vec3 charges[10];
        charges[0] = vec3(0,0,10);
        charges[1] = vec3(0.1,0.1,-10);
        const int N = 2;        
        vec2 position = gl_FragCoord.xy / resolution.xy - resolution.xy/2.0;
        position.x = (gl_FragCoord.x - resolution.x/2.0)/resolution.x;
        position.y = (gl_FragCoord.y - resolution.y/2.0)/resolution.x;
        float r = distance(position.xy,vec2(mouse.x - 0.5, (mouse.y - 0.5)*resolution.y/resolution.x));
        float s = mouse_charge/(r*r);
        for(int i=0; i < N; i++){
                r = distance(position.xy,charges[i].xy);
                s += charges[i].z / (r*r);
        }
        gl_FragColor = vec4(fract(-log(s)*10.),fract(-log(s)*1.),fract(-log(s)/10.),1.);
}
