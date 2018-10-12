import os
import json
import click
import subprocess
import sys

CONFIG_FILE = 'dove.json'
VERSION = 'version'
FORMAT = 'format'
ALTERNATE = 'alternate_formats'

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


def get_update_tag_from_config(config, position=None, alt=None):
  old_version = config[VERSION]
  version_parts = old_version.split('.')
  if position is not None:
    version_parts = update_version(old_version, map(int, position))
    config[VERSION] = to_version_string(version_parts)
  if alt is not None:
    if alt not in config[ALTERNATE]:
      raise ValueError('Error: No alternate tag found for name ' + alt)
    return config[ALTERNATE][alt].format(*version_parts)
  return config[FORMAT].format(*version_parts)


def validate_config(config):
  if config is None:
    click.echo('Error: The json configuration was not found')
  if VERSION not in config or FORMAT not in config:
    click.echo('Error: The json configuration is invalid')
    return


def extend_command(*args):
  command = []
  for arg in args:
    if type(arg) is list or type(arg) is tuple:
      command.extend(extend_command(*arg))
    elif type(arg) is str or type(arg) is unicode:
      split = arg.split(' ')
      for part in split:
        command.append(part)
    else:
      raise ValueError('Unknown type specified in command')
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
@click.option('--alt', '-l', help='Alternate tag format to use')
def build(position, args, cfgpath, alt):
  """Build the docker image with saved tag"""
  try:
    config = read_config(cfgpath)
    validate_config(config)
    new_tag = get_update_tag_from_config(config, position, alt)
    click.echo('Using tag: [{}]'.format(new_tag))
    command = extend_command(['docker', 'build'], args, ['-t', new_tag, './'])
    subprocess.check_call(command, cwd=str(__location__))
    write_config(config, cfgpath)
  except BaseException as e:
    click.echo(str(e))
    sys.exit(1)


@click.command(name='tag')
@click.option('--srcimg', '-s', help='Tag of the source image', required=True)
@click.option('--position', '-p', multiple=True,
              help='Version position(s) to bump')
@click.option('--cfgpath', '-c', help='Path to the json configuration file',
              type=click.Path())
@click.option('--alt', '-l', help='Alternate tag format to use')
def tag(srcimg, position, cfgpath, alt):
  """Tag another image with the saved tag"""
  try:
    config = read_config(cfgpath)
    validate_config(config)
    new_tag = get_update_tag_from_config(config, position, alt)
    click.echo('Using tag: [{}]'.format(new_tag))
    command = ['docker', 'tag', srcimg, new_tag]
    subprocess.check_call(command, cwd=str(__location__))
    write_config(config, cfgpath)
  except BaseException as e:
    click.echo(str(e))
    sys.exit(1)


@click.command(name='new')
@click.option('--format', '-f', help='Image name string format', required=True)
@click.option('--initial', '-i', help='The initial version to start from',
              required=True)
@click.option('--cfgpath', '-c', help='Path to the json configuration file',
              type=click.Path())
@click.option('--alt', '-l',
              help='Alternate formats to add to the JSON configuration',
              type=click.Tuple([str, str]), multiple=True)
def create_new(format, initial, cfgpath, alt):
  """Initialize a new dove config"""
  try:
    new_config = dict()
    new_config[FORMAT] = format
    new_config[VERSION] = initial
    if alt is not None:
      alt_formats = dict()
      new_config[ALTERNATE] = alt_formats
      for name, alt_format in list(alt):
        alt_formats[name] = alt_format
    write_config(new_config, cfgpath)
    click.echo('New config generated: \n' +
               json.dumps(obj=new_config, indent=4, sort_keys=True))
  except BaseException as e:
    click.echo(str(e))
    sys.exit(1)


@click.command(name='get')
@click.option('--version', '-v', help='Just get the version', is_flag=True)
@click.option('--cfgpath', '-c', help='Path to the json configuration file',
              type=click.Path())
@click.option('--alt', '-l', help='Alternate tag format to use')
def get_tag(version, cfgpath, alt):
  """Get the current tag from the config"""
  try:
    config = read_config(cfgpath)
    validate_config(config)
    if version is True:
      click.echo(config[VERSION])
    else:
      tag = get_update_tag_from_config(config, alt=alt)
      click.echo(tag)
      return tag
  except BaseException as e:
    click.echo(str(e))
    sys.exit(1)


@click.command(name='push')
@click.option('--args', '-a', multiple=True, help='Docker command arguments')
@click.option('--cfgpath', '-c', help='Path to the json configuration file',
              type=click.Path())
@click.option('--alt', '-l', help='Alternate tag format to use')
def push(args, cfgpath, alt):
  """Push the image with tag saved in the config"""
  try:
    config = read_config(cfgpath)
    validate_config(config)
    tag = get_update_tag_from_config(config, alt=alt)
    click.echo("Pushing image: [{}]".format(tag))
    command = extend_command(['docker', 'push'], args, [tag])
    subprocess.check_call(command, cwd=str(__location__))
  except BaseException as e:
    click.echo(str(e))
    sys.exit(1)


@click.command(name='bump')
@click.option('--position', '-p', multiple=True,
              help='Version position(s) to bump', required=True)
@click.option('--cfgpath', '-c', help='Path to the json configuration file',
              type=click.Path())
@click.option('--alt', '-l',
              help='Alternate tag format to use when returning the tag')
def bump(position, cfgpath, alt):
  """Just bump up the current version"""
  try:
    config = read_config(cfgpath)
    validate_config(config)
    new_tag = get_update_tag_from_config(config, position, alt)
    write_config(config, cfgpath)
    click.echo(new_tag)
  except BaseException as e:
    click.echo(str(e))
    sys.exit(1)


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
    old_version = config[VERSION]
    version_parts = old_version.split('.')
    if position is not None:
      version_parts = reset_version(old_version, map(int, position))
      config[VERSION] = to_version_string(version_parts)
    write_config(config, cfgpath)
    new_tag = config[FORMAT].format(*version_parts)
    click.echo(new_tag)
  except BaseException as e:
    click.echo(str(e))
    sys.exit(1)


@click.command(name='save')
@click.option('--filepath', '-f', help='Path to file where to save the image',
              required=True)
@click.option('--cfgpath', '-c', help='Path to the json configuration file',
              type=click.Path())
@click.option('--alt', '-l', help='Alternate tag format to use')
def save(filepath, cfgpath, alt):
  """Save an image with the tag from the config"""
  try:
    config = read_config(cfgpath)
    validate_config(config)
    tag = get_update_tag_from_config(config, alt=alt)
    command = ['docker', 'save', '-o', filepath, tag]
    subprocess.check_call(command, cwd=str(__location__))
  except BaseException as e:
    click.echo(str(e))
    sys.exit(1)


@click.command(name='alts')
@click.option('--names', '-n', help='Just print the names of alternates',
              is_flag=True)
@click.option('--cfgpath', '-c', help='Path to the json configuration file',
              type=click.Path())
def alts(names, cfgpath):
  """Print all the alternates from the config"""
  try:
    config = read_config(cfgpath)
    validate_config(config)
    if ALTERNATE not in config or config[ALTERNATE] is None:
      click.echo('No alternates configured')
      sys.exit(1)
    for name in config[ALTERNATE]:
      if names:
        click.echo(name)
      else:
        tag = get_update_tag_from_config(config, alt=name)
        click.echo(name + '\t' + tag)
  except BaseException as e:
    click.echo(str(e))
    sys.exit(1)


@click.command(name='add-alt')
@click.option('--alt', '-l',
              help='Alternate formats to add to the JSON configuration',
              type=click.Tuple([str, str]), multiple=True, required=True)
@click.option('--cfgpath', '-c', help='Path to the json configuration file',
              type=click.Path())
def addalt(alt, cfgpath):
  """Add a new alternate tag format to the config"""
  try:
    config = read_config(cfgpath)
    validate_config(config)
    if ALTERNATE not in config or config[ALTERNATE] is None:
      alt_formats = dict()
      config[ALTERNATE] = alt_formats
    else:
      alt_formats = config[ALTERNATE]
    for name, alt_format in list(alt):
      alt_formats[name] = alt_format
    write_config(config, cfgpath)
  except BaseException as e:
    click.echo(str(e))
    sys.exit(1)


@click.command(name='remove-alt')
@click.option('--name', '-n', help='Name of the alternate', multiple=True,
              required=True)
@click.option('--cfgpath', '-c', help='Path to the json configuration file',
              type=click.Path())
def removealt(name, cfgpath):
  """Removes an alternate format from the config"""
  try:
    config = read_config(cfgpath)
    validate_config(config)
    if ALTERNATE not in config or config[ALTERNATE] is None:
      click.echo('No alternates configured')
      sys.exit(1)
    for alt_name in list(name):
      if alt_name not in config[ALTERNATE]:
        click.echo("No alternate found for name " + alt_name)
        exit(1)
      del config[ALTERNATE][alt_name]
    if len(config[ALTERNATE]) is 0:
      del config[ALTERNATE]
    write_config(config, cfgpath)
  except BaseException as e:
    click.echo(str(e))
    sys.exit(1)


cli.add_command(build)
cli.add_command(tag)
cli.add_command(create_new)
cli.add_command(push)
cli.add_command(get_tag)
cli.add_command(save)
cli.add_command(bump)
cli.add_command(reset)
cli.add_command(alts)
cli.add_command(addalt)
cli.add_command(removealt)
