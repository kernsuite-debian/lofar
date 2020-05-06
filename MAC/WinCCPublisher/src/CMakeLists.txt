include(LofarPackageVersion)

lofar_add_bin_program(winccpublisher
    WinCCPublisherMain.cc 
    Program.cc
    ConfigReaderImpl.cc
    PublisherResources.cc
    ToBusImpl.cc)

