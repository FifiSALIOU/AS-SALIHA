"""
Script d'initialisation de la base de données
Crée les tables et les rôles par défaut
"""
from app.database import Base, engine, SessionLocal
from app import models
from app.security import get_password_hash
from sqlalchemy import text

def init_roles(db):
    """Crée les rôles par défaut"""
    roles_data = [
        {
            "name": "Utilisateur",
            "description": "Utilisateur standard qui peut créer des tickets et suivre leur statut"
        },
        {
            "name": "Secrétaire DSI",
            "description": "Peut assigner et gérer les tickets"
        },
        {
            "name": "Adjoint DSI",
            "description": "Peut assigner, réassigner, escalader et générer des rapports"
        },
        {
            "name": "Technicien",
            "description": "Peut prendre en charge et résoudre les tickets"
        },
        {
            "name": "DSI",
            "description": "Directeur des Systèmes Informatiques - Accès complet"
        },
        {
            "name": "Admin",
            "description": "Administrateur système avec tous les droits"
        }
    ]
    
    for role_data in roles_data:
        existing = db.query(models.Role).filter(models.Role.name == role_data["name"]).first()
        if not existing:
            role = models.Role(**role_data)
            db.add(role)
            print(f"OK - Role cree: {role_data['name']}")
        else:
            print(f"-> Role existe deja: {role_data['name']}")
    
    db.commit()

def init_admin_user(db):
    """Crée un utilisateur administrateur par défaut"""
    admin_role = db.query(models.Role).filter(models.Role.name == "Admin").first()
    if not admin_role:
        print("ERREUR: Le role Admin n'existe pas")
        return
    
    existing = db.query(models.User).filter(models.User.username == "admin").first()
    if not existing:
        admin_user = models.User(
            full_name="Administrateur",
            email="admin@example.com",
            username="admin",
            password_hash=get_password_hash("admin123"),  # Changez ce mot de passe en production !
            role_id=admin_role.id,
            agency="Agence IT",
            status="actif"
        )
        db.add(admin_user)
        db.commit()
        print("OK - Utilisateur admin cree (username: admin, password: admin123)")
        print("ATTENTION: Changez le mot de passe admin en production !")
    else:
        print("-> Utilisateur admin existe deja")


def init_ticket_types_and_categories(db):
    """
    Initialise les types et catégories de tickets par défaut si les tables sont vides.
    Ces données pourront ensuite être modifiées directement dans la base.
    """
    # Types de tickets
    existing_types = db.query(models.TicketTypeModel).count()
    if existing_types == 0:
        default_types = [
            {"code": "materiel", "label": "Matériel"},
            {"code": "applicatif", "label": "Applicatif"},
        ]
        for t in default_types:
            db.add(models.TicketTypeModel(**t))
        db.commit()
        print("OK - Types de tickets par défaut créés")

    # Catégories de tickets
    existing_categories = db.query(models.TicketCategory).count()
    if existing_categories == 0:
        default_categories = [
            # Matériel
            {"name": "Ordinateur portable", "description": None, "type_code": "materiel"},
            {"name": "Ordinateur de bureau", "description": None, "type_code": "materiel"},
            {"name": "Imprimante", "description": None, "type_code": "materiel"},
            {"name": "Scanner", "description": None, "type_code": "materiel"},
            {"name": "Écran/Moniteur", "description": None, "type_code": "materiel"},
            {"name": "Clavier/Souris", "description": None, "type_code": "materiel"},
            {"name": "Réseau (Switch, Routeur)", "description": None, "type_code": "materiel"},
            {"name": "Serveur", "description": None, "type_code": "materiel"},
            {"name": "Téléphone/IP Phone", "description": None, "type_code": "materiel"},
            {"name": "Autre matériel", "description": None, "type_code": "materiel"},
            # Applicatif
            {"name": "Système d'exploitation", "description": None, "type_code": "applicatif"},
            {"name": "Logiciel bureautique", "description": None, "type_code": "applicatif"},
            {"name": "Application métier", "description": None, "type_code": "applicatif"},
            {"name": "Email/Messagerie", "description": None, "type_code": "applicatif"},
            {"name": "Navigateur web", "description": None, "type_code": "applicatif"},
            {"name": "Base de données", "description": None, "type_code": "applicatif"},
            {"name": "Sécurité/Antivirus", "description": None, "type_code": "applicatif"},
            {"name": "Application web", "description": None, "type_code": "applicatif"},
            {"name": "API/Service", "description": None, "type_code": "applicatif"},
            {"name": "Autre applicatif", "description": None, "type_code": "applicatif"},
        ]
        for c in default_categories:
            db.add(models.TicketCategory(**c))
        db.commit()
        print("OK - Catégories de tickets par défaut créées")

def main():
    print("Initialisation de la base de donnees...")
    print("-" * 50)
    
    # Créer toutes les tables
    print("\nCreation des tables...")
    Base.metadata.create_all(bind=engine)
    print("OK - Tables creees")

    # S'assurer que la table ticket_categories possède bien la colonne type_code
    try:
        with engine.begin() as conn:
            conn.execute(
                text(
                    "ALTER TABLE ticket_categories "
                    "ADD COLUMN IF NOT EXISTS type_code VARCHAR(50) "
                    "DEFAULT 'materiel' NOT NULL"
                )
            )
            conn.execute(
                text(
                    "ALTER TABLE ticket_categories "
                    "ALTER COLUMN type_code DROP DEFAULT"
                )
            )
    except Exception as e:
        print(f"Attention: impossible de vérifier/ajouter la colonne type_code sur ticket_categories: {e}")
    
    # Initialiser les rôles
    print("\nCreation des roles...")
    db = SessionLocal()
    try:
        init_roles(db)
        init_admin_user(db)
        init_ticket_types_and_categories(db)
    finally:
        db.close()
    
    print("\n" + "-" * 50)
    print("OK - Initialisation terminee avec succes !")
    print("\nVous pouvez maintenant:")
    print("  - Lancer le backend: uvicorn app.main:app --reload")
    print("  - Vous connecter avec: username=admin, password=admin123")

if __name__ == "__main__":
    main()

