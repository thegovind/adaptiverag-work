import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { BarChart3, TrendingUp, Clock, DollarSign } from 'lucide-react';

interface TokenUsage {
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
  model?: string;
  cost?: number;
  error?: string;
}

interface ProcessingMetadata {
  processing_time_ms: number;
  retrieval_method: string;
  success: boolean;
}

interface TokenUsageDisplayProps {
  tokenUsage?: TokenUsage;
  processingMetadata?: ProcessingMetadata;
  ragMode: string;
}

export function TokenUsageDisplay({ tokenUsage, processingMetadata, ragMode }: TokenUsageDisplayProps) {
  if (!tokenUsage) {
    return (
      <Card className="p-6">
        <div className="text-center text-gray-500">
          No token usage data available
        </div>
      </Card>
    );
  }

  if (tokenUsage.error) {
    return (
      <Card className="p-6">
        <div className="text-center text-red-500">
          Error tracking tokens: {tokenUsage.error}
        </div>
      </Card>
    );
  }

  const inputCostRate = 0.0001; // $0.0001 per 1K tokens (example rate)
  const outputCostRate = 0.0002; // $0.0002 per 1K tokens (example rate)
  
  const inputCost = (tokenUsage.prompt_tokens / 1000) * inputCostRate;
  const outputCost = (tokenUsage.completion_tokens / 1000) * outputCostRate;
  const totalCost = inputCost + outputCost;

  const tokensPerSecond = processingMetadata?.processing_time_ms 
    ? Math.round((tokenUsage.total_tokens / processingMetadata.processing_time_ms) * 1000)
    : 0;

  const efficiency = processingMetadata?.success ? 'Optimal' : 'Degraded';

  return (
    <Card className="p-6">
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h3 className="font-medium text-gray-900 flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Token Usage Statistics
          </h3>
          <Badge variant="outline" className="text-xs">
            {ragMode.toUpperCase()}
          </Badge>
        </div>
        
        {/* Token Usage Overview */}
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center p-4 bg-blue-50 rounded-lg border border-blue-100">
            <div className="text-2xl font-bold text-blue-600">{tokenUsage.prompt_tokens.toLocaleString()}</div>
            <div className="text-sm text-gray-600">Prompt Tokens</div>
            <div className="text-xs text-gray-500 mt-1">Input</div>
          </div>
          <div className="text-center p-4 bg-green-50 rounded-lg border border-green-100">
            <div className="text-2xl font-bold text-green-600">{tokenUsage.completion_tokens.toLocaleString()}</div>
            <div className="text-sm text-gray-600">Completion Tokens</div>
            <div className="text-xs text-gray-500 mt-1">Output</div>
          </div>
          <div className="text-center p-4 bg-purple-50 rounded-lg border border-purple-100">
            <div className="text-2xl font-bold text-purple-600">{tokenUsage.total_tokens.toLocaleString()}</div>
            <div className="text-sm text-gray-600">Total Tokens</div>
            <div className="text-xs text-gray-500 mt-1">Combined</div>
          </div>
        </div>

        {/* Cost Breakdown */}
        <div className="space-y-3">
          <h4 className="font-medium text-gray-900 flex items-center gap-2">
            <DollarSign className="h-4 w-4" />
            Cost Breakdown
          </h4>
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Input Cost ({tokenUsage.prompt_tokens.toLocaleString()} tokens):</span>
                <span className="font-medium">${inputCost.toFixed(4)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Output Cost ({tokenUsage.completion_tokens.toLocaleString()} tokens):</span>
                <span className="font-medium">${outputCost.toFixed(4)}</span>
              </div>
              <div className="flex justify-between border-t pt-2 font-medium">
                <span className="text-gray-900">Total Cost:</span>
                <span className="font-bold text-green-600">${totalCost.toFixed(4)}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Performance Metrics */}
        {processingMetadata && (
          <div className="space-y-3">
            <h4 className="font-medium text-gray-900 flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />
              Performance Metrics
            </h4>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-blue-50 rounded-lg p-4 border border-blue-100">
                <div className="flex items-center gap-2 mb-2">
                  <Clock className="h-4 w-4 text-blue-600" />
                  <span className="text-sm font-medium text-gray-700">Processing Time</span>
                </div>
                <div className="text-xl font-bold text-blue-600">
                  {processingMetadata.processing_time_ms}ms
                </div>
                <div className="text-xs text-gray-500">
                  {(processingMetadata.processing_time_ms / 1000).toFixed(2)}s total
                </div>
              </div>
              
              <div className="bg-green-50 rounded-lg p-4 border border-green-100">
                <div className="flex items-center gap-2 mb-2">
                  <TrendingUp className="h-4 w-4 text-green-600" />
                  <span className="text-sm font-medium text-gray-700">Throughput</span>
                </div>
                <div className="text-xl font-bold text-green-600">
                  {tokensPerSecond > 0 ? tokensPerSecond.toLocaleString() : 'N/A'}
                </div>
                <div className="text-xs text-gray-500">tokens/second</div>
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div className="bg-gray-50 rounded-lg p-3">
                <span className="font-medium text-gray-700">Retrieval Method:</span>
                <div className="text-gray-600 capitalize">{processingMetadata.retrieval_method.replace('_', ' ')}</div>
              </div>
              <div className="bg-gray-50 rounded-lg p-3">
                <span className="font-medium text-gray-700">Efficiency:</span>
                <div className={`font-medium ${efficiency === 'Optimal' ? 'text-green-600' : 'text-orange-600'}`}>
                  {efficiency}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Model Information */}
        {tokenUsage.model && (
          <div className="space-y-3">
            <h4 className="font-medium text-gray-900">Model Information</h4>
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-gray-700">Model Used:</span>
                <Badge variant="outline" className="font-mono text-xs">
                  {tokenUsage.model}
                </Badge>
              </div>
            </div>
          </div>
        )}

        {/* Token Efficiency Analysis */}
        <div className="space-y-3">
          <h4 className="font-medium text-gray-900">Efficiency Analysis</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div className="bg-blue-50 rounded-lg p-3 border border-blue-100">
              <div className="font-medium text-blue-900 mb-1">Input Efficiency</div>
              <div className="text-blue-700">
                {tokenUsage.prompt_tokens < 1000 ? 'Excellent' : 
                 tokenUsage.prompt_tokens < 2000 ? 'Good' : 
                 tokenUsage.prompt_tokens < 4000 ? 'Moderate' : 'High Usage'}
              </div>
              <div className="text-xs text-blue-600 mt-1">
                {tokenUsage.prompt_tokens < 1000 ? 'Concise prompting' : 
                 tokenUsage.prompt_tokens < 2000 ? 'Reasonable context' : 
                 'Consider prompt optimization'}
              </div>
            </div>
            
            <div className="bg-green-50 rounded-lg p-3 border border-green-100">
              <div className="font-medium text-green-900 mb-1">Output Quality</div>
              <div className="text-green-700">
                {tokenUsage.completion_tokens > 500 ? 'Comprehensive' : 
                 tokenUsage.completion_tokens > 200 ? 'Detailed' : 
                 tokenUsage.completion_tokens > 50 ? 'Concise' : 'Brief'}
              </div>
              <div className="text-xs text-green-600 mt-1">
                {tokenUsage.completion_tokens > 500 ? 'Rich, detailed response' : 
                 tokenUsage.completion_tokens > 200 ? 'Well-structured answer' : 
                 'Quick, focused response'}
              </div>
            </div>
          </div>
        </div>

        {/* Cost per Token Visualization */}
        <div className="space-y-3">
          <h4 className="font-medium text-gray-900">Cost Distribution</h4>
          <div className="relative">
            <div className="flex h-4 bg-gray-200 rounded-full overflow-hidden">
              <div 
                className="bg-blue-500 transition-all duration-300"
                style={{ width: `${(inputCost / totalCost) * 100}%` }}
                title={`Input: ${((inputCost / totalCost) * 100).toFixed(1)}%`}
              />
              <div 
                className="bg-green-500 transition-all duration-300"
                style={{ width: `${(outputCost / totalCost) * 100}%` }}
                title={`Output: ${((outputCost / totalCost) * 100).toFixed(1)}%`}
              />
            </div>
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>Input ({((inputCost / totalCost) * 100).toFixed(1)}%)</span>
              <span>Output ({((outputCost / totalCost) * 100).toFixed(1)}%)</span>
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
}
