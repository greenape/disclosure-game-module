__all__ = ["sqlite_dump", "sqlite_merge"]

from random import Random

def random_expectations(depth=0, breadth=3, low=1, high=10, random=Random()):
    """
    Generate depth x breadth array of random numbers where each row sums to
    high, with a minimum of low.
    """
    result = []
    if depth == 0:
        initial = high + 1
        for i in range(breadth - 1):
            n = random.randint(low, initial - (low * (breadth - i)))
            initial -= n
            result.append(n)
        result.append(initial - low)
        random.shuffle(result)
    else:
        result = [random_expectations(depth - 1, breadth, low, high, random) for x in range(breadth)]
    return result

def weighted_random_choice(choices, weights, random=Random()):
    population = [val for val, cnt in zip(choices, weights) for i in range(int(cnt))]
    return random.choice(population)

def shuffled(target, random=Random()):
    """
    Return a shuffled version of the argument
    """
    a = list(target)
    random.shuffle(a)
    return a

def make_pbs_script(kwargs, hours=60, mins=0, ppn=16, script_name=None):
    """
    Generate a PBS run script to be submitted.
    """

    from disclosuregame.Util.sqlite_merge import list_matching
    from os.path import split
    
    args_dir, name = split(kwargs.kwargs[0])
    kwargs_files = list_matching(args_dir, name)
    count = len(kwargs_files)

    import sys
    args = sys.argv[1:]
    args = " ".join(args)
    args = args.replace("*", "${PBS_ARRAYID}")
    args = args.replace(" %s " % kwargs.file_name, " ${PBS_ARRAYID}_%s " % kwargs.file_name)
    if kwargs.file_name == "":
        args += " -f ${PBS_ARRAYID}"
    interpreter = sys.executable
    run_script = ["#!/bin/bash -vx"]
    run_script.append("#PBS -l walltime=%d:%d:00" % (hours, mins))
    #Doesn't work on multiple nodes, sadly
    run_script.append("#PBS -l nodes=1:ppn=%d" % ppn)
    run_script.append("module load python")

    #Set up the call
    run_call = "%s -m disclosuregame.run %s" % (interpreter, args)

    run_script.append(run_call)

    #Cleanup after all jobs have run

    if script_name is not None:
        run_script.append("if [$PBS_ARRAYID -eq %d]" % count)
        run_script.append("then")
        run_script.append("\trm %s" % script_name)
        run_script.append("fi")

    return('\n'.join(run_script), count)

    #${python} Run.py -R 100 -s ${sig} -r ${resp} --pickled-arguments ../experiment_args/sensitivity_${PBS_ARRAYID}.args -f ${PBS_ARRAYID}_sensitivity -i 1000 -d ${dir} -g ${game}
