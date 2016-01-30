# Getting setup

The quickest way to get the project setup for development is to use 
[virtualenvwrapper] and then:

```shell
$ mkvirtualenv gocd
$ make develop
```
  
This will install all dependencies and setup a git hook that'll ensure you
can't push unless you're compliant with PEP8.

## Style

This project aims to follow the [Google Python Style Guide][gpsg] and
particularly the section on [commenting the code][commenting].

## Linting

This project follows [PEP8] and uses [flake8] to check the code for violations.
There's also a linter in place for ReStructured Text files.

To run the linting do:

```shell
$ make lint
```

## Commit messages

Follow Tim Pope's style on how to write [good commit messages.][commit]

# Making a release

* Update CHANGELOG.rst with the changes going in
* Run linting (make lint)
* Update the version number according to [semver].
  ($ bumpversion <major|minor|patch>)
* Push the branch and the tag (git push && git push --tags)
* Add a release on GitHub and set the entries from the changelog in the 
  [release](https://github.com/gaqzi/py-gocd/releases). 
* After successfully building click the "Release to Pypi" stage on Snap

[virtualenvwrapper]: https://virtualenvwrapper.readthedocs.org/en/latest/
[gpsg]: https://google-styleguide.googlecode.com/svn/trunk/pyguide.html
[commenting]: https://google-styleguide.googlecode.com/svn/trunk/pyguide.html?showone=Comments#Comments
[commit]: http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html
[semver]: http://semver.org/
