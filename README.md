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


