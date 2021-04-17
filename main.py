import sys
import sqlite3
import re
import threading
import time
import os

class scheduler():
    ID = 0
    SINGLE_RUN_EXPECTED_INTERVAL = 1
    FREQUENCY = 2
    PATH = 3
    LAST_RUN_TIMESTAMP = 4

    def __init__(self):
        self.threads = 10
        self.currentlyRunningJobs = []

    def calculateSeconds(self, timeString):
        if not re.compile("(\d+hr)? ?(\d+m)? ?(\d+s)?").fullmatch(timeString):
            return -1
        time = timeString.split(" ")
        seconds = 0
        for v in time:
            if re.compile("\d+hr").match(v):
                hours = int(v[:-2])
                seconds += 3600 * hours
            elif re.compile("\d+m").match(v):
                min = int(v[:-1])
                seconds += 60 * min
            elif re.compile("\d+s").match(v):
                s = int(v[:-1])
                seconds += s
            else:
                return -1
        return seconds

    def runJob(self, row, start_at):
        print("running job: ", row[self.ID])
        file_object = open("./logs/" + row[self.ID] + ".txt", 'a')
        file_object.write('\nStarted job at: ' + str(start_at))
        file_object.write('\n')
        file_object.flush()
        command = "python3 " + row[self.PATH] +" >> " + "./logs/" + row[self.ID] + ".txt"
        os.system(command)
        self.currentlyRunningJobs = [d for d in self.currentlyRunningJobs if d.get('job_id') != row[self.ID]]
        finished_at = time.time()
        file_object = open("./logs/" + row[self.ID] + ".txt", 'a')
        file_object.write('job done at: '+ str(finished_at))
        file_object.write('\nduration: ' + str(finished_at - start_at)+ " seconds")
        file_object.write('\n')
        file_object.close()
        print("job finished: ", row[self.ID])

    def runScheduler(self):
        conn = sqlite3.connect('scheduler.db')
        while True:
            c = conn.cursor()
            c.execute("SELECT * FROM jobs WHERE last_run_timestamp is NULL or last_run_timestamp + frequency <= ?",
                      (int(time.time()),))
            rows = c.fetchall()
            for row in rows:
                if len(self.currentlyRunningJobs) < self.threads:
                    start_at = time.time()
                    c = conn.cursor()
                    c.execute("UPDATE jobs SET last_run_timestamp = ? WHERE id = ?",
                              (int(start_at),row[self.ID],))
                    conn.commit()
                    t = threading.Thread(target=self.runJob, args=(row, start_at,))
                    t.start()
                    self.currentlyRunningJobs.append({
                        'thread': t,
                        'expected_interval': int(row[self.SINGLE_RUN_EXPECTED_INTERVAL]),
                        'job_id': row[self.ID],
                        'started_at': start_at
                    })
                else:
                    print("Maximum allowed threads reached")
            for job in self.currentlyRunningJobs:
                if int(time.time()) - job['started_at'] > job['expected_interval']:
                    print("job '" + job['job_id'] + "' - exceeded expected run interval")

            time.sleep(5)

    def setupDB(self, conn):
        c = conn.cursor()
        c.execute("DROP TABLE IF EXISTS jobs")
        sql = '''CREATE TABLE jobs(
                   id CHAR(256) PRIMARY KEY UNIQUE NOT NULL,
                   single_run_expected_interval INT NOT NULL,
                   frequency INT NOT NULL,
                   path TEXT NOT NULL,
                   last_run_timestamp BIGINT
                )'''
        c.execute(sql)
        print("Table created successfully")
        conn.commit()
        conn.close()

    def addJob(self, conn, id, interval, frequency, path):
        c = conn.cursor()
        c.execute("INSERT INTO jobs (id,single_run_expected_interval,frequency, path) VALUES (?,?,?, ?)",
                  (id, interval, frequency, path))
        conn.commit()
        f = open("./logs/" + id + ".txt", 'w+')
        f.write("Job created at: " + str(int(time.time())))
        f.close()


if __name__ == '__main__':
    arguments = sys.argv
    conn = sqlite3.connect('scheduler.db')
    schedulerInstance = scheduler()
    command = arguments[1]
    if command == "setupDB":
        schedulerInstance.setupDB(conn)
    elif command == "add":
        job_id = arguments[2]
        interval = schedulerInstance.calculateSeconds(arguments[3])
        if interval == -1:
            print("wrong single_run_interval format")
            exit(-1)
        frequency = schedulerInstance.calculateSeconds(arguments[4])
        if frequency == -1:
            print("wrong frequency format")
            exit(-1)
        path = arguments[5]
        schedulerInstance.addJob(conn, job_id, interval, frequency, path)
        print("job added successfully")
    elif command == "start":
        if len(arguments) == 3:
            schedulerInstance.threads = int(arguments[2])
        threading.Thread(target=schedulerInstance.runScheduler).start()
