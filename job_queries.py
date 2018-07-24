import json
import argparse
import glob
import shutil
import os

from rnamake_server import job_queue, daemon, tools, settings

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-info', help='what mode is the daemon being run in', required=False)
    parser.add_argument('-delete', help='', required=False)
    parser.add_argument('-to_csv', help='what mode is the daemon being run in', required=False)
    parser.add_argument('-list_queued', help='', required=False,  action='store_true')
    parser.add_argument('-list', help='', required=False,  action='store_true')
    parser.add_argument('-next_job', help='', required=False, action='store_true')
    parser.add_argument('-clean_data', help='', required=False, action='store_true')
    parser.add_argument('-initiate_queue', help='', required=False, action='store_true')
    #parser.add_argument('-add_job', help='', required=False, action='store_true')

    args = parser.parse_args()
    return args

def setup_and_run_job(pdb, job_id, job_type, args, jq, d):
    if not os.path.isdir("data/"+job_id):
        os.mkdir("data/"+job_id)

    # copy pdb
    shutil.copy(pdb, "data/"+job_id+"/input.pdb")

    # run pymol to create image
    if settings.OS == 'osx':
        tools.render_pdb_to_png_mac("data/"+job_id+"/input.pdb",
                                    "data/"+job_id+"/input.png")
    else:
        tools.render_pdb_to_png("data/"+job_id+"/input.pdb",
                                "data/"+job_id+"/input.png")

    # create job
    jq.add_job(job_id, job_type, json.dumps(args))

    # run job
    d.run_job(job_id)

if __name__ == "__main__":
    args = parse_args()

    jq = job_queue.JobQueue()

    if args.info:
        j = jq.get_job(args.info)
        if j is None:
            raise ValueError(args.info + " is a unknown job id")
        else:
            print j

    if args.list_queued:
        jobs = jq.get_queued()
        for j in jobs:
            print j

    if args.list:
        jobs = jq.get_all()
        for j in jobs:
            print j

    if args.next_job:
        print jq.get_next_queued_job()

    if args.delete:
        jq.delete_job(args.delete)

    if args.clean_data:
        dirs = glob.glob("data/*")
        for d in dirs:
            spl = d.split("/")
            j = jq.get_job(spl[1])
            if j is None:
                shutil.rmtree(d)

    if args.initiate_queue:
        print "are you sure? this is permanent [Y/n]",
        s = raw_input()
        if s.upper() != "Y":
            exit()
        print "creating backup because I am still not sure this is a good idea"
        shutil.copy("jobs.db", "jobs.db.bak")
        os.remove("jobs.db")

        jq = job_queue.JobQueue()

        if settings.OS == 'osx':
            d = daemon.RNAMakeDaemon("devel")
        else:
            d = daemon.RNAMakeDaemon("release")

        # generate scaffold example job
        setup_and_run_job(
            "res/unittest_res/test_pdbs/test_scaffold/min_tetraloop_receptor.pdb",
            "example_scaffold",
            job_queue.JobType.SCAFFOLD,
            {"nstruct": 10, "start_bp": "A221-A252", "end_bp": "A145-A158"},
            jq, d)

        # generate apt stablization example job
        setup_and_run_job(
            "res/unittest_res/test_pdbs/test_stablization/atp_apt.pdb",
            "example_apt_stablization",
            job_queue.JobType.APT_STABLIZATION,
            {"nstruct": 10},
            jq, d)








