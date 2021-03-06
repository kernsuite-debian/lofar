#                                                          LOFAR PIPELINE SCRIPT
#
#                                           running an executable with arguments
#                                                         Stefan Froehlich, 2014
#                                                      s.froehlich@fz-juelich.de
# ------------------------------------------------------------------------------

import copy
import sys
import os
import errno
import lofarpipe.support.lofaringredient as ingredient

from lofarpipe.support.baserecipe import BaseRecipe
from lofarpipe.support.remotecommand import RemoteCommandRecipeMixIn
from lofarpipe.support.remotecommand import ComputeJob
from lofarpipe.support.data_map import DataMap, validate_data_maps, align_data_maps, DataProduct
from lofarpipe.support.parset import Parset


class executable_args(BaseRecipe, RemoteCommandRecipeMixIn):
    """
    Basic script for running an executable with arguments.
    Passing a mapfile along so the executable can process MS.
    """
    inputs = {
        'executable': ingredient.ExecField(
            '--executable',
            help="The full path to the relevant executable",
            optional=True
        ),
        'arguments': ingredient.ListField(
            '-a', '--arguments',
            help="List of arguments for the executable. Will be added as ./exe arg0 arg1...",
            default='',
            optional=True
        ),
        'nthreads': ingredient.IntField(
            '--nthreads',
            default=8,
            help="Number of threads per process"
        ),
        'nodescript': ingredient.StringField(
            '--nodescript',
            help="Name of the node script to execute",
            default='executable_args',
            optional=True
        ),
        'parset': ingredient.FileField(
            '-p', '--parset',
            help="Path to the arguments for this executable. Will be converted to --key=value",
            optional=True
        ),
        'inputkey': ingredient.StringField(
            '-i', '--inputkey',
            help="Parset key that the executable will recognize as key for inputfile",
            default='',
            optional=True
        ),
        'outputkey': ingredient.StringField(
            '-0', '--outputkey',
            help="Parset key that the executable will recognize as key for outputfile",
            default='',
            optional=True
        ),
        'inputkeys': ingredient.ListField(
            '--inputkeys',
            help="List of parset keys that the executable will recognize as key for inputfile",
            default=[],
            optional=True
        ),
        'outputkeys': ingredient.ListField(
            '--outputkeys',
            help="List of parset keys that the executable will recognize as key for outputfile",
            default=[],
            optional=True
        ),
        'mapfiles_in': ingredient.ListField(
            '--mapfiles-in',
            help="List of the input mapfiles containing the names of the "
                 "data to run the recipe on",
            default=[],
            optional=True
        ),
        'mapfiles_as_string': ingredient.ListField(
            '--mapfiles_as_string',
            help="List of the input mapfiles to ignore and just use the name string instead.",
            default=[],
            optional=True
        ),
        'mapfiles_out': ingredient.ListField(
            '--mapfiles-out',
            help="List of the output mapfiles containing the names of the "
                 "data produced by the recipe",
            default=[],
            optional=True
        ),
        'mapfile_in': ingredient.StringField(
            '--mapfile-in',
            help="Name of the input mapfile containing the names of the "
                 "MS-files to run the recipe",
            default='',
            optional=True
        ),
        'mapfile_out': ingredient.StringField(
            '--mapfile-out',
            help="Name of the output mapfile containing the names of the "
                 "MS-files produced by the recipe",
            default='',
            optional=True
        ),
        'skip_infile': ingredient.BoolField(
            '--skip-infile',
            help="Dont give the input file to the executable.",
            default=False,
            optional=True
        ),
        'skip_outfile': ingredient.BoolField(
            '--skip-outfile',
            help="Dont produce an output file",
            default=False,
            optional=True
        ),
        'inplace': ingredient.BoolField(
            '--inplace',
            help="Manipulate input files inplace",
            default=False,
            optional=True
        ),
        'outputsuffixes': ingredient.ListField(
            '--outputsuffixes',
            help="Suffixes for the outputfiles",
            default=[]
        ),
        'parsetasfile': ingredient.BoolField(
            '--parsetasfile',
            help="Will the argument be a parsetfile or --opt=var",
            default=False
        ),
        'args_format': ingredient.StringField(
            '--args_format',
            help="Will change the format of the arguments. Standard definitions are...dont know yet",
            default='gnu'
        ),
        'args_format_argument': ingredient.StringField(
            '--args_format_argument',
            help="Will change the format of the arguments without option fields.",
            default=''
        ),
        'args_format_option': ingredient.StringField(
            '--args_format_option',
            help="Will change the format of option fields.",
            default='-'
        ),
        'args_format_longoption': ingredient.StringField(
            '--args_format_longoption',
            help="Will change the format of long option fields. Typically '--'",
            default='--'
        ),
        'args_format_option_argument': ingredient.StringField(
            '--args_format_option_argument',
            help="Will change the format of the arguments without option fields.",
            default='='
        ),
        'max_per_node': ingredient.IntField(
            '--max_per_node',
            help="Sets the number of jobs per node",
            default=0
        ),
        'stepname': ingredient.StringField(
            '--stepname',
            help="stepname for individual naming of results",
            optional=True
        ),
        'environment': ingredient.DictField(
            '--environment',
            help="Update environment variables for this step.",
            optional=True
        ),
        'error_tolerance': ingredient.BoolField(
            '--error_tolerance',
            help="Controls if the program exits on the first error or continues with succeeded MS.",
            default=True,
            optional=True
        )
    }

    outputs = {
        'mapfile': ingredient.FileField(
            help="The full path to a mapfile describing the processed data"
        )
    }

    def go(self):
        if 'executable' in self.inputs:
            executable = self.inputs['executable']

        if self.inputs['nthreads']:
            self.environment["OMP_NUM_THREADS"] = str(self.inputs['nthreads'])

        if 'environment' in self.inputs:
            self.environment.update(self.inputs['environment'])

        self.logger.info("Starting %s run" % executable)
        super(executable_args, self).go()

        # args format stuff
        args_format = {'args_format': self.inputs['args_format'],
                       'args_format_argument': self.inputs['args_format_argument'],
                       'args_format_option': self.inputs['args_format_option'],
                       'args_formatlongoption': self.inputs['args_format_longoption'],
                       'args_format_option_argument': self.inputs['args_format_option_argument']}
        mapfile_dir = os.path.join(self.config.get("layout", "job_directory"), "mapfiles")
        work_dir = os.path.join(self.inputs['working_directory'], self.inputs['job_name'])
        # *********************************************************************
        # try loading input/output data file, validate output vs the input location if
        #    output locations are provided
        try:
            inputmapfiles = []
            inlist = []
            if self.inputs['mapfile_in']:
                inlist.append(self.inputs['mapfile_in'])

            if self.inputs['mapfiles_in']:
                for item in self.inputs['mapfiles_in']:
                    inlist.append(item)
                self.inputs['mapfile_in'] = self.inputs['mapfiles_in'][0]

            for item in inlist:
                inputmapfiles.append(DataMap.load(item))

        except Exception:
            self.logger.error('Could not load input Mapfile %s' % inlist)
            return 1

        outputmapfiles = []
        if self.inputs['mapfile_out']:
            try:
                outdata = DataMap.load(self.inputs['mapfile_out'])
                outputmapfiles.append(outdata)
            except Exception:
                self.logger.error('Could not load output Mapfile %s' % self.inputs['mapfile_out'])
                return 1
            # sync skip fields in the mapfiles
            align_data_maps(inputmapfiles[0], outputmapfiles[0])

        elif self.inputs['mapfiles_out']:
            for item in self.inputs['mapfiles_out']:
                outputmapfiles.append(DataMap.load(item))
            self.inputs['mapfile_out'] = self.inputs['mapfiles_out'][0]

        else:
            # ouput will be directed in the working directory if no output mapfile is specified
            outdata = copy.deepcopy(inputmapfiles[0])
            if not self.inputs['inplace']:
                for item in outdata:
                    item.file = os.path.join(
                        self.inputs['working_directory'],
                        self.inputs['job_name'],
                        #os.path.basename(item.file) + '.' + os.path.split(str(executable))[1]
                        os.path.splitext(os.path.basename(item.file))[0] + '.' + self.inputs['stepname']
                    )
                self.inputs['mapfile_out'] = os.path.join(mapfile_dir, self.inputs['stepname'] + '.' + 'mapfile')
                self.inputs['mapfiles_out'].append(self.inputs['mapfile_out'])
            else:
                self.inputs['mapfile_out'] = self.inputs['mapfile_in']
                self.inputs['mapfiles_out'].append(self.inputs['mapfile_out'])
            outputmapfiles.append(outdata)

        if not validate_data_maps(inputmapfiles[0], outputmapfiles[0]):
            self.logger.error(
                "Validation of data mapfiles failed!"
            )
            return 1

        if self.inputs['outputsuffixes']:
            # Handle multiple outputfiles
            for name in self.inputs['outputsuffixes']:
                outputmapfiles.append(copy.deepcopy(inputmapfiles[0]))
                self.inputs['mapfiles_out'].append(os.path.join(mapfile_dir, self.inputs['stepname'] + name + '.' + 'mapfile'))
                for item in outputmapfiles[-1]:
                    item.file = os.path.join(
                        work_dir,
                        os.path.splitext(os.path.basename(item.file))[0] + '.' + self.inputs['stepname'] + name
                    )
            self.inputs['mapfile_out'] = self.inputs['mapfiles_out'][0]

        # prepare arguments
        arglist = self.inputs['arguments']
        parsetdict = {}
        if 'parset' in self.inputs:
            parset = Parset()
            parset.adoptFile(self.inputs['parset'])
            for k in parset.keys:
                parsetdict[k] = str(parset[k])

        # construct multiple input data
        if self.inputs['inputkey'] and not self.inputs['inputkey'] in self.inputs['inputkeys']:
            self.inputs['inputkeys'].insert(0, self.inputs['inputkey'])

        if not self.inputs['outputkeys'] and self.inputs['outputkey']:
            self.inputs['outputkeys'].append(self.inputs['outputkey'])

        if not self.inputs['skip_infile'] and len(self.inputs['inputkeys']) is not len(inputmapfiles):
            self.logger.error("Number of input mapfiles %d and input keys %d have to match." %
                              (len(inputmapfiles), len(self.inputs['inputkeys'])))
            return 1

        filedict = {}
        if self.inputs['inputkeys'] and not self.inputs['skip_infile']:
            for key, filemap, mapname in zip(self.inputs['inputkeys'], inputmapfiles, inlist):
                if not mapname in self.inputs['mapfiles_as_string']:
                    filedict[key] = []
                    for inp in filemap:
                        filedict[key].append(inp.file)
                else:
                    if key != mapname:
                        filedict[key] = []
                        for inp in filemap:
                            filedict[key].append(mapname)

        if self.inputs['outputkey']:
            filedict[self.inputs['outputkey']] = []
            for item in outputmapfiles[0]:
                filedict[self.inputs['outputkey']].append(item.file)

        # ********************************************************************
        # Call the node side of the recipe
        # Create and schedule the compute jobs
        #command = "python3 %s" % (self.__file__.replace('master', 'nodes')).replace('executable_args', self.inputs['nodescript'])
        recipe_dir_str = str(self.config.get('DEFAULT', 'recipe_directories'))
        recipe_directories = recipe_dir_str.rstrip(']').lstrip('[').split(',')
        pylist = os.getenv('PYTHONPATH').split(':')
        command = None
        for pl in pylist:
            if os.path.isfile(os.path.join(pl,'lofarpipe/recipes/nodes/'+self.inputs['nodescript']+'.py')):
                command = "python3 %s" % os.path.join(pl,'lofarpipe/recipes/nodes/'+self.inputs['nodescript']+'.py')
        for pl in recipe_directories:
            if os.path.isfile(os.path.join(pl,'nodes/'+self.inputs['nodescript']+'.py')):
                command = "python3 %s" % os.path.join(pl,'nodes/'+self.inputs['nodescript']+'.py')

        inputmapfiles[0].iterator = outputmapfiles[0].iterator = DataMap.SkipIterator
        jobs = []
        for i, (outp, inp,) in enumerate(zip(
            outputmapfiles[0], inputmapfiles[0])
        ):
            arglist_copy = copy.deepcopy(arglist)
            parsetdict_copy = copy.deepcopy(parsetdict)

            if filedict:
                for name, value in filedict.items():
                    replaced = False
                    if arglist_copy:
                        for arg in arglist:
                            if name == arg:
                                ind = arglist_copy.index(arg)
                                arglist_copy[ind] = arglist_copy[ind].replace(name, value[i])
                                replaced = True
                    if parsetdict_copy:
                        if name in list(parsetdict_copy.values()):
                            for k, v in parsetdict_copy.items():
                                if v == name:
                                    parsetdict_copy[k] = value[i]
                        else:
                            if not replaced:
                                parsetdict_copy[name] = value[i]

            jobs.append(
                ComputeJob(
                    inp.host, command,
                    arguments=[
                        inp.file,
                        executable,
                        arglist_copy,
                        parsetdict_copy,
                        work_dir,
                        self.inputs['parsetasfile'],
                        args_format,
                        self.environment
                    ],
                    resources={
                        "cores": self.inputs['nthreads']
                    }
                )
            )
        max_per_node = self.inputs['max_per_node']
        self._schedule_jobs(jobs, max_per_node)
        jobresultdict = {}
        resultmap = {}
        for job, outp in zip(jobs, outputmapfiles[0]):
            if job.results['returncode'] != 0:
                outp.skip = True
                if not self.inputs['error_tolerance']:
                    self.logger.error("A job has failed with returncode %d and error_tolerance is not set. Bailing out!" % job.results['returncode'])
                    return 1
            for k, v in list(job.results.items()):
                if not k in jobresultdict:
                    jobresultdict[k] = []
                jobresultdict[k].append(DataProduct(job.host, job.results[k], outp.skip))
                if k == 'break':
                    self.outputs.update({'break': v})

        # temp solution. write all output dict entries to a mapfile
        #mapfile_dir = os.path.join(self.config.get("layout", "job_directory"), "mapfiles")
        #check directory for stand alone mode
        if not os.path.isdir(mapfile_dir):
            try:
                os.mkdir(mapfile_dir, )
            except OSError as exc:  # Python >2.5
                if exc.errno == errno.EEXIST and os.path.isdir(mapfile_dir):
                    pass
                else:
                    raise
        for k, v in list(jobresultdict.items()):
            dmap = DataMap(v)
            dmap.save(os.path.join(mapfile_dir, self.inputs['stepname'] + '.' + k + '.mapfile'))
            resultmap[k + '.mapfile'] = os.path.join(mapfile_dir, self.inputs['stepname'] + '.' + k + '.mapfile')
        self.outputs.update(resultmap)
        # *********************************************************************
        # Check job results, and create output data map file
        if self.error.isSet():
            # Abort if all jobs failed
            if all(job.results['returncode'] != 0 for job in jobs):
                self.logger.error("All jobs failed. Bailing out!")
                return 1
            else:
                self.logger.warn(
                    "Some jobs failed, continuing with succeeded runs"
                )
        mapdict = {}
        for item, name in zip(outputmapfiles, self.inputs['mapfiles_out']):
            self.logger.debug("Writing data map file: %s" % name)
            item.save(name)
            mapdict[os.path.basename(name)] = name

        self.outputs['mapfile'] = self.inputs['mapfile_out']
        if self.inputs['outputsuffixes']:
            self.outputs.update(mapdict)

        return 0

if __name__ == '__main__':
    sys.exit(executable_args().main())
