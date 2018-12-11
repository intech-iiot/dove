# Dove
### A docker versioning extension

Have the static tagging mechanism of docker bugged you and prevented you from creating flawless and incrementally versioned CD/CI of docker images? Well then you may like this tool. 

### What it does?

You keep a docker tag template and a version in a configuration file and you use this toolkit, which can automatically increment the version stored in the configuration file when building and tagging the image, and automatically pick the full tag when saving and deploying the image. How does it help? Well you combine it with git and you got yourself a flawless CD/CI without any hardcoded tags.

## Installation

You'd need docker(duh), python3 and pip3 (for python3). Simply clone the repository and do a
```
pip install dove-docker
```
inside the cloned repository.

## Usage

Like docker, it's a command-line tool. Do a `dove` on the shell to display all the help.

```
Usage: dove [OPTIONS] COMMAND [ARGS]...

  A docker versioning extension that manages docker tags through a JSON
  file, so that the user doesn't have to get into the hassle of writing and
  updating image tags.

  Maintained by: Intech A&I

  For more info, visit:

      https://github.com/intech-iiot/dove

Options:
  --help  Show this message and exit.

Commands:
  build  Build the docker image with saved tag
  bump   Just bump up the current version
  get    Get the current tag from the config
  new    Initialize a new dove config
  push   Push the image with tag saved in the config
  reset  Reset the version at position(s) to 0
  save   Save an image with the tag from the config
  tag    Tag another image with the saved tag

```

## Create new config

The tool requires a `dove.json` configuration file to be placed with the Dockerfile. This file can be created by executing the following on shell:

```
dove new -t my-repo/my-image:{0}.{1}.{2} -i 3.2.1
```

The `-t` puts a tag template with string positional parameters and the `-i` puts an initial version for the image.

## View current tag

After creating the configuration file, run the following in the directory with rhe configuration file:

```
dove get
```

This will show `my-repo/my-image:3.2.1` for the above configuration. Evidently, the version is split using a dot(.) and the components are substituted on the positional parameters. Ofcourse you can use the tag in other commands such as: 

```
docker image inspect $(dove get)
```


## Building the image with current tag

For this, a dockerfile must be present with the dove configuration. Do a:

```
dove build
```

This will start building the docker image with the current tag from the configuration file. To bump up the version, do a:

```
dove build --bump 0
```

This will increment the portion of the version that is supposed to replace the positional parameter at {0}. Similarly, to bump up multiple portions, do a:

```
dove build --bump 0 --bump 1
```

## Just bumping up the tag

if you're inclined to use the docker cli commands yourself, you can still use the configuration and its version bumping features by bumping the version manually. To do so, do a:

```
dove bump --position 0
```

This will update the version in the configuration and return the bumped up tag in the stdout, which can be nested in a docker command itself e.g.

```
docker build -t $(dove bump --position 0) ./
```

or you can simply get the tag afterwards

```
docker build -t $(dove get) ./
```

## Reseting version in tag

You can also reset the version number at any position by:

```
dove reset --position 0
```

This will reset the version number at position 0, which is useful if you follow a major-minor release cycle since a major release bump means a reset of the minor release version to 0.

## Tagging an existing image

An existing image can be tagged with a dove configuration. To do so, do a:

```
dove tag -s source-image-tag
```

The source-image will be tagged with the tag inferred from the configuration file in the current context

## Saving the image

To save the image with the inferred tag from the configuration, do a:

```
dove save -f filename
```

## Pushing the image

If the tag format contained a remote repo, I also have implemented a push function. To do so, simply do a:

```
dove push
```

## Docker arguments

The `dove build` and `dove push` commands can be provided with `docker build` and `docker push` command-line arguments through the `--args` or `-a` argument. For example:

```
dove build -a --pull
```

or 

```
dove build -a --pull -a --no-cache -a --label=pickle-rick
```

Yeah I know, it's pretty repetitive, and you can only use the long version with `=`, but I didn't know any other way of separating the dove and docker command line args. At least it's better than nothing.

## Alternate Tag Formats

From version 0.0.3 onwards commands and parameters for maintaining alternate tag formats was introduced. What this means is that the `dove.json` can contain more than one tag format in which the version is substituted. This is done by keeping a primary tag format and maintaining a name-value pair of alternate tag formats. These tags can be used in the other commands by means of a `-l` or `--alt` flag. This is very useful for multi-stage builds. You can have a different tag with the same version for different builds by using this.

### Adding a new alternate tag format

To add a new alternate tag to the existing `dove.json` configuration, do a:

```
dove add-alt -l my-alt-tag my-repo/my-image:{0}.{1}.{2}
```

### Viewing all the alternates

To view the alternates that were added to the configuration file, do a: 

```
dove alts
```

### Removing an alternate tag format

An alternate can be removed through it's name by doing a:

```
dove remove-alt -n my-alt-tag
```

### Using alternate tags in the other commands

Any command that uses tags from the configuration file has an existing flag `-l` or `--alt` which is used to specify the name of the alternate you itend to use. For example, to build an image with an alternate tag, do a: 

```
dove build -l my-alt-tag
```

## Contributing

I'm strictly not a python programmer and really did it as a side project so I can make some pretty streamlined CD/CI. I'd really appreciate if you want to contribute to this little utility of mine.
