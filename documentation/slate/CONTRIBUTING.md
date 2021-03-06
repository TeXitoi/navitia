# Contributing to the documentation

Navitia.io documentation is built using [Slate](https://github.com/tripit/slate).

These sources are published to [http://canaltp.github.io/navitia](http://canaltp.github.io/navitia).


## Editing documentation content

All documentation is in `includes` directory, and uses Markdown text format,
plus some Slate widgets (such as notices).


## Preview changes

Once some changes has been done, Slate needs to build HTML sources from Markdown files.

First, check that Slate dependencies are installed:

``` bash
cd documentation/slate
bundle install
```

Then build the documentation:

``` bash
cd documentation/slate
bundle exec middleman build
```

That will generate a `build/` folder with an `index.html` inside which is the doc.

Just open `documentation/slate/build/index.html` to see how it will be published.
