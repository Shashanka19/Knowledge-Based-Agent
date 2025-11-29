# 🚀 Quick Setup Guide

## ❌ Current Issues Fixed:

1. **"Couldn't find relevant information" errors** - This happens when:
   - No documents are uploaded to the knowledge base
   - Invalid/missing OpenAI API key

2. **API Key Setup** - The placeholder key needs to be replaced

## ✅ How to Fix:

### Step 1: Get OpenAI API Key
1. Go to: https://platform.openai.com/api-keys
2. Sign in or create account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)

### Step 2: Update Configuration
1. Open the `.env` file in the project folder
2. Find this line: `OPENAI_API_KEY=sk-test-key-placeholder`
3. Replace with your actual key: `OPENAI_API_KEY=sk-your_actual_key_here`
4. Save the file

### Step 3: Test with Sample Document
1. Restart the application (Ctrl+C, then run again)
2. Go to the **Upload** tab
3. Upload the provided `sample_company_policies.txt` file
4. Click "Process Documents"
5. Go to **Chat** tab and ask: "What is the remote work policy?"

## 🎯 Test Questions:
Once you upload the sample document, try these questions:
- "What is the remote work policy?"
- "How do I get IT support?"
- "What are the employee benefits?"
- "What is the vacation policy?"
- "How do I access the VPN?"

## 📞 Expected Results:
After fixing the API key and uploading documents, you should see:
- ✅ Detailed answers with source citations
- 📚 Document references showing where info came from
- 🎯 Relevant content based on your questions

The system is working correctly - it just needs real documents and a valid API key!