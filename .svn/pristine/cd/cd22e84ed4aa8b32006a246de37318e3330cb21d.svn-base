
Generic Pipeline
================

This Chapter will explain how to define a pipeline for the execution with the Lofar Pipeline Framework. For this purpose a Generic Pipeline has been created which can be configured to integrate user programs in a flexible way.

Introduction
------------
The Pipeline Framework is used for automated processing on the CEP cluster systems for example for the MSSS pipelines. Writing these pipelines is complicated and requires a lot of knowledge of the framework itself and some programming skills.

The generic pipeline is a pipeline based on that system. It helps users with the design and execution of their own workflow without the need to understand the underlying system. For a pipeline the user should organize the work into building blocks. Typically you want to use existing blocks that do standard operations like Calibrate-Stand-Alone or DPPP or the AWImager. Work that has to be done in preparation or post processing for these operations can and should be implemented as additional steps for the pipeline.

The advantage is that the user does not need to manage any kind of multiprocessing for data parallel operations. Input and output filenames of steps are mostly hidden and can be managed in a consistent way. Parameters can be reduced to a minimum with different sets of default parsets for every step. Integration of other peoples steps and reusing existing work are one of the primary goals of the generic pipeline. A users pipeline can run on a single workstation and in a cluster environment without the need to change the pipeline parset or to program process management.

In an ideal case there are enough predefined possible steps for the user to choose from so that defining a pipeline comes down configuring a minimal set of program arguments.

Steps and arguments to the steps are defined in a parset file. This parset is then the argument for the ``genericpipeline.py``. The pipelines name will be the first part of the parsets name ``mypipeline.parset``. Log files will be tracked under that name and have to be deleted along with the working directory when the pipeline should be restartet from the beginning.

Usage
-----
The generic pipeline is part of the Lofar Software Package and is basically a runnable python script. The pipeline definition is written in a parset file. After you have loaded the Lofar environment it can be run with the command:
::

	> genericpipeline.py <parset-file> [options]

Where possible options are ``-d`` for debug logging and ``-c <config-file>`` to use a specific pipeline configuration file.

Quick Start
-----------

Before you can use the genericpipeline you need to customize the configuration 
file:

	* Copy ``$LOFARROOT/share/pipeline/pipeline.cfg`` to someplace in your ``$HOME`` and open it in an editor.
	* It starts with a section **[DEFAULT]**, in there you need to edit two entries:
	
		#. **runtime\_directory**: This is the directory where the pipeline puts logfiles, parsets, the status of successful steps etc. Set this to a directory in your ``$HOME``, e.g. ``/home/<username>/PipelineExample/runtime``
		#. **working\_directory**: This is the directory where the processed data of the intermediate and final steps is put. Set this to a directory on your data disk, e.g. ``/data/scratch/<username>/PipelineExample``
	
	* In case you do not run it on a cluster, you need to tell the pipeline to start the processes on the local machine:
		
			#. Search for the section **[cluster]**, set the entry **clusterdesc** to: ``(lofarroot)s/share/local.clusterdesc``
			#. Add a section ``[remote]`` by adding the following lines: 
					::

						[remote]
						method = local 
						max_per_node = <NumCPUCores>
					
			If there is already another section **[remote]**, then remove that.
		
	* The pipeline framework contains a number of parallel processing schemes for working on multi-node clusters. Ask you local sysadmin for advice.

Once the pipeline is configured you need a pipeline-parset. A simple example 
would be: 
::


  # Pipeline for running NDPPP on all files in a directory

  #variable parameters
  #path to the directory where we are looking for the input data
  ! input_path = /data/scratch/dummyuser/test-in
  # path to the parset
  ! ndppp_parset = /home/dummyuser/parsets/NDPPP-preproc-parset.proto

  pipeline.steps=[createmap,ndppp]

  #Step 1: search for all measurement sets in one directory and generate a mapfile
  createmap.control.kind            =   plugin
  createmap.control.type            =   addMapfile
  createmap.control.cmdline.create  =   mapfile_from_folder
  createmap.control.mapfile_dir     =   input.output.mapfile_dir  #this is the name that the mapfile will have
  createmap.control.filename        =   input_data.mapfile
  createmap.control.folder          =   {{ input_path }}          #this references to the path we defined above

  #Step 2: run NDPPP with a given parset on all files that the previous step found
  ndppp.control.type                   =  dppp
  ndppp.control.parset                 =  {{ ndppp_parset }}      #this references to the parset we defined above
  ndppp.control.max_per_node           =  4                       #run 4 instances of NDPPP in parallel
  ndppp.control.environment            =  {OMP_NUM_THREADS: 6}    #tell NDPPP to use only 6 threads
  ndppp.argument.msin                  =  createmap.output.mapfile


Pipeline configuration
----------------------

The configuration of the Pipeline Framework is mainly done in the two files ``pipeline.cfg`` and ``tasks.cfg``. The ``pipeline.cfg`` contains general settings like job and working directories and where your pipeline installation and task configuration resides. The ``tasks.cfg`` contains the steps that can be used in a pipeline. If you want to use your own configuration the ``pipeline.cfg`` should be an argument to the pipeline call.

Copy the file ``pipeline.cfg`` from your installation. In a Lofar Framework installation the file can be found in ``LOFARROOT/share/pipeline/pipeline.cfg``. In this file you can configure the basic setup of the Pipeline Framework. You might want to modify the ``runtime_directory`` and the ``working_directory`` especially if you are not the only one using that machine. Those are a little bit ambiguous but generally the ``runtime_directory`` contains parsets, mapfiles, logfiles automatically generated for running the pipeline system. The ``working_directory`` is where the actual data products are being placed and the directory from where the individual programs are called. So look there for any temporary data you would expect. It is fine to set both parameters to point to the same directory and have everything in one place.

If you want to add your own operations to the generic pipeline some additional configuration is necessary. In the ``pipeline.cfg`` you have to add to the list of ``task_files`` your own ``tasks.cfg``. See the next section for a description of such a file. In the standard install only standard operations are defined and of course only programs that come with the Lofar Software Stack.

If you want to run a pipeline on your local machine you need to add the following to the configuration:
::

	[remote]
	method       = local
	max_per_node = 1

The ``max_per_node`` value can be overwritten on a step by step bases and indicates how many subprocesses of that step are started concurrently. This number depends on the workload a specific step puts on the system.

The more advanced user might need to modify the underlying scripts that execute the job. You can use your own master and node scripts without having access to the install directories of the pipeline. Edit the ``recipe_directories`` in the ``pipeline.cfg`` and point it to the folder where you have your ``master``, ``node`` and ``plugin`` directories.

Task definitions
----------------
Possible steps for a pipeline are configured as a task in the ``tasks.cfg`` file. The format is comparable to the python configparser class. That means the name of the task is given in brackets followed by parameters for this task. Example:
::

	[dppp]
	recipe      = executable_args
	executable  = (lofarroot)s/bin/NDPPP
	args_format = lofar
	outputkey   = msout

This task is now accessible in a parset:
::

	dppp_step.control.type = dppp
	dppp_step.argument.msin...

The ``recipe`` variable is mandatory and needs to be the name of a master script. Historically there are master and node scripts implementing functionality. The generic pipeline only uses one master script, the ``executable_args``. The old ones are still usable but you will most likely never use them. The ``outputkey = msout`` means that the automatically generated file name from the step will be mapped to the argument ``msout``. So now your dppp step has a default argument ``dppp_step.argument.msout=<inputfile>.dppp_step``.

Node scripts handle the actual process call. Most of the time the node script version of ``executable_args`` will suffice and does not need to be specified. A second useful node script loads python files and runs their ``main()`` method. Meaning you have to have a function called ``main()``. In this way you can store parameters in the pipeline context and use them in later steps. Fore more information on python plugins please look at the feature section. A minimal task for your own python plugin would look like this:
::

	[mypythontask]
	recipe      = executable_args
	nodescript  = python_plugin
	executable  =/path/to/my_python_script.py

Now the task can be used in the parset by simply doing the following:
::

	my_python_step.control.type = mypythontask
	my_python_step.argument...


Mapfiles
--------
Mapfiles are the data descriptors of the pipeline framework. Only primitive functions to create and manipulate mapfiles are available at the moment as it is subject of development (see keyword section).

Contents of a mapfile is the hostname of the machine where your data is, the path to your input data and a field that lets you specify whether to skip the data or not (mark it as bad data).
A mapfile holds entries for all the measurement sets you want to use. 

For every entry in a mapfile a compute job will be created. With the ``max_per_node`` parameter in the step configuration you can specify how many of those should run at the same time on one node. The content of a mapfile is a python dictionary:
::

	{'host': 'localhost', file: '/path/to/MS', 'skip': False}

Only primitive functions to create and manipulate mapfiles are available at the moment as it is subject of development. Right now plugins are used  (see keyword section on createMapfile plugin)

Pipeline
--------
Parset
^^^^^^
The pipeline itself will be described in a parset. The steps are given as a list. Other general parameters for the pipeline are the optional path to a plugins directory and an existing mapfile. The beginning of a parset looks like this:
::

	pipeline.steps      = [step1,step2,step3,...]
	pipeline.pluginpath = plugins                     # optional
	pipeline.mapfile    = /path/to/your_data.mapfile  # optional

This steplist determines the order of execution. In what order the steps are implemented in the parset does not matter. However to every rule there is an exception. When using more than one mapfile in a step, the file entries in the first one will be used for the automatic naming scheme. Make sure your first mapfile contains individual names (measurement sets for example). Otherwise you might overwrite your results.

To prevent the steplist from getting too long you can use sublists like this:

::

    pipeline.steps           = [step1,substeps,step3,...]
    pipeline.steps.substeps  = [substep1,substep2,...]

Steps
^^^^^
Step names are arbitrary but have to be unique in one pipeline. Step options are organized into two blocks. The first to configure the task and the second to give arguments to program that is called. The keyword for the task options is ``control`` and the step arguments is ``argument``. Any options given here overwrite the ones in the ``tasks.cfg``. If you already have configured all task options in your ``tasks.cfg`` you only need to specify what type of task this step should be. Minimum general usage:
::

	step.control.type   = taskname
	step.argument.flags = [command,line,-flags]

A more specific example:
::

	step.control.type            = dppp
	step.control.args_format     = lofar
	step.control.max_per_node    = 4
	step.control.environment     = {OMP_NUM_THREADS: 8, SOME_OTHER: env_variable}
	step.argument.steps          = [c]
	step.argument.c.type         = gaincal
	step.argument.c.usebeammodel = True
	.
	.
	.

Parameters specified after ``argument`` are passed to the program in a "long option" kind of way. In the example above ``args_format = lofar`` was specified which means the argument will be given as:
::

	c.type gaincal

Default is the posix way of giving long options which would look like:
::

	--c.type=gaincal

For more option descriptions look at the complete list of keywords for the ``executable_args`` task. There are more things a step could be other than a task. For this the keyword ``step.control.kind`` is used. Please see the "Features" section for details.

Features
^^^^^^^^

**Plugins**

For quick hacking of functionality plugins can also be used as steps. They are simple python scripts but in contrast to the ``pythontask`` are not tracked by the framework. Also plugins are only executed once and for every entry in a mapfile as this input is not mandatory. Their standard location is in the recipes directory. An extra ``pipelinepath`` can be specified in the pipeline parset. This location will then also be searched when trying to load the plugins.

Self written plugins must contain the method called ``plugin_main`` which can have a dictionary as return value:
::

	def plugin_main(args, **kwargs):
		result = {}
		<some code>
		return result

Plugins were introduced for development purposes and should be removed in the future. But for now they are used to create and manipulate mapfiles.

**Internal dictionary**

The pipeline holds an internal results dictionary. Entries are dictionaries themselves. Every step can put his own dictionary in there to pass variables down the pipeline. The default dictionary after starting a pipeline has the same name as the pipeline and has all key value pairs from the ``pipeline.cfg`` as entries. You can also access the following: ``job_dir``, ``parset_dir``, ``mapfile_dir`` and ``mapfile`` if it was given with ``pipeline.mapfile``.

Normal steps chosen from the tasks list always put a dictionary in the results with their output mapfile. It either has the values of its input or the filenames of the computed output. The name of the dictionary is the steps name.

A ``python_plugin`` task can write a dictionary to the results dictionary by simply returning an object of that type.

This output dictionary can be accessed with a special notation ``stepname.output.variable`` useable in any argument. On the left is the stepname of which you want the output from and on the right the name of the variable that was chosen in that steps dictionary. Most of the time you only want to access mapfiles from previous steps. Lets say you created a mapfile in a step called ``createmap``. An example of getting  that mapfile in a later step would be:
::

	mystep.argument.inputfile = createmap.output.mapfile

Notice that the mapfile represents the input file. If written like this the step will be executed for every "file" entry in the mapfile.

**String replacement syntax**

Since you want your step description ordered one after the other but maybe have used arguments that other users need to edit a Replacement Syntax as a convenience feature has been added. This means that you can use placeholders in your step arguments and have the real argument at the top of parset for easier access. The syntax for the placeholder is:
::

	pipeline.replace.my_awimager = /path/to/my/awimager
	.
	.
	.
	myAWImagerStep.control.executable = {{ my_awimager }}

Also possible is a partial string replacement in the argument like so:
::

	pipeline.replace.my_awimager_path = /path/to/my/
	.
	.
	.
	myAWImagerStep.control.executable = {{ my_awimager_path }}awimager

Notice the trailing slash on the path and no space after the curly brackets. The space inside the brackets around the variable is necessary.
An alternative syntax to define the replacement string is to use an exclamation mark like in the popular python package jinja2:
::

    ! my_awimager = /path/to/my/awimager

This is just a different way of writing. The first version is more in line with the usual way of writing parsets.

It is also possible to use environment variables in the replacement value (from version 2.18 onwards).
::

    ! my_awimager = $HOME/local/bin/awimager

**Python Plugins**

A way of using your own scripts within the pipeline framework is taking advantage of the python plugin mechanism. The script only needs to have a function called ``main()``. Any arguments you define in the step have to be handled as arguments of this main function. Lets look at an example where we define a step to be a python plugin:
::

	toystep.control.type       = pythonplugin
	toystep.control.executable = /path/to/my/script.py
	toystep.argument.flags     = previousstep.output.previousstep.mapfile    # a positional argument with output filenames from a previous step
	toystep.argument.optional  = 6      # some more arguments
	toystep.argument.threshold = 4      # we want to have in the script

Now the script would look something like this:
::

	def main(positional, optional=0, passthrough=0):
		outdict = {}
		print 'File name: ', str(positional)
		
		# cast to types is a good idea/needed because parsets only work on strings
		derivedval = int(optional) / 2
		
		# names in outdict get saved as 'optionalhalf.mapfile' and 'threspix.mapfile'
		outdict['optionalhalf'] = derivedval
		outdict['threshold'] = passthrough
		
		return outdict

You can of course compute values depending on the input data. The different results will be saved in the output mapfiles and are associated to the data in this way for later use. A next step might use your output like this:
::

	nextstep.control.type                   = another_task
	nextstep.argument.needed_computed_value = toystep.output.optionalhalf.mapfile
	nextstep.argument.some_other_value      = toystep.output.threshold.mapfile

This enables you to write simple scripts which can be tested on a single measurement set. Within the pipeline framework the script can then operate on the whole observation.

**Loops**

It is possible to loop steps. A loop is a different kind of step and contains a list of steps:
::

	loopme.control.kind      = loop
	loopme.control.type      = conditional
	loopme.control.loopcount = [int]
	loopme.control.loopsteps = [loopstep1,loopstep2,loopstep3,...]

The steps will be looped until one of the steps puts in its output dictionary a ``'break': True`` or until the loop counter reaches the specified integer ``loopcount``. So maybe as last step of your list inside the loop you want a step that checks a break condition and outputs its value.

**Subpipelines**

A subpipeline is like the loop another kind of step. This construct is for the case that you have a working set of steps and do not want to clutter your parset or want to have a structure with individual parsets for individual functionality. You can hand over mapfiles to a subpipeline and access it with the output keyword mechanism ``subpipeline_name.output.mapfile``. Arguments you give to the subpipeline will be handled as string replacements (see paragraph above). This enables you to write parsets that can be run individually or as subpipelines without any change to the parset.

The steps that will be added from the subpipeline will be prefixed with the subpipeline name. This makes it possible to have step definitions with the same name in the master parset and in the subpipeline parset without creating any conflicts. The following would be an example of a subpipeline step and the beginning of the subpipeline. The step:
::

	subpipe.control.kind       = pipeline
	subpipe.control.type       = my_subpipeline.parset
	subpipe.control.mapfile_in = some_previous_step.output.mapfile


Syntax and Keywords
^^^^^^^^^^^^^^^^^^^
ToDo: longish tables of possible keywords and their explanation for createMapfile plugin, executable\_args task, subpipeline controls etc.

List of possible pipeline parameters

+-------------------------+-------------+-------------------------------------------------------------------------------------------------------+
|Parameter                |Type         |Description                                                                                            |
+=========================+=============+=======================================================================================================+
|**Pipeline**             |             |                                                                                                       |
+-------------------------+-------------+-------------------------------------------------------------------------------------------------------+
|pipeline.steps           |list         |The list of steps the pipeline will execute                                                            |
+-------------------------+-------------+-------------------------------------------------------------------------------------------------------+
|pipeline.steps.<sublist> |list         |This list will replace the <sublist> in the steplist defined in the argument above.                    |
+-------------------------+-------------+-------------------------------------------------------------------------------------------------------+
|pipeline.pluginpath      |string       |(optional) The folder that contains additional plugins.                                                |
+-------------------------+-------------+-------------------------------------------------------------------------------------------------------+
|pipeline.mapfile         |string       |(optional) An existing mapfile that is then available in the input dictionary                          |
+-------------------------+-------------+-------------------------------------------------------------------------------------------------------+
|pipeline.replace.<arg>   |string       |(optional) Will search the rest of the parset for {{ <arg> }} and will replace it with the value       |
+-------------------------+-------------+-------------------------------------------------------------------------------------------------------+
|                         |             |You can also use the jinja2 style with an exclamation mark (! <arg>)                                   |
+-------------------------+-------------+-------------------------------------------------------------------------------------------------------+
|                         |             |The value may contain environment variables that will be parsed from the system environment.           |
+-------------------------+-------------+-------------------------------------------------------------------------------------------------------+
|**Steps**                |             |                                                                                                       |
+-------------------------+-------------+-------------------------------------------------------------------------------------------------------+
|<step>.control.type      |string       |What task should be executed by this step.                                                             |
+-------------------------+-------------+-------------------------------------------------------------------------------------------------------+
|<step>.control.<arg>     |             |Any control argument to configure the chosen type of step.                                             |
|                         |             |For executable_args see the list below.                                                                |
+-------------------------+-------------+-------------------------------------------------------------------------------------------------------+
|<step>.argument.flags    |list         |This optional list will be passed as command line arguments to the executable.                         |
+-------------------------+-------------+-------------------------------------------------------------------------------------------------------+
|<step>.argument.parset   |string       |You can specifiy a parset file here with parameters. Usually specified in tasks or the control block.  |
+-------------------------+-------------+-------------------------------------------------------------------------------------------------------+
|<step>.argument.<arg>    |             |Any long option argument for the executable.                                                           |
+-------------------------+-------------+-------------------------------------------------------------------------------------------------------+
|**Loop Step**            |             |**<step>.control.kind = loop**                                                                         |
+-------------------------+-------------+-------------------------------------------------------------------------------------------------------+
|<step>.control.loopsteps |list         |The list of steps for this loop.                                                                       |
+-------------------------+-------------+-------------------------------------------------------------------------------------------------------+
|<step>.control.loopcount |int          |Number of times the loop will run.                                                                     |
+-------------------------+-------------+-------------------------------------------------------------------------------------------------------+
|**Subpipeline**          |             |**<step>.control.kind = pipeline**                                                                     |
+-------------------------+-------------+-------------------------------------------------------------------------------------------------------+
|<step>.control.type      |             |The parset of the pipeline to run.                                                                     |
+-------------------------+-------------+-------------------------------------------------------------------------------------------------------+
|<step>.control.mapfile_in|string       |If you want to start the subpipeline with a specific mapfile.                                          |
+-------------------------+-------------+-------------------------------------------------------------------------------------------------------+
|<step>.argument.<arg>    |             |The <arg> and <value> of the arguments will be used in the subpipeline string replacement mechanism    |
+-------------------------+-------------+-------------------------------------------------------------------------------------------------------+
|**Plugins**              |             |**<step>.control.kind = plugin**                                                                       |
+-------------------------+-------------+-------------------------------------------------------------------------------------------------------+
|<step>.control.arguments |list         |List of arguments that will be passed as args to the plugin                                            |
+-------------------------+-------------+-------------------------------------------------------------------------------------------------------+
|<step>.control.<arg>     |             |Arguments that will passed as \*\*kwargs to the plugin                                                 |
+-------------------------+-------------+-------------------------------------------------------------------------------------------------------+

Defining a task with the master script ``executable_args``. The following are the possible control keys (<step>.control.<parameter>)

+----------------------+-------------+---------------+---------------------------------------------------------------------------------------+
|Parameter             |Type         | Default       |Description                                                                            |
+======================+=============+===============+=======================================================================================+
|**Mandatory**         |             |               |                                                                                       |
+----------------------+-------------+---------------+---------------------------------------------------------------------------------------+
|[<task_name>]         |string       |               |The header that gives the step its name (the type value of the step in the parset).    |
+----------------------+-------------+---------------+---------------------------------------------------------------------------------------+
|recipe                |string       |               |The master script we want to call. Needs to be ``executable_args``                     |
+----------------------+-------------+---------------+---------------------------------------------------------------------------------------+
|executable            |string       |               |Path to the program that this task will execute.                                       |
+----------------------+-------------+---------------+---------------------------------------------------------------------------------------+
|**Optional**          |             |               |                                                                                       |
+----------------------+-------------+---------------+---------------------------------------------------------------------------------------+
|nodescript            |string       |executable_args|                                                                                       |
+----------------------+-------------+---------------+---------------------------------------------------------------------------------------+
|parsetasfile          |boolean      |False          |Should the arguments of the step be passed as a parset file to the program?            |
+----------------------+-------------+---------------+---------------------------------------------------------------------------------------+
|nthreads              |int          |8              |Short argument for setting OMP_NUM_THREADS as environment variable.                    |
+----------------------+-------------+---------------+---------------------------------------------------------------------------------------+
|parset                |string       |               |Path to a parset that contains the arguments for this task.                            |
+----------------------+-------------+---------------+---------------------------------------------------------------------------------------+
|arguments             |list         |               |List of arguments for the task.                                                        |
+----------------------+-------------+---------------+---------------------------------------------------------------------------------------+
|mapfile_in            |string       |               |The mapfile for this task. Usually contains the input files for the program            |
+----------------------+-------------+---------------+---------------------------------------------------------------------------------------+
|mapfiles_in           |list         |               |A list of mapfiles if you have multiple sources of input for this task.                |
+----------------------+-------------+---------------+---------------------------------------------------------------------------------------+
|inputkey              |string       |               |The key in the arguments that gets the entries from the mapfile as value.              |
+----------------------+-------------+---------------+---------------------------------------------------------------------------------------+
|inputkeys             |string list  |               |The keys for multiple input mapfiles.                                                  |
+----------------------+-------------+---------------+---------------------------------------------------------------------------------------+
|mapfile_out           |string       |               |Create your own mapfile with outputnames if you want tospecify them yourself.          |
+----------------------+-------------+---------------+---------------------------------------------------------------------------------------+
|mapfiles_out          |list         |               |Same as above for multiple outputs (imagers for example)                               |
+----------------------+-------------+---------------+---------------------------------------------------------------------------------------+
|outputkey             |string       |               |The key in the arguments that gets the entries from the output mapfile as value.       |
+----------------------+-------------+---------------+---------------------------------------------------------------------------------------+
|outputkeys            |string list  |               |The keys for multiple output mapfiles.                                                 |
+----------------------+-------------+---------------+---------------------------------------------------------------------------------------+
|skip_infile           |boolean      |False          |Do not pass the input files to the program. Execute it for every entry in the mapfile  |
+----------------------+-------------+---------------+---------------------------------------------------------------------------------------+
|skip_outfile          |boolean      |False          |Do not produce output files.                                                           |
+----------------------+-------------+---------------+---------------------------------------------------------------------------------------+
|inplace               |boolean      |False          |Use input names for the output names. Manipulate files inplace.                        |
+----------------------+-------------+---------------+---------------------------------------------------------------------------------------+
|outputsuffixes        |list         |               |List of suffixes that the program adds to the output filename (useful for imagers).    |
+----------------------+-------------+---------------+---------------------------------------------------------------------------------------+
|parsetasfile          |boolean      |False          |Parset given to node scripts is a positional argument or content are named arguments.  |
+----------------------+-------------+---------------+---------------------------------------------------------------------------------------+
|stepname              |string       |               |For custom nameing the result. Default is the stepname from the pipeline parset.       |
+----------------------+-------------+---------------+---------------------------------------------------------------------------------------+
|max_per_node          |int          |               |How many times should this program run on one node.                                    |
+----------------------+-------------+---------------+---------------------------------------------------------------------------------------+
|environment           |dict         |               |Add environment variables formatted as a python dictionary (number of threads for ex.).|
+----------------------+-------------+---------------+---------------------------------------------------------------------------------------+
|error_tolerance       |boolean      |True           |Controls if the program exits on the first error or continues with succeeded MS.       |
+----------------------+-------------+---------------+---------------------------------------------------------------------------------------+

List of available tasks

+----------------------+-------------+-------------+---------------------------------------------------------------------------------------+
|Task                                                                                                                                      |
+----------------------+-------------+-------------+---------------------------------------------------------------------------------------+
|Parameter             |Type         | Default     |Description                                                                            |
+======================+=============+=============+=======================================================================================+
|recipe                |string       |             |Option only used in the tasks.cfg for defining the master recipe to use for the task.  |
+----------------------+-------------+-------------+---------------------------------------------------------------------------------------+
|kind                  |string       |recipe       |Tell the pipeline the kind of step [recipe, plugin, loop, pipeline].                   |
+----------------------+-------------+-------------+---------------------------------------------------------------------------------------+
|type                  |string       |             |If kind is recipe specify which task from the tasks.cfg are we going to use            |
+----------------------+-------------+-------------+---------------------------------------------------------------------------------------+


Cookbook example
^^^^^^^^^^^^^^^^

This is a pipeline version of the Lofar Imaging Cookbook practical example from chapter thirteen:
::

    # Pipeline that runs the processing steps from the LOFAR Cookbook tutorial.

    pipeline.steps=[finddata, flag_compress, calibrate1, flagstation, calibrate2, image3c295, make_concatmap, combineMS, reCalibrate, imageCombined, subtract3C295, copySubtracted, parmDBmap, applycal, imageField]

    #variable parameters
    pipeline.replace.input_path = /globaldata/COOKBOOK/Tutorial/3c295/data/L74759/
    pipeline.replace.flag_compress_parset = /globaldata/COOKBOOK/Tutorial/3c295/parsets/hba/NDPPP_HBA_preprocess.parset
    pipeline.replace.bbs_calibration_parset = /globaldata/COOKBOOK/Tutorial/3c295/parsets/hba/bbs.parset
    pipeline.replace.calibrator_skymodel = /globaldata/COOKBOOK/Tutorial/3c295/models/3C295TWO.skymodel
    pipeline.replace.bbs_subtraction_parset = /globaldata/COOKBOOK/Tutorial/3c295/parsets/hba/bbs_subtract3c295.parset
    pipeline.replace.bbs_correct_parset = /globaldata/COOKBOOK/Tutorial/3c295/parsets/hba/bbs_correct3c295.parset

    # 1st step
    # find the data that we want to process and create a mapfile
    finddata.control.kind            =   plugin                # plugin -> short, non-parallel step
    finddata.control.type            =   createMapfile         # generate a new mapfile
    finddata.control.method          =   mapfile_from_folder   # look for all files in a given directory
    finddata.control.folder          =   {{ input_path }}          # directory in which to look for the data
    finddata.control.mapfile_dir     =   input.output.mapfile_dir  # put the mapfile into the runtime directory
    finddata.control.filename        =   finddata.mapfile          # name of the generated mapfile
    finddata.control.pattern         =   L*_uv.MS                  # use only files that match this pattern

    # 2nd step:
    # run NDPPP on all files, this will generate new files with the compressed data
    flag_compress.control.type          =  dppp                        # run ndppp
    flag_compress.control.parset        =  {{ flag_compress_parset }}  # name of the parset to use
    flag_compress.control.max_per_node  =  4                           # run at most 4 NDPPP processes per node
    flag_compress.control.environment   =  {OMP_NUM_THREADS: 8}        # tell NDPPP to use at most 8 threads per process
    flag_compress.argument.msin         =  finddata.output.mapfile     # process the data in the mapfile that was produced in the finddata step

    # 3rd step
    # calibrate the data with BBS
    calibrate1.control.type          =  python-calibrate-stand-alone  # run BBS on single files
    calibrate1.control.max_per_node  =  20                            # run at most 20 BBS processes per node
    calibrate1.argument.force        =  True                          # force replaceing of parmDB and skyDB
    calibrate1.argument.observation  =  flag_compress.output.mapfile  # run on files generated by flag_compress step
    calibrate1.argument.parset       =  {{ bbs_calibration_parset }}  # which parset to use (path specified above)
    calibrate1.argument.catalog      =  {{ calibrator_skymodel }}     # which skymodel to use

    # 4th step:
    # run NDPPP
    # This time without an external parset, specifying everything in here.
    flagstation.control.type          =  dppp                 # run ndppp
    flagstation.control.max_per_node  =  4                    # run at most 4 NDPPP processes per node
    flagstation.control.environment   =  {OMP_NUM_THREADS: 8} # tell NDPPP to use at most 8 threads per process
    flagstation.control.outputkey     =                       # no "outputkey" -> don't generate new outputfiles
    flagstation.argument.msin          =  flag_compress.output.mapfile # run on files generated by flag_compress step
    flagstation.argument.msout         =  .                   # set msout to "." in parset -> update input file
    flagstation.argument.steps         =  [flag]
    flagstation.argument.flag.type     =  preflagger
    flagstation.argument.flag.baseline =  [[RS508HBA,RS509HBA],[RS208HBA,RS509HBA],[CS302HBA*]]

    # 5th step
    # re-calibrate the data with BBS, (exactly like step 3)
    calibrate2.control.type          =  python-calibrate-stand-alone  # run BBS on single files
    calibrate2.control.max_per_node  =  20                            # run at most 20 BBS processes per node
    calibrate2.argument.force        =  True                          # force replaceing of parmDB and skyDB
    calibrate2.argument.observation  =  flag_compress.output.mapfile  # run on files generated by flag_compress step
    calibrate2.argument.parset       =  {{ bbs_calibration_parset }}  # which parset to use (path specified above)
    calibrate2.argument.catalog      =  {{ calibrator_skymodel }}     # which skymodel to use

    # 6th step
    # make a clean image of the calibrated data with awimager
    # this will run one awimager process for each subband (so two for the tutorial data)
    image3c295.control.type          =  awimager                     # run the awimager
    image3c295.control.max_per_node  =  2                            # run at most 2 awimager processes per node
    image3c295.control.environment   =  {OMP_NUM_THREADS: 10}        # maximum number of parallel threads
    image3c295.argument.ms           =  flag_compress.output.mapfile # run on files generated by flag_compress step
    image3c295.argument.data         =  CORRECTED_DATA               # read from the CORRECTED_DATA column
    image3c295.argument.weight       =  briggs                       # further imaging parameters ...
    image3c295.argument.robust       =  0
    image3c295.argument.npix         =  4096
    image3c295.argument.cellsize     =  5.5arcsec
    image3c295.argument.padding      =  1.2
    image3c295.argument.stokes       =  I
    image3c295.argument.operation    =  mfclark
    image3c295.argument.wmax         =  20000
    image3c295.argument.UVmin        =  0.08
    image3c295.argument.UVmax        =  18
    image3c295.argument.niter        =  1000

    # 7th step
    # make a mapfile that will allow us to concatenate all data-files into one
    make_concatmap.control.kind            =   plugin                        # plugin -> short, non-parallel step
    make_concatmap.control.type            =   createMapfile                 # generate a new mapfile
    make_concatmap.control.method          =   mapfile_all_to_one            # put all files into one entry
    make_concatmap.control.mapfile_in      =   flag_compress.output.mapfile  # name of the input-mapfile
    make_concatmap.control.mapfile_dir     =   input.output.mapfile_dir      # put new mapfile into runtime directory
    make_concatmap.control.filename        =   concat.mapfile                # name of the new mapfile

    # 8th step
    # now combine the MSs with the help of the mapfile from step 7
    combineMS.control.type          =  dppp                   # run ndppp
    combineMS.control.max_per_node  =  1                      # run only one NDPPP process at a time
    combineMS.control.environment   =  {OMP_NUM_THREADS: 10}  # tell NDPPP to use at most 10 threads
    combineMS.argument.msin         =  make_concatmap.output.mapfile  # use the mapfile from the make_concatmap step
    combineMS.argument.msin.datacolumn  =  DATA               # read from the DATA column
    combineMS.argument.steps            =  []                 # don't really do anything with the data
    combineMS.argument.msin.missingdata =  True               # fill missing data with flagged dummy values

    # 9th step
    # calibrate the combined MS (we copied the uncorrected data)
    # nearly the same as step 3 (and step 5), but this time we work on the combined MS and change "CellSize.Freq"
    reCalibrate.control.type          =  python-calibrate-stand-alone  # run BBS on single files
    reCalibrate.control.max_per_node  =  20                            # run at most 20 BBS processes per node
    reCalibrate.argument.force        =  True                          # force replaceing of parmDB and skyDB
    reCalibrate.argument.observation  =  combineMS.output.mapfile      # run on file generated by combineMS step
    reCalibrate.argument.parset       =  {{ bbs_calibration_parset }}  # which parset to use (path specified above)
    reCalibrate.argument.catalog      =  {{ calibrator_skymodel }}     # which skymodel to use
    reCalibrate.argument.Step.solve.Solve.CellSize.Freq = 4            # overwrite one parameter in the BBS parset

    # 10th step
    # make a clean image of the combined data with awimager
    imageCombined.control.type          =  awimager                     # run the awimager
    imageCombined.control.max_per_node  =  1                            # run only one process at a time
    imageCombined.control.environment   =  {OMP_NUM_THREADS: 20}        # maximum number of parallel threads
    imageCombined.argument.ms           =  combineMS.output.mapfile # run on files generated by flag_compress step
    imageCombined.argument.data         =  CORRECTED_DATA               # read from the CORRECTED_DATA column
    imageCombined.argument.weight       =  briggs                       # further imaging parameters ...
    imageCombined.argument.robust       =  0
    imageCombined.argument.npix         =  4096
    imageCombined.argument.cellsize     =  5.5arcsec
    imageCombined.argument.padding      =  1.2
    imageCombined.argument.stokes       =  I
    imageCombined.argument.operation    =  mfclark
    imageCombined.argument.wmax         =  20000
    imageCombined.argument.UVmin        =  0.08
    imageCombined.argument.UVmax        =  18
    imageCombined.argument.niter        =  5000
    imageCombined.argument.threshold    =  0.1Jy

    # 11th step
    # subtract 3C295 from the data
    subtract3C295.control.type          =  python-calibrate-stand-alone  # run BBS on single files
    subtract3C295.control.max_per_node  =  20                            # run at most 20 BBS processes per node
    subtract3C295.argument.force        =  False                         # keep old parmDB and skyDB
    subtract3C295.argument.observation  =  combineMS.output.mapfile      # run on file generated by combineMS step
    subtract3C295.argument.parset       =  {{ bbs_subtraction_parset }}  # which parset to use (path specified above)
    subtract3C295.argument.catalog      =  {{ calibrator_skymodel }}     # which skymodel to use

    # 12th step:
    # run NDPPP on all files, this will generate new files with the compressed data
    copySubtracted.control.type             =  dppp                      # run ndppp
    copySubtracted.control.max_per_node     =  4                         # just my standard...
    copySubtracted.control.environment      =  {OMP_NUM_THREADS: 8}      # just my standard...
    copySubtracted.argument.msin            =  combineMS.output.mapfile  # data that was used in subtract3C295 step
    copySubtracted.argument.msin.datacolumn =  3C295_SUBTRACTED          # read data from the column it was written to
    copySubtracted.argument.steps           =  []                        # don't really do anything with the data

    # 13th step
    # generate a mapfile that points to the parmdb generated in step 9
    # i.e. take the file-name(s) used in step 9 and add "/instrument" to them
    parmDBmap.control.kind        =  plugin                   # plugin, -> short non-parallel step
    parmDBmap.control.type        =  changeMapfile
    parmDBmap.control.mapfile_in  =  combineMS.output.mapfile
    parmDBmap.control.join_files  =  instrument
    parmDBmap.control.newname     =  parmdb.mapfile

    # 14th step
    # Apply old calibration to the data
    applycal.control.type          =  python-calibrate-stand-alone  # run BBS on single files
    applycal.control.max_per_node  =  20                            # run at most 20 BBS processes per node
    applycal.argument.observation  =  copySubtracted.output.mapfile # run on file generated by combineMS step
    applycal.argument.parmdb       =  parmDBmap.output.mapfile      # mapfile with the existing parmDB(s) to use
    applycal.argument.parset       =  {{ bbs_correct_parset }}      # which parset to use
    applycal.argument.catalog      =  {{ calibrator_skymodel }}     # which skymodel to use

    # 15th step
    # make a clean image of the data where we subtracted 3C925 with awimager
    imageField.control.type          =  awimager                     # run the awimager
    imageField.control.max_per_node  =  1                            # run only one process at a time
    imageField.control.environment   =  {OMP_NUM_THREADS: 20}        # maximum number of parallel threads
    imageField.argument.ms           =  copySubtracted.output.mapfile # read input MS here
    imageField.argument.data         =  CORRECTED_DATA               # read from the CORRECTED_DATA column
    imageField.argument.weight       =  briggs                       # further imaging parameters ...
    imageField.argument.robust       =  0
    imageField.argument.npix         =  4096
    imageField.argument.cellsize     =  5.5arcsec
    imageField.argument.padding      =  1.2
    imageField.argument.stokes       =  I
    imageField.argument.operation    =  mfclark
    imageField.argument.wmax         =  20000
    imageField.argument.UVmin        =  0.08
    imageField.argument.UVmax        =  18
    imageField.argument.niter        =  1000
    imageField.argument.threshold    =  30mJy

Installation on Jureca
----------------------
The installation process has changed over the past years and is now relying mostly on the system components. Only install what is not provided by the system.
The current local installation is in the home directory of user ``htb003``. For any mentioned script please look there.
To find out which modules to load use the ``module avail`` command. To get more information about a specific module or to search for specific software use ``module spider``.
The latest install is Lofar version 2.17 and it uses the following modules from the Jureca software stack 2016a:
::

    module load GCC/5.3.0-2.26  ParaStationMPI/5.1.5-1
    module load Python/2.7.11
    module load CMake/3.4.3
    module load Boost/1.60.0-Python-2.7.11
    module load GSL/2.1
    module load HDF5/1.8.16
    module load flex/2.6.0
    module load XML-LibXML/2.0124-Perl-5.22.1
    module load SciPy-Stack/2016a-Python-2.7.11

In addition to these modules the Lofar software is depending on ``cfitsio``, ``wcslib``, ``casacore``, ``casacore-python``(pyrap), ``casarest``, ``aoflagger``. In preperation to compile the rest of the software the following paths are set with a a shell script.
For different versions of the software there are different scripts for loading the appropriate environment. This for example is what the Lofar version 2.17 with Jureca stack2016a looks like:
::

    #!/bin/sh
    export PYTHONPATH=/homea/htb00/htb003/local_jureca_stack2016a/lib/python2.7/site-packages
    export PYTHONPATH=/homea/htb00/htb003/lofar_jureca_2.17_stack2016a/lib/python2.7/site-packages:$PYTHONPATH
    #export PYTHONHOME=/homea/htb00/htb003/local_jureca_stack2016a
    #
    export PATH=/homea/htb00/htb003/local_jureca_stack2016a/bin:$PATH
    export PATH=/homea/htb00/htb003/lofar_jureca_2.17_stack2016a/bin:$PATH
    export PATH=/homea/htb00/htb003/lofar_jureca_2.17_stack2016a/sbin:$PATH
    #
    export LD_LIBRARY_PATH=/homea/htb00/htb003/lofar_jureca_2.17_stack2016a/lib:$LD_LIBRARY_PATH
    export LD_LIBRARY_PATH=/homea/htb00/htb003/lofar_jureca_2.17_stack2016a/lib64:$LD_LIBRARY_PATH
    export LD_LIBRARY_PATH=/homea/htb00/htb003/local_jureca_stack2016a/lib:$LD_LIBRARY_PATH
    export LD_LIBRARY_PATH=/homea/htb00/htb003/local_jureca_stack2016a/lib64:$LD_LIBRARY_PATH
    #
    export LOFAR_BUILD_DIR=/homea/htb00/htb003
    export LOFAR_MAKER=release
    export F77=gfortran
    export FC=gfortran
    export BLAS=/usr/local/software/jureca/Stages/2016a/software/OpenBLAS/0.2.15-GCC-5.3.0-2.26-LAPACK-3.6.0/lib/libopenblas.so
    export LAPACK=/usr/local/software/jureca/Stages/2016a/software/OpenBLAS/0.2.15-GCC-5.3.0-2.26-LAPACK-3.6.0/lib/libopenblas.so
    export LOFARROOT=${LOFAR_BUILD_DIR}/lofar_jureca_2.17_stack2016a
    #
    module load GCC/5.3.0-2.26  ParaStationMPI/5.1.5-1
    module load Python/2.7.11
    module load CMake/3.4.3
    module load Boost/1.60.0-Python-2.7.11
    module load GSL/2.1
    module load HDF5/1.8.16
    module load flex/2.6.0
    module load XML-LibXML/2.0124-Perl-5.22.1
    module load SciPy-Stack/2016a-Python-2.7.11
    export PYTHONSTARTUP=/homea/htb00/htb003/pythonstart
    #
    export CC=/usr/local/software/jureca/Stages/2016a/software/GCCcore/5.3.0/bin/gcc
    export CXX=/usr/local/software/jureca/Stages/2016a/software/GCCcore/5.3.0/bin/g++
    #
    export PKG_CONFIG_PATH=/homea/htb00/htb003/local_jureca_stack2016a/lib/pkgconfig:$PKG_CONFIG_PATH
    # since Lofar 2.15. Flags for dependency building of aoflagger
    # only for building aoflagger
    export LDFLAGS=-L/homea/htb00/htb003/local_jureca_stack2016a/lib
    export CPPFLAGS=-L/homea/htb00/htb003/local_jureca_stack2016a/include
    #
    export GSETTINGS_SCHEMA_DIR=/homea/htb00/htb003/local_jureca/share/glib-2.0/schemas

In addition to this environment there have always been little changes that had to be made to ensure proper compiling and installation of the rest of the software. These changes differed from version to version so that no general solution can be presented.
The follwong only shows one possible guideline.

cfitsio, wcslib
^^^^^^^^^^^^^^^
Nothing special here. Just go the normal configure, make, make install way and add the ``prefix`` option to configure to install the libraries in userspace.

Casacore, Python-Casacore, Casarest
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
In general proceed as instructed on the project webpages for these packages. On Jureca the program ``ccmake``  in contrast to just calling ``cmake`` was used to configure the paths to all required libraries and the proper compiler version.
The cmake configuration files usualy do not find the correct libraries configured by the settings above as they are not in standard directories of fresh system installs.

AOFlagger
^^^^^^^^^
There were problems with the cmake project files. Because none of the software packages are in standard places the "FOUND" value for GTKMM and BOOST_ASIO might have to be set to true in the CMakeLists file in order to compile everything.
Not sure if this problem exists in the latest version. But without the graphical programs the compile should be straight forward.

**RFIGUI, PGPLOT**

Graphical programs are only available for the older Jureca software stack and can be loaded with ``env_lofar_2.15.sh`` and ``env_lofar_2.17.sh`` (authors comment: i recommend to not try to comile those in future versions if the system is not providing the gtkmm package.
compiling the gtk packages and integrating it in the environment is a major pain.).

WSClean
^^^^^^^
Nothing special. Take care of setting all options to the proper values for your locally (or not standard) installed libraries.

Lofar Software Stack
^^^^^^^^^^^^^^^^^^^^
To compile the Lofar software with a compiler in a custom location you have to edit the file ``CMake/variants/GNU.cmake``. This is also the place to change additional compiler options. This file gets read every time you use cmake for the Lofar software and overwrites changes you make in ccmake or in the CMakeCache.txt file.

In the latest releases there was a weired problem with the ``shared`` option for the PyBDSM target. It only compiled when forcing the option via the environment variable ``LDFLAGS="-shared"``.

Again, double check all paths you set in for the options in cmake.


Python Packages
^^^^^^^^^^^^^^^
The least troublesome way to install additional python packages was to download them individually and use their recommended install process. Which is mostly callsing ``setup.py``. Give the option for the local install path you chose (can differ from package to package).
You can also use ``pip`` to install locally but it does not work in all cases. Sometimes it was not detecting that dependencies were already installed in the system paths and tried to overwrite them with diefferent version.
Installing with ``pip`` without dependencies the option is ``--no-deps``. Examples:
::

    pip install APLpy --no-deps --target /homea/htb00/htb003/local_jureca_stack2016a/lib/python2.7/site-packages

    or using a setup.py in a local source directory:

    python setup.py install --prefix=/homea/htb00/htb003/local_jureca_stack2016a

GSM Database
^^^^^^^^^^^^
Log into head node jrl09 and run the script ``/homea/htb00/htb003/start_gsm_database.sh``. It has to be node 09 because that one is hardcoded in the ``gsm.py``.

Notes for Developers
--------------------
Some more deatiled information.

Structure
^^^^^^^^^
The structure of the generic pipeline has four levels. The parset, the pipeline parser, the master scripts and the node scripts. So very similar to the old pipeline structure.

**Parset**

The parset describes the pipeline as explained in the documentation.

**Pipeline parser**

The ``genericpipeline.py`` is the parser for any pipeline parset written in the generic pipeline way. Here the steps are created, keywords replaced and where the internal result dictionary is held.
This is pretty much complete. This is pretty much complete and is only extended when users find something limiting or bugs. Latest adddition for example was to enable the use of environment variables in the replacement mechanism.
Or to give the possibility to split the steplist in sublists so they are easier to read and to group by theme.

There are some little remnants in the code from an attempt to make the construction of a pipeline interactive in a pythonconsole. Adding methods to add steps in specific places or getting output of all possible steps. Not sure if its worth to pursue this approach.


**master scripts**

The master script for the generic pipeline is the ``executable_args.py``. But also the older framework master scripts can be used (Slightliy different calling convention. Please compare msss pipelines with prefactor.). There is only one master script because basically a step is one program that needs some input arguments and the return code needs to be tracked. This can in principle be done in a single script. Maybe a more basic script would better and then one could derive own versions of that class to handle outputs differently.

**node scripts**

There are only a few new node scripts. One general ``executable_args.py`` and for specific purpose ``python_plugin.py``, ``executable_casa.py`` and ``calibrate-stand-alone.py``. The casa and calibrate scripts needed too much special tinkering to put them into the executable_args as well.
All of these scripts can be called from the one new master script.

Error reporting
^^^^^^^^^^^^^^^
The most prominant thing missing from the generic pipeline framework are meaningful error messages. Because the structure of the redesign was not clear from the beginning error checking has not been top priority.
For validity checking of arguments one would need a reference. But there are no interface definitions for possible steps in a pipeline. Theese would have to be defined first to have meaningful argument checking.
For the control arguments there should be better checks. For example if there is no mapfile give out the message that there is no mapfile specified instead of the out of bounds on the mapfile array.

Mapfiles
^^^^^^^^
Another important thing is handling of mapfiles. The plugins mostly exist because of the lack of possibilities to create mapfiles with the standard framework. Now the utility code for mapfiles is copy pasted across different plugins... that is bad.
So there needs to be an overhaul of the mapfile class of the framework. The additional functionality from the dataproduct and multidataproduct classes should be merged into the framework. This way the plugins would contain less code or could be replaced with proper python steps in the pipelines.
What is mainly missing is the possibility to create mapfiles from given folders with file name patterns. Split and merge mapfiles and create proper file fields in the mapfiles for concat and split operations of ``dppp``. Other programs like ``wsclean`` might need different formatting of files lists (having external programs conform to interfaces would be better though).

Parset
^^^^^^
The framework allows to create two different kinds of parset objects. This caused some confusion more than once and the classes need to be unified or be made consistent some other way.
There is a class ``Parset`` in ``CEP/Pipeline/framework/lofarpipe/support/parset.py`` and one in ``CEP/Pipeline/framework/lofarpipe/cuisine/parset.py``. And then there is the ``pyparameterset`` class. Someone needs to take a look at all that.