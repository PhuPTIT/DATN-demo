import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

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

const Index = () => {
  // Tab states
  const [activeTab, setActiveTab] = useState("url");

  // URL Input states
  const [urlInput, setUrlInput] = useState("");
  const [isCheckingFull, setIsCheckingFull] = useState(false);
  const [urlAnalysisResult, setUrlAnalysisResult] = useState<EnsembleResponse | null>(null);
  const [urlError, setUrlError] = useState("");

  // HTML File Upload states
  const [htmlFile, setHtmlFile] = useState<File | null>(null);
  const [htmlFileContent, setHtmlFileContent] = useState<string>("");
  const [isAnalyzingFile, setIsAnalyzingFile] = useState(false);
  const [fileAnalysisResult, setFileAnalysisResult] = useState<EnsembleResponse | null>(null);
  const [fileError, setFileError] = useState("");

  // ============ Helper Functions ============

  const getRiskLevel = (probability: number) => {
    if (probability < 0.33) return { level: "LOW", color: "bg-green-500", textColor: "text-green-600" };
    if (probability < 0.67) return { level: "MEDIUM", color: "bg-yellow-500", textColor: "text-yellow-600" };
    return { level: "HIGH", color: "bg-red-500", textColor: "text-red-600" };
  };

  const formatPercentage = (prob: number) => (prob * 100).toFixed(2);

  // ============ URL Tab Functions ============

  const analyzeUrlFull = async () => {
    if (!urlInput.trim()) {
      setUrlError("Please enter a URL");
      return;
    }

    if (!urlInput.startsWith("http://") && !urlInput.startsWith("https://")) {
      setUrlError("URL must start with http:// or https://");
      return;
    }

    setIsCheckingFull(true);
    setUrlError("");
    setUrlAnalysisResult(null);

    try {
      const response = await fetch("http://localhost:8001/api/analyze_url_full", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: urlInput, normalize: true })
      });

      if (!response.ok) {
        const error = await response.text();
        throw new Error(error || `HTTP ${response.status}`);
      }

      const data: EnsembleResponse = await response.json();
      setUrlAnalysisResult(data);
    } catch (err: any) {
      setUrlError("Error analyzing URL: " + (err.message || String(err)));
    } finally {
      setIsCheckingFull(false);
    }
  };

  // ============ HTML File Upload Functions ============

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith(".html") && !file.name.endsWith(".txt")) {
      setFileError("Only .html and .txt files are supported");
      return;
    }

    setHtmlFile(file);
    setFileError("");
    setFileAnalysisResult(null);

    // Read file content
    const reader = new FileReader();
    reader.onload = (event) => {
      setHtmlFileContent(event.target?.result as string);
    };
    reader.onerror = () => {
      setFileError("Error reading file");
    };
  };

  const analyzeHtmlFile = async () => {
    if (!htmlFileContent.trim()) {
      setFileError("No HTML content to analyze");
      return;
    }

    setIsAnalyzingFile(true);
    setFileError("");
    setFileAnalysisResult(null);

    try {
      const response = await fetch("http://localhost:8001/api/analyze_html_file", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ html: htmlFileContent })
      });

      if (!response.ok) {
        const error = await response.text();
        throw new Error(error || `HTTP ${response.status}`);
      }

      const data = await response.json();
      setFileAnalysisResult(data);
    } catch (err: any) {
      setFileError("Error analyzing HTML file: " + (err.message || String(err)));
    } finally {
      setIsAnalyzingFile(false);
    }
  };

  // ============ Result Card Component ============

  const ResultCard = ({ result }: { result: AnalysisResult }) => {
    if (!result) return null;

    const risk = getRiskLevel(result.probability);
    const isUnknown = result.label === "UNKNOWN";

    return (
      <Card className="p-6 mb-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">{result.model_name}</h3>
          {!isUnknown && (
            <div className={`px-3 py-1 rounded-full text-white text-sm font-bold ${risk.color}`}>
              {risk.level}
            </div>
          )}
        </div>

        {!isUnknown ? (
          <>
            <div className="mb-4">
              <div className="flex justify-between mb-2">
                <span className="font-medium">Prediction:</span>
                <span className={`font-bold ${result.label === "PHISHING" ? "text-red-600" : "text-green-600"}`}>
                  {result.label}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className={`h-3 rounded-full ${
                    result.label === "PHISHING" ? "bg-red-500" : "bg-green-500"
                  }`}
                  style={{ width: `${formatPercentage(result.probability)}%` }}
                ></div>
              </div>
              <div className="text-sm text-gray-600 mt-2">
                Confidence: {formatPercentage(result.probability)}%
              </div>
            </div>

            <div>
              <h4 className="font-medium mb-2">Analysis Details:</h4>
              <ul className="space-y-2">
                {result.explanations && result.explanations.map((exp, idx) => (
                  <li key={idx} className="text-sm text-gray-700 flex items-start">
                    <span className="mr-2">•</span>
                    <span>{exp}</span>
                  </li>
                ))}
              </ul>
            </div>
          </>
        ) : (
          <div className="text-yellow-600">
            <p className="text-sm mb-2">⚠️ Unable to analyze</p>
            {result.explanations && (
              <ul className="space-y-1">
                {result.explanations.map((exp, idx) => (
                  <li key={idx} className="text-sm">{exp}</li>
                ))}
              </ul>
            )}
          </div>
        )}
      </Card>
    );
  };

  // ============ Ensemble Summary Component ============

  const EnsembleSummary = ({ ensemble }: { ensemble: AnalysisResult }) => {
    const risk = getRiskLevel(ensemble.probability);

    return (
      <Card className={`p-6 mb-6 border-2 ${risk.color}`}>
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold">🎯 Overall Assessment</h2>
          <div className={`px-4 py-2 rounded-lg text-white text-lg font-bold ${risk.color}`}>
            {risk.level} RISK
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4 mb-4">
          <div>
            <div className="text-sm text-gray-600">Verdict</div>
            <div className={`text-2xl font-bold ${ensemble.label === "PHISHING" ? "text-red-600" : "text-green-600"}`}>
              {ensemble.label}
            </div>
          </div>
          <div>
            <div className="text-sm text-gray-600">Score</div>
            <div className="text-2xl font-bold">{formatPercentage(ensemble.probability)}%</div>
          </div>
          <div>
            <div className="text-sm text-gray-600">Confidence</div>
            <div className="text-2xl font-bold">{(ensemble.confidence * 100).toFixed(0)}%</div>
          </div>
        </div>

        <div className="w-full bg-gray-300 rounded-full h-4 mb-4">
          <div
            className={`h-4 rounded-full ${ensemble.label === "PHISHING" ? "bg-red-500" : "bg-green-500"}`}
            style={{ width: `${formatPercentage(ensemble.probability)}%` }}
          ></div>
        </div>

        <div>
          <h4 className="font-medium mb-2">Summary:</h4>
          <ul className="space-y-1">
            {ensemble.explanations && ensemble.explanations.map((exp, idx) => (
              <li key={idx} className="text-sm text-gray-700">{exp}</li>
            ))}
          </ul>
        </div>
      </Card>
    );
  };

  // ============ Render ============

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 py-8 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-slate-900 mb-2">🛡️ Phishing URL Guardian</h1>
          <p className="text-slate-600">Advanced phishing detection using 3 AI models (RNN, Transformer, GCN)</p>
        </div>

        {/* Main Tab Interface */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-2 mb-6">
            <TabsTrigger value="url" className="text-lg">
              📎 Check URL
            </TabsTrigger>
            <TabsTrigger value="html" className="text-lg">
              📄 Upload HTML
            </TabsTrigger>
          </TabsList>

          {/* ===== TAB 1: URL INPUT ===== */}
          <TabsContent value="url" className="space-y-6">
            <Card className="p-6">
              <h2 className="text-2xl font-semibold mb-4">Analyze URL with All 3 Models</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Enter URL:</label>
                  <Input
                    type="text"
                    value={urlInput}
                    onChange={(e) => setUrlInput(e.target.value)}
                    placeholder="https://example.com"
                    disabled={isCheckingFull}
                    onKeyPress={(e) => e.key === "Enter" && analyzeUrlFull()}
                  />
                </div>

                <Button
                  onClick={analyzeUrlFull}
                  disabled={isCheckingFull}
                  className="w-full"
                  size="lg"
                >
                  {isCheckingFull ? "🔍 Analyzing..." : "🔍 Check URL"}
                </Button>

                {urlError && (
                  <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
                    ❌ {urlError}
                  </div>
                )}
              </div>
            </Card>

            {/* Loading State */}
            {isCheckingFull && (
              <Card className="p-6 text-center">
                <div className="space-y-4">
                  <div className="animate-spin text-4xl">⏳</div>
                  <p className="text-gray-600">Running URL Model (RNN)...</p>
                  <p className="text-gray-600">Fetching HTML content...</p>
                  <p className="text-gray-600">Running HTML Model (Transformer)...</p>
                  <p className="text-gray-600">Running DOM Model (GCN)...</p>
                  <p className="text-gray-600">Combining results...</p>
                </div>
              </Card>
            )}

            {/* Results */}
            {urlAnalysisResult && (
              <div>
                <EnsembleSummary ensemble={urlAnalysisResult.ensemble} />

                <div>
                  <h3 className="text-xl font-bold mb-4">📊 Individual Model Results</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {urlAnalysisResult.url_model && (
                      <div>
                        <ResultCard result={urlAnalysisResult.url_model} />
                      </div>
                    )}
                    {urlAnalysisResult.html_model && (
                      <div>
                        <ResultCard result={urlAnalysisResult.html_model} />
                      </div>
                    )}
                    {urlAnalysisResult.dom_model && (
                      <div>
                        <ResultCard result={urlAnalysisResult.dom_model} />
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </TabsContent>

          {/* ===== TAB 2: HTML FILE UPLOAD ===== */}
          <TabsContent value="html" className="space-y-6">
            <Card className="p-6">
              <h2 className="text-2xl font-semibold mb-4">Upload HTML File</h2>
              <div className="space-y-4">
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-gray-400 transition">
                  <input
                    type="file"
                    accept=".html,.txt"
                    onChange={handleFileSelect}
                    disabled={isAnalyzingFile}
                    className="hidden"
                    id="html-file-input"
                  />
                  <label
                    htmlFor="html-file-input"
                    className="cursor-pointer block"
                  >
                    <div className="text-4xl mb-2">📂</div>
                    <p className="font-medium text-gray-700">
                      {htmlFile ? htmlFile.name : "Click to upload HTML file"}
                    </p>
                    <p className="text-sm text-gray-500">or drag and drop</p>
                    <p className="text-xs text-gray-400 mt-2">.html and .txt files only</p>
                  </label>
                </div>

                {htmlFile && (
                  <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                    <p className="text-green-700">✅ File selected: {htmlFile.name}</p>
                  </div>
                )}

                <Button
                  onClick={analyzeHtmlFile}
                  disabled={isAnalyzingFile || !htmlFile}
                  className="w-full"
                  size="lg"
                >
                  {isAnalyzingFile ? "🔍 Analyzing..." : "🔍 Analyze HTML"}
                </Button>

                {fileError && (
                  <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
                    ❌ {fileError}
                  </div>
                )}
              </div>
            </Card>

            {/* Loading State */}
            {isAnalyzingFile && (
              <Card className="p-6 text-center">
                <div className="space-y-4">
                  <div className="animate-spin text-4xl">⏳</div>
                  <p className="text-gray-600">Running HTML Model (Transformer)...</p>
                  <p className="text-gray-600">Running DOM Model (GCN)...</p>
                  <p className="text-gray-600">Combining results...</p>
                </div>
              </Card>
            )}

            {/* Results */}
            {fileAnalysisResult && (
              <div>
                <EnsembleSummary ensemble={fileAnalysisResult.ensemble} />

                <div>
                  <h3 className="text-xl font-bold mb-4">📊 Model Results</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {fileAnalysisResult.html_model && (
                      <ResultCard result={fileAnalysisResult.html_model} />
                    )}
                    {fileAnalysisResult.dom_model && (
                      <ResultCard result={fileAnalysisResult.dom_model} />
                    )}
                  </div>
                </div>
              </div>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default Index;
