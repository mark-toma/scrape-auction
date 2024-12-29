# auction-scrape


# Setup

Clone to your computer

```bash
# Navigate to parent directory for repo
git clone git@github.com:mark-toma/scrape-auction.git
cd scrape-auction
```

Add scripts directory to path.

```bash
cd path/to/scrape-auction # Navigate to repo root
echo "" >> ~/.bashrc
echo "# Add scrape-auction scripts directory to PATH" >> ~/.bashrc
echo "export PATH=$PATH:$(pwd)/scripts" >> ~/.bashrc
```

Make sure the script is executable.

```bash
cd path/to/scrape-auction # Navigate to repo root
chmod ug+x scripts/scrape-auction
```

Check for existence of script on PATH

```bash
which scrape-auction
# => /path/to/scrape-auction/scripts/scrape-auction
```

# Usage

## First run without any previous data

The following runs this script to generate an output file with data matching all combinations of
the provided make(s) and model(s). At least one make and model must be provided. 

```bash
scrape-auction --makes ford --models taurus # Defaults to output file data.csv
scrape-auction --outfile ford-taurus.csv --makes ford --models taurus
```

Multiple makes and/or models may be specified as well.

```bash
scrape-auction --outfile ford-taurus.csv --makes ford --models taurus fpis sedan
```

## Updating a prior run with new data

An existing data file cannot be overwritten unless it's also specified as the input file.

```bash
scrape-auction --infile ford-taurus.csv --outfile ford-taurus.csv --makes ford --models taurus fpis sedan
```

## Run headless or with Chrome webdriver

Both options require platform dependency. The Chrome driver is used by preference. For headless
operation, [XVFB](https://www.x.org/archive/X11R7.7/doc/man/man1/Xvfb.1.xhtml) must be installed on your system.

Add the flag `-n` or `--no-gui` to run in headless mode.

```bash
scrape-auction --no-gui --infile ford-taurus.csv --outfile ford-taurus.csv --makes ford --models taurus fpis sedan
```

## Example `crontab` definitions

This example uses `bash` with non-interactive `~/.bash_profile` to find `scrape-auction` and then
uses the `logger` utility to catch all output so that cron doesn't have issues with unhandled
output and lack of configured MTA on the system.

```shell
SHELL=/bin/bash
BASH_ENV=~/.bash_profile
0   3 * * * scrape-auction -n -i ford-taurus.csv   -o ford-taurus.csv   --makes ford  --models taurus fpis sedan   | logger -t scrape-auction
30  3 * * * scrape-auction -n -i dodge-charger.csv -o dodge-charger.csv --makes dodge --models charger interceptor | logger -t scrape-auction
0   4 * * * scrape-auction -n -i ford-escape.csv   -o ford-escape.csv   --makes ford  --models escape              | logger -t scrape-auction
30  4 * * * scrape-auction -n -i ford-focus.csv    -o ford-focus.csv    --makes ford  --models focus               | logger -t scrape-auction
```

# Interpreting data

The primary expected interaction with this data is to search the VIN for substrings identifying
specific vehicles of interest. This section documents these for each model and associated characteristics.

## Ford Police Interceptor Sedan (Taurus)

- Powertrain code `P2MT` in digits 5-8
  - AWD with 3.5 turbocharged engine
  - Code: `'p2mt' == vin.lower()[4-7]`

## Dodge Police Pursuit Vehicle (Charger)

- Vehicle code `CDXKT` in digits 4-8
  - AWD with 5.7 hemi engine
  - Code: `'cdxkt' == vin.lower()[3-7]`

## Ford Escape

- TODO
  - AWD with 2.0 turbocharged engine

## TODO:

https://www.reddit.com/r/MechanicAdvice/comments/qkl53z/how_to_tell_if_a_vehicle_is_equipped_with_police/?captcha=1

Consider adding the fusion to the search list based on enginer availability?
