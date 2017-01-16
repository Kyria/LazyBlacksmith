# -*- encoding: utf-8 -*-
import sys
import time

from lazyblacksmith.models import Activity
from lazyblacksmith.models import ActivityMaterial
from lazyblacksmith.models import ActivityProduct
from lazyblacksmith.models import ActivitySkill
from lazyblacksmith.models import Constellation
from lazyblacksmith.models import Decryptor
from lazyblacksmith.models import IndustryIndex
from lazyblacksmith.models import Item
from lazyblacksmith.models import ItemAdjustedPrice
from lazyblacksmith.models import OreRefining
from lazyblacksmith.models import Region
from lazyblacksmith.models import SolarSystem
from lazyblacksmith.models import db


class Importer(object):
    DELETE = 0
    UPDATE = 1


    # Import object in the list must be class from models to work
    IMPORT_ORDER = [
        (Item, UPDATE),
        (OreRefining, DELETE),
        (Decryptor, DELETE),
        (Activity, DELETE),
        (ActivityMaterial, DELETE),
        (ActivityProduct, DELETE),
        (ActivitySkill, DELETE),
        (Region, DELETE),
        (Constellation, DELETE),
        (SolarSystem, DELETE),
        (ItemAdjustedPrice, DELETE),
        (IndustryIndex, DELETE),
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

        print '%d/%d (%0.2fs)' % (added, total, time.time() - start)

    def import_all(self):
        """
        Import all tables from SDE using the IMPORT_ORDER to launch import functions
        """
        print "\nIMPORT ALL TABLES"
        print "================="
        for table in self.IMPORT_ORDER:
            self.import_table(table[0].__name__.lower())

    def import_table(self, table):
        """
        Import the given table from the SDE
        """
        self.time_func(table, getattr(self, "import_" + table))

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
            if table[1] == Importer.DELETE:
                self.delete_table(table[0].__tablename__)

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

        new = []
        update = []
        bulk_data = {}
        item_list = []
        
        # get all data, marketGroupID > 35k == dust514
        self.sde_cursor.execute("""
            SELECT
                  i.typeID
                , i.typeName
                , ib.maxProductionLimit
                , i.marketGroupID
                , ig.categoryID
                , i.marketGroupID
            FROM invTypes i
            LEFT JOIN industryBlueprints ib
                ON ib.typeID = i.typeID
            JOIN invGroups ig
                ON ig.groupID = i.groupID
            WHERE i.published=1
        """)

        for row in self.sde_cursor:
            bulk_data[int(row[0])] = row[1:]
        
        items = Item.query.all()
        for item in items:
            item_list.append(item.id)

        # for each item from SDE, check valid data and check if it doesn't exist yet in our db
        for id, data in bulk_data.items():
            total += 1

            if not data[0]:
                continue

            item = {
                'name': data[0],
                'max_production_limit': int(data[1]) if data[1] else None,
                'market_group_id': int(data[2]) if data[2] else None,
                'category_id': int(data[3]) if data[3] else None,
            }
            
            if id in item_list:
                item['update_id'] = id
                update.append(item)
            else:
                item['id'] = id
                new.append(item)
                
            added += 1

        # then create the new item if they exist
        if new:
            self.lb_engine.execute(
                Item.__table__.insert(),
                new
            )
            
        if update:
            update_stmt = Item.__table__.update()
            update_stmt = update_stmt.where(
                Item.id == db.bindparam('update_id')
            )
            db.engine.execute(
                update_stmt,
                update,
            )

        return (added, total)

    def import_orerefining(self):
        """
        Import ore (ice / ore) refining data

        CCP Table : invTypeMaterials
        """
        added = 0
        total = 0

        # get all data
        self.sde_cursor.execute("""
            SELECT it1.typeID
                  ,it1.volume
                  ,it1.portionSize
                  ,it1.marketGroupID
                  ,it2.typeID
                  ,quantity
            FROM invTypeMaterials itm
            JOIN invTypes it1 ON it1.typeid = itm.typeid
            JOIN invTypes it2 ON itm.materialtypeid = it2.typeid
            JOIN invGroups ig ON ig.groupID = it1.groupID
            WHERE ig.categoryID = 25
                AND it1.published = 1
        """)

        new = []
        for row in self.sde_cursor:
            total += 1

            if not row[0] or not row[2] or not row[5]:
                continue

            ore_id = int(row[0])
            volume = int(row[1])
            batch = int(row[2])
            market_group_id = int(row[3])
            material_id = int(row[4])
            quantity = int(row[5])

            # if volume = 100 and marketGroupId = 1855 (Ice), it's some compressed Ice
            # if portionSize = 1 and marketGroupID != 1855, it's some compressed ore
            ice = False
            compressed = False
            if market_group_id == 1855:
                ice = True
                compressed = (volume == 100)
            else:
                compressed = (batch == 1)

            ore_refining = {
                'ore_id': ore_id,
                'material_id': material_id,
                'quantity': quantity,
                'batch': batch,
                'is_compressed': compressed,
                'is_ice': ice,
            }

            new.append(ore_refining)
            added += 1

        # then create the new blueprints if they exist
        if new:
            self.lb_engine.execute(
                OreRefining.__table__.insert(),
                new
            )

        return (added, total)

    def import_decryptor(self):
        """
        Import the decryptor stats in a specific table.

        CCP Table : dgmTypeAttributes, invTypes
        """
        added = 0
        total = 0

        # get all data
        self.sde_cursor.execute("""
            SELECT
                i.typeID,
                COALESCE(dta2.valueInt,dta2.valueFloat) multiplier,
                COALESCE(dta3.valueInt,dta3.valueFloat) me,
                COALESCE(dta4.valueInt,dta4.valueFloat) te,
                COALESCE(dta5.valueInt,dta5.valueFloat) runs
            FROM invTypes i
            JOIN dgmTypeAttributes dta2 ON (dta2.typeid = i.typeid AND dta2.attributeID = 1112)
            JOIN dgmTypeAttributes dta3 ON (dta3.typeid = i.typeid AND dta3.attributeID = 1113)
            JOIN dgmTypeAttributes dta4 ON (dta4.typeid = i.typeid AND dta4.attributeID = 1114)
            JOIN dgmTypeAttributes dta5 ON (dta5.typeid = i.typeid AND dta5.attributeID = 1124)
            WHERE i.groupID = 1304
        """)

        # for each decryptor from SDE, check valid data and import them.
        new = []
        for data in self.sde_cursor:
            total += 1

            if not data[0]:
                continue

            decryptor = {
                'item_id': int(data[0]),
                'probability_multiplier': float(data[1]),
                'material_modifier': int(data[2]),
                'time_modifier': int(data[3]),
                'run_modifier': int(data[4]),
            }

            new.append(decryptor)
            added += 1

        # then create the new blueprints if they exist
        if new:
            self.lb_engine.execute(
                Decryptor.__table__.insert(),
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

            if not data[0] or not data[1] or not data[2] or not data[3]:
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

            if not data[0] or not data[1] or not data[2] or not data[3]:
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

            if not data[0] or not data[1] or not data[2] or not data[3]:
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

    def import_itemadjustedprice(self):
        """
        import item adjusted price into DB
        """
        from lazyblacksmith.tasks.adjusted_price import update_adjusted_price
        return update_adjusted_price()

    def import_industryindex(self):
        """
        import industry index into DB
        """
        from lazyblacksmith.tasks.industry_index import update_industry_index
        return update_industry_index()
