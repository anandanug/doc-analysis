import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import ChatOpenAI
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
import time
import os

# Sidebar navigation
st.sidebar.title("Navigasi")
page = st.sidebar.selectbox("Pilih Halaman", ["Tutorial", "Aplikasi", "Tentang"])

# Title
st.title("Aplikasi Analisis Dokumen")

# Configuration for API Key
api_key = "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"

# About Page
if page == "Tentang":
    st.header("Tentang Aplikasi ini")
    st.markdown("""
### Aplikasi Tanya Jawab Dokumen

Aplikasi ini dirancang untuk membantu pengguna berinteraksi dengan dan mendapatkan wawasan dari dokumen PDF melalui pertanyaan bahasa alami. Dengan menggunakan model bahasa canggih dari OpenAI, aplikasi ini mencari dan mengambil informasi yang relevan dari dokumen yang diunggah, sehingga memudahkan pengguna menemukan jawaban spesifik tanpa perlu mencari secara manual di seluruh dokumen besar.

#### Fitur Utama
- **Unggah Dokumen**: Unggah dokumen PDF untuk dianalisis.
- **Tanya Jawab Kontekstual**: Ajukan pertanyaan dalam bahasa alami tentang isi dokumen.
- **Pengambilan Informasi yang Efisien**: Aplikasi ini menggunakan pencarian berbasis vektor untuk menemukan bagian yang paling relevan dengan cepat.
- **Integrasi Model Bahasa**: Didukung oleh GPT dari OpenAI, menyediakan jawaban dan ringkasan berkualitas tinggi.

#### Teknologi yang Digunakan
- **Streamlit**: Untuk membuat antarmuka pengguna berbasis web.
- **LangChain**: Untuk menangani pemuatan dokumen, pemisahan, dan pengambilan informasi.
- **OpenAI GPT-4**: Untuk menghasilkan respons berdasarkan konten dokumen.

#### Cara Kerja
1. **Pemuatan dan Pemisahan Dokumen**: Dokumen PDF yang diunggah diproses dan dibagi menjadi bagian-bagian yang dapat dikelola untuk meningkatkan akurasi pengambilan informasi.
2. **Penyimpanan Vektor Embedding**: Setiap bagian diubah menjadi embedding, yang memungkinkan pencarian berbasis vektor yang efisien.
3. **Rantai Tanya Jawab**: Aplikasi mencocokkan pertanyaan pengguna dengan bagian dokumen yang relevan dan menghasilkan jawaban yang ringkas dan relevan.

#### Peningkatan di Masa Depan
- **Dukungan untuk Jenis File Tambahan**: Termasuk DOCX, TXT, dan lainnya.
- **Dukungan Multi-Bahasa**: Memperluas dukungan bahasa di luar bahasa Inggris.
- **Akurasi Pengambilan yang Lebih Baik**: Meningkatkan proses pencocokan dan peringkasan.

Kami berharap aplikasi ini memudahkan pengguna dalam mengekstrak informasi berharga dari dokumen mereka dengan cepat dan efektif.

    """)

# Tutorial Page
elif page == "Tutorial":
    st.header("Tutorial Penggunaan")
    st.markdown("""
    ### Langkah-langkah Menggunakan Aplikasi ini:
    
    1. **Masukkan API Key OpenAI Anda** di bilah samping.
       - API Key ini digunakan untuk mengakses model bahasa OpenAI.
       - Pastikan API Key Anda tetap aman dan tidak dibagikan dengan orang lain.
    
    2. **Unggah Dokumen PDF** yang ingin Anda tanyakan.
       - Aplikasi ini hanya mendukung file PDF. Klik tombol "Upload" di bagian utama untuk memilih file PDF.
    
    3. **Tunggu Hingga Dokumen Diproses.**
       - Setelah diunggah, dokumen Anda akan diproses secara otomatis, dipecah menjadi bagian-bagian kecil agar model dapat membaca dan mencari informasi yang relevan.
    
    4. **Masukkan Pertanyaan Anda.**
       - Setelah pemrosesan selesai, Anda akan melihat kotak teks di mana Anda bisa memasukkan pertanyaan.
       - Ketik pertanyaan yang relevan dengan isi dokumen yang diunggah.
    
    5. **Dapatkan Jawaban.**
       - Aplikasi akan mencari konteks dalam dokumen dan memberikan jawaban singkat serta menampilkan bagian dari dokumen yang relevan.
    
    ### Tips untuk Penggunaan yang Efektif
    - Pastikan pertanyaan Anda spesifik dan terkait dengan dokumen.
    - Jika jawaban yang diberikan kurang jelas, cobalah merumuskan ulang pertanyaan Anda.
    - Aplikasi ini tidak dapat memberikan informasi di luar dokumen yang diunggah, jadi pastikan untuk hanya menanyakan hal-hal yang tercantum dalam dokumen.
    """)

# Main Page for Document Q&A
elif page == "Aplikasi":
    # st.header("Document Q&A")

    # Ensure the API key is provided
    if not api_key:
        st.warning("Please enter your OpenAI API key to continue.")
        st.stop()

    # Upload PDF file
    # uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")
    uploaded_file = "doc/HR-Employee Handbook.pdf"

    # Process the uploaded PDF
    if uploaded_file:
        with st.spinner("Memuat dokumen..."):
            # Load the PDF document
            loader = PyPDFLoader(uploaded_file)
            docs = loader.load()
            
            # Split the document into manageable chunks
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            splits = text_splitter.split_documents(docs)
            
            # Create the vector store
            vectorstore = InMemoryVectorStore.from_documents(
                documents=splits,
                embedding=OpenAIEmbeddings(api_key=api_key)
            )
            
            # Set up retriever and chains
            retriever = vectorstore.as_retriever()
            
            # Configure the prompt template
            system_prompt = (
                "You are an assistant for question-answering tasks. "
                "Use the following pieces of retrieved context to answer "
                "the question. If you don't know the answer, say that you "
                "don't know. Use three sentences maximum and keep the "
                "answer concise."
                "\n\n"
                "{context}"
            )

            prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", system_prompt),
                    ("human", "{input}"),
                ]
            )
            
            # Initialize LLM and create chains
            llm = ChatOpenAI(model="gpt-4", api_key=api_key)
            question_answer_chain = create_stuff_documents_chain(llm, prompt)
            rag_chain = create_retrieval_chain(retriever, question_answer_chain)

        st.success("Dokumen selesai dimuat dan berhasil di proses!")

        # Input box for question
        question = st.text_input("Masukkan pertanyaan kamu tentang dokumen:")

        if question:
            # Mulai pencatatan waktu pemrosesan
            start_time = time.time()  # Waktu saat pertanyaan diterima
            
            # Proses pertanyaan
            with st.spinner("Mendapatkan jawaban..."):
                results = rag_chain.invoke({"input": question})
                
                # Catat waktu selesai pemrosesan
                end_time = time.time()  # Waktu saat jawaban diberikan
                
                # Hitung durasi pemrosesan
                processing_time = end_time - start_time  # Durasi dalam detik
                
                # Tampilkan durasi pemrosesan
                st.write(f"Waktu pemrosesan: {processing_time:.2f} detik")
                
                # Display the answer and context
                if "context" in results:
                    st.subheader("Jawaban:")
                    st.write(results.get("answer", "Tidak ada jawaban ditemukan."))
                    
                    st.subheader("Konteks yang Relevan:")
                    st.write(results["context"][0].page_content)
                else:
                    st.write("Tidak ada konteks yang relevan.")
    else:
        st.info("Please upload a PDF file to get started.")