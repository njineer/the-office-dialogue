from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from os.path import realpath
from contextlib import contextmanager

Base = declarative_base()
Session = sessionmaker()

class OfficeQuote(Base):
    __tablename__ = "office_quotes"

    id = Column(Integer, primary_key=True)
    season = Column(Integer)
    episode = Column(Integer)
    scene = Column(Integer)
    speaker = Column(String)
    line = Column(String)
    deleted = Column(Boolean)

    def __repr__(self):
        return "<OfficeQuote(season={}, episode={}, scene={}, speaker={}, line={}, deleted={}".format(
            self.season, self.episode, self.scene, self.speaker, self.line, self.deleted) 


class Database():
    def __init__(self, db_file=""):
        # create engine
        self.engine = create_engine("sqlite:///{}".format(realpath(db_file)), echo=True)

        # create schema
        Base.metadata.create_all(self.engine)

        # connect session
        Session.configure(bind=self.engine)


    @staticmethod
    @contextmanager
    def session_scope():
        """
        Provide a transactional scope around a series of operations.
        """
        session = Session()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def addQuote(self, quote):
        with self.session_scope() as session:
            session.add(quote) # dialogLine instance



if __name__ == "__main__":

    from collections import namedtuple
    Scene = namedtuple("Scene", ['quotes', 'deleted'])
    Quote = namedtuple("Quote", ['speaker', 'line'])
    Episode = namedtuple("Episode", ['number', 'season', 'scenes'])

    eps = Episode(
        2,
        3,
        [ #scenes
            ( # scene
                [ # quotes
                    ("Jim", "Bears beets battlestar"),
                    ("Dwight", "Identity thief"),
                ],
                True # deleted
            ),
            ( # scene
                [
                    ("Pam", "Yep."),
                    ("Oscar", "actually..."),
                ],
                False
            )
        ]
    )

    def writeToDatabase(episode, db):
        for scene, (quotes, deleted) in enumerate(episode.scenes):
            for speaker, line in quotes:
                db.addQuote(OfficeQuote(
                    season=episode.season,
                    episode=episode.number,
                    scene=scene,
                    speaker=speaker,
                    line=line,
                    deleted=deleted))

    writeToDatabase(eps, Database("testdb.sqlite"))
