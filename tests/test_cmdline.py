#
"""test_cmdline - Test command line functionality."""
# Copyright © 2011-2019  James Rowe <jnrowe@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0+
#
# This file is part of rdial.
#
# rdial is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# rdial is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# rdial.  If not, see <http://www.gnu.org/licenses/>.

from datetime import datetime
from shutil import copytree
from typing import Callable, Optional

from click import (BadParameter, Context, Option, command, echo, option,
                   pass_context, pass_obj)
from click.testing import CliRunner
from pytest import fixture, mark, raises

from rdial import events as events_mod
from rdial.cmdline import (StartTimeParamType, TaskNameParamType, cli,
                           get_stop_message, main, task_option)
from rdial.events import (Event, TaskNotExistError, TaskNotRunningError,
                          TaskRunningError)


@fixture(autouse=True)
def temp_user_cache(monkeypatch, tmpdir):
    cache_dir = tmpdir.join('cache')
    cache_dir.mkdir()
    monkeypatch.setattr(events_mod.xdg_basedir, 'user_cache',
                        lambda s: cache_dir.strpath)


@mark.parametrize('string, expected', [
    ('valid_name', True),
    ('also-valid-name', True),
    ('.invalid_name', BadParameter),
    ('valid.name', True),
    ('invalid/name', BadParameter),
    ('', BadParameter),
    ('x' * 256, BadParameter),
    ('-bad-start', BadParameter),
])
def test_task_name_validity(string: str, expected: Optional[BadParameter]):
    p = TaskNameParamType()
    if expected is True:
        assert p.convert(string, None, None) == string
    else:
        with raises(expected):
            p.convert(string, None, None)


def test_task_name_from_dir(tmpdir):
    @task_option
    @command()
    def cli(task):
        echo(task)

    runner = CliRunner()
    result = runner.invoke(cli, '--from-dir')
    assert result.stdout == 'rdial\n'
    with tmpdir.mkdir('new_dir').as_cwd():
        result = runner.invoke(cli, '--from-dir')
        assert result.stdout.endswith('new_dir\n')


@mark.parametrize('string, expected', [
    ('yesterday', True),
    ('', True),
    ('2011-05-04T09:15:00Z', True),
    ('AB1 time', BadParameter),
])
def test_start_time_validity(string: str, expected: Optional[BadParameter]):
    p = StartTimeParamType()
    if expected is True:
        assert isinstance(p.convert(string, None, None), datetime)
    else:
        with raises(expected):
            p.convert(string, None, None)


@mark.parametrize('edit_func, message', [
    (lambda s, **kwargs: s, 'finished'),
    (lambda _, **kwargs: None, ''),
])
def test_get_stop_message(edit_func: Callable, message: str, monkeypatch):
    monkeypatch.setattr('click.edit', edit_func)
    ev = Event('task', '2011-05-04T09:30:00Z', '', message)
    assert get_stop_message(ev) == message


def test_get_stop_message_template(monkeypatch):
    output = []
    monkeypatch.setattr('click.edit',
                        lambda s, **kwargs: output.extend(s.splitlines()))
    ev = Event('task', '2011-05-04T09:30:00Z')
    get_stop_message(ev)
    assert '# Task “task” started 2011-05-04T09:30:00Z' in output


@mark.parametrize('config, output', [
    ('color', True),
    ('no_color', False),
])
def test_colour_for_u_deficient(config: str, output: bool):
    @cli.command()
    @pass_obj
    def echo_colour(obj):
        echo(obj.colour)

    runner = CliRunner()
    result = runner.invoke(cli,
                           f'--config tests/data/{config}.ini echo-colour')
    assert result.stdout.strip() == repr(output)


def test_command_defaults():
    @cli.command()
    @option('--choice')
    @pass_context
    def echo_choice(ctx: Context, choice: Option):
        echo(ctx.default_map['choice'])

    runner = CliRunner()
    result = runner.invoke(cli, '--config tests/data/defaults.ini echo-choice')
    assert result.stdout.strip() == 'questionable'


def test_bug_data():
    runner = CliRunner()
    result = runner.invoke(cli, 'bug-data')
    assert result.exit_code == 0
    assert '{' not in result.stdout
    assert '}' not in result.stdout


def test_start_event(tmpdir):
    test_dir = tmpdir.join('test').strpath
    copytree('tests/data/test_not_running', test_dir)
    runner = CliRunner()
    result = runner.invoke(cli, f'--directory {test_dir} start task')
    assert result.exit_code == 0
    assert result.stdout == ''


def test_restart_event(tmpdir):
    test_dir = tmpdir.join('test').strpath
    copytree('tests/data/test_not_running', test_dir)
    runner = CliRunner()
    result = runner.invoke(cli, f'--directory {test_dir} start --continue')
    assert result.exit_code == 0
    assert result.stdout == ''


def test_stop_event(tmpdir):
    test_dir = tmpdir.join('test').strpath
    copytree('tests/data/test', test_dir)
    runner = CliRunner()
    result = runner.invoke(cli, f'--directory {test_dir} stop')
    assert result.exit_code == 0
    assert 'Task task running for' in result.stdout


def test_stop_event_with_file_message(tmpdir):
    test_dir = tmpdir.join('test').strpath
    msg_file = tmpdir.join('message').strpath
    with open(msg_file, 'w') as f:
        f.write('stopping message')
    copytree('tests/data/test', test_dir)
    runner = CliRunner()
    result = runner.invoke(cli, f'--directory {test_dir} stop -F {msg_file}')
    assert result.exit_code == 0
    assert 'Task task running for' in result.stdout
    with tmpdir.join('test', 'task.csv').open() as f:
        assert f.read().endswith('stopping message\n')


def test_stop_event_not_running(tmpdir):
    test_dir = tmpdir.join('test').strpath
    copytree('tests/data/test_not_running', test_dir)
    runner = CliRunner()
    result = runner.invoke(cli, f'--directory {test_dir} stop')
    assert isinstance(result.exception, TaskNotRunningError)
    assert result.exception.args[0] == 'No task running!'


def test_stop_event_running_amend(tmpdir):
    test_dir = tmpdir.join('test').strpath
    copytree('tests/data/test', test_dir)
    runner = CliRunner()
    result = runner.invoke(cli, f'--directory {test_dir} stop --amend')
    assert isinstance(result.exception, TaskRunningError)
    assert result.exception.args[0] == 'Can’t amend running task task!'


def test_stop_event_amend_message_reuse(tmpdir):
    test_dir = tmpdir.join('test').strpath
    copytree('tests/data/test_not_running', test_dir)
    runner = CliRunner()
    result = runner.invoke(cli, f'--directory {test_dir} stop --amend')
    assert result.exit_code == 0
    assert 'Task task running for' in result.stdout
    with tmpdir.join('test', 'task.csv').open() as f:
        assert f.read().endswith('stop message\n')


def test_stop_event_running_interactive(monkeypatch, tmpdir):
    monkeypatch.setattr('click.edit',
                        lambda s, **kwargs: 'interactive message')
    test_dir = tmpdir.join('test').strpath
    copytree('tests/data/test', test_dir)
    runner = CliRunner()
    result = runner.invoke(cli, f'--directory {test_dir} --interactive stop')
    assert result.exit_code == 0
    assert 'Task task running for' in result.stdout
    with tmpdir.join('test', 'task.csv').open() as f:
        assert f.read().endswith('interactive message\n')


def test_switch_event(tmpdir):
    test_dir = tmpdir.join('test').strpath
    copytree('tests/data/test', test_dir)
    runner = CliRunner()
    result = runner.invoke(cli, f'--directory {test_dir} switch task2')
    assert result.exit_code == 0
    assert 'Task task running for' in result.stdout
    with tmpdir.join('test', 'task2.csv').open() as f:
        assert len(f.read().splitlines()) == 3


def test_switch_event_with_file_message(tmpdir):
    test_dir = tmpdir.join('test').strpath
    msg_file = tmpdir.join('message').strpath
    with open(msg_file, 'w') as f:
        f.write('stopping message')
    copytree('tests/data/test', test_dir)
    runner = CliRunner()
    result = runner.invoke(
        cli, f'--directory {test_dir} switch -F {msg_file} task2')
    assert result.exit_code == 0
    assert 'Task task running for' in result.stdout
    with tmpdir.join('test', 'task.csv').open() as f:
        assert f.read().endswith('stopping message\n')
    with tmpdir.join('test', 'task2.csv').open() as f:
        assert len(f.read().splitlines()) == 3


def test_switch_event_not_running(tmpdir):
    test_dir = tmpdir.join('test').strpath
    copytree('tests/data/test_not_running', test_dir)
    runner = CliRunner()
    result = runner.invoke(cli, f'--directory {test_dir} switch task2')
    assert isinstance(result.exception, TaskNotRunningError)
    assert result.exception.args[0] == 'No task running!'


def test_switch_invalid_new_task(tmpdir):
    test_dir = tmpdir.join('test').strpath
    copytree('tests/data/test', test_dir)
    runner = CliRunner()
    result = runner.invoke(cli, f'--directory {test_dir} switch whoops')
    assert isinstance(result.exception, TaskNotExistError)
    assert 'Task whoops does not exist!' in result.exception.args[0]


def test_switch_start_date_overlaps(tmpdir):
    test_dir = tmpdir.join('test').strpath
    copytree('tests/data/test', test_dir)
    runner = CliRunner()
    result = runner.invoke(
        cli,
        f'--directory {test_dir} switch --time 2011-05-04T09:15:00Z task2')
    assert isinstance(result.exception, TaskNotRunningError)
    assert result.exception.args[0] \
        == 'Can’t specify a start time before current task started!'


def test_switch_event_running_interactive(monkeypatch, tmpdir):
    monkeypatch.setattr('click.edit',
                        lambda s, **kwargs: 'interactive message')
    test_dir = tmpdir.join('test').strpath
    copytree('tests/data/test', test_dir)
    runner = CliRunner()
    result = runner.invoke(
        cli, f'--directory {test_dir} --interactive switch task2')
    assert result.exit_code == 0
    assert 'Task task running for' in result.stdout
    with tmpdir.join('test', 'task.csv').open() as f:
        assert f.read().endswith('interactive message\n')
    with tmpdir.join('test', 'task2.csv').open() as f:
        assert len(f.read().splitlines()) == 3


def test_switch_event_running_amend(tmpdir):
    test_dir = tmpdir.join('test').strpath
    copytree('tests/data/test', test_dir)
    runner = CliRunner()
    result = runner.invoke(cli, f'--directory {test_dir} switch --amend task2')
    assert isinstance(result.exception, TaskRunningError)
    assert result.exception.args[0] == 'Can’t amend running task task!'


def test_switch_event_amend_message_reuse(tmpdir):
    test_dir = tmpdir.join('test').strpath
    copytree('tests/data/test_not_running', test_dir)
    runner = CliRunner()
    result = runner.invoke(cli, f'--directory {test_dir} switch --amend task2')
    assert result.exit_code == 0
    assert 'Task task running for' in result.stdout
    with tmpdir.join('test', 'task.csv').open() as f:
        assert f.read().endswith('stop message\n')


def test_run_timed(capfd, tmpdir):
    test_dir = tmpdir.join('test').strpath
    copytree('tests/data/test_not_running', test_dir)
    runner = CliRunner()
    result = runner.invoke(
        cli,
        f"""--directory {test_dir} run -c 'echo "long running command"' task"""
    )
    assert result.exit_code == 0
    assert 'Task task running for' in result.stdout
    assert capfd.readouterr()[0] == 'long running command\n'


def test_run_event_already_running(tmpdir):
    test_dir = tmpdir.join('test').strpath
    copytree('tests/data/test', test_dir)
    runner = CliRunner()
    result = runner.invoke(cli, f'--directory {test_dir} run task2')
    assert isinstance(result.exception, TaskRunningError)
    assert result.exception.args[0] == 'Task task is already started!'


def test_run_failed_command(tmpdir):
    test_dir = tmpdir.join('test').strpath
    copytree('tests/data/test_not_running', test_dir)
    runner = CliRunner()
    result = runner.invoke(
        cli, f'--directory {test_dir} run -c "( exit 50 )" task')
    assert isinstance(result.exception, OSError)
    assert result.exception.args == (50, 'Command failed')


def test_run_with_file_message(capfd, tmpdir):
    test_dir = tmpdir.join('test').strpath
    msg_file = tmpdir.join('message').strpath
    with open(msg_file, 'w') as f:
        f.write('stopping message')
    copytree('tests/data/test_not_running', test_dir)
    runner = CliRunner()
    result = runner.invoke(
        cli, f"""
        --directory {test_dir} run -F {msg_file}
        -c 'echo "long running command"' task
        """)
    assert result.exit_code == 0
    assert 'Task task running for' in result.stdout
    with tmpdir.join('test', 'task.csv').open() as f:
        assert f.read().endswith('stopping message\n')
    assert capfd.readouterr()[0] == 'long running command\n'


def test_run_interactive(monkeypatch, tmpdir):
    monkeypatch.setattr('click.edit',
                        lambda s, **kwargs: 'interactive message')
    test_dir = tmpdir.join('test').strpath
    copytree('tests/data/test_not_running', test_dir)
    runner = CliRunner()
    result = runner.invoke(
        cli, f"""
        --directory {test_dir} --interactive run
        -c 'echo "long running command"' task
        """)
    assert result.exit_code == 0
    assert 'Task task running for' in result.stdout
    with tmpdir.join('test', 'task.csv').open() as f:
        assert f.read().endswith('interactive message\n')


def test_wrapper_no_config():
    runner = CliRunner()
    result = runner.invoke(
        cli, '--config tests/data/defaults.ini wrapper calendar')
    assert isinstance(result.exception, SystemExit)
    assert "No such wrapper 'calendar'" in result.stdout


def test_wrapper_run_command(capfd, tmpdir):
    test_dir = tmpdir.join('test').strpath
    copytree('tests/data/test_not_running', test_dir)
    runner = CliRunner()
    result = runner.invoke(
        cli, f"""
        --config tests/data/wrappers.ini --directory {test_dir}
        wrapper calendar
        """)
    assert result.exit_code == 0
    assert 'Task task running for' in result.stdout
    with tmpdir.join('test', 'task.csv').open() as f:
        assert len(f.read().splitlines()) == 4
    assert 'May 2011' in capfd.readouterr()[0]


@mark.parametrize('task', [
    '',
    'task',
])
def test_report(task):
    runner = CliRunner()
    result = runner.invoke(
        cli, f'--directory tests/data/test_not_running report {task}')
    assert result.exit_code == 0
    assert 'task    2:00:00' in result.stdout


def test_report_stats():
    runner = CliRunner()
    result = runner.invoke(
        cli, '--directory tests/data/test_not_running report --stats')
    assert result.exit_code == 0
    assert 'Duration of events 2:15:00' in result.stdout
    assert 'First entry started at 2011-05-04 08:00:00' in result.stdout
    assert 'Last entry started at 2011-05-04 09:30:00' in result.stdout


def test_report_stats_no_events(tmpdir):
    runner = CliRunner()
    result = runner.invoke(cli, f'--directory {tmpdir.strpath} report --stats')
    assert result.exit_code == 0
    assert 'Duration of events 0:00:00' in result.stdout


def test_report_event_running():
    runner = CliRunner()
    result = runner.invoke(cli, '--directory tests/data/test report')
    assert result.exit_code == 0
    assert 'Task “task” started 2011-05-04T09:30:00Z' \
        in result.stdout.splitlines()


@mark.parametrize('database, expected', [
    ('test', 'Task “task” started'),
    ('test_not_running', 'No task is running!'),
])
def test_running(database: str, expected: str):
    runner = CliRunner()
    result = runner.invoke(cli, f'--directory tests/data/{database} running')
    assert result.exit_code == 0
    assert expected in result.stdout


@mark.parametrize('database, expected', [
    ('test', 'Task task is still running'),
    ('test_no_message', 'Last task task, ran for 1:00:00'),
    ('test_not_running', 'stop message'),
])
def test_last(database: str, expected: str):
    runner = CliRunner()
    result = runner.invoke(cli, f'--directory tests/data/{database} last')
    assert result.exit_code == 0
    assert expected in result.stdout


@mark.parametrize('task', [
    '',
    'task',
])
def test_ledger(task: str):
    runner = CliRunner()
    result = runner.invoke(
        cli, f'--directory tests/data/test_not_running ledger {task}')
    assert result.exit_code == 0
    assert '2011-05-04 * 09:30-10:30' in result.stdout


def test_ledger_running():
    runner = CliRunner()
    result = runner.invoke(cli, '--directory tests/data/test ledger')
    assert result.exit_code == 0
    assert ';; Running event not included in output!' in result.stdout


@mark.parametrize('task', [
    '',
    'task',
])
def test_timeclock(task: str):
    runner = CliRunner()
    result = runner.invoke(
        cli, f'--directory tests/data/test_not_running timeclock {task}')
    assert result.exit_code == 0
    assert 'i 2011-05-04 09:30:00 task' in result.stdout.splitlines()
    assert 'o 2011-05-04 10:30:00  ; stop message' in \
        result.stdout.splitlines()


def test_timeclock_running():
    runner = CliRunner()
    result = runner.invoke(cli, '--directory tests/data/test timeclock')
    assert result.exit_code == 0
    assert ';; Running event not included in output!' in result.stdout


def test_main_wrapper(monkeypatch, capsys):
    monkeypatch.setattr('sys.argv',
                        ['rdial', '--directory', 'tests/data/test', 'running'])

    def exit_mock(n):
        if n == 0:
            return n
        else:
            raise ValueError(n)

    monkeypatch.setattr('sys.exit', exit_mock)
    result = main()
    assert result == 0
    assert 'Task “task” started' in capsys.readouterr()[0]


def test_main_wrapper_error(monkeypatch, capsys):
    monkeypatch.setattr(
        'sys.argv',
        ['rdial', '--directory', 'tests/data/test_not_running', 'stop'])

    def exit_mock(n):
        if n == 0:
            return n
        else:
            raise ValueError(n)

    monkeypatch.setattr('sys.exit', exit_mock)
    result = main()
    assert result == 2
    assert capsys.readouterr()[1] == 'No task running!\n'


def test_main_wrapper_informative_return_code(capsys, monkeypatch, tmpdir):
    test_dir = tmpdir.join('test').strpath
    copytree('tests/data/test_not_running', test_dir)
    monkeypatch.setattr(
        'sys.argv',
        ['rdial', '--directory', test_dir, 'run', '-c', '( exit 50 )', 'task'])
    result = main()
    assert result == 50
    assert 'Task task running for' in capsys.readouterr()[0]
