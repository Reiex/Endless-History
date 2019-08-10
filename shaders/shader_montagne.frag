uniform sampler2D texture;
uniform vec2 pos_joueur;
uniform vec2 resolution;
uniform float level;


float distance(in float x1, in float y1, in float x2, in float y2)
{
	return sqrt(pow((x1-x2), 2.0) + pow((y1-y2), 2.0));
}


void main()
{
	vec4 pixel = texture2D(texture, gl_TexCoord[0].xy);
	vec2 pos_pixel = vec2(gl_FragCoord.x, gl_FragCoord.y);

	float d = distance(pos_pixel[0], resolution[1]-pos_pixel[1], pos_joueur[0], pos_joueur[1]);
	float coeff = exp(-level*d/1000.0);
	
	gl_FragColor = vec4(pixel.r*coeff + (1.0 - coeff)*(153.0/255.0), pixel.g*coeff + (1.0 - coeff)*(217.0/255.0), pixel.b*coeff + (1.0 - coeff)*(234.0/255.0), pixel.a);
	
}