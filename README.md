# knowledge Graph Generator

Knowledge Graph Generator - A way to create a node graph to visualize connections between data. The program is written in python 3.9.2 and mainly uses pandas for data management. It has a simple UI interface (currently with some bugs) that lets you define data, nodes, and edges and also generate the files. The program itself does not visualize the data, but generate the necessary files to use a visulization tool like [Gephi](https://gephi.org/).

## Running the program

You have two options to run the program. Either run the executable in releases, or with python.

### Running with python

First you need to install the required libraries. To do this, run `python -m pip install -r requirements.txt`. After that you can run the program with `python main.py`.

## How it works

The program is sectioned into 5 sections:
* [Data](#data)
* [Data settings](#data-settings)
* [Node settings](#node-settings)
* [Edge settings](#edge-settings)
* [Generate Graph](#generate-graph)

### Data

In this section it lets you define what files you want to import. It will let you import multiple files, but in the current version it only uses the first one. If a file is removed from the data section, it will not remove all the connected nodes and edges to that file in the current version.

So a rule of thumb: Only use 1 file (as of the beta version)

### Data settings

In this section it lets you define what the column types are. To sets the data columns, just click the file in the datapane on the left. The settings menu is a little buggy, so you might need to click the datafile a few times before the column settings want to behave properly. There are only a couple of options as of right now: *integer*, *float*, *string*, and *boolean*. All columns are read as strings when the program launches, so make sure to change the column types before you get data from it if you want to do more data processing on it later.

### Node settings

In this section it lets you define what nodes you want. Select the datafile you want in the pane on the left, and the nodes you can add shows up on the bottom. The select node pane is a list of your columns that you can set as nodes. When you check a column of as a node, it appears in the node pane on the left.

### Edge settings

In this section it lets you define edges from the nodes you have added. This menu is also a little buggy, so you might need to click a node a few times before the menu behaves properly. In the menu under the node pane to the left, and edge pane to the right, you see your selected node on the bottom, and a box to select other nodes on the right. Under you can select if you want the edge to be directional or not.

### Generate Graph

In this section you define the output files for the program. Here you set the path for the nodeFile and edgeFile. A warning about setting the node and edge file is that it will reset the file to 0 bytes, so be sure not to overwrite any files you want. To generate the files after setting the path for the node and edge path, just hit the *Generate Graph* button. This make take some time depending on the size of the data and the amount of nodes and edges, but usually finishes in under 15 seconds.

## Known Bugs

These are the known bugs:
* Settings menues not acting correctly before they have been clicked a few times.
* Edges are only removed visually, but are not actually removed.
* Nodes are only removed visually, but are not actually removed.

## Plan moving forward

The plan forward is to continue to fix and develop the frontend, and hopefully switch over to [eel](https://github.com/python-eel/Eel) - a python library to use HTML and JS as GUI for apps - and add more options for having metadata in the nodes and edges.

## How to contribute

If you find something you want to change, please feel free to create a pull request with the changes you have created. If you do not have the time to implement the changes yourself, you can add it as an issue such that we can add it to the development plan.
