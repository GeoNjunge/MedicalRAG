export interface LandingBadge {
 label: string;
}

export interface LandingMetric {
 title: string;
 value: string;
 highlight: string;
 accent: 'orange' | 'green' | 'blue';
}

export interface PipelineStep {
 step: number;
 title: string;
 subtitle: string;
 icon: 'upload' | 'parse' | 'infer' | 'optimize' | 'output';
}

export const LANDING_BADGES: LandingBadge[] = [
 { label: 'Works Offline on 2-Core CPU' },
 { label: 'Zero GPU Dependency' },
 { label: '57% Latency Reduction (warm cache)' },
];

export interface LandingTrustPoint {
 label: string;
 detail: string;
}

export const LANDING_TRUST_POINTS: LandingTrustPoint[] = [
 {
 label: 'Works offline on 2-core CPU',
 detail: 'Built for clinics on ordinary laptops - local inference without a data center.',
 },
 {
 label: 'Zero GPU dependency',
 detail: 'Quantized CPU models and efficient pipelines for resource-constrained sites.',
 },
 {
 label: 'Facts before summaries',
 detail: 'Extract → validate → summarize. Designed for reliability and correctness, not demo speed.',
 },
];

export const LANDING_METRICS: LandingMetric[] = [
 {
 title: 'Core approach',
 value: 'Extract First',
 highlight: 'Diseases, labs, and ICD-10 pulled out before any summary is generated',
 accent: 'green',
 },
 {
 title: 'Built for',
 value: 'Low Resource',
 highlight: 'Offline-friendly local mode on consumer hardware - privacy and air-gapped use',
 accent: 'blue',
 },
 {
 title: 'Clinical output',
 value: 'Validated',
 highlight: 'Schema-checked JSON you can review - explainable, not a black-box paragraph',
 accent: 'orange',
 },
];

export const PIPELINE_STEPS: PipelineStep[] = [
 {
 step: 1,
 title: 'Ingestion',
 subtitle: 'Clinical PDF uploaded locally or via API',
 icon: 'upload',
 },
 {
 step: 2,
 title: 'Parse & segment',
 subtitle: 'Text extraction, cleanup, and section splits',
 icon: 'parse',
 },
 {
 step: 3,
 title: 'Fact extraction',
 subtitle: 'Diseases, labs, ICD-10 - MedSpaCy + rules',
 icon: 'infer',
 },
 {
 step: 4,
 title: 'Organize',
 subtitle: 'Structured JSON - validated before generation',
 icon: 'optimize',
 },
 {
 step: 5,
 title: 'Summarize',
 subtitle: 'Plain-language summary from extracted facts only',
 icon: 'output',
 },
];

export const STACK_TAGS: string[] = [
 'FastAPI',
 'llama-cpp',
 'Qwen-1.5B',
 'ONNX Runtime',
 'Docling',
 'MedSpaCy',
 'Pytest',
 'Docker',
];

export interface ArchitectureCard {
 id: 'local' | 'production';
 title: string;
 highlightTag: string;
 steps: { order: number; label: string; detail: string }[];
 engineeringFocus: string;
 accent: 'orange' | 'blue';
}

export const ARCHITECTURE_COMPARISON: ArchitectureCard[] = [
 {
 id: 'local',
 title: 'Local mode - offline clinics & limited infrastructure',
 highlightTag: '2-Core CPU | Offline-first',
 steps: [
 {
 order: 1,
 label: 'Asynchronous PDF Ingestion',
 detail: 'FastAPI + Docling',
 },
 {
 order: 2,
 label: 'Vector Embeddings & Hybrid Search',
 detail: 'ONNX Runtime + MedSpaCy',
 },
 {
 order: 3,
 label: 'Local Quantized Inference',
 detail: 'llama-cpp-python + Qwen-1.5B INT4',
 },
 {
 order: 4,
 label: 'Summarize extracted facts only',
 detail: 'Local LLM on structured JSON - not raw PDF dumping',
 },
 ],
 engineeringFocus:
 'Privacy, offline operation, and predictable behavior on everyday hardware - built for small clinics, not ideal lab conditions.',
 accent: 'orange',
 },
 {
 id: 'production',
 title: 'Production mode - hosted demo & lighter deployment',
 highlightTag: 'Cloud APIs when local GPU/CPU is unavailable',
 steps: [
 {
 order: 1,
 label: 'Client Payload Submission',
 detail: 'Frontend / UI',
 },
 {
 order: 2,
 label: 'FastAPI Ingestion Layer',
 detail: 'Render Free Tier',
 },
 {
 order: 3,
 label: 'Cloud Inference Router',
 detail: 'Groq API (llama-3.3-70b-versatile)',
 },
 {
 order: 4,
 label: 'Direct JSON Response Formatting',
 detail: 'Structured SSE + validated output schema',
 },
 ],
 engineeringFocus:
 'Same extract-then-summarize schema; heavier reasoning delegated to cloud APIs for this live demo.',
 accent: 'blue',
 },
];

export const DUAL_APPROACH_CALLOUT =
 'Local mode is the target story: process records where connectivity and hardware are limited. Production mode keeps this demo reachable while preserving the same structured clinical output.';
