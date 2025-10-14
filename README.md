# TennisToLiquipedia
Python Jupyer Notebook script to convert results from the ATP website into Liquipedia wiki code
(Semi-scrapping tool using the info from the [ATP Tournaments](https://www.atptour.com/en) website)

It is made for ATP Men tournaments with a Best of 5 Sets series and using 128 players.

Currently it retrieves the following information:
- Player name (First letter + surname)
- Nationality of player (flag)
- Score per set
  - When Set 4/5 is not played it will add |finished=skip

Current "bugs" / still to do:
- A walkover win is not noted, the match will stay as unfinished on Liquipedia, it will require manually adding |score=W/|score=FF on that match.
- Tiebreak scores are not shown, since we don't have a display for it on the lab/commons wiki iirc.
- Make the amount of start players more dynamic
  - Dynamic Version added, see "Main Script" file.
- Make the amount of BoX dynamic

## Current Options
- Set amount of players in the bracket in the settings:
  - 128 Players (Grand Slam Events)
  - 96 Players (To-Do)
  - 64 Players
  - 32 Players (ATP 500/1000 Events for example)
  - 28 Players (4x 1st round bgye, ATP 250)
- Change BoX in the settigs
- Change Full name or Short name in the settings

# Installation
For the use of this file Jupyter Notebook is required.
I use it from the [Anaconda Navigator](https://www.anaconda.com/products/navigator) package (once installed open JupyterLab)

# Usage Guide
## Cell Information
The notebook will contain 3 cells:
1. Import of libraries
2. Input cell for the copied HTML Code
3. Code to check the input and output the wikicode.

## How to use
1. Go to your desired tournament on the ATP website, for example Wimbledon and go to the draw, in the URL you can change the year.
2. Example event: https://www.atptour.com/en/scores/archive/wimbledon/540/2021/draws
3. Go to round of 128
4. Go to your dev tools and select the left of the 1st round, you will likely select class=draw draw-round-1 (red box)
5. Click in the dev screen on the mother container, with the class called "atp-draw-container" (white box)
6. CTRL+C (Copy the code)
7. Go to your notebook and dump the code in the 2nd cell, between the brackets.
8. Run the cell, and the cell after this.
9. If everything went correctly the code will be outputed and you can copy it to use it on Liquipedia.
<hr/>
<img width="1730" height="772" alt="image" src="https://github.com/user-attachments/assets/958daf17-ea39-45ea-947c-1619a9c04477" />
<hr/>
