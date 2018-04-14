import os
import json
import click
import subprocess

CONFIG_FILE = 'dove.json'
__location__ = os.path.realpath(os.path.join(os.getcwd()))


def default_path():
  return os.path.join(__location__, CONFIG_FILE)


def read_config(path=None):
  if path is None:
    path = default_path()
  with open(path) as version_file:
    return json.load(version_file)


def write_config(config, path=None):
  if path is None:
    path = default_path()
  with open(path, 'w') as version_file:
    version_file.write(json.dumps(obj=config, indent=4, sort_keys=True))


def update_version(version, pos):
  components = version.split('.')
  for position in pos:
    components[position] = str(int(components[position]) + 1)
  return components


def reset_version(version, pos):
  components = version.split('.')
  for position in pos:
    components[position] = '0'
  return components


def to_version_string(components):
  version = ''
  for i in range(0, len(components)):
    version += components[i]
    if i != len(components) - 1:
      version += '.'
  return version


def validate_config(config):
  if config is None:
    click.echo('Error: The json configuration was not found')
  if 'version' not in config or 'format' not in config:
    click.echo('Error: The json configuration is invalid')
    return


def extend_command(*args):
  command = None
  for arr in args:
    if command is None:
      command = arr
    else:
      command.extend(arr)
  return command


@click.group(name='dove')
def cli():
  """A docker versioning extension that manages docker tags
     through a JSON file, so that the user doesn't have to
     get into the hassle of writing and updating image tags.\n
     Maintained by: Intech A&I \n
     For more info, visit: \n
     \t https://github.com/intech-iiot/dove
     """
  pass


@click.command(name='build')
@click.option('--position', '-p', multiple=True,
              help='Version position(s) to bump')
@click.option('--args', '-a', multiple=True,
              help='Docker build arguments (Except --tag, -t)')
@click.option('--cfgpath', '-c', help='Path to the json configuration file',
              type=click.Path())
def build(position, args, cfgpath):
  """Build the docker image with saved tag"""
  try:
    config = read_config(cfgpath)
    validate_config(config)
    old_version = config['version']
    version_parts = old_version.split('.')
    if position is not None:
      version_parts = update_version(old_version, map(int, position))
      config['version'] = to_version_string(version_parts)
    new_tag = config['format'].format(*version_parts)
    click.echo('Using tag: [{}]'.format(new_tag))
    command = extend_command(['docker', 'build'], args, ['-t', new_tag, './'])
    subprocess.check_call(command, cwd=str(__location__))
    write_config(config, cfgpath)
  except BaseException as e:
    click.echo(str(e))


@click.command(name='tag')
@click.option('--srcimg', '-s', help='Tag of the source image', required=True)
@click.option('--position', '-p', multiple=True,
              help='Version position(s) to bump')
@click.option('--cfgpath', '-c', help='Path to the json configuration file',
              type=click.Path())
def tag(srcimg, position, cfgpath):
  """Tag another image with the saved tag"""
  try:
    config = read_config(cfgpath)
    validate_config(config)
    old_version = config['version']
    version_parts = old_version.split('.')
    if position is not None:
      version_parts = update_version(old_version, map(int, position))
      config['version'] = to_version_string(version_parts)
    new_tag = config['format'].format(*version_parts)
    click.echo('Using tag: [{}]'.format(new_tag))
    command = ['docker', 'tag', srcimg, new_tag]
    subprocess.check_call(command, cwd=str(__location__))
    write_config(config, cfgpath)
  except BaseException as e:
    click.echo(str(e))


@click.command(name='new')
@click.option('--template', '-t', help='Image name template', required=True)
@click.option('--initial', '-i', help='The initial version to start from',
              required=True)
@click.option('--cfgpath', '-c', help='Path to the json configuration file',
              type=click.Path())
def create_new(template, initial, cfgpath):
  """Initialize a new dove config"""
  try:
    new_config = dict()
    new_config['format'] = template
    new_config['version'] = initial
    write_config(new_config, cfgpath)
    click.echo('New config generated: \n' +
               json.dumps(obj=new_config, indent=4, sort_keys=True))
  except BaseException as e:
    click.echo(str(e))


@click.command(name='get')
@click.option('--version', '-v', help='Just get the version', is_flag=True)
@click.option('--cfgpath', '-c', help='Path to the json configuration file',
              type=click.Path())
def get_tag(version, cfgpath):
  """Get the current tag from the config"""
  try:
    config = read_config(cfgpath)
    validate_config(config)
    if version is True:
      click.echo(config['version'])
    else:
      version = config['version'].split('.')
      tag = config['format'].format(*version)
      click.echo(tag)
      return tag
  except BaseException as e:
    click.echo(str(e))


@click.command(name='push')
@click.option('--args', '-a', multiple=True, help='Docker command arguments')
@click.option('--cfgpath', '-c', help='Path to the json configuration file',
              type=click.Path())
def push(args, cfgpath):
  """Push the image with tag saved in the config"""
  try:
    config = read_config(cfgpath)
    validate_config(cfgpath)
    version = config['version'].split('.')
    tag = config['format'].format(*version)
    click.echo("Pushing image: [{}]".format(tag))
    command = extend_command(['docker', 'push'], args, [tag])
    subprocess.check_call(command, cwd=str(__location__))
  except BaseException as e:
    click.echo(str(e))


@click.command(name='bump')
@click.option('--position', '-p', multiple=True,
              help='Version position(s) to bump', required=True)
@click.option('--cfgpath', '-c', help='Path to the json configuration file',
              type=click.Path())
def bump(position, cfgpath):
  """Just bump up the current version"""
  try:
    config = read_config(cfgpath)
    validate_config(config)
    old_version = config['version']
    version_parts = old_version.split('.')
    if position is not None:
      version_parts = update_version(old_version, map(int, position))
      config['version'] = to_version_string(version_parts)
    write_config(config, cfgpath)
    new_tag = config['format'].format(*version_parts)
    click.echo(new_tag)
  except BaseException as e:
    click.echo(str(e))


@click.command(name='reset')
@click.option('--position', '-p', multiple=True,
              help='Version position(s) to reset', required=True)
@click.option('--cfgpath', '-c', help='Path to the json configuration file',
              type=click.Path())
def reset(position, cfgpath):
  """Reset the version at position(s) to 0"""
  try:
    config = read_config(cfgpath)
    validate_config(config)
    old_version = config['version']
    version_parts = old_version.split('.')
    if position is not None:
      version_parts = reset_version(old_version, map(int, position))
      config['version'] = to_version_string(version_parts)
    write_config(config, cfgpath)
    new_tag = config['format'].format(*version_parts)
    click.echo(new_tag)
  except BaseException as e:
    click.echo(str(e))


@click.command(name='save')
@click.option('--filepath', '-f', help='Path to file where to save the image',
              required=True)
@click.option('--cfgpath', '-c', help='Path to the json configuration file',
              type=click.Path())
def save(filepath, cfgpath):
  """Save an image with the tag from the config"""
  try:
    config = read_config(cfgpath)
    validate_config(config)
    version = config['version'].split('.')
    tag = config['format'].format(*version)
    command = ['docker', 'save', '-o', filepath, tag]
    subprocess.check_call(command, cwd=str(__location__))
  except BaseException as e:
    click.echo(str(e))


cli.add_command(build)
cli.add_command(tag)
cli.add_command(create_new)
cli.add_command(push)
cli.add_command(get_tag)
cli.add_command(save)
cli.add_command(bump)
cli.add_command(reset)
