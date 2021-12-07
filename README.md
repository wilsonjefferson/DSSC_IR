# DSSC: Information Retrieval
In this repo you will find information on Information Retrieval course attended at Trieste University. In details,this is the project folder containing an implementation of the Quasi-Real Music Recommender System, well summarized by the pdf presentation.

The aim of this project is develop a Recommender System, but here 4 different Recommender Systems are proposed:
- **RelevanceBasedRS** - It is a, so called, Cold Start Recommender System providing N items to the user according a certain set of fields about the feature of the items themself;
- **CoolStartRS** - It is a Recommender System based just on the current item and the features of all the items;
- **WeightedMFRS** - It is a Recommendr System implementing the WALS algorithm;
- **UserBasedRS** - It is a Recommender System implementing a collaborative recommendation among the users.

Those RSs are mixed together to provide the best possible set of recommendation to the end-user.
## Structure of the Git Folder
The project folder is organized in several directories, here there is a short explanation of those:
- Folder `core` - contains the core of the project such as the tables, recommender systems and so on;
- Folder`data_manipulation` - contains scripts to manipulate the row datasets and obtain the processed data;
- `exceptions` - contains exceptions that may occurred during the execution of the program, and warnings to allert the user about something relevant but not fatal for the correct execution of the program;
- `sources` - contains the data used in this project;
- `tests` - contains the tests implemented for some classes in the core folder.
And the following files:
- `main.py` - the main python script, to run the project run this file;
- `requirements.txt` - txt file containing the requirements for this project.

> ATTENTION
> 
> - `sources` is not present because some of the data used are from Yahoo Music and they cannot shared,
> to request this data visit the [Yahoo Music](https://webscope.sandbox.yahoo.com/catalog.php?datatype=r&guccounter=1&guce_referrer=aHR0cHM6Ly9naXRodWIuY29tL2Nhc2VyZWMvRGF0YXNldHMtZm9yLVJlY29tbWVuZGVyLVN5c3RlbXM&guce_referrer_sig=AQAAAN7Rd9jwCX7K1RAoHy0O-E4Y0cUUn8QcWM0yc7VjxbnRtRONGrG52TDRggfsMBvPjpANTkyOo1tzLtourTvc5PBpNETew-JPPnTLovfgtNmZnQ4ZO0L0T4YoofnxKE5J_Pxho1j413SRUfNNsTxVcgewZbdR45h19YdaatKjRvB6) webpage and submit a request.
> - this project use a sql database called located in ./sources/user_dataset.db, so if you want to run this project you need to define the source folder with this database.

## Data
For this project two dataset are taken from external sources:
- `SpotifyFeatures.csv` from [Kaggle](https://www.kaggle.com/zaheenhamidani/ultimate-spotify-tracks-db), it contains the fetures of each songs like author, name, and also technical information about the songs;
- `Ratings.csv` from [Yahoo Music](https://webscope.sandbox.yahoo.com/catalog.php?datatype=r&guccounter=1&guce_referrer=aHR0cHM6Ly9naXRodWIuY29tL2Nhc2VyZWMvRGF0YXNldHMtZm9yLVJlY29tbWVuZGVyLVN5c3RlbXM&guce_referrer_sig=AQAAAN7Rd9jwCX7K1RAoHy0O-E4Y0cUUn8QcWM0yc7VjxbnRtRONGrG52TDRggfsMBvPjpANTkyOo1tzLtourTvc5PBpNETew-JPPnTLovfgtNmZnQ4ZO0L0T4YoofnxKE5J_Pxho1j413SRUfNNsTxVcgewZbdR45h19YdaatKjRvB6), it contains the ratings that users have given to songs.

Other two dataset are created from these datasets:
- `History.csv` from `Ratings.csv`, containing the history of each user, in particular songs they have listened;
- `User.csv` from `Ratings.csv`, containing artificial users;

These datasets are connected by means of primary keys, unfortunately there is no logical connection between `SpotifyFeatures.csv` and `Ratings.csv` since it was possible to find proper datasets.
In any case, it is not a big problem since data from Yahoo are anonymized and we are interested just on the implementation of Recommender Systems.

## Running the program
After having set the requirements, just run the `main.py` script. At the first stage the database is filled with the data from the csv files (safe storage) and then the program continue to use the database as data source.
When the program is finished, the csv are not updated but the database persist.