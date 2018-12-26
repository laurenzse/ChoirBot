regular_jobs = []

job_queue = None


def add_job(name, job_method, job_time_generator):
    regular_jobs.append((name, job_method, job_time_generator))


def update_after_calling(bot, job, job_method):
    job_method(bot, job)
    check_message_jobs()


def delete_all_jobs():
    queue = job_queue._queue
    with queue.mutex:
        queue.queue.clear()


def check_message_jobs():
    if not job_queue:
        return

    existing_jobs = list(map(lambda job: job.name, job_queue.jobs()))

    for regular_job in regular_jobs:
        job_name, job_method, job_time_generator = regular_job

        def job_and_update(bot, job, method=job_method):
            method(bot, job)
            check_message_jobs()

        if job_name not in existing_jobs:
            job_queue.run_once(job_and_update,
                               job_time_generator(),
                               name=job_name)



