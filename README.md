# nestris-leaderboard-tools

A large collection of things for scraping and parsing a very specific type of Google Sheet.

## Motivation

The [NES Tetris leaderboard](https://docs.google.com/spreadsheets/d/1ZBxkZEsfwDsUpyire4Xb16er36Covk7nhR8BN_LPodI/) contains the current high score ranking for top classic tetris players in a variety of categories. Over three and half years of usage, it's been updated almost 40,000 times. Since Google Drive stores revisions over time, it's theoretically possible to access the leaderboard at any point in time, providing rich historical data. However, access to this is complicated for several reasons; fetching previous revisions is clunky and slow, data can be disorganized, edits can be made haphazardly, and many other problems related to the ad-hoc nature of spreadsheets.

This repository contains tools meant to make this process easier by converting the spreadsheet history into a format that's easier to parse. Its main program is a gui which can display arbitrary versions of a spreadsheet in the collection and also show the differences between different versions. The scripts that I use to actually download and wrangle the data are also included.

## Setup

Before running the gui, you'll need to install `node.js` and `npm`, which you can find instructions for [here](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm). Once you have that, navigate your command line into this directory and execute the command `npm install`. This fetches all of the packages that it depends on.

From here, run `npm build` to finish setting up the gui.

The contents of the `scripts/` folder are all run using Python 3.10. The dependent packages can be found at the top of each file, which can be installed using something like `pip`.

## Usage

To start the gui, execute the command `npm run preview` on your command line, and go to the indicated link in your browser (it should be [http://localhost:4173/](http://localhost:4173/)). If you need to run it in development mode (e.g. you want to change the code and see results faster), then use `npm run build`. However, this is not recommended otherwise, as this slows down the program.

Once again, for anything found in `scripts/`, you're on your own for now, sorry. Documentation for that may come later, but its contents are basically for my use only.

## Data

Virtually all of the tools are useless without data to act on (indeed, most of them will probably crash without the presence of certain folders). As a very rough overview, it was collected by running `python scripts/scrape.py` with the appropriate parameters to download the html for specific spreadsheets, then running various iterations of `python scripts/parse.py` to auto-generate most everything else. There are some exceptions, e.g. `data/leaderboards.json` is hand constructed for the case of a leaderboard transferring across different sheets[^1].

The best way to get the data is probably to ask me to send it to you (I'm `fractal161` on Discord). Alternatively, you can run the commands manually, but this will take some time (scraping in particular is usually the better half of a day).

[^1]: This actually only happens once lol, but it's still good for trimming out unecessary data.
