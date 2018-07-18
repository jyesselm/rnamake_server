import json
import argparse

from rnamake_server import job_queue

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-info', help='what mode is the daemon being run in', required=False)
    parser.add_argument('-delete', help='', required=False)
    parser.add_argument('-to_csv', help='what mode is the daemon being run in', required=False)
    parser.add_argument('-list_queued', help='', required=False,  action='store_true')
    parser.add_argument('-list', help='', required=False,  action='store_true')
    parser.add_argument('-next_job', help='', required=False, action='store_true')
    parser.add_argument('-clean_data', help='', required=False, action='store_true')

    args = parser.parse_args()
    return args

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







