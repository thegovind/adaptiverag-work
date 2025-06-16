import React, { useState } from 'react';
import { ChatLayout } from '../components/ChatLayout';
import { useChatStream } from '../hooks/useChatStream';
import { MessageBubble } from '../components/MessageBubble';
import { Button } from '../components/ui/button';
import { Textarea } from '../components/ui/textarea';
import { Card } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Loader2, Send, RotateCcw, Shield, CheckCircle } from 'lucide-react';

export function QAWithVerification() {
  const [query, setQuery] = useState('');
  const { messages, isLoading, sendMessage, clearMessages } = useChatStream('qa-verification');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      sendMessage(query);
      setQuery('');
    }
  };

  const exampleQueries = [
    "Compare R&D spend for Microsoft vs Google 2021",
    "Which company had higher revenue growth in 2023?",
    "Analyze the debt-to-equity ratios across tech companies"
  ];

  return (
    <ChatLayout>
      {/* Messages area - scrollable */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4" style={{ height: 'calc(100vh - 200px)' }}>
        {messages.length === 0 && (
          <div className="flex flex-col items-center justify-center space-y-6">
            <Card className="p-8 max-w-2xl mx-auto text-center bg-white/80 backdrop-blur-sm border-gray-200 shadow-lg">
              <div className="w-16 h-16 bg-microsoft-green rounded-full flex items-center justify-center mx-auto mb-4">
                <Shield className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-microsoft-gray mb-2">
                Welcome to Agentic QA with Source Verification
              </h3>
              <p className="text-gray-600 mb-4">
                Ask complex questions that require multi-source verification. Our system includes source credibility assessment and confidence scoring.
              </p>
              <div className="flex items-center justify-center space-x-4 mb-6">
                <Badge className="bg-microsoft-green text-white">
                  <CheckCircle className="h-3 w-3 mr-1" />
                  Source Verification
                </Badge>
                <Badge className="bg-microsoft-blue text-white">
                  <Shield className="h-3 w-3 mr-1" />
                  Confidence Scoring
                </Badge>
              </div>
              <div className="space-y-3">
                <p className="text-sm font-medium text-gray-700">Try these example queries:</p>
                <div className="space-y-2">
                  {exampleQueries.map((example, idx) => (
                    <button
                      key={idx}
                      onClick={() => setQuery(example)}
                      className="block w-full text-left p-3 text-sm bg-green-50 hover:bg-green-100 rounded-lg border border-green-200 transition-colors"
                    >
                      "{example}"
                    </button>
                  ))}
                </div>
              </div>
            </Card>
          </div>
        )}

        {messages.map((msg, idx) => (
          <MessageBubble key={idx} message={msg} />
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <Card className="bg-white border-gray-200 shadow-sm">
              <div className="p-4">
                <div className="flex items-center space-x-3">
                  <Loader2 className="h-4 w-4 animate-spin text-microsoft-green" />
                  <span className="text-sm text-gray-600">Verifying sources and generating response...</span>
                </div>
              </div>
            </Card>
          </div>
        )}
      </div>

      {/* Input area - fixed at bottom */}
      <div className="flex-shrink-0 p-6 bg-white/80 backdrop-blur-sm border-t border-gray-200">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
          <div className="flex gap-3">
            <div className="flex-1">
              <Textarea
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask complex questions requiring multi-source verification..."
                className="min-h-[80px] resize-none border-gray-300 focus:border-microsoft-green focus:ring-microsoft-green"
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSubmit(e);
                  }
                }}
              />
            </div>
            <div className="flex flex-col gap-2">
              <Button
                type="submit"
                disabled={isLoading || !query.trim()}
                className="bg-microsoft-green hover:bg-green-700 text-white px-6 py-3 h-auto"
              >
                {isLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Send className="h-4 w-4" />
                )}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={clearMessages}
                className="px-6 py-3 h-auto border-gray-300 hover:bg-gray-50"
              >
                <RotateCcw className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </form>
      </div>
    </ChatLayout>
  );
}
