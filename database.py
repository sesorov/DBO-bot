import pymongo


class BankDatabase:

    def __init__(self):
        self.client = pymongo.MongoClient()

        self.banks = self.client['banks']  # database name

    def add_individual(self, bank_info: dict):
        self.banks['individuals'].insert_one(bank_info)

    def add_entitiy(self, bank_info: dict):
        self.banks['entities'].insert_one(bank_info)

    def get_individuals(self) -> list:
        return list(self.banks['individuals'].find())
        # return {'name': bank['name'], 'license': bank['license'], 'site': bank['site'], 'is_mobile': bank[
        # 'is_mobile']}

    def get_entity(self) -> list:
        return list(self.banks['entities'].find())
