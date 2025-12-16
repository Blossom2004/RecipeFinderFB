import os
from typing import Dict, Any, List
from azure.cosmos import CosmosClient, PartitionKey

class CosmosService:
    def __init__(self):
        self.endpoint = os.getenv("COSMOS_ENDPOINT", "")
        self.key = os.getenv("COSMOS_KEY", "")
        self.db_name = os.getenv("COSMOS_DATABASE", "RecipeFinderDB")
        self.container_name = os.getenv("COSMOS_CONTAINER", "recipeRuns")
        self.partition_key_path = os.getenv("COSMOS_PARTITION_KEY", "/sessionId")

        self.client = None
        self.db = None
        self.container = None

        if self.endpoint and self.key:
            self.client = CosmosClient(self.endpoint, credential=self.key)
            self.db = self.client.create_database_if_not_exists(id=self.db_name)
            self.container = self.db.create_container_if_not_exists(
                id=self.container_name,
                partition_key=PartitionKey(path=self.partition_key_path),
                offer_throughput=400,
            )

    def upsert_run(self, doc: Dict[str, Any]) -> None:
        if not self.container:
            return
        self.container.upsert_item(doc)

    def list_runs(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        if not self.container:
            return []
        query = "SELECT TOP @limit * FROM c WHERE c.sessionId = @sid ORDER BY c.createdAt DESC"
        params = [{"name": "@sid", "value": session_id}, {"name": "@limit", "value": limit}]
        items = list(self.container.query_items(
            query=query,
            parameters=params,
            partition_key=session_id,
            enable_cross_partition_query=False
        ))
        return items
