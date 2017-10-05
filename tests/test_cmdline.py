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

from datetime import datetime
from shutil import copytree

from click import (BadParameter, command, echo, group, option, pass_context,
                   pass_obj)
from click.testing import CliRunner
from pytest import (mark, raises)

from rdial.cmdline import (HiddenGroup, StartTimeParamType, TaskNameParamType,
                           cli, get_stop_message, hidden, task_option)
from rdial.events import (Event, TaskNotRunningError, TaskRunningError)


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
def test_task_name_validity(string, expected):
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
def test_start_time_validity(string, expected):
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
def test_get_stop_message(edit_func, message, monkeypatch):
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
def test_colour_for_u_deficient(config, result):
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
    def raise_context(ctx, choice):
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
