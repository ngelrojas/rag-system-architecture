# naive/run_pipeline.py — run the naive pipeline end to end (needs OPENAI_API_KEY)
#
#   uv run python -m naive.run_pipeline
from naive.ingest import ingest_document
from naive.query import answer

if __name__ == "__main__":
    ingest_document(
        "The 2023 travel policy allows economy class for flights under six hours "
        "and premium economy above six hours. Receipts are required for every expense.",
        doc_id="travel-policy-2023",
    )
    print(answer("Which class can I book for a seven-hour flight?"))
