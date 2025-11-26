import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ChevronDown, Copy, Download, RotateCw, Trash2, Moon, Sun } from "lucide-react";

// API Base URL - auto-detect backend URL based on domain
const API_BASE_URL = (() => {
  if (typeof window !== 'undefined' && window.location.hostname.includes('onrender.com')) {
    return 'https://datn-demo.onrender.com';
  }
  return import.meta.env.VITE_API_URL || "http://localhost:8002";
})();

interface AnalysisResult {
  probability: number;
  label: string;
  confidence: number;
  explanations: string[];
  model_name: string;
}

interface EnsembleResponse {
  url: string;
  url_model: AnalysisResult;
  html_model: AnalysisResult;
  dom_model: AnalysisResult;
  ensemble: AnalysisResult;
}

interface HistoryItem {
  url: string;
  result: EnsembleResponse;
  timestamp: number;
}

// ============ Helper Functions ============
function getRiskLevel(probability: number): { level: string; color: string; bgColor: string } {
  if (probability < 0.33) return { level: "LOW", color: "text-green-600", bgColor: "bg-green-50 border-green-200" };
  if (probability < 0.67) return { level: "MEDIUM", color: "text-yellow-600", bgColor: "bg-yellow-50 border-yellow-200" };
  return { level: "HIGH", color: "text-red-600", bgColor: "bg-red-50 border-red-200" };
}

function exportAsJSON(data: any, filename: string) {
  const json = JSON.stringify(data, null, 2);
  const blob = new Blob([json], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

function copyToClipboard(text: string) {
  navigator.clipboard.writeText(text);
}

// ============ Result Card Component ============
function ResultCard({ result, modelIcon }: { result: AnalysisResult; modelIcon: string }) {
  const [expanded, setExpanded] = useState(false);
  const risk = getRiskLevel(result.probability);

  return (
    <Card className={`p-4 border ${risk.bgColor}`}>
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="text-2xl">{modelIcon}</span>
          <div>
            <h3 className="font-semibold">{result.model_name}</h3>
            <p className={`text-sm ${risk.color}`}>
              {result.label} ({result.probability.toFixed(1)}%)
            </p>
          </div>
        </div>
        <div className={`px-3 py-1 rounded-full text-xs font-semibold ${risk.color}`}>
          {risk.level} Risk
        </div>
      </div>

      {/* Confidence Badge */}
      <div className="mb-3">
        <div className="flex justify-between mb-1">
          <span className="text-xs text-gray-600">Confidence</span>
          <span className="text-xs font-semibold">{(result.confidence * 100).toFixed(0)}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-blue-500 h-2 rounded-full transition-all"
            style={{ width: `${result.confidence * 100}%` }}
          />
        </div>
      </div>

      {/* Explanations */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center gap-2 text-sm text-gray-700 hover:text-gray-900 font-medium"
      >
        <ChevronDown
          size={16}
          className={`transition-transform ${expanded ? "rotate-180" : ""}`}
        />
        Why this verdict?
      </button>

      {expanded && (
        <div className="mt-3 space-y-2">
          {result.explanations.map((exp, idx) => (
            <div key={idx} className="text-sm text-gray-700 pl-6 flex gap-2">
              <span>•</span>
              <span>{exp}</span>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}

// ============ Ensemble Verdict Component ============
function EnsembleVerdictCard({ result }: { result: AnalysisResult }) {
  const risk = getRiskLevel(result.probability);
  const isPhishing = result.label === "PHISHING";

  return (
    <Card
      className={`p-6 border-2 text-center ${risk.bgColor}`}
    >
      <div className="mb-4">
        <h2 className="text-3xl font-bold mb-2">
          {isPhishing ? "⚠️ PHISHING DETECTED" : "✅ LEGITIMATE"}
        </h2>
        <p className={`text-2xl font-bold ${risk.color}`}>
          {risk.level} RISK
        </p>
      </div>

      <div className="mb-4">
        <div className="flex justify-center gap-4 mb-3">
          <div>
            <p className="text-sm text-gray-600">Confidence</p>
            <p className="text-2xl font-bold">{(result.confidence * 100).toFixed(0)}%</p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Probability</p>
            <p className="text-2xl font-bold">{(result.probability * 100).toFixed(1)}%</p>
          </div>
        </div>
      </div>

      <div className="space-y-2">
        {result.explanations.map((exp, idx) => (
          <p key={idx} className="text-sm text-gray-700">
            {exp}
          </p>
        ))}
      </div>
    </Card>
  );
}

// ============ History Panel Component ============
function HistoryPanel({ history, onSelectUrl }: { history: HistoryItem[]; onSelectUrl: (url: string) => void }) {
  return (
    <Card className="p-4">
      <h3 className="font-semibold mb-3">📋 Recent Checks</h3>
      {history.length === 0 ? (
        <p className="text-sm text-gray-500">No history yet</p>
      ) : (
        <div className="space-y-2">
          {history.slice(-10).reverse().map((item, idx) => (
            <div key={idx} className="flex items-center justify-between p-2 bg-gray-50 rounded hover:bg-gray-100">
              <div className="flex-1 min-w-0">
                <p className="text-xs text-gray-500 truncate">{item.url}</p>
                <p className={`text-xs font-semibold ${item.result.ensemble.label === "PHISHING" ? "text-red-600" : "text-green-600"}`}>
                  {item.result.ensemble.label}
                </p>
              </div>
              <button
                onClick={() => onSelectUrl(item.url)}
                className="ml-2 p-1 hover:bg-gray-200 rounded"
                title="Re-check"
              >
                <RotateCw size={14} />
              </button>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
}

// ============ Main Component ============
export default function Index() {
  const [url, setUrl] = useState("");
  const [htmlFile, setHtmlFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<EnsembleResponse | null>(null);
  const [history, setHistory] = useState<HistoryItem[]>(() => {
    const saved = localStorage.getItem("phishing_history");
    return saved ? JSON.parse(saved) : [];
  });
  const [darkMode, setDarkMode] = useState(() => {
    return localStorage.getItem("darkMode") === "true";
  });
  const [activeTab, setActiveTab] = useState("url");

  // Save history to localStorage
  useEffect(() => {
    localStorage.setItem("phishing_history", JSON.stringify(history));
  }, [history]);

  // Save dark mode preference
  useEffect(() => {
    localStorage.setItem("darkMode", String(darkMode));
    if (darkMode) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }, [darkMode]);

  // Analyze URL
  async function analyzeUrl() {
    if (!url) {
      setError("Please enter a URL");
      return;
    }

    setError("");
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/proxy/analyze_url_full`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url, normalize: true }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Analysis failed");
      }

      const data = await response.json();
      setResult(data);

      // Add to history
      setHistory([...history, { url, result: data, timestamp: Date.now() }]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error occurred");
    } finally {
      setLoading(false);
    }
  }

  // Analyze HTML File
  async function analyzeHtmlFile() {
    if (!htmlFile) {
      setError("Please select an HTML file");
      return;
    }

    setError("");
    setLoading(true);
    try {
      const html = await htmlFile.text();
      const response = await fetch(`${API_BASE_URL}/proxy/analyze_html_file`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ html_content: html }),
      });

      if (!response.ok) {
        throw new Error("HTML analysis failed");
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error occurred");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={darkMode ? "dark" : ""}>
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800 p-6">
        {/* Header */}
        <div className="max-w-7xl mx-auto mb-8 flex justify-between items-center">
          <div>
            <h1 className="text-4xl font-bold text-gray-900 dark:text-white">🔗 URL Guardian</h1>
            <p className="text-gray-600 dark:text-gray-400">Phishing URL Detection using 3 AI Models</p>
          </div>
          <button
            onClick={() => setDarkMode(!darkMode)}
            className="p-2 rounded-full bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600"
          >
            {darkMode ? <Sun size={20} /> : <Moon size={20} />}
          </button>
        </div>

        <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-2">
            <Card className="p-6 dark:bg-gray-800 dark:border-gray-700">
              <Tabs value={activeTab} onValueChange={setActiveTab}>
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="url">🔗 Check URL</TabsTrigger>
                  <TabsTrigger value="html">📄 Upload HTML</TabsTrigger>
                </TabsList>

                {/* URL Tab */}
                <TabsContent value="url" className="space-y-4 mt-4">
                  <div className="flex gap-2">
                    <Input
                      type="url"
                      placeholder="https://example.com"
                      value={url}
                      onChange={(e) => setUrl(e.target.value)}
                      onKeyPress={(e) => e.key === "Enter" && analyzeUrl()}
                      className="dark:bg-gray-700 dark:text-white dark:border-gray-600"
                    />
                    <Button onClick={analyzeUrl} disabled={loading}>
                      {loading ? "Analyzing..." : "Check"}
                    </Button>
                  </div>
                </TabsContent>

                {/* HTML Tab */}
                <TabsContent value="html" className="space-y-4 mt-4">
                  <div className="border-2 border-dashed rounded-lg p-6 text-center hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer">
                    <input
                      type="file"
                      accept=".html"
                      onChange={(e) => setHtmlFile((e.target as HTMLInputElement).files?.[0] || null)}
                      className="hidden"
                      id="html-input"
                    />
                    <label htmlFor="html-input" className="cursor-pointer">
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {htmlFile ? `📁 ${htmlFile.name}` : "📁 Drop HTML file here or click to select"}
                      </p>
                    </label>
                  </div>
                  {htmlFile && (
                    <Button onClick={analyzeHtmlFile} disabled={loading} className="w-full">
                      {loading ? "Analyzing..." : "Analyze HTML"}
                    </Button>
                  )}
                </TabsContent>
              </Tabs>

              {/* Error Message */}
              {error && (
                <div className="mt-4 p-4 bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-700 rounded text-red-700 dark:text-red-100">
                  ❌ {error}
                </div>
              )}

              {/* Results */}
              {result && (
                <div className="mt-6 space-y-6">
                  {/* Ensemble Verdict */}
                  <EnsembleVerdictCard result={result.ensemble} />

                  {/* Individual Model Results */}
                  <div>
                    <h3 className="font-semibold mb-3">📊 Individual Model Results</h3>
                    <div className="space-y-3">
                      <ResultCard result={result.url_model} modelIcon="🔗" />
                      <ResultCard result={result.html_model} modelIcon="📄" />
                      <ResultCard result={result.dom_model} modelIcon="🌳" />
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex gap-2 flex-wrap">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => copyToClipboard(JSON.stringify(result, null, 2))}
                      className="gap-1"
                    >
                      <Copy size={14} /> Copy
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => exportAsJSON(result, "phishing-analysis.json")}
                      className="gap-1"
                    >
                      <Download size={14} /> Export
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => {
                        setResult(null);
                        setUrl("");
                      }}
                      className="gap-1"
                    >
                      <Trash2 size={14} /> Clear
                    </Button>
                  </div>
                </div>
              )}
            </Card>
          </div>

          {/* Sidebar */}
          <div className="space-y-4">
            <HistoryPanel
              history={history}
              onSelectUrl={(selectedUrl) => {
                setUrl(selectedUrl);
                setActiveTab("url");
              }}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
