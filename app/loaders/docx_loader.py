from langchain_community.document_loaders import Docx2txtLoader


class DOCXLoader:
    def __init__(self, file_path: str):
        self.file_path = file_path

    def load(self):
        loader = Docx2txtLoader(self.file_path)
        return loader.load()
