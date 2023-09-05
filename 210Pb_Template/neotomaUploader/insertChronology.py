import datetime
import logging

def insertChronology(cur, collunitid, agetype, agemodel, ages,
                     contactname, default = True,
                     chronologyname = 'Default 210Pb',
                     dateprepared = datetime.datetime.today().date()):
    def cleanage(x):
        try:
            y = float(x)
        except ValueError:
            y = None
        return y
        
    cleanage = list(map(lambda x: cleanage(x), ages))
    minage = min([i for i in cleanage if i is not None])
    maxage = max([i for i in cleanage if i is not None])

    addChron = """SELECT ts.insertchronology(_collectionunitid := %(collunitid)s,
        _agetypeid := %(agetype)s,
        _contactid := %(contactid)s,
        _isdefault := TRUE,
        _chronologyname := %(chronologyname)s,
        _dateprepared := %(dateprepared)s,
        _agemodel := %(agemodel)s,
        _ageboundyounger := %(maxage)s,
        _ageboundolder := %(minage)s)"""
    get_cont = """SELECT contactid FROM ndb.contacts WHERE %(contactname)s %% contactname;"""    
    cur.execute(get_cont, {'contactname': contactname[0]})
    contactid = cur.fetchone()[0]
    if agetype == 'cal yr BP':
        agetypeid = 2
    elif agetype == 'CE/BCE':
        agetypeid = 1
    else:
        logging.error("The provided age type is incorrect..")
    cur.execute(addChron, {'collunitid':collunitid, 'contactid': contactid,
                           'chronologyname': chronologyname,
                           'agetype': agetypeid,
                           'dateprepared': dateprepared, 'agemodel': agemodel,
                           'maxage': int(maxage), 'minage': int(minage)})
    chronid = cur.fetchone()[0]
    return chronid
