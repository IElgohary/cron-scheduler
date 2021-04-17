## Description
A basic command line cron scheduler. The scheduler runs as follows:

1- The jobs are stored in a SQLite database where each job is described by a unique id, expected running interval, frequency of running the job, path to the job file and timestamp for the last run of the job

2- The scheduler and the command line tool are implemented in python

3- To setup the project, run:
```
python3 main.py setupDB
```
this initializes the db that stores the jobs and creates a table for the jobs

4- jobs are added through the command line tool by running

```
python3 main.py [id] [expected interval] [frequency] [path] 
```

frequency and expected interval format is `0hr 0m 0s` eg. `1hr 30m`.
This command also creates a file in the logs directory with the job id where output of the job is saved in addition to information about the duration and termination time.

5- The scheduler is also started through the command line by running:
```
python3 main.py start [maximum number of threads]
```
the default number of threads is 10

### How it works

1- the scheduler checks the jobs in the database every 5 seconds. It checks if there are any jobs that should start by comparing the last run timestamp and frequency to the current time.

2- it then loops over all the jobs that should run and checks if there are available threads to run the job.

3- if there are available threads, the job runs in a separet thread and the number of available threads is decremented by 1. Internally, the job is started by running 
```
python3 [jobs's path] >> [job's log file path]
```

4- if there are no available threads, the scheduler doesn't run the job and prints that there are no available threads.

5- the scheduler then checks the running jobs. If a job exceeds its expected running interval a message is printed with the id of the job.

### Technical decisions reasoning

For the language, I was comparing go and python but I decided to use python as it is faster to implement.

For storing the jobs, at first I thought of using a map as it is faster but I decided to go for something on disk to be more fault tolerant in case the script fails for any reason. I would've also needed to create a daemon separate from the script to make an in memory datastructure work but that would've also required more time.
I decided to go for SQLite simply because it's fast and reliable and there is no much need to scale the db so there is no need to use a distributed database. 

I thought of using crontab but I decided not to do that as I wanted to implement the algorithm myself.

For storing the jobs, I considered storing the functions in the database as strings but I found it cleaner to store the path of the file. After making that choice, it was intuitive to run the jobs by simply using the command line api in the `os` library. It was also very easy to append the output of the jobs to the logs afterwards by using `>>`

In general, I tried to make the simplest implementation I could think of and I did my best to avoid over engineering the solution.

### Possible future improvements

1- add ability to update and delete jobs

2- add ability to list all the jobs and currently running jobs

3- find a better way to handle threads that exceed their expected duration

4- more tests

5- allow for running jobs in other languages than python