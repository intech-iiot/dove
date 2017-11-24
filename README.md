# Dove
### A docker versioning extension

Have the static tagging mechanism of docker bugged you and prevented you from creating flawless and incrementally versioned CD/CI of docker images? Well then you may like this tool. 

### What it does?

You keep a docker tag template and a version in a configuration file and you use this toolkit, which can automatically increment the version stored in the configuration file when building and tagging the iamge and automatically pick the full tag when saving and deploying an image. How does it help? Well you combine it with git and you got yourself a flawless CD/CI without any hardcoded tags.

## Installation

You'd need python3 and pip. Simply clone the repository and do a
```
sudo -H pip install ./
```
inside the cloned repository.

## Usage

Like docker, it's a command-line tool. Do a `dove` on the shell to display all the help.

```
Usage: dove [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  build  Used to call docker build
  get    Gets the current tag of the image
  new    Used to initialize a new dove configuration
  push   Used to call docker push
  save   Used to call a docker save
  tag    Used to call docker tag

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

This will show `my-repo/my-image:3.2.1` for the above configuration. Evidently, the version is split using a dot(.) and the components are substituted on the positional parameters.


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

## Contributing

I'm strictly not a python programmer and really did it as a side project so I can make some pretty streamlined CD/CI. I'd really appreciate if you want to contribute to this little utility of mine.
