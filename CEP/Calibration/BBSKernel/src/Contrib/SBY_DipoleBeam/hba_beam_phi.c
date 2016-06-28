#include <math.h>
#include <complex.h>

/* Note: formulas have been optimized! */
/* alpha1=50/180*pi;
 * alpha2=80/180*pi;
 * L=0.366;
 * h=45/100;
 */
#define palpha1  0.87266462599716
#define palpha2  1.39626340159546
#define sin_alpha1 0.76604444311898
#define sin_alpha2 0.98480775301221
#define cos_alpha1 0.64278760968654
#define cos_alpha2 0.17364817766693
#define tan_alpha1 1.19175359259421 
#define tan_alpha2 5.67128181961771
#define pH 0.450
#define pL 0.366
#define pL1  0.13275660600238
#define pL2  0.23888953394781
#define pC 299792458.0 /* speed of light */
#define TOL 1e-9
#define del1 0.47777906789561
#define del2 0.37164613995018

/* see writeup for the exact formula */
inline complex double
Gammplus(double A, double B, double k, double L, double alpha) {
  double salpha=1/sin(alpha);
  double tmp=k*B;
  complex double z=-(cos(tmp)+_Complex_I*sin(tmp))/(A*A-salpha*salpha+TOL);
  tmp=k*A*L;
  double ang1=k*(L)*salpha;
  complex double part1=cos(tmp)+_Complex_I*sin(tmp);
  part1=part1*salpha-_Complex_I*A*sin(ang1)-salpha*cos(ang1);
  return z*part1;
}
inline complex double
Gammminus(double A, double B, double k, double L, double alpha) {
  double salpha=1/sin(alpha);
  double tmp=k*B;
  complex double z=-(cos(tmp)+_Complex_I*sin(tmp))/(A*A-salpha*salpha+TOL);
  tmp=-k*A*L;
  double ang1=k*(L)*salpha;
  complex double part1=cos(tmp)+_Complex_I*sin(tmp);
  part1=part1*salpha+_Complex_I*A*sin(ang1)-salpha*cos(ang1);
  return z*part1;
}
inline complex double
Gammplus0(double A, double B, double k, double L) {
  double tmp=k*B;
  complex double z=-(cos(tmp)+_Complex_I*sin(tmp))/(A*A-1.0+TOL);
  tmp=k*A*L;
  double ang1=k*(L);
  complex double part1=cos(tmp)+_Complex_I*sin(tmp);
  part1=part1-_Complex_I*A*sin(ang1)-cos(ang1);
  return z*part1;
}
inline complex double
Gammminus0(double A, double B, double k, double L) {
  double tmp=k*B;
  complex double z=-(cos(tmp)+_Complex_I*sin(tmp))/(A*A-1.0+TOL);
  tmp=-k*A*L;
  double ang1=k*(L);
  complex double part1=cos(tmp)+_Complex_I*sin(tmp);
  part1=part1+_Complex_I*A*sin(ang1)-cos(ang1);
  return z*part1;
}

/* 
 * equation - droopy dipole
 * equation: see writeup
 * c: speed of light, f : frequency
 * th: pi/2-elevation
 * phi: phi_0+azimuth, phi_0: dipole orientation
 * parameters: h,L,alpha,phi_0
 * h: height of center from ground, L: projected arm length
 * alpha: droop angle
 * axes: time,freq, az, el
 */
double test_double(const double *par,const double *x){
  return (0);
}

complex double test_complex(const complex *par,const complex *x){
  const double x1=creal(x[1]);
  const double x2=creal(x[2]);
  const double x3=creal(x[3]);
  //const double p0=creal(par[0]);
 // const double p1=creal(par[1]);
  //const double p2=creal(par[2]);
  const double p0=creal(par[0]);

  if (x3<=0.0) return (0+0*_Complex_I); /* below horizon */
  const double theta=M_PI_2-x3;
  const double phi=p0+x2; /* take orientation into account */

  /* some essential constants */
  double k=2*M_PI*x1/pC;

  /* calculate needed trig functions */
  double sin_theta=sin(theta);
  double cos_theta=cos(theta);
  double sin_phi=sin(phi);
  double cos_phi=cos(phi);

  /* mu/4PI=10e-7  x omega*/
  //const double mop=1.0;//(1e-7)*2*M_PI*x1;
  //const double mop=(1e-7)*2*M_PI*x1;
  //add normalization constant to make gain almost equal to 0.01 (b*x+c)
  const double mop=(1e-7)*2*M_PI*x1*(-0.0000897*x1/1e6+0.0233)/100.0;


  complex double Phi11=Gammplus(sin_theta*cos_phi-cos_theta/tan_alpha1,pH*cos_theta,k,pL,palpha1);
  complex double Eph1=sin_alpha1*sin_phi*Phi11;
  Phi11=Gammplus(sin_theta*cos_phi+cos_theta/tan_alpha2,pH*cos_theta,k,pL,M_PI-palpha2);
  Eph1+=sin_alpha2*sin_phi*Phi11;


  Phi11=Gammminus(-sin_theta*cos_phi+cos_theta/tan_alpha1,pH*cos_theta,k,pL,palpha1);
  complex double Eph2=sin_alpha1*sin_phi*Phi11;
  Phi11=Gammminus(-sin_theta*cos_phi-cos_theta/tan_alpha2,pH*cos_theta,k,pL,M_PI-palpha2);
  Eph2+=sin_alpha2*sin_phi*Phi11;


  Phi11=Gammminus(-sin_theta*cos_phi-cos_theta/tan_alpha1,-pH*cos_theta,k,pL,palpha1);
  complex double Eph3=-sin_alpha1*sin_phi*Phi11;
  Phi11=Gammminus(-sin_theta*cos_phi+cos_theta/tan_alpha2,-pH*cos_theta,k,pL,M_PI-palpha2);
  Eph3+=-sin_alpha2*sin_phi*Phi11;


  Phi11=Gammplus(sin_theta*cos_phi+cos_theta/tan_alpha1,-pH*cos_theta,k,pL,palpha1);
  complex double Eph4=-sin_alpha1*sin_phi*Phi11;
  Phi11=Gammplus(sin_theta*cos_phi-cos_theta/tan_alpha2,-pH*cos_theta,k,pL,M_PI-palpha2);
  Eph4+=-sin_alpha2*sin_phi*Phi11;

  //enable below for H symmetry
  //complex double Eph=Eph1+_Complex_I*Eph2+_Complex_I*Eph3+Eph4;
  //this is my original version
  complex double Eph=Eph1+Eph2+Eph3+Eph4;
  return (Eph*mop);
}
int Npar_test=1;
int Nx_test=4;
