import json
import os
import logging
from dotenv import load_dotenv
from pymongo import MongoClient
import rdflib
from rdflib import Namespace, Literal, URIRef
from rdflib.namespace import RDF, OWL, RDFS, XSD

# Configuration du logging structuré
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("StreamVaultPipeline")

# Chargement des variables d'environnement depuis le .env
load_dotenv()

MONGO_USER = os.getenv("MONGO_INITDB_ROOT_USERNAME", "admin")
MONGO_PASS = os.getenv("MONGO_INITDB_ROOT_PASSWORD", "password")
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = os.getenv("MONGO_PORT", "27017")

def run_mongodb_pipeline():
    logger.info("==================================================")
    logger.info(" NIVEAU 1 : AUTOMATISATION MONGODB (PYMONGO)")
    logger.info("==================================================")
    
    uri = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/"
    client = MongoClient(uri)
    db = client["bibliotheque"]
    collection = db["livres"]
    
    if collection.count_documents({}) == 0:
        json_path = "livres.json"
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list) and data:
                    collection.insert_many(data)
                elif isinstance(data, dict):
                    collection.insert_one(data)
            logger.info(f"📁 Données de '{json_path}' importées avec succès dans MongoDB !")
        else:
            logger.warning(f"⚠️ Attention : le fichier {json_path} est introuvable !")

    count_initial = collection.count_documents({})
    logger.info(f"[Q3] Documents totaux : {count_initial}")
    
    first = collection.find_one()
    second = collection.find().skip(1).limit(1).next()
    logger.info(f"[Q4] Premier livre (Titre) : {first.get('titre')}")
    logger.info(f"[Q5] Deuxième livre (Auteur) : {second.get('auteur', second.get('auteurs'))}")
    
    multi = collection.find_one({"auteurs": {"$exists": True}})
    if multi:
        logger.info(f"[Q6] Livre multi-auteurs : {multi.get('titre')}")
        logger.info(f"[Q7] Chapitres associés : {multi.get('chapitres')}")
        
    oldest = collection.find_one(sort=[("annee", 1)])
    newest = collection.find_one(sort=[("annee", -1)])
    logger.info(f"[Q8] Plus ancien : {oldest.get('titre')} ({oldest.get('annee')})")
    logger.info(f"[Q9] Plus récent : {newest.get('titre')} ({newest.get('annee')})")
    
    gt_2000 = collection.count_documents({"annee": {"$gt": 2000}})
    lt_1950 = collection.count_documents({"annee": {"$lt": 1950}})
    logger.info(f"[Q12] > 2000 : {gt_2000} | [Q13] < 1950 : {lt_1950}")
    
    new_doc = {"titre": "Les Sentinelles de l'Algorithme", "auteur": "E. Turin", "annee": 2025}
    res = collection.insert_one(new_doc)
    logger.info(f"[Q19] Insertion OK -> Compteur : {collection.count_documents({})}")
    collection.delete_one({"_id": res.inserted_id})
    logger.info(f"[Q20] Suppression OK -> Compteur initial restauré : {collection.count_documents({})}\n")

def generate_ontology_code():
    logger.info("==================================================")
    logger.info(" NIVEAU 2 : GÉNÉRATION DE L'ONTOLOGIE OWL/RDF")
    logger.info("==================================================")
    
    g = rdflib.Graph()
    EX = Namespace("http://www.semanticweb.org/streamvault/onto#")
    g.bind("ex", EX)
    g.bind("owl", OWL)
    g.bind("rdfs", RDFS)
    g.bind("xsd", XSD)

    # 1. Classes
    classes = ["Personne", "Acteur", "Realisateur", "Film", "Genre", "Studio"]
    for c in classes:
        g.add((EX[c], RDF.type, OWL.Class))
    
    g.add((EX.Acteur, RDFS.subClassOf, EX.Personne))
    g.add((EX.Realisateur, RDFS.subClassOf, EX.Personne))

    # 2. Object Properties
    obj_props = {
        "aJoueDans": (EX.Acteur, EX.Film, EX.aPourActeur, False),
        "aRealise": (EX.Realisateur, EX.Film, EX.estRealisePar, False),
        "aPourGenre": (EX.Film, EX.Genre, EX.estDuGenre, False),
        "estProduitPar": (EX.Film, EX.Studio, EX.aProduit, False),
        "estSuiteDe": (EX.Film, EX.Film, EX.aPourSuite, False),
        "estFilialeDe": (EX.Studio, EX.Studio, EX.aPourFiliale, True)
    }
    
    for prop, (domain, range_cls, inverse, is_transitive) in obj_props.items():
        g.add((EX[prop], RDF.type, OWL.ObjectProperty))
        g.add((EX[prop], RDFS.domain, domain))
        g.add((EX[prop], RDFS.range, range_cls))
        g.add((EX[prop], OWL.inverseOf, inverse))
        if is_transitive:
            g.add((EX[prop], RDF.type, OWL.TransitiveProperty))

    # 3. Data Properties avec leurs Domaines rattachés
    data_props = {
        "aPourTitre": (EX.Film, XSD.string),
        "aPourAnnee": (EX.Film, XSD.integer),
        "aPourNoteIMDB": (EX.Film, XSD.float),
        "aPourIdentifiantIMDB": (EX.Film, XSD.string),
        "aPourNom": (EX.Personne, XSD.string)
    }
    
    for dp, (domain_cls, range_type) in data_props.items():
        g.add((EX[dp], RDF.type, OWL.DatatypeProperty))
        g.add((EX[dp], RDF.type, OWL.FunctionalProperty))
        g.add((EX[dp], RDFS.domain, domain_cls))
        g.add((EX[dp], RDFS.range, range_type))

    # 4. Individus et relations
    individuals = {
        "ChristopherNolan": (EX.Realisateur, {EX.aPourNom: "Christopher Nolan"}),
        "LeonardoDiCaprio": (EX.Acteur, {EX.aPourNom: "Leonardo DiCaprio"}),
        "Inception": (EX.Film, {EX.aPourTitre: "Inception", EX.aPourAnnee: 2010, EX.aPourNoteIMDB: 8.8, EX.aPourIdentifiantIMDB: "tt1375666"}),
        "Casablanca": (EX.Film, {EX.aPourTitre: "Casablanca", EX.aPourAnnee: 1942}),
        "ActionGenre": (EX.Genre, {}),
        "DrameGenre": (EX.Genre, {}),
        "WarnerBros": (EX.Studio, {}),
        "WarnerAnimation": (EX.Studio, {}),
        "WarnerBrosGroup": (EX.Studio, {})
    }

    for ind, (cls, props) in individuals.items():
        g.add((EX[ind], RDF.type, cls))
        for p_uri, val in props.items():
            dt = XSD.integer if isinstance(val, int) else (XSD.float if isinstance(val, float) else XSD.string)
            g.add((EX[ind], p_uri, Literal(val, datatype=dt)))

    assertions = [
        (EX.ChristopherNolan, EX.aRealise, EX.Inception),
        (EX.LeonardoDiCaprio, EX.aJoueDans, EX.Inception),
        (EX.Inception, EX.aPourGenre, EX.ActionGenre),
        (EX.Inception, EX.estProduitPar, EX.WarnerBros),
        (EX.WarnerAnimation, EX.estFilialeDe, EX.WarnerBros),
        (EX.WarnerBros, EX.estFilialeDe, EX.WarnerBrosGroup)
    ]
    
    for subj, pred, obj in assertions:
        g.add((subj, pred, obj))

    output_file = "streamvault_auto_ontology.owl"
    g.serialize(destination=output_file, format="xml")
    logger.info(f"✅ Ontologie OWL générée et enregistrée dans '{output_file}' ({len(g)} triplets).")

if __name__ == "__main__":
    run_mongodb_pipeline()
    generate_ontology_code()