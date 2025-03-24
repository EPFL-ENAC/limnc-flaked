# API

Flaked is a process that runs in the background. It exposes a REST API so that one can query the current status of the service, and can modify the configuration.

The interactive documentation of the REST API is available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

## Scheduler status

It is possible to start/stop or pause/resume the scheduler.

## Instrument jobs

For each instrument scheduling directive (`cron` or `interval`) there is a job. Each of this job has the following properties:

| Key             | Description                         |
| --------------- | ----------------------------------- |
| `id`            | The job unique identifier, is based on the corresponding instrument's name, postfixed by the scheduling type. |
| `name`          | The name of the corresponding instrument.                                                   |
| `trigger`       | The trigger directive, either an interval in seconds or the details of the cron expression. |
| `next_run_time` | When will be the next execution. When the job is paused, there is none.                     |

It is possible to start/stop or pause/resume a job in the scheduler. Stopping removes the job from the scheduler, restarting it recreates the job according to the instrument specifications. Pausing a job postpones its next execution. Resuming it recalculates the next run time according to the job trigger definition.