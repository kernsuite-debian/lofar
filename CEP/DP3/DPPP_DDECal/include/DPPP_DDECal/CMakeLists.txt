# $Id: CMakeLists.txt 30990 2015-02-12 12:27:47Z diepen $

# List of header files that will be installed.
set(inst_HEADERS
  Register.h DDECal.h MultiDirSolver.h H5Parm.h
  Constraint.h KernelSmoother.h ScreenConstraint.h TECConstraint.h
  PiercePoint.h Matrix2x2.h PieceWisePhaseFitter.h
  RotationConstraint.h RotationAndDiagonalConstraint.h
  SmoothnessConstraint.h )

# Create symbolic link to include directory.
execute_process(COMMAND ${CMAKE_COMMAND} -E create_symlink
  ${CMAKE_CURRENT_SOURCE_DIR}
  ${CMAKE_BINARY_DIR}/include/${PACKAGE_NAME})

# Install header files.
#install(FILES ${inst_HEADERS} DESTINATION include/${PACKAGE_NAME})
