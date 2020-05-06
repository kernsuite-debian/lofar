# $Id: CMakeLists.txt 20934 2012-05-15 09:26:48Z schoenmakers $

# TODO 20190122 RAServices is not the correct name for a subsystem. We should change it to SCU.
lofar_package(RAServices
                DEPENDS MAC_Services
                        MoMQueryService
                        MoMutils
                        OTDBtoRATaskStatusPropagator
                        RATaskSpecifiedService
                        RAtoOTDBTaskSpecificationPropagator
                        ResourceAssigner
                        ResourceAssignmentDatabase
                        ResourceAssignmentEditor
                        ResourceAssignmentEstimator
                        ResourceAssignmentService
                        SpecificationServices
                        TBB
                        TBBService
                        TriggerServices
                        TriggerEmailService
                        TaskPrescheduler
                        DataManagement
                        QPIDInfrastructure
                        RAScripts
                        StaticMetaData
                        RACommon
                        ltastorageoverview
                        QA_Service
                        MessageLogger)

# supervisord config files
install(FILES
  RAServices.ini
  DESTINATION etc/supervisord.d)
