#ifndef MULTI_DIR_SOLVER_H
#define MULTI_DIR_SOLVER_H

#ifdef AOPROJECT
#include "PhaseFitter.h"
#include "Constraint.h"
#define UPTR std::unique_ptr
#else
#include <DPPP/PhaseFitter.h>
#include <DPPP_DDECal/Constraint.h>
#define UPTR std::auto_ptr
#endif

#include <armadillo>

#include <complex>
#include <vector>
#include <memory>

class MultiDirSolver
{
public:
  typedef std::complex<double> DComplex;
  typedef std::complex<float> Complex;
  
  struct SolveResult {
    size_t iterations, constraintIterations;
    std::vector<std::vector<Constraint::Result> > _results;
  };
  
  MultiDirSolver();
  
  void init(size_t nAntennas, size_t nDirections, size_t nChannels, 
            const std::vector<int>& ant1, const std::vector<int>& ant2);
  
  // data[i] is een pointer naar de data voor tijdstap i, vanaf die pointer staat het in volgorde als in MS (bl, chan, pol)
  // mdata[i] is een pointer voor tijdstap i naar arrays van ndir model data pointers (elk van die data pointers staat in zelfde volgorde als data)
  // solutions[ch] is een pointer voor channelblock ch naar antenna x directions oplossingen.
  SolveResult processScalar(std::vector<Complex*>& data, std::vector<std::vector<Complex* > >& modelData,
    std::vector<std::vector<DComplex> >& solutions, double time) const;
  
  /**
   * Same as @ref processScalar(), but solves full Jones matrices.
   * @param data als in @ref processScalar()
   * @param modelData als in @ref processScalar()
   * @param solutions An array, where @c solutions[ch] is a pointer to channelblock @c ch, that points to
   * antenna x directions solutions. Each solution consists of 4 complex values forming the full Jones matrix.
   */
  SolveResult processFullMatrix(std::vector<Complex *>& data,
    std::vector<std::vector<Complex *> >& modelData,
    std::vector<std::vector<DComplex> >& solutions, double time) const;
  
  void set_phase_only(bool phaseOnly) { _phaseOnly = phaseOnly; }
  
  void set_channel_blocks(size_t nChannelBlocks) { _nChannelBlocks = nChannelBlocks; }
  
  size_t max_iterations() const { return _maxIterations; }
  void set_max_iterations(size_t maxIterations) { _maxIterations = maxIterations; }
  
  void set_accuracy(double accuracy) {
    _accuracy = accuracy;
  }
  void set_constraint_accuracy(double constraintAccuracy) {
    _constraintAccuracy = constraintAccuracy;
  }
  void set_step_size(double stepSize) { _stepSize = stepSize; }
  
  void add_constraint(Constraint* constraint) { _constraints.push_back(constraint); }
  
private:
  void performScalarIteration(size_t channelBlockIndex,
                             std::vector<arma::cx_mat>& gTimesCs,
                             std::vector<arma::cx_vec>& vs,
                             const std::vector<DComplex>& solutions,
                             std::vector<DComplex>& nextSolutions,
                             const std::vector<Complex *>& data,
                             const std::vector<std::vector<Complex *> >& modelData) const;
                             
  void performFullMatrixIteration(size_t channelBlockIndex,
                             std::vector<arma::cx_mat>& gTimesCs,
                             std::vector<arma::cx_mat>& vs,
                             const std::vector<DComplex>& solutions,
                             std::vector<DComplex>& nextSolutions,
                             const std::vector<Complex *>& data,
                             const std::vector<std::vector<Complex *> >& modelData) const;

  void makeStep(const std::vector<std::vector<DComplex> >& solutions,
    std::vector<std::vector<DComplex> >& nextSolutions) const;
                
  void makeSolutionsFinite(std::vector<std::vector<DComplex> >& solutions, size_t perPol) const;
                
  /**
   * Assign the solutions in nextSolutions to the solutions.
   * @returns whether the solutions have been converged.
   */
  bool assignSolutions(std::vector<std::vector<DComplex> >& solutions,
    std::vector<std::vector<DComplex> >& nextSolutions, bool useConstraintAccuracy) const;
                             
  size_t _nAntennas, _nDirections, _nChannels, _nChannelBlocks;
  std::vector<int> _ant1, _ant2;
  
  // Calibration setup
  size_t _maxIterations;
  double _accuracy, _constraintAccuracy;
  double _stepSize;
  bool _phaseOnly;
  std::vector<Constraint*> _constraints;
};

#endif
