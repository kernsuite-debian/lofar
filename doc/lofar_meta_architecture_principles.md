#LOFAR Meta Architecture Principles {#lofar_meta_architecture_principles}

##Architecture Principles
  * Code should have unit tests.
  * Services should have tests that cover all functions.
  * Code should mostly be in Python, C++ or Java.
  * Communication between components should use the [LOFAR Qpid framework](@ref qpid_main).
  * Services should be combined into a single executable when this makes sense to simplify monitoring and management.
  * The [LOFAR Definition of Started/Done](@ref rrr_dos_dod) should be followed.
 
###Note
The initial version of this was copied from [RRR Architecture principles](https://www.astron.nl/lofarwiki/doku.php?id=rrr:architecture_principles)