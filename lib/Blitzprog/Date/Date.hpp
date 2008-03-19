////////////////////////////////////////////////////////////////////////
// Module:				Blitzprog.Date
// Author:				Eduard Urbach
// Description:			Date and time functions
////////////////////////////////////////////////////////////////////////

#ifndef BLITZPROG_DATE_HPP_
#define BLITZPROG_DATE_HPP_

////////////////////////////////////////////////////////////////////////
// Includes
////////////////////////////////////////////////////////////////////////

//Modules
#include <Blitzprog/header.hpp>
#include <Blitzprog/Core/Core.hpp>

//Boost
//#include <boost/date_time/gregorian/gregorian.hpp>

//Namespaces
//using namespace boost::gregorian;

////////////////////////////////////////////////////////////////////////
// Classes
////////////////////////////////////////////////////////////////////////



////////////////////////////////////////////////////////////////////////
// Constants
////////////////////////////////////////////////////////////////////////

//Undef CurrentTime
#ifdef CurrentTime
	#undef CurrentTime
#endif

////////////////////////////////////////////////////////////////////////
// Variables
////////////////////////////////////////////////////////////////////////



////////////////////////////////////////////////////////////////////////
// Functions
////////////////////////////////////////////////////////////////////////

//CurrentDate
String CurrentDate();

//CurrentTime
String CurrentTime();

////////////////////////////////////////////////////////////////////////
// Inline functions
////////////////////////////////////////////////////////////////////////

//CurrentDate2
/*inline String CurrentDate2()
{
	return to_simple_string(day_clock::local_day());
}*/

#endif /*BLITZPROG_DATE_HPP_*/
