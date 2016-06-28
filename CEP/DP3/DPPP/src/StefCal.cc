//# StefCal.cc: Perform StefCal algorithm for gain calibration
//# Copyright (C) 2013
//# ASTRON (Netherlands Institute for Radio Astronomy)
//# P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
//#
//# This file is part of the LOFAR software suite.
//# The LOFAR software suite is free software: you can redistribute it and/or
//# modify it under the terms of the GNU General Public License as published
//# by the Free Software Foundation, either version 3 of the License, or
//# (at your option) any later version.
//#
//# The LOFAR software suite is distributed in the hope that it will be useful,
//# but WITHOUT ANY WARRANTY; without even the implied warranty of
//# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//# GNU General Public License for more details.
//#
//# You should have received a copy of the GNU General Public License along
//# with the LOFAR software suite. If not, see <http://www.gnu.org/licenses/>.
//#
//# $Id: StefCal.cc 21598 2012-07-16 08:07:34Z diepen $
//#
//# @author Tammo Jan Dijkema

#include <lofar_config.h>
#include <DPPP/StefCal.h>
#include <DPPP/DPInput.h>

#include <vector>
#include <algorithm>
#include <limits>

#include <iostream>

using namespace casa;

namespace LOFAR {
  namespace DPPP {

    StefCal::StefCal(uint solInt, uint nChan, const string& mode,
                     double tolerance, uint maxAntennas,
                     bool detectStalling, uint debugLevel)
    : _nSt    (maxAntennas),
      _badIters (0),
      _veryBadIters (0),
      _solInt (solInt),
      _nChan  (nChan),
      _mode   (mode),
      _tolerance (tolerance),
      _detectStalling (detectStalling),
      _debugLevel (debugLevel)
    {
      resetVis();

      _nSt = maxAntennas;
      if (_mode=="fulljones") {
        _nCr=4;
        _nSp=1;
        _savedNCr=4;
      } else if (_mode=="scalarphase" || _mode=="scalaramplitude") {
        _nCr=1;
        _nSp=2;
        _savedNCr=1;
      } else { // mode=="phaseonly", mode=="diagonal", mode=="amplitudeonly"
        _nCr=1;
        _nSp=1;
        _savedNCr=2;
      }

      _vis.resize(IPosition(6,_nSt,2,_solInt,_nChan,2,_nSt));
      _mvis.resize(IPosition(6,_nSt,2,_solInt,_nChan,2,_nSt));

      if (_mode=="fulljones" || _mode=="scalarphase" || _mode=="scalaramplitude") {
        _nUn = _nSt;
      } else { // mode=="phaseonly", mode=="diagonal", mode=="amplitudeonly"
        _nUn = 2*_nSt;
      }

      _g.resize(_nUn,_nCr);
      _gold.resize(_nUn,_nCr);
      _gx.resize(_nUn,_nCr);
      _gxx.resize(_nUn,_nCr);
      _h.resize(_nUn,_nCr);
      _z.resize(_nUn*_nChan*_solInt*_nSp,_nCr);

      _stationFlagged.resize(_nSt, false);

      init(true);
    }

    void StefCal::resetVis() {
      _vis=0;
      _mvis=0;
    }

    void StefCal::clearStationFlagged() {
      fill(_stationFlagged.begin(), _stationFlagged.end(), false);
    }

    void StefCal::init(bool initSolutions) {
      _dg=1.0e29;
      _dgx=1.0e30;
      _dgs.clear();

      _badIters=0;
      _veryBadIters=0;

      if (initSolutions) {
        double ginit=1.0;
        if (_mode != "phaseonly" && _mode != "scalarphase" ) {
          // Initialize solution with sensible amplitudes
          double fronormvis=0;
          double fronormmod=0;

          DComplex* t_vis_p=_vis.data();
          DComplex* t_mvis_p=_mvis.data();

          uint vissize=_vis.size();
          for (uint i=0;i<vissize;++i) {
            fronormvis+=norm(t_vis_p[i]);
            fronormmod+=norm(t_mvis_p[i]);
          }

          fronormvis=sqrt(fronormvis);
          fronormmod=sqrt(fronormmod);
          if (abs(fronormmod)>1.e-15) {
            ginit=sqrt(fronormvis/fronormmod);
          } else {
            ginit=1.0;
          }
        }

        if (_nCr==4) {
          for (uint ant=0;ant<_nUn;++ant) {
              _g(ant,0)=ginit;
              _g(ant,1)=0.;
              _g(ant,2)=0.;
              _g(ant,3)=ginit;
          }
        } else {
          _g=ginit;
        }
      } else { // Take care of NaNs in solution
        for (uint ant=0; ant<_nUn; ++ant) {
          double ginit=0;
          if (!isFinite(_g(ant,0).real()) ) {
            if (ginit==0 && !_stationFlagged[ant%_nSt]) {
              // Avoid calling getAverageUnflaggedSolution for stations that are always flagged
              ginit = getAverageUnflaggedSolution();
            }
            if (_nCr==4) {
              _g(ant,0)=ginit;
              _g(ant,1)=0.;
              _g(ant,2)=0.;
              _g(ant,3)=ginit;
            } else {
              _g(ant,0)=ginit;
            }
          }
        }
      }
    }

    double StefCal::getAverageUnflaggedSolution() {
      // Get average solution of unflagged antennas only once
      double total=0.;
      uint unflaggedstations=0;
      for (uint ant2=0; ant2<_nUn; ++ant2) {
        if (isFinite(_g(ant2,0).real())) {
          total += abs(_g(ant2,0));
          unflaggedstations++;
          if (_nCr==4) {
            total += abs(_g(ant2,3));
            unflaggedstations++;
          }
        }
      }
      return total/unflaggedstations;
    }

    StefCal::Status StefCal::doStep(uint iter) {
      _gxx = _gx;
      _gx = _g;

      if (_mode=="fulljones") {
        doStep_polarized();
        doStep_polarized();
        return relax(2*iter);
      } else {
        doStep_unpolarized();
        doStep_unpolarized();
        return relax(2*iter);
      }
    }

    void StefCal::doStep_polarized() {
      _gold = _g;

      for (uint st=0;st<_nSt;++st) {
        _h(st,0)=conj(_g(st,0));
        _h(st,1)=conj(_g(st,1));
        _h(st,2)=conj(_g(st,2));
        _h(st,3)=conj(_g(st,3));
      }

      for (uint st1=0;st1<_nSt;++st1) {
        if (_stationFlagged[st1]) {
          continue;
        }

        DComplex* vis_p;
        DComplex* mvis_p;
        Vector<DComplex> w(_nCr);
        Vector<DComplex> t(_nCr);

        for (uint time=0;time<_solInt;++time) {
          for (uint ch=0;ch<_nChan;++ch) {
            uint zoff=_nSt*ch+_nSt*_nChan*time;
            mvis_p=&_mvis(IPosition(6,0,0,time,ch,0,st1)); for (uint st2=0;st2<_nSt;++st2) { _z(st2+zoff,0)  = _h(st2,0) * mvis_p[st2]; } // itsMVis(IPosition(6,st2,0,time,ch,0,st1))
            mvis_p=&_mvis(IPosition(6,0,1,time,ch,0,st1)); for (uint st2=0;st2<_nSt;++st2) { _z(st2+zoff,0) += _h(st2,2) * mvis_p[st2]; } // itsMVis(IPosition(6,st2,0,time,ch,1,st1))
            mvis_p=&_mvis(IPosition(6,0,0,time,ch,1,st1)); for (uint st2=0;st2<_nSt;++st2) { _z(st2+zoff,1)  = _h(st2,0) * mvis_p[st2]; } // itsMVis(IPosition(6,st2,1,time,ch,0,st1))
            mvis_p=&_mvis(IPosition(6,0,1,time,ch,1,st1)); for (uint st2=0;st2<_nSt;++st2) { _z(st2+zoff,1) += _h(st2,2) * mvis_p[st2]; } // itsMVis(IPosition(6,st2,1,time,ch,1,st1))
            mvis_p=&_mvis(IPosition(6,0,0,time,ch,0,st1)); for (uint st2=0;st2<_nSt;++st2) { _z(st2+zoff,2)  = _h(st2,1) * mvis_p[st2]; } // itsMVis(IPosition(6,st2,0,time,ch,0,st1))
            mvis_p=&_mvis(IPosition(6,0,1,time,ch,0,st1)); for (uint st2=0;st2<_nSt;++st2) { _z(st2+zoff,2) += _h(st2,3) * mvis_p[st2]; } // itsMVis(IPosition(6,st2,0,time,ch,1,st1))
            mvis_p=&_mvis(IPosition(6,0,0,time,ch,1,st1)); for (uint st2=0;st2<_nSt;++st2) { _z(st2+zoff,3)  = _h(st2,1) * mvis_p[st2]; } // itsMVis(IPosition(6,st2,1,time,ch,0,st1))
            mvis_p=&_mvis(IPosition(6,0,1,time,ch,1,st1)); for (uint st2=0;st2<_nSt;++st2) { _z(st2+zoff,3) += _h(st2,3) * mvis_p[st2]; } // itsMVis(IPosition(6,st2,1,time,ch,1,st1))
          }
        }

        w=0;

        for (uint time=0;time<_solInt;++time) {
          for (uint ch=0;ch<_nChan;++ch) {
            for (uint st2=0;st2<_nSt;++st2) {
              uint zoff=st2+_nSt*ch+_nSt*_nChan*time;
              w(0) += conj(_z(zoff,0))*_z(zoff,0) + conj(_z(zoff,2))*_z(zoff,2);
              w(1) += conj(_z(zoff,0))*_z(zoff,1) + conj(_z(zoff,2))*_z(zoff,3);
              w(3) += conj(_z(zoff,1))*_z(zoff,1) + conj(_z(zoff,3))*_z(zoff,3);
            }
          }
        }
        w(2)=conj(w(1));

        t=0;

        for (uint time=0;time<_solInt;++time) {
          for (uint ch=0;ch<_nChan;++ch) {
            vis_p=&_vis(IPosition(6,0,0,time,ch,0,st1)); for (uint st2=0;st2<_nSt;++st2) { t(0) += conj(_z(st2+_nSt*ch+_nSt*_nChan*time,0)) * vis_p[st2]; }// itsVis(IPosition(6,st2,0,time,ch,0,st1))
            vis_p=&_vis(IPosition(6,0,1,time,ch,0,st1)); for (uint st2=0;st2<_nSt;++st2) { t(0) += conj(_z(st2+_nSt*ch+_nSt*_nChan*time,2)) * vis_p[st2]; }// itsVis(IPosition(6,st2,0,time,ch,1,st1))
            vis_p=&_vis(IPosition(6,0,0,time,ch,1,st1)); for (uint st2=0;st2<_nSt;++st2) { t(1) += conj(_z(st2+_nSt*ch+_nSt*_nChan*time,0)) * vis_p[st2]; }// itsVis(IPosition(6,st2,1,time,ch,0,st1))
            vis_p=&_vis(IPosition(6,0,1,time,ch,1,st1)); for (uint st2=0;st2<_nSt;++st2) { t(1) += conj(_z(st2+_nSt*ch+_nSt*_nChan*time,2)) * vis_p[st2]; }// itsVis(IPosition(6,st2,1,time,ch,1,st1))
            vis_p=&_vis(IPosition(6,0,0,time,ch,0,st1)); for (uint st2=0;st2<_nSt;++st2) { t(2) += conj(_z(st2+_nSt*ch+_nSt*_nChan*time,1)) * vis_p[st2]; }// itsVis(IPosition(6,st2,0,time,ch,0,st1))
            vis_p=&_vis(IPosition(6,0,1,time,ch,0,st1)); for (uint st2=0;st2<_nSt;++st2) { t(2) += conj(_z(st2+_nSt*ch+_nSt*_nChan*time,3)) * vis_p[st2]; }// itsVis(IPosition(6,st2,0,time,ch,1,st1))
            vis_p=&_vis(IPosition(6,0,0,time,ch,1,st1)); for (uint st2=0;st2<_nSt;++st2) { t(3) += conj(_z(st2+_nSt*ch+_nSt*_nChan*time,1)) * vis_p[st2]; }// itsVis(IPosition(6,st2,1,time,ch,0,st1))
            vis_p=&_vis(IPosition(6,0,1,time,ch,1,st1)); for (uint st2=0;st2<_nSt;++st2) { t(3) += conj(_z(st2+_nSt*ch+_nSt*_nChan*time,3)) * vis_p[st2]; }// itsVis(IPosition(6,st2,1,time,ch,1,st1))
          }
        }
        DComplex invdet= 1./(w(0) * w (3) - w(1)*w(2));
        _g(st1,0) = invdet * ( w(3) * t(0) - w(1) * t(2) );
        _g(st1,1) = invdet * ( w(3) * t(1) - w(1) * t(3) );
        _g(st1,2) = invdet * ( w(0) * t(2) - w(2) * t(0) );
        _g(st1,3) = invdet * ( w(0) * t(3) - w(2) * t(1) );
      }
    }

    void StefCal::doStep_unpolarized() {
      _gold=_g;

      for (uint ant=0;ant<_nUn;++ant) {
        _h(ant,0)=conj(_g(ant,0));
      }

      for (uint st1=0;st1<_nUn;++st1) {
        if (_stationFlagged[st1%_nSt]) {
          continue;
        }
        DComplex* vis_p;
        DComplex* mvis_p;
        double ww=0; // Same as w, but specifically for pol==false
        DComplex tt=0; // Same as t, but specifically for pol==false

        DComplex* z_p=_z.data();
        mvis_p=&_mvis(IPosition(6,0,0,0,0,st1/_nSt,st1%_nSt));
        vis_p = &_vis(IPosition(6,0,0,0,0,st1/_nSt,st1%_nSt));
        for (uint st1pol=0;st1pol<_nSp;++st1pol) {
          for (uint ch=0;ch<_nChan;++ch) {
            for (uint time=0;time<_solInt;++time) {
              DComplex* h_p=_h.data();
              for (uint st2=0;st2<_nUn;++st2) {
                *z_p = h_p[st2] * *mvis_p; //itsMVis(IPosition(6,st2%nSt,st2/nSt,time,ch,st1/nSt,st1%nSt));
                ww+=norm(*z_p);
                tt+=conj(*z_p) * *vis_p; //itsVis(IPosition(6,st2%nSt,st2/nSt,time,ch,st1/nSt,st1%nSt));
                mvis_p++;
                vis_p++;
                z_p++;
              }
              //cout<<"iS.z bij ch="<<ch<<"="<<iS.z<<endl<<"----"<<endl;
            }
          }
        }
        //cout<<"st1="<<st1%nSt<<(st1>=nSt?"y":"x")<<", t="<<tt<<"       ";
        //cout<<", w="<<ww<<"       ";
        _g(st1,0)=tt/ww;
        //cout<<", g="<<iS.g(st1,0)<<endl;
        if (_mode=="phaseonly" || _mode=="scalarphase") {
          _g(st1,0)/=abs(_g(st1,0));
        } else if (_mode=="amplitudeonly" || _mode=="scalaramplitude") {
          _g(st1,0) = abs(_g(st1,0));
        }

        if (_debugLevel>2) {
          cout<<endl<<"gi=[";
          uint ant=0;
          for (; ant<_nUn-1; ++ant) {
            cout<<_g(ant,0)<<",";
          }
          cout<<_g(ant,0)<<"]"<<endl;
        }
      }
    }

    casa::Matrix<casa::DComplex> StefCal::getSolution(bool setNaNs) {
      if (setNaNs && _debugLevel>0) {
        cout<<endl<<"dg=[";
        uint iter=0;
        for (; iter<_dgs.size()-1; ++iter) {
          cout<<_dgs[iter]<<",";
        }
        cout<<_dgs[iter]<<"]"<<endl;
      }

      if (_debugLevel>2) {
        cout<<endl<<"g=[";
        uint ant=0;
        for (; ant<_nUn-1; ++ant) {
          cout<<_g(ant,0)<<",";
        }
        cout<<_g(ant,0)<<"]"<<endl;
      }

      if (setNaNs) {
        for (uint ant=0; ant<_nUn; ++ant) {
          if (_stationFlagged[ant%_nSt]) {
            for (uint cr=0; cr<_nCr; ++cr) {
              _g(ant,cr)=std::numeric_limits<double>::quiet_NaN();
            }
          }
        }
      }

      return _g;
    }

    StefCal::Status StefCal::relax(uint iter) {
      if (_nSt==0) {
        return CONVERGED;
      }

      double f2 = -1.0;
      double f3 = -0.5;
      double f1 = 1 - f2 - f3;
      double f2q = -0.5;
      double f1q = 1 - f2q;
      double omega = 0.5;
      uint nomega = 24;
      double c1 = 0.5;
      double c2 = 1.2;
      double dgxx;
      bool threestep = false;
      uint maxBadIters=3;

      int sstep=0;

      if (_detectStalling && iter > 3) {
        double improvement = _dgx-_dg;

        if (abs(improvement) < 5.0e-2*_dg) {
        // This iteration did not improve much upon the previous
        // Stalling detection only after 4 iterations, to account for
        // ''startup problems''
          if (_debugLevel>3) {
            cout<<"**"<<endl;
          }
          _badIters++;
        } else if (improvement < 0) {
          _veryBadIters++; 
        } else {
          //TODO slingergedrag
          _badIters=0;
        }

        if (_badIters>=maxBadIters || _veryBadIters > maxBadIters) {
          if (_debugLevel>3) {
            cout<<"Detected stall"<<endl;
          }
          return STALLED;
        }
      }

      dgxx = _dgx;
      _dgx  = _dg;

      double fronormdiff=0;
      double fronormg=0;
      for (uint ant=0;ant<_nUn;++ant) {
        for (uint cr=0;cr<_nCr;++cr) {
          DComplex diff=_g(ant,cr)-_gold(ant,cr);
          fronormdiff+=abs(diff*diff);
          fronormg+=abs(_g(ant,cr)*_g(ant,cr));
        }
      }
      fronormdiff=sqrt(fronormdiff);
      fronormg=sqrt(fronormg);

      _dg = fronormdiff/fronormg;
      if (_debugLevel>0) {
        _dgs.push_back(_dg);
      }

      if (_dg <= _tolerance) {
        return CONVERGED;
      }

      if (_debugLevel>7) {
        cout<<"Averaged"<<endl;
      }

      for (uint ant=0;ant<_nUn;++ant) {
        for (uint cr=0;cr<_nCr;++cr) {
          _g(ant,cr) = (1-omega) * _g(ant,cr) +
                      omega     * _gold(ant,cr);
        }
      }

      if (!threestep) {
        threestep = (iter+1 >= nomega) ||
            ( max(_dg,max(_dgx,dgxx)) <= 1.0e-3 && _dg<_dgx && _dgx<dgxx);
        if (_debugLevel>7) {
          cout<<"Threestep="<<boolalpha<<threestep<<endl;
        }
      }

      if (threestep) {
        if (sstep <= 0) {
          if (_dg <= c1 * _dgx) {
            if (_debugLevel>7) {
              cout<<"dg<=c1*dgx"<<endl;
            }
            for (uint ant=0;ant<_nUn;++ant) {
              for (uint cr=0;cr<_nCr;++cr) {
                _g(ant,cr) = f1q * _g(ant,cr) +
                            f2q * _gx(ant,cr);
              }
            }
          } else if (_dg <= _dgx) {
            if (_debugLevel>7) {
              cout<<"dg<=dgx"<<endl;
            }
            for (uint ant=0;ant<_nUn;++ant) {
              for (uint cr=0;cr<_nCr;++cr) {
                _g(ant,cr) = f1 * _g(ant,cr) +
                            f2 * _gx(ant,cr) +
                            f3 * _gxx(ant,cr);
              }
            }
          } else if (_dg <= c2 *_dgx) {
            if (_debugLevel>7) {
              cout<<"dg<=c2*dgx"<<endl;
            }
            _g = _gx;
            sstep = 1;
          } else {
            //cout<<"else"<<endl;
            _g = _gxx;
            sstep = 2;
          }
        } else {
          if (_debugLevel>7) {
            cout<<"no sstep"<<endl;
          }
          sstep = sstep - 1;
        }
      }
      return NOTCONVERGED;
    }
  } //# end namespace
}
