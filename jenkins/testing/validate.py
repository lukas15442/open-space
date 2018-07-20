import time


def validate(job):
    print(job.working_dir)
    print(job.timeout)
    print(job.submission_id)
    print(job.file_id)
    print(job.submitter_name)
    print(job.submitter_student_id)
    print(job.submitter_studyprogram)
    print(job.author_names)
    print(job.course)
    print(job.assignment)
    time.sleep(60)

    job.send_pass_result("sdfsdf")
