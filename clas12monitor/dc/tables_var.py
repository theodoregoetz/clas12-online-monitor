import re

from clas12monitor.database.localdb import Column, Integer, Float, \
    String, Enum, \
    ForeignKey, ForeignKeyConstraint, UniqueConstraint, \
    relationship, Base

class StatusDCHVCrate(Base):
    __tablename__ = '/status/drift_chamber/high_voltage/crate'
    id       = Column(Integer, primary_key=True)
    crate_id = Column(Integer, nullable=False)
    begin    = Column(Integer, nullable=False)
    end      = Column(Integer, nullable=True)
    status   = Column(Integer, nullable=False)
    author   = Column(Integer, nullable=False)
    comment  = Column(String, nullable=False)
    def __str__(self):
        fmt = '[{id}/{crate_id},{begin}-{end}]({status})'
        return fmt.format(**vars(self))
    def __repr__(self):
        fmt = 'StatusDCHVCrate(id={id},crate_id={crate_id},begin={begin},end={end},status={status},author={author},comment="{comment}")'
        return fmt.format(**vars(self))

class StatusDCHVSupplyBoard(Base):
    __tablename__ = '/status/drift_chamber/high_voltage/supply_board'
    id        = Column(Integer, primary_key=True)
    crate_id  = Column(Integer, ForeignKey(CalibDCHVCrate.__tablename__+'.id'))
    slot_id   = Column(Integer, nullable=False)
    wire_type = Column(Enum('sense','field','guard'))
    doublet_connector = Column(Integer, nullable=False)
    status    = Column(Integer, nullable=False)
    subslots = relationship('CalibDCHVSubslot', backref='supply_board')
    __table_args__ = (
        UniqueConstraint(
            'crate_id',
            'slot_id'),)
    def __str__(self):
        fmt = '[{id}/{crate_id},{slot_id}]({wire_type},{doublet_connector},{status})'
        return fmt.format(**vars(self))
    def __repr__(self):
        fmt = re.sub(r'\s+','','''\
            CalibDCHVSupplyBoard(
                id={id},
                crate_id={crate_id},
                slot_id={slot_id},
                wire_type={wire_type},
                doublet_connector={doublet_connector},
                status={status})''')
        return fmt.format(**vars(self))
