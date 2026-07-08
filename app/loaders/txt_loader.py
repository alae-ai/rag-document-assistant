from langchain_community.document_loaders import TextLoader


class TXTLoader:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def load(self):
        loader = TextLoader(self.file_path)
        return loader.load()
