# maskDatacardBins
Small tool to remove requested bins from a CMS Combine datacard

To mask bins in a single datacard run:
```
python maskBins.py  < path to datacard >  < space separated list of bin numbers ( counting from 1 ) >
```

To mask bins for all datacards in a given directory run:
```
python maskBinsForAllCards.py < path to directory > < space separated list of bin numbers ( counting from 1 ) >
```
