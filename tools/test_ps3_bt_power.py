"""Regression checks for the actual Windows-to-WSL launcher boundary."""
import io
import subprocess
from pathlib import PureWindowsPath
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import ps3_bt_power as power


class WslLaunchTests(unittest.TestCase):
    def test_worker_stdout_and_stderr_share_one_child_stream(self):
        log = io.BytesIO()
        result = SimpleNamespace(returncode=0)
        with patch.object(power.subprocess, 'run', return_value=result) as run:
            self.assertIs(power._run(['worker'], log, timeout=5), result)
        self.assertIs(run.call_args.kwargs['stdout'], log)
        self.assertEqual(run.call_args.kwargs['stderr'], subprocess.STDOUT)

    def test_captured_json_keeps_errors_separate(self):
        log = io.BytesIO()
        with patch.object(power.subprocess, 'run', return_value=SimpleNamespace(returncode=0, stdout=b'{}')) as run:
            power._run(['worker'], log, timeout=5, capture=True)
        self.assertEqual(run.call_args.kwargs['stdout'], subprocess.PIPE)
        self.assertIs(run.call_args.kwargs['stderr'], log)

    def test_path_conversion_bypasses_shell_and_preserves_windows_path(self):
        windows_path = PureWindowsPath(r'C:\Users\test user\project $literal\tools\worker.py')
        linux_path = '/mnt/c/Users/test user/project $literal/tools/worker.py'
        result = SimpleNamespace(returncode=0, stdout=(linux_path + '\n').encode())
        with patch.object(power, 'WORKER', windows_path), patch.object(power, '_run', return_value=result) as run:
            self.assertEqual(power._linux_worker_path(io.BytesIO()), linux_path)
        command = run.call_args.args[0]
        self.assertEqual(command[5:], ['--exec', 'wslpath', '-u', windows_path.as_posix()])

    def test_worker_path_is_passed_to_exec_as_one_literal_argument(self):
        linux_path = '/mnt/c/Users/test user/project $literal/tools/worker.py'
        with patch.object(power, '_run', return_value=SimpleNamespace(returncode=0)) as run:
            self.assertEqual(power._worker(linux_path, '--wake', io.BytesIO()), 0)
        command = run.call_args.args[0]
        self.assertEqual(command[5:7], ['--exec', 'timeout'])
        self.assertEqual(command[-2:], [linux_path, '--wake'])
        self.assertEqual(run.call_args.kwargs['timeout'], 95)

    def test_recovery_uses_the_same_direct_execution_route(self):
        with patch.object(power, '_run', return_value=SimpleNamespace(returncode=0)) as run:
            self.assertEqual(power._worker('/mnt/c/worker.py', '--restore-only', io.BytesIO()), 0)
        self.assertEqual(run.call_args.args[0][5:7], ['--exec', 'timeout'])
        self.assertEqual(run.call_args.kwargs['timeout'], 20)


if __name__ == '__main__':
    unittest.main()
