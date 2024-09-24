""" Japanese Flask Application - dictionary.py

This file is used to deal with the Japanese-English dictionary data.

It populates and selects data from the database.

This script is imported by main_app.py when the main program is run.

The packages that should be installed to be able to run this file are:
bs4 (BeautifulSoup), lxml, sqlite3
"""


from bs4 import BeautifulSoup
import lxml
import sqlite3


"""
# example entry for dictionary in JMdict_e:
<entry>
            # unique identifier of the entry
<ent_seq>1464530</ent_seq>
<k_ele>
            # kanji/ first reading
    <keb>日本語</keb>
            # the priority of the word
    <ke_pri>news1</ke_pri>
    <ke_pri>nf02</ke_pri>
</k_ele>
<r_ele>
            # primary reading
    <reb>にほんご</reb>
    <re_pri>news1</re_pri>
    <re_pri>nf02</re_pri>
</r_ele>
<r_ele>
            # secondary reading
    <reb>にっぽんご</reb>
</r_ele>
<sense>
            # type of word
    <pos>&n;</pos>
            # see also
    <xref>国語・こくご・2</xref>
            # meaning of the word
    <gloss>Japanese (language)</gloss>
</sense>
</entry>
"""


class Database:
    """
    Database class

    Attributes
    ----------
    db: str
        The path to the database file that will be accessed.

    Methods
    -------
    execute_multiple_responses(sql: str, tup: tuple)
        Executes query and returns list of responses.

    execute_query(sql: str, tup: tuple)
        Executes query and doesn't return anything.

    execute_query_rowid(sql: str, tup: tuple)
        Executes query and returns ID of the new row inserted.

    create_word()
        Deletes the currently existing WordTable and re-creates it.

    create_reading()
        Deletes the currently existing WordReadingTable and re-creates it.

    create_meaning()
        Deletes the currently existing WordMeaningTable and re-creates it.
    """
    def __init__(self):
        self.db = "databases/website_database2.db"

    # when more than one response is expected, returning a list from all of the valid results
    def execute_multiple_responses(self, sql, tup):
        """
        Connects to the database, executes the SQL query, and returns all responses.

        Used for SELECT queries where one or more responses are expected.

        parameters
        ----------
        sql: str
            the SQL query to be executed
        tup: tuple
            additional variables to be added into the SQL query, can be empty tuple.

        returns
        --------
        list
        """
        with sqlite3.connect(self.db) as db:
            cursor = db.cursor()
            cursor.execute(sql, tup)
            result = cursor.fetchall()
            return result

    def execute_query(self, sql, tup):
        """
        Connects to the database and executes the SQL query passed in.

        Used for INSERT and DELETE queries - no values are returned from this method.

        parameters
        ---------
        sql: str
            the SQL query to be executed
        tup: tuple
            additional variables to be added into the SQL query, can be empty tuple.

        returns
        --------
        None
        """
        with sqlite3.connect(self.db) as conn:
            cursor = conn.cursor()
            cursor.execute(sql, tup)
            conn.commit()

    def execute_query_rowid(self, sql, tup):
        """
        Connects to the database, executes the SQL query and returns the primary key of the row just added.

        Used when a new chat/game is added and the system needs to know the ID of the game/chat
        for the user to be admitted.

        parameters
        ---------
        sql: str
            the SQL query to be executed
        tup: tuple
            additional variables to be added into the SQL query, can be empty tuple.

        returns
        --------
        integer
        """
        with sqlite3.connect(self.db) as conn:
            cursor = conn.cursor()
            cursor.execute(sql, tup)
            conn.commit()
            return cursor.lastrowid

    def create_word(self):
        """
        Deletes the currently existing WordTable and re-creates it.

        No required parameters.

        Returns
        -------
        None
        """
        sql = "DROP TABLE WordTable"
        self.execute_query(sql, ())
        sql = "CREATE TABLE IF NOT EXISTS WordTable(" \
              "WordID INTEGER," \
              "PrimaryReading TEXT," \
              "primary key (WordID)" \
              ")"
        self.execute_query(sql, ())

    def create_reading(self):
        """
        Deletes the currently existing WordReadingTable and re-creates it.

        No required parameters.

        Returns
        -------
        None
        """
        sql = "DROP TABLE WordReadingTable"
        self.execute_query(sql, ())
        sql = "CREATE TABLE IF NOT EXISTS WordReadingTable(" \
              "ReadingID INTEGER," \
              "WordID INTEGER," \
              "Reading TEXT," \
              "primary key (ReadingID)," \
              "foreign key(WordID) references WordTable(WordID)" \
              ")"
        self.execute_query(sql, ())

    def create_meaning(self):
        """
        Deletes the currently existing WordMeaningTable and re-creates it.

        No required parameters.

        Returns
        -------
        None
        """
        sql = "DROP TABLE WordMeaningTable"
        self.execute_query(sql, ())
        sql = "CREATE TABLE IF NOT EXISTS WordMeaningTable(" \
              "MeaningID INTEGER," \
              "WordID INTEGER," \
              "Meaning TEXT," \
              "primary key (MeaningID)," \
              "foreign key(WordID) references WordTable(WordID)" \
              ")"
        self.execute_query(sql, ())


class Entry(Database):
    """
    Entry class

    Inherits from superclass Database.

    Deals with SQL queries and data related to the dictionary

    Attributes
    ----------
    soup: object
        The beautiful soup object containing all of the data from the JMdict_e file.

    Methods
    -------
    get_from_wordid(wordid: int)
        Returns a dictionary of the primary reading, other readings and
        meanings associated with a WordID.

    get_from_query(word: str)
        Returns a list of dictionaries containing all words/meanings/readings
        similar to what the user has entered.

    check_primary(word: str)
        Returns the list of tuples of WordIDs of primary readings that match the user's search.

    check_readings(word: str)
        Returns the list of tuples of WordIDs of other readings that match the user's search.

    check_meanings(word: str)
        Returns the list of tuples of WordIDs of meanings that are similar to the user's search.

    insert_all_data()
        Resets the three database tables, inserts all of the data from the XML file into the tables.
    """

    def __init__(self, soup=False):
        super().__init__()
        if soup:
            with open("databases/JMdict_e", encoding="utf8") as fle:
                self.soup = BeautifulSoup(fle, 'xml')

    def get_from_wordid(self, wordid):
        """
        Returns a dictionary of the primary reading, other readings and
        meanings associated with a WordID.

        Parameters
        ----------
        wordid: int
            The WordID of the readings/meanings to get.

        Returns
        -------
        dict
        """
        sql = "SELECT WordTable.PrimaryReading, WordMeaningTable.Meaning, WordReadingTable.Reading " \
              "FROM WordTable " \
              "INNER JOIN WordMeaningTable ON WordTable.WordID = WordMeaningTable.WordID " \
              "LEFT JOIN WordReadingTable ON WordTable.WordID = WordReadingTable.WordID " \
              "WHERE WordTable.WordID = '" + str(wordid) + "'"
        returned = self.execute_multiple_responses(sql, ())
        return_values = {"PrimaryReading": "", "Meanings": [], "Readings": []}

        # constructs the dictionary with the readings and meanings to be returned
        for result in returned:
            return_values["PrimaryReading"] = result[0]
            if result[1] not in return_values["Meanings"]:
                return_values["Meanings"].append(result[1])
            if result[2] not in return_values["Readings"]:
                return_values["Readings"].append(result[2])
        return return_values

    def get_from_query(self, word):
        """
        Returns a list of dictionaries containing all words/meanings/readings
        similar to what the user has entered.

        Parameters
        ----------
        word: str
            The word that the user searched for.

        Returns
        -------
        list[dict]
        """
        word = word.replace("'", "''")
        # when the user searches a word, the program cannot tell whether they have entered english, kana or kanji.
        # therefore, the program searches through the reading and meaning tables to find matching values, as well
        # as the kanji/primary reading itself.
        total_words = []
        # finds out the WordID of every direct match to an entry in the WordTable
        primary_results = self.check_primary(word)
        for primary in primary_results:
            # finds all of the readings and meanings associated with the WordID returned in the
            # list of PrimaryReading matches (returns a dictionary) -- adds it to the list of results to return
            total_words.append(self.get_from_wordid(primary[0]))
        # finds out the WordID of every instance where one of the meanings is similar to what was searched
        meaning_results = self.check_meanings(word)
        for mean in meaning_results:
            # finds all of the readings and meanings associated with the WordID returned in the
            # list of Meaning matches (returns a dictionary) -- adds it to the list of results to return
            total_words.append(self.get_from_wordid(mean[0]))
        # finds out the WordID of every instance where one of the readings matches what was searched
        reading_results = self.check_readings(word)
        for read in reading_results:
            # finds all of the readings and meanings associated with the WordID returned in the
            # list of PrimaryReading matches (returns a dictionary) -- adds it to the list of results to return
            total_words.append(self.get_from_wordid(read[0]))

        # returns the list of dictionaries with relevant results
        return total_words

    def check_primary(self, word):
        """
        Returns the list of tuples of WordIDs of primary readings that match the user's search.

        Parameters
        ----------
        word: str
            The word that the user searched.

        Returns
        -------
        list[tup[int,]]
        """
        sql = "SELECT WordID FROM WordTable WHERE PrimaryReading = '" + str(word) + "'"
        results = self.execute_multiple_responses(sql, ())
        return results

    def check_readings(self, word):
        """
        Returns the list of tuples of WordIDs of other readings that match the user's search.

        Parameters
        ----------
        word: str
            The word that the user searched.

        Returns
        -------
        list[tup[int,]]
        """
        sql = "SELECT WordID FROM WordReadingTable WHERE Reading = '" + str(word) + "'"
        results = self.execute_multiple_responses(sql, ())
        return results

    def check_meanings(self, word):
        """
        Returns the list of tuples of WordIDs of primary readings that
        are similar to the user's search.

        Parameters
        ----------
        word: str
            The word that the user searched.

        Returns
        -------
        list[tup[int,]]
        """
        sql = "SELECT WordID FROM WordMeaningTable WHERE Meaning LIKE '%" + word + "%' LIMIT 8"
        results = self.execute_multiple_responses(sql, ())
        return results

    def insert_all_data(self):
        """
        Resets the three database tables, inserts all of the data from the XML file into the tables.

        No required parameters.

        Returns
        -------
        None
        """
        # clears all of the current word tables (drops them and remakes them)
        self.create_word()
        self.create_meaning()
        self.create_reading()
        entries = self.soup.find_all('entry')
        # for each entry
        for entry in entries:
            # create a list of all of the reb, keb and gloss tags
            other_readings = entry.find_all('reb')
            kanji = entry.find_all('keb')
            meanings = entry.find_all('gloss')
            # if there is at least one keb tag
            if kanji != []:
                # if there is more than one
                if len(kanji) > 1:
                    # add all but the first to 'other_readings'
                    for x in range(1, (len(kanji))):
                        other_readings.append(kanji[x])
                # make 'kanji' be a list with the single element which is the first keb element
                kanji = kanji[:1]
            else:
                # let 'kanji' be the first reb element, and remove it from other_readings
                kanji = other_readings[:1]
                other_readings.pop(0)
            try:
                s_readings = []
                s_kanji = []
                s_meanings = []
                # adds the 'text' part of the tag to the appropriate list.
                for item in other_readings:
                    s_readings.append(item.contents[0])
                for item in kanji:
                    s_kanji.append(item.contents[0])
                for item in meanings:
                    s_meanings.append(item.contents[0])

                if len(s_kanji) != 0:
                    # insert the data from the entry into the database tables.
                    id_ = 0
                    for k in s_kanji:
                        sql = "INSERT INTO WordTable(PrimaryReading) VALUES (?)"
                        # returns the ID of the new primary reading added, so that the other
                        # readings and meanings can be associated to it.
                        id_ = self.execute_query_rowid(sql, (k,))
                    for reading in s_readings:
                        sql = "INSERT INTO WordReadingTable(WordID, Reading) VALUES (?,?)"
                        tup = (id_, reading)
                        self.execute_query(sql, tup)
                    for meaning in s_meanings:
                        sql = "INSERT INTO WordMeaningTable(WordID, Meaning) VALUES (?,?)"
                        tup = (id_, meaning)
                        self.execute_query(sql, tup)
                else:
                    pass
            except Exception as e:
                pass


if __name__ == "__main__":
    pass
