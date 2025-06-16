import { Card } from './ui/card';
import { Badge } from './ui/badge';
import { User, Bot } from 'lucide-react';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface MessageBubbleProps {
  message: Message;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user';
  
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`max-w-3xl ${isUser ? 'ml-12' : 'mr-12'}`}>
        <div className="flex items-start space-x-3">
          {!isUser && (
            <div className="flex-shrink-0 w-8 h-8 bg-microsoft-blue rounded-full flex items-center justify-center">
              <Bot className="h-4 w-4 text-white" />
            </div>
          )}
          <Card className={`flex-1 ${
            isUser 
              ? 'bg-microsoft-blue text-white border-microsoft-blue shadow-lg' 
              : 'bg-white border-gray-200 shadow-sm hover:shadow-md transition-shadow'
          }`}>
            <div className="p-4">
              <div className="flex items-center justify-between mb-2">
                <Badge variant={isUser ? "secondary" : "outline"} className={`text-xs ${
                  isUser ? 'bg-white/20 text-white border-white/30' : 'bg-gray-100 text-gray-600'
                }`}>
                  {isUser ? 'You' : 'AI Assistant'}
                </Badge>
                <span className={`text-xs ${
                  isUser ? 'text-white/70' : 'text-gray-500'
                }`}>
                  {message.timestamp ? message.timestamp.toLocaleTimeString() : new Date().toLocaleTimeString()}
                </span>
              </div>
              <div 
                className={`message-content text-sm leading-relaxed ${
                  isUser ? 'text-white' : 'text-gray-900'
                }`}
                dangerouslySetInnerHTML={{ __html: message.content }}
              />
            </div>
          </Card>
          {isUser && (
            <div className="flex-shrink-0 w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center">
              <User className="h-4 w-4 text-white" />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
