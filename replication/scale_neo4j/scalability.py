from neo4j import GraphDatabase

# Fonction pour créer un nœud avec une propriété 'name'
def create_node(driver, name):
    with driver.session() as session:
        result = session.write_transaction(create_node_tx, name)
        return result

def create_node_tx(tx, name):
    return tx.run("CREATE (n:Person {name: $name}) RETURN id(n)", name=name).single().value()

# Fonction pour lire les données depuis un nœud spécifique
def read_node(driver, node_id):
    with driver.session() as session:
        result = session.read_transaction(read_node_tx, node_id)
        return result

def read_node_tx(tx, node_id):
    return tx.run("MATCH (n) WHERE id(n) = $node_id RETURN n.name AS name", node_id=node_id).single().value()

# Configuration de la connexion à Neo4j
uri = "bolt://neo4j-core1:7687"  # URI de neo4j-core1
username = "neo4j"
password = "votre_mot_de_passe"

# Établir une connexion à Neo4j
driver = GraphDatabase.driver(uri, auth=(username, password))

# Créer un nœud dans neo4j-core1
node_name = "Alice"
node_id = create_node(driver, node_name)
print(f"Nœud créé avec l'ID : {node_id}")

# Lire le nœud créé depuis neo4j-core2
read_result = read_node(driver, node_id)
if read_result:
    print(f"Nom du nœud lu depuis neo4j-core2: {read_result}")
else:
    print("Le nœud n'a pas été trouvé dans neo4j-core2")

# Fermer le pilote Neo4j
driver.close()
