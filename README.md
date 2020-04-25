# Flask Boom

Flask Boom is a CLI for creating flask projects and generating modules within the project. This all came to be when I was not content with the project generation in Jetbrains PyCharm for flask projects.
With some inspiration taken from Angular's ng CLI, the goal of Boom is to streamline the process of generating projects and modules within the project.

Flask Boom uses templates to create projects. At the moment there are two kinda of templates included (app based and functional based). I plan to add more and more variations of the two (i.e. REST APIs, GraphQL APIs, etc.).

## In Development

This project is still a work in progress and I **DO NOT** recommend using it in a production environment. Feel free to contribute in the mean time.

## Documentation

Flask Boom works using templates to define how projects are structured.

### Creating Templates

**_(Coming Soon)_**

### Template variables
The Jinja Templating language is used, more details on exactly how to use it can be found here 
[Jinja Docs](https://jinja.palletsprojects.com)

##### Globally Available Variables

| Variable Name        | Type           | Example                        | Description                          |
| -------------------- |:--------------:|:------------------------------:| ------------------------------------ |
| project_name         | String         | `My Project`                   | The human friendly name of the project
| project_name_path    | String         | `my-project`                   | The project name in a path safe string
| project_description  | String         | `A test project :D`            | Description of the project             
| required_packages    | String[]       | `['flask', 'jinja2']`          | Array of required python packages     
| author_name          | String         | `Tom Grozev`                   | Name of the author                    
| author_url           | String         | `https://github.com/TomGrozev` | URL to author github, website, etc.   
| project_root         | String         | `/home/tom/dev/my-project`     | Absolute path to project root         


##### Module Available Variables

| Variable Name        | Type           | Example                        | Description                          |
| -------------------- |:--------------:|:------------------------------:| ------------------------------------ |
| module_name          | String         | `user`                         | The Name of the module (this can be plural)
| module_name_plural   | String         | `users`                        | The Name of the module as a plural (regardless if module_name is plural or not)


## Built With

* [Click](https://click.palletsprojects.com/) - The CLI Kit
* [PyInquirer](https://github.com/CITGuru/PyInquirer) - CLI questions

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/TomGrozev/flask-boom/tags). 

## Authors

* **Tom Grozev** - *Initial work* - [GitHub Page](https://github.com/TomGrozev)

See also the list of [contributors](https://github.com/TomGrozev/flask-boom/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Angular CLI for inspiration
* PurpleBooth's README Template

