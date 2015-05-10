from . import db

class Item(db.Model):
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    name = db.Column(db.String(100), nullable=True)
    max_production_limit = db.Column(db.Integer, nullable=True)
    
    # foreign keys
    activities = db.relationship('Activity', backref='blueprint', lazy='dynamic')
    activity_products = db.relationship('ActivityProduct', backref='blueprint', lazy='dynamic', foreign_keys='ActivityProduct.item_id')
    activity_skills = db.relationship('ActivitySkill', backref='blueprint', lazy='dynamic', foreign_keys='ActivitySkill.item_id')
    activity_materials = db.relationship('ActivityMaterial', backref='blueprint', lazy='dynamic', foreign_keys='ActivityMaterial.item_id')
    
    product_for_activities = db.relationship('ActivityProduct', backref='product', lazy='dynamic', foreign_keys='ActivityProduct.product_id')
    skill_for_activities = db.relationship('ActivitySkill', backref='skill', lazy='dynamic', foreign_keys='ActivitySkill.skill_id')
    material_for_activities = db.relationship('ActivityMaterial', backref='material', lazy='dynamic', foreign_keys='ActivityMaterial.material_id')
    
