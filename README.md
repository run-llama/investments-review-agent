# Investments Review Agent

Demo that uses LlamaAgents in combination with LlamaExtract, LlamaClassify and LlamaSheets to showcase the features of LlamaCloud in the fields of financial documents, specifically for what concerns investments spreadsheets and board updates/management presentations.

## Installation and Usage

Clone the repository:

```bash
git clone https://github.com/run-llama/investments-review-agent
cd investments-review-agent
``` 

Install the application:

```bash
uv pip install .
```

Export the necessary env variables:

```bash
export OPENAI_API_KEY="..."
export LLAMA_CLOUD_API_KEY="..."
```

Run the server:

```bash
serve
```

Access the application at `http://localhost:8000/`.

## How it works

From the frontend of the application, you can choose whether to upload a presentation or an excel sheet.

If you choose 'presentation', you can upload either a Management Presentation or a Board Update Deck:

1. The uploaded document will be uploaded to the S3 storage in LlamaCloud
2. The uploaded document will be classified as either a Management Presentation or a Board Update Deck (LlamaClassify)
3. Based on the classification, details will be extracted from the file and sent back to the frontend for rendering

Find an example in [`data/Board-Deck-Template.pdf`](data/Board-Deck-Template.pdf)

If you choose 'excel sheet', you can upload a spreadsheet containing details on an investment portoflio:

- The file will be uploaded to LlamaCloud S3 Storage
- It will be parsed by LlamaSheets and the data will be extracted and downloaded as parquet files
- The parquet files will be converted to markdown tables
- An OpenAI model will create a summary of the investment portfolio trends and performances.

Find an example in [`data/portfolio.xlsx`](./data/portfolio.xlsx)
