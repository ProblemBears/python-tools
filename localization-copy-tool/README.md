# Documentation

## Docker
- Clone the Repo
- Install Docker
- In the folder `localization-copy-tool` place your `Game.po` and `.xlsx` file (the name doesn't matter) into a folder that MUST be called `translations`
- Open a terminal at the location of the folder `localization-copy-tool`
- Run the following commands :
 - `docker-compose build` - Will output a lot of info. It generates a container at the end, do the next command when it finishes.
 - `docker-compose run po-translator` - Runs the Actual program
- There is text UI that guides you on what can be done. Type the number of the command you want to run after the `Enter yoiur choice :` text

## Todo Python venv or Executable