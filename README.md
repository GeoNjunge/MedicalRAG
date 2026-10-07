# MedicalRAG(MedNLP)

I built MedicalRAG to solve a problem I kept noticing in healthcare software: most systems simply feed raw PDF documents to an LLM and hope for the best. That approach is fast, but in medical workflows it can be risky. Important facts get missed, details get made up, and the output is hard to trust.

MedicalRAG is a document processing system that takes medical PDFs, extracts the useful information first, and then builds a summary from that structured data. The idea is simple: don’t ask the model to read a messy document from scratch if you can first pull out the facts it actually needs.

---

## What it does

Upload a medical PDF and the system can:

- Extract diseases and clinical findings
- Pull out lab values and test results
- Map diagnoses to ICD-10 codes where possible
- Generate a short plain-language summary based on the extracted facts

This is useful when you want a system that is more reliable, more explainable, and less likely to hallucinate.

---

## Why I built it

Medical documents are messy. They are long, noisy, full of tables, headers, and inconsistent formatting. A lot of AI systems try to solve that by sending the whole document to a model and asking it to figure it out.

I wanted a better approach.

The system first reads the document and extracts structured information using rules and specialized NLP models. Only then does it summarize the result. That helps keep the output grounded in the actual document instead of the model guessing.

---

## The real-world problem behind it

I built this with a very specific real-world goal in mind: helping smaller clinics, especially in places with limited infrastructure, make better use of medical records without needing expensive hardware or constant internet access.

In many settings, clinics do not have powerful GPUs, high-end servers, or stable cloud connectivity. They often work on regular laptops and limited bandwidth. I wanted a system that could still help them process patient documents in a practical way.

That is why the project is designed around low-resource thinking:
- local processing where possible
- lighter models and efficient workflows
- offline-friendly behavior
- systems that can run on ordinary consumer hardware

This is not an “ideal lab” project. It is a system built for the reality many clinics face.

---

## How it works

The basic flow is:

PDF → read text → clean and split content → extract key facts → summarize

At a high level, the pipeline does this:

1. Read the document text from the PDF
2. Break it into smaller sections
3. Find disease names and relevant clinical data
4. Extract labs and values
5. Clean up and organize the results
6. Summarize only the extracted facts

This keeps the whole process more controlled and makes the output much easier to trust.

---

## Local and production setup

The project supports two modes:

### Local mode
This is the full research/development setup. It runs locally on a machine and uses a more complete NLP pipeline with offline models.

Best for:
- Offline work
- Research and experimentation
- Lower-resource local development

### Production mode
This is the lighter cloud version. It keeps the app lean by using external API services for the heavier reasoning work.

Best for:
- Hosted deployment
- Faster setup
- Lower local memory usage

---

## Performance and engineering focus

I also spent a lot of time on performance and reliability. A lot of the work here was about reducing unnecessary model reloads, optimizing CPU use, and getting the system to behave predictably under real constraints.

Some of the practical engineering work included:

- reducing cold-start latency by avoiding repeated heavy model initialization
- improving local inference performance on CPU-only machines
- tuning how models are loaded and reused
- improving job flow and progress tracking
- making the pipeline more robust for real-world use

This project is as much about systems design and optimization as it is about AI.

---

## Tech stack

The project uses a mix of backend, frontend, NLP, and AI tooling:

- FastAPI for the backend
- Redis for background job processing
- Angular for the frontend
- Python-based NLP pipeline
- Local model inference for offline use
- Cloud-based LLM access for lighter production deployment

---

## What makes this project different

A lot of AI demos stop at “upload a file and show a summary.”

This project goes a bit further:

- it tries to reduce hallucinations
- it uses extracted facts instead of raw document dumping
- it works with messy real-world healthcare content
- it tries to stay practical on limited hardware
- it balances model power with reliability

That is the core idea behind MedicalRAG.

---

## Challenges and limitations

This is still a research-style and prototype-oriented project in parts. It is not trying to pretend it is a perfect production healthcare system yet.

Some limitations include:

- medical documents can be inconsistent and hard to parse
- real clinical workflows need deeper validation and review
- the local pipeline depends on model setup and hardware constraints
- production behavior can vary depending on the upstream model provider

So this is a serious engineering project, but it is still evolving.

---

## Why I’m proud of it

What I like most about this project is that it tries to solve a real problem instead of just showing off AI output.

It is built around a practical idea:

If the system has to make decisions in a high-stakes domain, it should not rely on a model guessing from a noisy document. It should extract meaningful facts first and only then generate a summary.

That approach is more thoughtful, more reliable, and more useful in the real world.

It also matters because I designed it for settings where resources are limited. A small clinic should not need a data center to benefit from this kind of technology. It should work on everyday hardware, with reasonable performance and realistic constraints.

---

## Project status

This project is a working prototype and learning platform with a strong engineering focus. It combines AI work, backend architecture, performance tuning, and real-world system constraints.

It is not just a toy demo — it is a serious attempt at building a medical document pipeline that is more grounded, more efficient, and more accountable.

---

## Roadmap: Next optimizations

The current bottleneck is Python + CPU-bound NLP inference. The next phase is:

1. **C++ worker pool for inference** — Move the expensive parts (model loading, forward pass) into a native C++ service with manual memory management. This should give another 2–3x speedup.

2. **Parallel window processing** — Instead of sliding windows sequentially, spawn multiple workers to process overlapping windows concurrently. On a 4-core machine, this could be 3–4x faster.

3. **Quantized models on GPU if available** — For clinics that have GPU access, quantized model inference would be another order of magnitude faster.

These are intentionally left for later because the current approach works well for the target use case (single-machine, offline processing). But they unlock real scale if needed.

## Author

George Njunge

I’m focused on building reliable software systems, especially where AI, backend engineering, and real-world constraints meet.