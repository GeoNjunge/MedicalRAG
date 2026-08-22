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
  { label: '2-Core CPU Limit' },
  { label: '57% Latency Reduction' },
  { label: 'Zero GPU Dependency' },
];

export const LANDING_METRICS: LandingMetric[] = [
  {
    title: 'Processing Time',
    value: '30s',
    highlight: 'Reduced from 70s - 57% faster execution',
    accent: 'orange',
  },
  {
    title: 'CPU Target',
    value: '2-Core',
    highlight: 'Memory-cached runtime initialization',
    accent: 'blue',
  },
  {
    title: 'Data Integrity',
    value: 'Zero Data Loss',
    highlight: 'Strict Pytest schema validation',
    accent: 'green',
  },
];

export const PIPELINE_STEPS: PipelineStep[] = [
  {
    step: 1,
    title: 'Ingestion',
    subtitle: 'User uploads clinical PDF',
    icon: 'upload',
  },
  {
    step: 2,
    title: 'Parsing',
    subtitle: 'Asynchronous Docling text extraction',
    icon: 'parse',
  },
  {
    step: 3,
    title: 'Inference & RAG',
    subtitle: 'llama-cpp + Qwen-1.5B (warm memory initialized)',
    icon: 'infer',
  },
  {
    step: 4,
    title: 'Optimization',
    subtitle: 'ONNX Runtime + Sentence Transformers',
    icon: 'optimize',
  },
  {
    step: 5,
    title: 'Output',
    subtitle: 'Validated JSON clinical summary',
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
    title: 'Local Constrained Architecture (Engineered & Benchmark-Tested)',
    highlightTag: '2-Core CPU | 8GB RAM Target',
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
        label: 'Cold Start vs. Warm Memory Initialization',
        detail: 'Global model cache — 57% latency reduction',
      },
    ],
    engineeringFocus:
      'Optimized for privacy, zero cloud costs, air-gapped environments, and strict memory budgeting.',
    accent: 'orange',
  },
  {
    id: 'production',
    title: 'Production Cloud Architecture (Hosted Live Web Demo)',
    highlightTag: 'Free Tier Serverless Hosting',
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
      'Low-latency serverless execution avoiding continuous container memory overhead.',
    accent: 'blue',
  },
];

export const DUAL_APPROACH_CALLOUT =
  'Why the dual approach? Local execution proves hardware resource optimization and C++ binding capabilities; Cloud deployment provides 100% or close to 100% uptime.';
