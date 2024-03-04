from langchain import FAISS
from langchain.document_loaders import PyPDFium2Loader
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceEmbeddings
from langchain.text_splitter import CharacterTextSplitter
import pypdfium2 as pdfium
from constants import chunk_size, chunk_overlap, number_snippets_to_retrieve, faiss_path


def download_and_index_pdf(url: list[str]) -> FAISS:
    """
    Download and index a list of PDFs based on the URLs
    """

    def __update_metadata(pages, url):
        """
        Add to the document metadata the title and original URL
        """
        for page in pages:
            pdf = pdfium.PdfDocument(page.metadata['source'])
            title = pdf.get_metadata_dict().get('Title', url)
            page.metadata['source'] = url
            page.metadata['title'] = title
        return pages

    all_pages = []
    # for url in urls:
    loader = PyPDFium2Loader(url)
    splitter = CharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    pages = loader.load_and_split(splitter)
    pages = __update_metadata(pages, url)
    all_pages += pages
    embedding = HuggingFaceEmbeddings(
        model_name="BAAI/bge-large-en-v1.5",
        model_kwargs = {'device':'cpu'},
    )
    faiss_index = FAISS.from_documents(all_pages, embedding)

    return faiss_index

def get_faiss_index():
    embedding = HuggingFaceEmbeddings(
        model_name="BAAI/bge-large-en-v1.5",
        model_kwargs = {'device':'cpu'},
    )
    faiss_index = FAISS.load_local(faiss_path, embedding)
    return faiss_index
def search_faiss_index(faiss_index: FAISS, query: str, top_k: int = number_snippets_to_retrieve) -> list:
    """
    Search a FAISS index, using the passed query
    """

    # docs = faiss_index.similarity_search(query, k=top_k)
    retriever = faiss_index.as_retriever(
    search_type="similarity_score_threshold", search_kwargs={"score_threshold": 0.45}
    )
    docs = retriever.get_relevant_documents(query)


    # print(docs)
    return docs
