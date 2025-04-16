
class Annotations:
    BBS_I = "BbsI"
    GRNA = "gRNA"
    SCAFFOLD = "Scaffold"
    AVR_II = "AvrII"
    PST_I = "PstI"
    HR2 = "HR2 Sequence"
    HR1 = "HR1 Sequence"

    SEQUENCE = "Sequence"

    OLIGO_SEQUENCE_KO_ORDER_REV = [
        BBS_I,
        GRNA,
        SCAFFOLD,
        HR1,
        AVR_II,
        HR2,
        PST_I,
    ]

    OLIGO_SEQUENCE_KO_ORDER_FW = [
        BBS_I,
        GRNA,
        SCAFFOLD,
        HR2,
        AVR_II,
        HR1,
        PST_I,
    ]

    OLIGO_SEQUENCE_TAG_ORDER = [
        BBS_I,
        GRNA,
        SCAFFOLD,
        HR1,
        AVR_II,
        HR2,
        PST_I,
    ]
