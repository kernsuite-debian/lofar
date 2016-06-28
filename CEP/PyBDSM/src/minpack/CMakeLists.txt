# $Id: CMakeLists.txt 20828 2012-05-02 11:24:10Z loose $

# Always use -fPIC to enable linking with shared libs.
add_library(minpack STATIC lmder.f lmpar.f qrfac.f qrsolv.f enorm.f dpmpar.f)
set_target_properties(minpack PROPERTIES COMPILE_FLAGS "-fPIC")

