#
"""test_cmdline - Test command line functionality"""
# Copyright © 2011-2016  James Rowe <jnrowe@gmail.com>
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
#
# SPDX-License-Identifier: GPL-3.0+

from datetime import datetime
from shutil import copytree
from typing import Callable, Optional

from click import (BadParameter, Context, Option, command, echo, group,
                   option, pass_context, pass_obj)
from click.testing import CliRunner
from pytest import mark, raises

from rdial.cmdline import (HiddenGroup, StartTimeParamType, TaskNameParamType,
                           cli, get_stop_message, hidden, main, task_option)
from rdial.events import Event, TaskNotRunningError, TaskRunningError


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
    result = runner.invoke(cli, ['--from-dir', ])
    assert result.output == 'rdial\n'
    with tmpdir.mkdir('new_dir').as_cwd():
        result = runner.invoke(cli, ['--from-dir', ])
        assert result.output.endswith('new_dir\n')


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


def test_HiddenGroup():
    @group(cls=HiddenGroup)
    def cli():
        pass

    @cli.command()
    def now_you_see_me():
        pass

    @hidden
    @cli.command()
    def now_you_dont():
        pass

    runner = CliRunner()
    result = runner.invoke(cli, ['--help'])
    lines = [s.strip() for s in result.output.splitlines()]
    assert 'now_you_see_me' in lines
    assert 'now_you_dont' not in lines


@mark.parametrize('edit_func, message', [
    (lambda s, **kwargs: s,
     'finished'),
    (lambda _, **kwargs: None,
     ''),
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
    assert '# Task “task” started 2011-05-04T09:30:00Z'.format(ev) in output


@mark.parametrize('config, result', [
    ('color', True),
    ('no_color', False),
])
def test_colour_for_u_deficient(config: str, result: bool):
    @cli.command()
    @pass_obj
    def raise_config(obj):
        raise ValueError(obj)

    runner = CliRunner()
    with raises(ValueError) as excinfo:
        runner.invoke(cli,
                      ['--config', 'tests/data/{}.ini'.format(config),
                       'raise_config'],
                      catch_exceptions=False)
    assert excinfo.value.args[0].colour is result


def test_command_defaults():
    @cli.command()
    @option('--choice')
    @pass_context
    def raise_context(ctx: Context, choice: Option):
        raise ValueError(ctx)

    runner = CliRunner()
    with raises(ValueError) as excinfo:
        runner.invoke(cli,
                      ['--config', 'tests/data/defaults.ini',
                       'raise_context', ],
                      catch_exceptions=False)
    defaults = excinfo.value.args[0].default_map
    assert defaults['choice'] == 'questionable'


def test_start_event(tmpdir):
    test_dir = tmpdir.join('test').strpath
    copytree('tests/data/test_not_running', test_dir)
    runner = CliRunner()
    result = runner.invoke(cli, ['--directory', test_dir, 'start', 'task'])
    assert result.exit_code == 0
    assert result.output == ''


def test_stop_event(tmpdir):
    test_dir = tmpdir.join('test').strpath
    copytree('tests/data/test', test_dir)
    runner = CliRunner()
    result = runner.invoke(cli, ['--directory', test_dir, 'stop'])
    assert result.exit_code == 0
    assert 'Task task running for' in result.output


def test_stop_event_with_file_message(tmpdir):
    test_dir = tmpdir.join('test').strpath
    msg_file = tmpdir.join('message').strpath
    with open(msg_file, 'w') as f:
        f.write('stopping message')
    copytree('tests/data/test', test_dir)
    runner = CliRunner()
    result = runner.invoke(cli, ['--directory', test_dir, 'stop', '-F',
                                 msg_file])
    assert result.exit_code == 0
    assert 'Task task running for' in result.output
    with tmpdir.join('test', 'task.csv').open() as f:
        assert f.read().endswith('stopping message\n')


def test_stop_event_not_running(tmpdir):
    test_dir = tmpdir.join('test').strpath
    copytree('tests/data/test_not_running', test_dir)
    runner = CliRunner()
    result = runner.invoke(cli, ['--directory', test_dir, 'stop'])
    assert isinstance(result.exception, TaskNotRunningError)
    assert result.exception.args[0] == 'No task running!'


def test_stop_event_running_amend(tmpdir):
    test_dir = tmpdir.join('test').strpath
    copytree('tests/data/test', test_dir)
    runner = CliRunner()
    result = runner.invoke(cli, ['--directory', test_dir, 'stop', '--amend'])
    assert isinstance(result.exception, TaskRunningError)
    assert result.exception.args[0] == 'Can’t amend running task task!'


def test_stop_event_amend_message_reuse(tmpdir):
    test_dir = tmpdir.join('test').strpath
    copytree('tests/data/test_not_running', test_dir)
    runner = CliRunner()
    result = runner.invoke(cli, ['--directory', test_dir, 'stop', '--amend'])
    assert result.exit_code == 0
    assert 'Task task running for' in result.output
    with tmpdir.join('test', 'task.csv').open() as f:
        assert f.read().endswith('stop message\n')


def test_stop_event_running_interactive(monkeypatch, tmpdir):
    monkeypatch.setattr('click.edit',
                        lambda s, **kwargs: 'interactive message')
    test_dir = tmpdir.join('test').strpath
    copytree('tests/data/test', test_dir)
    runner = CliRunner()
    result = runner.invoke(cli, ['--directory', test_dir, '--interactive',
                                 'stop'])
    assert result.exit_code == 0
    assert 'Task task running for' in result.output
    with tmpdir.join('test', 'task.csv').open() as f:
        assert f.read().endswith('interactive message\n')


def test_switch_event(tmpdir):
    test_dir = tmpdir.join('test').strpath
    copytree('tests/data/test', test_dir)
    runner = CliRunner()
    result = runner.invoke(cli, ['--directory', test_dir, 'switch', 'task2'])
    assert result.exit_code == 0
    assert 'Task task running for' in result.output
    with tmpdir.join('test', 'task2.csv').open() as f:
        assert len(f.read().splitlines()) == 3


def test_switch_event_with_file_message(tmpdir):
    test_dir = tmpdir.join('test').strpath
    msg_file = tmpdir.join('message').strpath
    with open(msg_file, 'w') as f:
        f.write('stopping message')
    copytree('tests/data/test', test_dir)
    runner = CliRunner()
    result = runner.invoke(cli, ['--directory', test_dir, 'switch', '-F',
                                 msg_file, 'task2'])
    assert result.exit_code == 0
    assert 'Task task running for' in result.output
    with tmpdir.join('test', 'task.csv').open() as f:
        assert f.read().endswith('stopping message\n')
    with tmpdir.join('test', 'task2.csv').open() as f:
        assert len(f.read().splitlines()) == 3


def test_switch_event_not_running(tmpdir):
    test_dir = tmpdir.join('test').strpath
    copytree('tests/data/test_not_running', test_dir)
    runner = CliRunner()
    result = runner.invoke(cli, ['--directory', test_dir, 'switch', 'task2'])
    assert isinstance(result.exception, TaskNotRunningError)
    assert result.exception.args[0] == 'No task running!'


def test_switch_start_date_overlaps(tmpdir):
    test_dir = tmpdir.join('test').strpath
    copytree('tests/data/test', test_dir)
    runner = CliRunner()
    result = runner.invoke(cli, ['--directory', test_dir, 'switch', '--time',
                                 '2011-05-04T09:15:00Z', 'task2'])
    assert isinstance(result.exception, TaskNotRunningError)
    assert result.exception.args[0] \
        == 'Can’t specify a start time before current task started!'


def test_switch_event_running_interactive(monkeypatch, tmpdir):
    monkeypatch.setattr('click.edit',
                        lambda s, **kwargs: 'interactive message')
    test_dir = tmpdir.join('test').strpath
    copytree('tests/data/test', test_dir)
    runner = CliRunner()
    result = runner.invoke(cli, ['--directory', test_dir, '--interactive',
                                 'switch', 'task2'])
    assert result.exit_code == 0
    assert 'Task task running for' in result.output
    with tmpdir.join('test', 'task.csv').open() as f:
        assert f.read().endswith('interactive message\n')
    with tmpdir.join('test', 'task2.csv').open() as f:
        assert len(f.read().splitlines()) == 3


def test_run_timed(capfd, tmpdir):
    test_dir = tmpdir.join('test').strpath
    copytree('tests/data/test_not_running', test_dir)
    runner = CliRunner()
    result = runner.invoke(cli, ['--directory', test_dir, 'run', '-c',
                                 'echo "long running command"', 'task'])
    assert result.exit_code == 0
    assert 'Task task running for' in result.output
    assert capfd.readouterr()[0] == 'long running command\n'


def test_run_event_already_running(tmpdir):
    test_dir = tmpdir.join('test').strpath
    copytree('tests/data/test', test_dir)
    runner = CliRunner()
    result = runner.invoke(cli, ['--directory', test_dir, 'run', 'task2'])
    assert isinstance(result.exception, TaskRunningError)
    assert result.exception.args[0] == 'Task task is already started!'


def test_run_failed_command(tmpdir):
    test_dir = tmpdir.join('test').strpath
    copytree('tests/data/test_not_running', test_dir)
    runner = CliRunner()
    result = runner.invoke(cli, ['--directory', test_dir, 'run', '-c',
                                 '( exit 50 )', 'task'])
    assert isinstance(result.exception, OSError)
    assert result.exception.args == (50, 'Command failed')


def test_run_with_file_message(capfd, tmpdir):
    test_dir = tmpdir.join('test').strpath
    msg_file = tmpdir.join('message').strpath
    with open(msg_file, 'w') as f:
        f.write('stopping message')
    copytree('tests/data/test_not_running', test_dir)
    runner = CliRunner()
    result = runner.invoke(cli, ['--directory', test_dir, 'run', '-F',
                                 msg_file, '-c',
                                 'echo "long running command"', 'task'])
    assert result.exit_code == 0
    assert 'Task task running for' in result.output
    with tmpdir.join('test', 'task.csv').open() as f:
        assert f.read().endswith('stopping message\n')
    assert capfd.readouterr()[0] == 'long running command\n'


def test_run_interactive(monkeypatch, tmpdir):
    monkeypatch.setattr('click.edit',
                        lambda s, **kwargs: 'interactive message')
    test_dir = tmpdir.join('test').strpath
    copytree('tests/data/test_not_running', test_dir)
    runner = CliRunner()
    result = runner.invoke(cli, ['--directory', test_dir, '--interactive',
                                 'run', '-c', 'echo "long running command"',
                                 'task'])
    assert result.exit_code == 0
    assert 'Task task running for' in result.output
    with tmpdir.join('test', 'task.csv').open() as f:
        assert f.read().endswith('interactive message\n')


def test_wrapper_no_config():
    runner = CliRunner()
    result = runner.invoke(cli, ['--config', 'tests/data/defaults.ini',
                                 'wrapper', 'calendar'])
    assert isinstance(result.exception, SystemExit)
    assert "No such wrapper 'calendar'" in result.output


def test_wrapper_run_command(capfd, tmpdir):
    test_dir = tmpdir.join('test').strpath
    copytree('tests/data/test_not_running', test_dir)
    runner = CliRunner()
    result = runner.invoke(cli, ['--config', 'tests/data/wrappers.ini',
                                 '--directory', test_dir,
                                 'wrapper', 'calendar'])
    assert result.exit_code == 0
    assert 'Task task running for' in result.output
    with tmpdir.join('test', 'task.csv').open() as f:
        assert len(f.read().splitlines()) == 4
    assert 'May 2011' in capfd.readouterr()[0]


def test_report():
    runner = CliRunner()
    result = runner.invoke(cli, ['--directory', 'tests/data/test_not_running',
                                 'report'])
    assert result.exit_code == 0
    assert 'task    2:00:00' in result.output


def test_report_stats():
    runner = CliRunner()
    result = runner.invoke(cli, ['--directory', 'tests/data/test_not_running',
                                 'report', '--stats'])
    assert result.exit_code == 0
    assert 'Duration of events 2:15:00' in result.output


def test_report_event_running():
    runner = CliRunner()
    result = runner.invoke(cli, ['--directory', 'tests/data/test', 'report'])
    assert result.exit_code == 0
    assert 'Task “task” started 2011-05-04T09:30:00Z' \
        in result.output.splitlines()


@mark.parametrize('database, expected', [
    ('test', 'Task “task” started'),
    ('test_not_running', 'No task is running!'),
])
def test_running(database: str, expected: str):
    runner = CliRunner()
    result = runner.invoke(cli, ['--directory', 'tests/data/' + database,
                                 'running'])
    assert result.exit_code == 0
    assert expected in result.output


@mark.parametrize('database, expected', [
    ('test', 'Task task is still running'),
    ('test_not_running', 'Last task task, ran for 1:00:00'),
])
def test_last(database: str, expected: str):
    runner = CliRunner()
    result = runner.invoke(cli, ['--directory', 'tests/data/' + database,
                                 'last'])
    assert result.exit_code == 0
    assert expected in result.output


def test_ledger():
    runner = CliRunner()
    result = runner.invoke(cli, ['--directory', 'tests/data/test_not_running',
                                 'ledger'])
    assert result.exit_code == 0
    assert '2011-05-04 * 09:30-10:30' in result.output


def test_ledger_running():
    runner = CliRunner()
    result = runner.invoke(cli, ['--directory', 'tests/data/test', 'ledger'])
    assert result.exit_code == 0
    assert ';; Running event not included in output!' in result.output


def test_main_wrapper(monkeypatch, capsys):
    monkeypatch.setattr('sys.argv', ['rdial', '--directory', 'tests/data/test',
                                     'running'])

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
    monkeypatch.setattr('sys.argv', ['rdial', '--directory',
                                     'tests/data/test_not_running', 'stop'])

    def exit_mock(n):
        if n == 0:
            return n
        else:
            raise ValueError(n)
    monkeypatch.setattr('sys.exit', exit_mock)
    result = main()
    assert result == 2
    assert capsys.readouterr()[0] == 'No task running!\n'


def test_main_wrapper_informative_return_code(capsys, monkeypatch, tmpdir):
    test_dir = tmpdir.join('test').strpath
    copytree('tests/data/test_not_running', test_dir)
    monkeypatch.setattr('sys.argv', ['rdial', '--directory', test_dir, 'run',
                                     '-c', '( exit 50 )', 'task'])
    result = main()
    assert result == 50
    assert 'Task task running for' in capsys.readouterr()[0]
