# -*- encoding: utf-8 -*-
import sys
import time

from lazyblacksmith.models import Activity
from lazyblacksmith.models import ActivityMaterial
from lazyblacksmith.models import ActivityProduct
from lazyblacksmith.models import ActivitySkill
from lazyblacksmith.models import Constellation
from lazyblacksmith.models import Item
from lazyblacksmith.models import Region
from lazyblacksmith.models import SolarSystem


class Importer(object):

    # Import object in the list must be class from models to work
    IMPORT_ORDER = [
        Item,
        Activity,
        ActivityMaterial,
        ActivityProduct,
        ActivitySkill,
        Region,
        Constellation,
        SolarSystem,
    ]

    def __init__(self, sde_connection, lb_engine):
        """
        Constructor
        """
        if sde_connection is not None:
            # sqlite3 UTF drama workaround
            sde_connection.text_factory = lambda x: unicode(x, "utf-8", "ignore")
            self.sde_cursor = sde_connection.cursor()

        self.lb_engine = lb_engine

    def time_func(self, text, f):
        """
        Trace function that show time used for each functions
        """
        start = time.time()
        print '=> %s:' % text,
        sys.stdout.flush()

        added, total = f()

        print '%d/%d (%0.2fs)' % (added, total,  time.time() - start)

    def import_all(self):
        """
        Import all tables from SDE using the IMPORT_ORDER to launch import functions
        """
        print "\nIMPORT ALL TABLES"
        print "================="
        for table in self.IMPORT_ORDER:
            self.import_table(table.__name__.lower())

    def import_table(self, table):
        """
        Import the given table from the SDE
        """
        self.time_func(table, getattr(self, "import_"+table))

    def delete_table(self, table):
        """
        Delete the content of the given table in the LB database
        """
        print "Deleting rows from %s " % table
        self.lb_engine.execute("DELETE FROM %s" % table)

    def delete_all(self):
        """
        Delete the content of all tables in LB Database using IMPORT_ORDER to
        determine dependencies.
        """
        print "\nDELETE ALL TABLES"
        print "================="
        delete_order = list(self.IMPORT_ORDER)
        delete_order.reverse()
        for table in delete_order:
            self.delete_table(table.__tablename__)

    # IMPORT CLASS FUNCTIONS START HERE
    ###################################

    def import_item(self):
        """
        Import items from SDE to our database.
        Add blueprint max production limit if exists

        CCP Table : InvTypes
        CCP Table : IndustryBlueprints
        """
        added = 0
        total = 0

        # get all data
        self.sde_cursor.execute("""
            SELECT
                  i.typeID
                , i.typeName
                , ib.maxProductionLimit
            FROM invTypes i
            LEFT JOIN industryBlueprints ib
                ON ib.typeID = i.typeID
            WHERE i.published=1
        """)

        bulk_data = {}
        for row in self.sde_cursor:
            bulk_data[int(row[0])] = row[1:]

        new = []

        # for each item from SDE, check valid data and check if it doesn't exist yet in our db
        for id, data in bulk_data.items():
            total += 1

            if not data[0]:
                continue

            item = {
                'id': id,
                'name': data[0],
                'max_production_limit': int(data[1]) if data[1] else None,
            }
            new.append(item)
            added += 1

        # then create the new item if they exist
        if new:
            self.lb_engine.execute(
                Item.__table__.insert(),
                new
            )

        return (added, total)

    def import_activity(self):
        """
        Import blueprints activity time from SDE to our database.

        CCP Table : IndustryActivity
        """
        added = 0
        total = 0

        # get all data
        self.sde_cursor.execute("""
            SELECT
                  ia.typeID
                , ia.time
                , ia.activityID
                , i.typeName
            FROM industryActivity ia
            JOIN invTypes i
                ON  i.typeID = ia.typeID
                AND i.published = 1
        """)

        bulk_data = []
        for row in self.sde_cursor:
            bulk_data.append(row)

        # for each blueprints from SDE, check valid data and import them.
        new = []
        for data in bulk_data:
            total += 1

            if not data[0] or not data[1] or not data[2] or not data[3]:
                continue

            activity = {
                'item_id': int(data[0]),
                'time': int(data[1]),
                'activity': int(data[2]),
            }

            new.append(activity)
            added += 1

        # then create the new blueprints if they exist
        if new:
            self.lb_engine.execute(
                Activity.__table__.insert(),
                new
            )

        return (added, total)

    def import_activitymaterial(self):
        """
        Import blueprints activity materials from SDE to our database.

        CCP Table : IndustryActivityMaterials
        """
        added = 0
        total = 0

        # get all data
        self.sde_cursor.execute("""
            SELECT
                  iam.typeID
                , iam.quantity
                , iam.activityID
                , iam.materialTypeID
                , i.typeName
            FROM industryActivityMaterials iam
            JOIN invTypes i
                ON  i.typeID = iam.typeID
                AND i.published = 1
            GROUP BY
                  iam.typeID
                , iam.activityID
                , iam.materialTypeID
        """)

        bulk_data = []
        for row in self.sde_cursor:
            bulk_data.append(row)

        # for each blueprints from SDE, check valid data and import them.
        new = []
        for data in bulk_data:
            total += 1

            if not data[0] or not data[1] or not data[2] or not data[3] or not data[4]:
                continue

            activitymaterial = {
                'item_id': int(data[0]),
                'quantity': int(data[1]),
                'activity': int(data[2]),
                'material_id': int(data[3]),
            }

            new.append(activitymaterial)
            added += 1

        # then create the new blueprints if they exist
        if new:
            self.lb_engine.execute(
                ActivityMaterial.__table__.insert(),
                new
            )

        return (added, total)

    def import_activityproduct(self):
        """
        Import blueprints activity products from SDE to our database.
        Add probability for each activity/product

        CCP Table : IndustryActivityProducts
        CCP Table : IndustryActivityProbabilities
        """
        added = 0
        total = 0

        # get all data
        self.sde_cursor.execute("""
            SELECT
                  iap.typeID
                , iap.activityID
                , iap.productTypeID
                , iap.quantity
                , iapr.probability
                , i.typeName
            FROM IndustryActivityProducts iap
            LEFT JOIN IndustryActivityProbabilities iapr
                ON iapr.typeID = iap.typeID
                AND iapr.activityID = iap.activityID
                AND iapr.productTypeID = iap.productTypeID
            JOIN invTypes i
                ON  i.typeID = iap.typeID
                AND i.published = 1
            JOIN invTypes i2
                ON  i2.typeID = iap.productTypeID
                AND i2.published = 1
        """)

        bulk_data = []
        for row in self.sde_cursor:
            bulk_data.append(row)

        # for each blueprints from SDE, check valid data and import them.
        new = []
        for data in bulk_data:
            total += 1

            if not data[0] or not data[1] or not data[2] or not data[3] or not data[5]:
                print data
                continue

            activityproduct = {
                'item_id': int(data[0]),
                'activity': int(data[1]),
                'product_id': int(data[2]),
                'quantity': int(data[3]),
                'probability': float(data[4] if data[4] is not None else 1.00),
            }

            new.append(activityproduct)
            added += 1

        # then create the new blueprints if they exist
        if new:
            self.lb_engine.execute(
                ActivityProduct.__table__.insert(),
                new
            )

        return (added, total)

    def import_activityskill(self):
        """
        Import blueprints activity skill from SDE to our database.

        CCP Table : IndustryActivitySkills
        """
        added = 0
        total = 0

        # get all data
        self.sde_cursor.execute("""
            SELECT
                  ias.typeID
                , ias.activityID
                , ias.skillID
                , ias.level
                , i.typeName
            FROM IndustryActivitySkills ias
            JOIN invTypes i
                ON  i.typeID = ias.typeID
                AND i.published = 1
            GROUP BY ias.typeID, ias.activityID, ias.skillID
        """)

        bulk_data = []
        for row in self.sde_cursor:
            bulk_data.append(row)

        # for each blueprints from SDE, check valid data and import them.
        new = []
        for data in bulk_data:
            total += 1

            if not data[0] or not data[1] or not data[2] or not data[3] or not data[4]:
                print data
                continue

            activityskill = {
                'item_id': int(data[0]),
                'activity': int(data[1]),
                'skill_id': int(data[2]),
                'level': int(data[3]),
            }

            new.append(activityskill)
            added += 1

        # then create the new blueprints if they exist
        if new:
            self.lb_engine.execute(
                ActivitySkill.__table__.insert(),
                new
            )

        return (added, total)

    def import_region(self):
        """
        Import region from SDE to our database.

        CCP Table : mapRegions
        """
        added = 0
        total = 0

        # get all data
        self.sde_cursor.execute("""
            SELECT
                  mr.regionID
                , mr.regionName
                , CASE WHEN mrj.fromRegionID IS NULL THEN 1 ELSE 0 END AS IS_WH
            FROM mapRegions mr
            LEFT JOIN mapRegionJumps mrj
            ON mrj.fromRegionID = mr.regionID OR mrj.toRegionID = mr.regionID
            GROUP BY mr.regionID, mr.regionName, IS_WH
        """)

        bulk_data = {}
        for row in self.sde_cursor:
            bulk_data[int(row[0])] = row[1:]

        new = []

        # for each item from SDE, check valid data and check if it doesn't exist yet in our db
        for id, data in bulk_data.items():
            total += 1

            if not data[0]:
                continue

            item = {
                'id': id,
                'name': data[0],
                'wh': data[1]
            }
            new.append(item)
            added += 1

        # then create the new item if they exist
        if new:
            self.lb_engine.execute(
                Region.__table__.insert(),
                new
            )

        return (added, total)

    def import_constellation(self):
        """
        Import Constellations from SDE to our database.

        CCP Table : mapConstellations
        """
        added = 0
        total = 0

        # get all data
        self.sde_cursor.execute("""
            SELECT
                  constellationID
                , regionID
                , constellationName
            FROM mapConstellations
        """)

        bulk_data = {}
        for row in self.sde_cursor:
            bulk_data[int(row[0])] = row[1:]

        new = []

        # for each item from SDE, check valid data and check if it doesn't exist yet in our db
        for id, data in bulk_data.items():
            total += 1

            if not data[0] or not data[1]:
                continue

            item = {
                'id': id,
                'region_id': int(data[0]),
                'name': data[1],
            }
            new.append(item)
            added += 1

        # then create the new item if they exist
        if new:
            self.lb_engine.execute(
                Constellation.__table__.insert(),
                new
            )

        return (added, total)

    def import_solarsystem(self):
        """
        Import solar systems from SDE to our database.

        CCP Table : mapSolarSystems
        """
        added = 0
        total = 0

        # get all data
        self.sde_cursor.execute("""
            SELECT
                  solarSystemID
                , solarSystemName
                , regionID
                , constellationID
            FROM mapSolarSystems
        """)

        bulk_data = {}
        for row in self.sde_cursor:
            bulk_data[int(row[0])] = row[1:]

        new = []

        # for each item from SDE, check valid data and check if it doesn't exist yet in our db
        for id, data in bulk_data.items():
            total += 1

            if not data[0] or not data[1] or not data[2]:
                continue

            item = {
                'id': id,
                'name': data[0],
                'region_id': int(data[1]),
                'constellation_id': int(data[2]),
            }
            new.append(item)
            added += 1

        # then create the new item if they exist
        if new:
            self.lb_engine.execute(
                SolarSystem.__table__.insert(),
                new
            )

        return (added, total)
