import sqlite3

class Job(object):
    def __init__(self, id, status, email, num, error_message):
        self.id, self.status, self.email = id, status, email
        self.error_message, self.num = error_message, num

class JobQueue(object):
    def __init__(self, db_name='jobs.db'):
        self._setup_sqlite_con`nection(db_name)
        self.current_pos = self.get_last_run_job_num() + 1

    def _setup_sqlite_connection(self, db_name):
        self.connection = sqlite3.connect(db_name)

        try:
            self.connection.execute('CREATE TABLE jobs( id TEXT, status REAL, \
                                     email TEXT, error_message TEXT, num REAL, \
                                     PRIMARY KEY(id));')

            self.add_job('start', num=0, status=1)
        except:
            pass


    def add_job(self, id, num=-1, status=0, email='', error_message=''):
        if num == -1:
            num = self.current_pos
        job = [id, status, email, num, error_message]
        self.connection.execute('INSERT INTO jobs (id,status,email,num,error_message) \
                                 VALUES(?,?,?,?,?)', job)
        self.connection.commit()
        self.current_pos += 1

    def get_job(self, nid):
        try:
            r = self.connection.execute("SELECT * FROM jobs WHERE id=:Id", {"Id":nid}).fetchone()
        except:
            return None
        r_obj = Job(*r)
        return r_obj


    def get_last_run_job_num(self):
        index = self.connection.execute('SELECT MAX(num) FROM jobs WHERE status=1').fetchone()
        return int(index[0])

    def get_queue_position(self, id):
        jobs = self.connection.execute('SELECT * FROM jobs WHERE status=0').fetchall()
        if len(jobs) == 0:
            return 0


if __name__ == '__main__':
    queue = JobQueue()
    #index = queue.get_last_run_job_num()
    queue.get_queue_position('test')
    #print index
    #queue.add_job('test', 'blah')
    #j = queue.get_job('start')

