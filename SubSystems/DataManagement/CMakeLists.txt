# $Id: CMakeLists.txt 20934 2012-05-15 09:26:48Z schoenmakers $

lofar_package(DataManagement
                DEPENDS Cleanup
                        StorageQueryService
                        ResourceTool)

# supervisord config files
install(FILES
  DataManagement.ini
  DESTINATION etc/supervisord.d)
