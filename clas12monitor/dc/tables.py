import re

from clas12monitor.database.localdb import Column, Integer, Float, Enum, \
    ForeignKey, ForeignKeyConstraint, UniqueConstraint, \
    relationship, Base

class CalibDCHVCrate(Base):
    __tablename__ = '/calibration/drift_chamber/high_voltage/crate'
    id     = Column(Integer, primary_key=True)
    status = Column(Integer, nullable=False)
    supply_boards = relationship('CalibDCHVSupplyBoard', backref='crate')
    def __str__(self):
        fmt = '[{id}]({status})'
        return fmt.format(**vars(self))
    def __repr__(self):
        fmt = 'CalibDCHVCrate(id={id},status={status})'
        return fmt.format(**vars(self))

class CalibDCHVSupplyBoard(Base):
    __tablename__ = '/calibration/drift_chamber/high_voltage/supply_board'
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

class CalibDCHVSubslot(Base):
    __tablename__ = '/calibration/drift_chamber/high_voltage/subslot'
    supply_board_id = Column(Integer, ForeignKey(CalibDCHVSupplyBoard.__tablename__+'.id'), primary_key=True)
    subslot_id      = Column(Integer, primary_key=True)
    sector          = Column(Integer, nullable=False)
    superlayer      = Column(Integer, nullable=False)
    doublets = relationship('CalibDCHVDoublet', backref='subslot')
    def __str__(self):
        fmt = '[{supply_board_id},{subslot_id}]({sector},{superlayer})'
        return fmt.format(**vars(self))
    def __repr__(self):
        fmt = re.sub(r'\s+','','''\
            CalibDCHVSubslot(
                supply_board_id={supply_board_id},
                subslot_id={subslot_id},
                sector={sector},
                superlayer={superlayer})''')
        return fmt.format(**vars(self))

class CalibDCHVTranslationBoard(Base):
    __tablename__ = '/calibration/drift_chamber/high_voltage/translation_board'
    board_id    = Column(Integer, primary_key=True)
    slot_id     = Column(Integer, primary_key=True)
    wire_offset = Column(Integer, nullable=False)
    nwires      = Column(Integer, nullable=False)
    def __str__(self):
        fmt = '[{board_id},{slot_id}]({wire_offset},{nwires})'
        return fmt.format(**vars(self))
    def __repr__(self):
        fmt = re.sub(r'\s+','','''\
            CalibDCHVTranslationBoard(
                board_id={board_id},
                slot_id={slot_id},
                wire_offset={wire_offset},
                nwires={nwires})''')
        return fmt.format(**vars(self))

class CalibDCWire(Base):
    __tablename__ = '/calibration/drift_chamber/high_voltage/wire'
    sector     = Column(Integer, primary_key=True)
    superlayer = Column(Integer, primary_key=True)
    layer      = Column(Integer, primary_key=True)
    wire       = Column(Integer, primary_key=True)
    status     = Column(Integer, nullable=False)
    __table_args__ = (
        ForeignKeyConstraint(
            ['sector','superlayer'],
            [CalibDCHVSubslot.__tablename__+'.sector',
             CalibDCHVSubslot.__tablename__+'.superlayer']),)
    def __str__(self):
        fmt = '[{sector},{superlayer},{layer},{wire}]({status})'
        return fmt.format(**vars(self))
    def __repr__(self):
        fmt = re.sub(r'\s+','','''\
            CalibDCWire(
                sector={sector},
                superlayer={superlayer},
                layer={layer},
                wire={wire},
                status={status})''')
        return fmt.format(**vars(self))

class CalibDCHVDoublet(Base):
    __tablename__ = '/calibration/drift_chamber/high_voltage/doublet'
    id                = Column(Integer, primary_key=True)
    supply_board_id   = Column(Integer, nullable=False)
    subslot_id        = Column(Integer, nullable=False)
    channel_id        = Column(Integer, nullable=False)
    distr_box_type    = Column(Enum('forward','backward'), nullable=False)
    quad_id           = Column(Integer, nullable=False)
    doublet_id        = Column(Integer, nullable=False)
    trans_board_id    = Column(Integer, nullable=False)
    trans_slot_id     = Column(Integer, nullable=False)
    status            = Column(Integer, nullable=False)
    trans_board = relationship('CalibDCHVTranslationBoard', backref='doublets')
    pins = relationship('CalibDCHVDoubletPin', backref='doublet')
    __table_args__ = (
        ForeignKeyConstraint(
            ['supply_board_id','subslot_id'],
            [CalibDCHVSubslot.__tablename__+'.supply_board_id',
             CalibDCHVSubslot.__tablename__+'.subslot_id']),
        ForeignKeyConstraint(
            ['trans_board_id','trans_slot_id'],
            [CalibDCHVTranslationBoard.__tablename__+'.board_id',
             CalibDCHVTranslationBoard.__tablename__+'.slot_id']),
        UniqueConstraint(
            'supply_board_id',
            'subslot_id',
            'distr_box_type',
            'quad_id',
            'doublet_id'),
        UniqueConstraint(
            'supply_board_id',
            'subslot_id',
            'trans_board_id',
            'trans_slot_id'),)
    def __str__(self):
        fmt = '[{id}]'\
            + '({supply_board_id},{subslot_id},{channel_id},'\
            + '{distr_box_type},{quad_id},{doublet_id},'\
            + '{status})'
        return fmt.format(**vars(self))
    def __repr__(self):
        fmt = re.sub(r'\s+','','''\
            CalibDCHVDoublet(
                id={id},
                supply_board_id={supply_board_id},
                subslot_id={subslot_id},
                channel_id={channel_id},
                distr_box_type={distr_box_type},
                quad_id={quad_id},
                doublet_id={doublet_id},
                status={status})''')
        return fmt.format(**vars(self))

class CalibDCHVDoubletPin(Base):
    __tablename__ = '/calibration/drift_chamber/high_voltage/doublet_pin'
    doublet_id = Column(Integer, ForeignKey(CalibDCHVDoublet.__tablename__+'.id'), primary_key=True)
    pin_id     = Column(Integer, primary_key=True)
    status     = Column(Integer, nullable=False)
    def __str__(self):
        fmt = '[{doublet_id},{pin_id}]({status})'
        return fmt.format(**vars(self))
    def __repr__(self):
        fmt = re.sub(r'\s+','','''\
            CalibDCHVDoubletPin(
                doublet_id={doublet_id},
                pin_id={pin_id},
                status={status})''')
        return fmt.format(**vars(self))

class CalibDCHVDoubletPinMap(Base):
    __tablename__ = '/calibration/drift_chamber/high_voltage/doublet_pin_map'
    doublet_id = Column(Integer, ForeignKey(CalibDCHVDoublet.__tablename__+'.doublet_id'), primary_key=True)
    pin_id     = Column(Integer, ForeignKey(CalibDCHVDoubletPin.__tablename__+'.pin_id'), primary_key=True)
    wire_type  = Column(Enum('sense','field','guard'),
                        ForeignKey(CalibDCHVSupplyBoard.__tablename__+'.wire_type'), primary_key=True)
    layer      = Column(Integer, ForeignKey(CalibDCWire.__tablename__+'.layer'), primary_key=True)
    def __str__(self):
        fmt = '[{doublet_id},{pin_id}/{wire_type},{layer}]'
        return fmt.format(**vars(self))
    def __repr__(self):
        fmt = re.sub(r'\s+','','''\
            CalibDCHVDoubletPinMap(
                doublet_id={doublet_id},
                pin_id={pin_id},
                wire_type={wire_type},
                layer={layer})''')
        return fmt.format(**vars(self))

class CalibDCSignalTranslationBoard(Base):
    __tablename__ = '/calibration/drift_chamber/signal_translation_board'
    id          = Column(Integer, primary_key=True)
    wire_offset = Column(Integer, nullable=False)
    nwires      = Column(Integer, nullable=False)
    def __str__(self):
        fmt = '[{id}]({wire_offset},{nwires})'
        return fmt.format(**vars(self))
    def __repr__(self):
        fmt = re.sub(r'\s+','','''\
            CalibDCSignalTranslationBoard(
                id={id},
                wire_offset={wire_offset},
                nwires={nwires})''')
        return fmt.format(**vars(self))

class CalibDCSignalCable(Base):
    __tablename__ = '/calibration/drift_chamber/signal_cable'
    id           = Column(Integer, primary_key=True)
    sector       = Column(Integer, nullable=False)
    superlayer   = Column(Integer, nullable=False)
    layer        = Column(Integer, nullable=False)
    board_id     = Column(Integer, ForeignKey(CalibDCSignalTranslationBoard.__tablename__+'.id'), nullable=False)
    connector_id = Column(Integer, nullable=False)
    time_delay   = Column(Float,   nullable=False)
    fuse_status  = Column(Integer, nullable=False)
    cable_status = Column(Integer, nullable=False)

    readout_connector = relationship('CalibDCSignalReadoutConnector', uselist=False, backref='cable')

    __table_args__ = (
        ForeignKeyConstraint(
            ['sector','superlayer','layer'],
            [CalibDCWire.__tablename__+'.sector',
             CalibDCWire.__tablename__+'.superlayer',
             CalibDCWire.__tablename__+'.layer']),
        UniqueConstraint(
            'sector',
            'superlayer',
            'board_id',
            'connector_id'),)
    def __str__(self):
        fmt = '[{id}/'\
            + '{sector},{superlayer},{layer}/'\
            + '{board_id},{connector_id}]'\
            + '({time_delay},{fuse_status},{cable_status})'
        return fmt.format(**vars(self))
    def __repr__(self):
        fmt = re.sub(r'\s+','','''\
            CalibDCSignalCable(
                id={id},
                sector={sector},
                superlayer={superlayer},
                board_id={board_id},
                connector_id={connector_id},
                time_delay={time_delay},
                fuse_status={fuse_status},
                cable_status={cable_status})''')
        return fmt.format(**vars(self))

class CalibDCSignalReadoutConnector(Base):
    __tablename__ = '/calibration/drift_chamber/signal_readout_connector'
    id           = Column(Integer, primary_key=True)
    cable_id     = Column(Integer, ForeignKey(CalibDCSignalCable.__tablename__+'.id'))
    crate_id     = Column(Integer, nullable=False)
    slot_id      = Column(Integer, nullable=False)
    connector_id = Column(Integer, nullable=False)
    status       = Column(Integer, nullable=False)
    __table_args__ = (
        UniqueConstraint(
            'crate_id',
            'slot_id',
            'connector_id'),)
    def __str__(self):
        fmt = '[{id}/{cable_id}/{crate_id},{slot_id},{connector_id}]({status})'
        return fmt.format(**vars(self))
    def __repr__(self):
        fmt = re.sub(r'\s+','','''\
            CalibDCSignalReadoutConnector(
                id={id}
                cable_id={cable_id},
                crate_id={crate_id},
                slot_id={slot_id},
                connector_id={connector_id},
                status={status})''')
        return fmt.format(**vars(self))


