# Hansard interjections

Here's some code to extract and analyse interjections from the [Hansard XML repository](https://github.com/wragge/hansard-xml). The repository covers the House of Representatives and Senate from the period 1901 to 1980, and was harvested from ParlInfo.

981,706 interjections were extracted from the XML files. You can download a [CSV file](https://www.dropbox.com/s/edk5w3ccbmhf7sh/interjections.zip?dl=0) (45mb zip file) containing all the interjections here. The Hansard OCR and markup isn't perfect so it's likely some will have been missed (and that some things identified as interjections really aren't).

The `list_interections` function will search interjections and list the results in markdown-formatted tables. For example:

* [Interjections less than 50 characters long including the word 'white'](https://gist.github.com/wragge/4d348aaedd7d6942f2727990e5b66e45)
* [Interjections less than 50 characters long including the word 'fascist'](https://gist.github.com/wragge/d205e949855fc697b9f6928a4c0c9a43)

The `top_interjectors` function produces something like this:

```

    TOP INTERJECTORS, HOUSE OF REPRESENTATIVES, 1901-80
    ==============================================+====

    COOK, Joseph                   22299 interjections
    PEARCE, George                 20542 interjections
    MILLEN, Edward                 17367 interjections
    FORREST, John                  12990 interjections
    SYMON, Josiah                  12883 interjections
    LYNE, William                  10085 interjections
    HUGHES, William Morris         9446 interjections
    GOULD, Albert                  8819 interjections
    FISHER, Andrew                 8802 interjections
    WRIGHT, Reginald               8393 interjections
    TUDOR, Frank                   8340 interjections
    GROOM, Littleton               8182 interjections
    WATSON, John Christian         8123 interjections
    DEAKIN, Alfred                 7820 interjections
    BEST, Robert                   7731 interjections
    PAGE, James                    7491 interjections
    DE LARGIE, Hugh                6792 interjections
    NEILD, John                    6788 interjections
    MCGREGOR, Gregor               6585 interjections
    GUTHRIE, Robert                6447 interjections

```

To explore the interjections reimagined as tweets -- naturally! -- have a look at [Real Words :: Imagined Tweets](http://hansard-interjections.herokuapp.com/tweets/).