////////////////////////////////////////////////////////////////////////
// Module:				Blitzprog.ParticleSystem
// Author:				Eduard Urbach
// Description:			Particle system
////////////////////////////////////////////////////////////////////////

#ifndef BLITZPROG_PARTICLESYSTEM_HPP_
#define BLITZPROG_PARTICLESYSTEM_HPP_

////////////////////////////////////////////////////////////////////////
// Includes
////////////////////////////////////////////////////////////////////////

//Modules
#include <Blitzprog/header.hpp>
#include <Blitzprog/Core/Core.hpp>
#include <Blitzprog/Graphics/Graphics.hpp>

////////////////////////////////////////////////////////////////////////
// Constants
////////////////////////////////////////////////////////////////////////



////////////////////////////////////////////////////////////////////////
// Classes
////////////////////////////////////////////////////////////////////////

//TODO: Improve this

//Particle2D
class TParticle2D
{
	public:
		
		TParticle2D(Image nImg, float xN, float yN, float endXN, float endYN, float rotN, float endRotN, int nr, int ng, int nb, int ner, int neg, int neb) : img(nImg), progress(0.0f), x(xN), y(yN), endX(endXN), endY(endYN), rot(rotN), endRot(endRotN), r(nr), g(ng), b(nb), er(ner), eg(neg), eb(neb)
		{
			
		}
		
		inline void Update(float speed)
		{
			progress += speed;
		}
		
		inline void Draw()
		{
			SetColor(static_cast<int>(r + (er - r) * progress), static_cast<int>(g + (eg - g) * progress), static_cast<int>(b + (eb - b) * progress), RGBFloatToByte(1 - progress));
			SetRotation(rot + (endRot - rot) * progress);
			//SetScale(0.25f, 0.25f);
			DrawImage(img, static_cast<int>(x + (endX - x) * progress), static_cast<int>(y + (endY - y) * progress));
		}
		
		inline float GetProgress()
		{
			return progress;
		}
		
		Image img;
		float progress;
		float x, y;
		float endX, endY;
		float rot, endRot;
		int r, g, b;
		int er, eg, eb;
};
typedef SharedPtr<TParticle2D> Particle2D;

////////////////////////////////////////////////////////////////////////
// Variables
////////////////////////////////////////////////////////////////////////



////////////////////////////////////////////////////////////////////////
// Functions
////////////////////////////////////////////////////////////////////////



////////////////////////////////////////////////////////////////////////
// Inline functions
////////////////////////////////////////////////////////////////////////



#endif /*BLITZPROG_PARTICLESYSTEM_HPP_*/
