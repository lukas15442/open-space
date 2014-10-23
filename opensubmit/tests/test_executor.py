import os

from django.test import LiveServerTestCase
from django.test.utils import override_settings
from opensubmit.tests.cases import StudentTestCase
from django.contrib.auth.models import User

from opensubmit.models import TestMachine, SubmissionTestResult

@override_settings(DEBUG=True)  # otherwise we have no traceback from live server
class ExecutorTestCase(StudentTestCase, LiveServerTestCase):
    def setUp(self):
        super(ExecutorTestCase, self).setUp()

    def _registerExecutor(self):
        return os.system("python3 jobexec/executor.py register opensubmit/tests/executor.cfg")

    def _runExecutor(self):
        return os.system("python3 jobexec/executor.py run opensubmit/tests/executor.cfg")

    def testRegisterExecutorExplicit(self):
        machine_count = TestMachine.objects.all().count()
        exit_status = self._registerExecutor()
        self.assertEquals(0, exit_status)
        self.assertEquals(machine_count+1, TestMachine.objects.all().count())

    def testRunRequestFromUnknownMachine(self):
        # This is expected to trigger a register action request from the server
        self.assertNotEquals(0, self._runExecutor())

    @override_settings(JOB_EXECUTOR_SECRET='foo')
    def testInvalidSecret(self):
        self.assertNotEquals(0, self._runExecutor())

    def testEverythingAlreadyTested(self):
        self.createValidatedSubmission(self.current_user)
        self.assertEquals(0, self._registerExecutor())
        self.assertEquals(0, self._runExecutor())

    def testCompleteRun(self):
        sub = self.createValidatableSubmission(self.current_user) 
        self.assertEquals(0, self._registerExecutor())
        # Compilation test
        self.assertEquals(0, self._runExecutor())
        num_compile_results = SubmissionTestResult.objects.filter(
            submission_file=sub.file_upload,
            kind=SubmissionTestResult.COMPILE_TEST
        ).count()
        self.assertEquals(1, num_compile_results)
