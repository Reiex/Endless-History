uniform sampler2D texture;
uniform vec2 pos_joueur;
uniform vec2 resolution;
uniform vec2 taille_map;
uniform vec2 decalage;
uniform sampler2D map;


float distance(in float x1, in float y1, in float x2, in float y2)
{
	return sqrt(pow((x1-x2), 2.0) + pow((y1-y2), 2.0));
}


float distance_brillants(in float x, in float y)
{
	
	float xb = (x + decalage[0])/64.0, yb = (y + decalage[1])/64.0;
	float d = 0.0;
	float d_min = -1.0;

	vec2 coord = vec2(xb, yb);
	if((coord[0] < taille_map[0]) && (coord[0] >= 0.0) && (coord[1] < taille_map[1]) && (coord[1] >= 0.0))
	{
		vec4 p = texture2D(map, vec2(coord[0]/taille_map[0], coord[1]/taille_map[1]));
		if((219.0 <= p.r*255.0) && (227.0 >= p.r*255.0))
		{
			return 0.0;
		}
	}

	coord = vec2(xb+1.0, yb);
	if((coord[0] < taille_map[0]) && (coord[0] >= 0.0) && (coord[1] < taille_map[1]) && (coord[1] >= 0.0))
	{
		vec4 p = texture2D(map, vec2(coord[0]/taille_map[0], coord[1]/taille_map[1]));
		if((219.0 <= p.r*255.0) && (227.0 >= p.r*255.0))
		{
			d = distance(coord[0], coord[1], int(coord[0]+1.0), coord[1]);
			if(d_min == -1.0 || d <= d_min)
			{
				d_min = d;
			}
		}
	}

	coord = vec2(xb-1.0, yb);
	if((coord[0] < taille_map[0]) && (coord[0] >= 0.0) && (coord[1] < taille_map[1]) && (coord[1] >= 0.0))
	{
		vec4 p = texture2D(map, vec2(coord[0]/taille_map[0], coord[1]/taille_map[1]));
		if((219.0 <= p.r*255.0) && (227.0 >= p.r*255.0))
		{
			d = distance(coord[0], coord[1], int(coord[0]), coord[1]);
			if(d_min == -1.0 || d <= d_min)
			{
				d_min = d;
			}
		}
	}

	coord = vec2(xb, yb+1.0);
	if((coord[0] < taille_map[0]) && (coord[0] >= 0.0) && (coord[1] < taille_map[1]) && (coord[1] >= 0.0))
	{
		vec4 p = texture2D(map, vec2(coord[0]/taille_map[0], coord[1]/taille_map[1]));
		if((219.0 <= p.r*255.0) && (227.0 >= p.r*255.0))
		{
			d = distance(coord[0], coord[1], coord[0], int(coord[1]+1.0));
			if(d_min == -1.0 || d <= d_min)
			{
				d_min = d;
			}
		}
	}

	coord = vec2(xb, yb-1.0);
	if((coord[0] < taille_map[0]) && (coord[0] >= 0.0) && (coord[1] < taille_map[1]) && (coord[1] >= 0.0))
	{
		vec4 p = texture2D(map, vec2(coord[0]/taille_map[0], coord[1]/taille_map[1]));
		if((219.0 <= p.r*255.0) && (227.0 >= p.r*255.0))
		{
			d = distance(coord[0], coord[1], coord[0], int(coord[1]));
			if(d_min == -1.0 || d <= d_min)
			{
				d_min = d;
			}
		}
	}

	coord = vec2(xb+1.0, yb+1.0);
	if((coord[0] < taille_map[0]) && (coord[0] >= 0.0) && (coord[1] < taille_map[1]) && (coord[1] >= 0.0))
	{
		vec4 p = texture2D(map, vec2(coord[0]/taille_map[0], coord[1]/taille_map[1]));
		if((219.0 <= p.r*255.0) && (227.0 >= p.r*255.0))
		{
			d = distance(coord[0], coord[1], int(coord[0]+1.0), int(coord[1]+1.0));
			if(d_min == -1.0 || d <= d_min)
			{
				d_min = d;
			}
		}
	}

	coord = vec2(xb+1.0, yb-1.0);
	if((coord[0] < taille_map[0]) && (coord[0] >= 0.0) && (coord[1] < taille_map[1]) && (coord[1] >= 0.0))
	{
		vec4 p = texture2D(map, vec2(coord[0]/taille_map[0], coord[1]/taille_map[1]));
		if((219.0 <= p.r*255.0) && (227.0 >= p.r*255.0))
		{
			d = distance(coord[0], coord[1], int(coord[0]+1.0), int(coord[1]));
			if(d_min == -1.0 || d <= d_min)
			{
				d_min = d;
			}
		}
	}

	coord = vec2(xb-1.0, yb+1.0);
	if((coord[0] < taille_map[0]) && (coord[0] >= 0.0) && (coord[1] < taille_map[1]) && (coord[1] >= 0.0))
	{
		vec4 p = texture2D(map, vec2(coord[0]/taille_map[0], coord[1]/taille_map[1]));
		if((219.0 <= p.r*255.0) && (227.0 >= p.r*255.0))
		{
			d = distance(coord[0], coord[1], int(coord[0]), int(coord[1]+1.0));
			if(d_min == -1.0 || d <= d_min)
			{
				d_min = d;
			}
		}
	}

	coord = vec2(xb-1.0, yb-1.0);
	if((coord[0] < taille_map[0]) && (coord[0] >= 0.0) && (coord[1] < taille_map[1]) && (coord[1] >= 0.0))
	{
		vec4 p = texture2D(map, vec2(coord[0]/taille_map[0], coord[1]/taille_map[1]));
		if((219.0 <= p.r*255.0) && (227.0 >= p.r*255.0))
		{
			d = distance(coord[0], coord[1], int(coord[0]), int(coord[1]));
			if(d_min == -1.0 || d <= d_min)
			{
				d_min = d;
			}
		}
	}

	return d_min;
}


void main()
{
	vec4 pixel = texture2D(texture, gl_TexCoord[0].xy);
	vec2 pos_pixel = vec2(gl_FragCoord.x, gl_FragCoord.y);


	float d = distance(pos_pixel[0], resolution[1]-pos_pixel[1], pos_joueur[0], pos_joueur[1]);
	float d_brillant = distance_brillants(pos_pixel[0], resolution[1]-pos_pixel[1]);


	float coeff = exp(-pow(d/250.0, 3.0));
	float coeff_brillant = exp(-d_brillant*5);

	bool brillant = false;
	if(d_brillant >= 0.0)
	{
		coeff = coeff_brillant + coeff;
		if(coeff >= 1)
		{
			coeff = 1;
		}
		brillant = true;
	}
	

	if(brillant)
	{
		gl_FragColor = vec4(pixel.r*coeff*(1+coeff_brillant), pixel.g*coeff*(1+coeff_brillant*0.5), pixel.b*coeff, pixel.a);
	}
	else
	{
		gl_FragColor = vec4(pixel.r*coeff, pixel.g*coeff, pixel.b*coeff, pixel.a);
	}
	
}