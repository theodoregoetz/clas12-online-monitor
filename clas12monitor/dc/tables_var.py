import re
from datetime import datetime

from clas12monitor.database.localdb import Column, Integer, Float, \
    String, Enum, DateTime, \
    ForeignKey, ForeignKeyConstraint, UniqueConstraint, \
    relationship, Base


class TableBase(Base):
    def __str__(self):
        return self.str_fmt.format(**vars(self))
    def __repr__(self):
        return self.repr_fmt.format(**vars(self))

class StatusTableBase(TableBase):
    id       = Column(Integer, primary_key=True)
    begin    = Column(Integer, nullable=False)
    end      = Column(Integer, nullable=True)
    status   = Column(Integer, nullable=False)
    author   = Column(Integer, ForeignKey(Author.__tablename__+'.id'))
    comment  = Column(Integer, ForeignKey(Comment.__tablename__+'.id'))
    added    = Column(DateTime, default=datetime.utcnow)


class Author(TableBase):
    __tablename__ = 'Author'
    id       = Column(Integer, primary_key=True)
    name     = Column(String, nullable=False)
    email    = Column(String, nullable=False)
    str_fmt  = '[{id}]({name}, {email})'
    repr_fmt = 'Author(id={id},name={name},email={email})'

class Comment(TableBase):
    __tablename__ = 'Comment'
    id       = Column(Integer, primary_key=True)
    message  = Column(String, nullable=False)
    str_fmt  = '[{id}]({message})'
    repr_fmt = 'Author(id={id},message="{message}")'


class DCHVCrateStatus(StatusTableBase):
    __tablename__ = 'DCHVCrateStatus'
    crate_id = Column(Integer, nullable=False)
    str_fmt  = '[{crate_id},{begin}-{end}]({status})'
    repr_fmt = re.sub(r'\s+','','''
            DCHVCrateStatus(
                id={id},
                crate_id={crate_id},
                begin={begin},
                end={end},
                status={status},
                author={author},
                comment={comment},
                added={added})''')

class DCHVSupplyBoardStatus(StatusTableBase):
    __tablename__ = 'DCHVSupplyBoardStatus'
    supply_board_id = Column(Integer, nullable=False)
    str_fmt  = '[{supply_board_id},{begin}-{end}]({status})'
    repr_fmt = re.sub(r'\s+','','''
            DCHVSupplyBoardStatus(
                id={id},
                supply_board_id={supply_board_id},
                begin={begin},
                end={end},
                status={status},
                author={author},
                comment={comment},
                added={added})''')

class DCHVTranslationBoardStatus(StatusTableBase):
    __tablename__ = 'DCHVTranslationBoardStatus'
    board_id    = Column(Integer, nullable=False)
    slot_id     = Column(Integer, nullable=False)
    str_fmt  = '[{board_id},{slot_id},{begin}-{end}]({status})'
    repr_fmt = re.sub(r'\s+','','''
            DCHVSupplyBoardStatus(
                id={id},
                board_id={board_id},
                slot_id={slot_id},
                begin={begin},
                end={end},
                status={status},
                author={author},
                comment={comment},
                added={added})''')
