import React, { useState, useEffect, useRef } from 'react';
import {
  Send,
  TrendingUp,
  DollarSign,
  Target,
  Menu,
  X,
  Plus,
} from 'lucide-react';
import './index.css';

const API_URL = 'http://localhost:8000/api/analyze-statement';

const FinancialAssistant = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [userProfile, setUserProfile] = useState({
    name: 'Ahmed',
    balance: 8450,
    monthlyIncome: 12000,
    spendingThisMonth: 6200,
    savingsGoal: 15000,
    currentSavings: 8450,
    restaurantSpending: 0,
    restaurantBaseline: 0,
  });
  const [showInsights, setShowInsights] = useState(false);
  const [uploadedFile, setUploadedFile] = useState(null);

  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Initial greeting
    setTimeout(() => {
      addMessage(
        'ai',
        "Hi Ahmed! You can upload your bank CSV for this month and I'll analyze your spending for you."
      );
    }, 500);
  }, []);

  const conversationFlows = {
    savingsProgress: [
      "Great news! You're currently progressing toward your savings goal.",
      'Based on your recent statement, we can fine-tune your savings rate.',
      'Would you like me to suggest some adjustments to accelerate this?',
    ],
    budgetHelp: [
      'I can help you create a flexible spending plan for the rest of the month.',
      'We can allocate your remaining budget across key categories.',
      'Would you like me to break this down by category?',
    ],
    encouragement: [
      'You are building good financial awareness by tracking your statements.',
      'Small adjustments in one or two categories can make a meaningful difference.',
    ],
  };

  const addMessage = (sender, text, type = 'text', data = null) => {
    const message = {
      id: Date.now() + Math.random(),
      sender,
      text,
      type,
      data,
      timestamp: new Date().toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
      }),
    };
    setMessages((prev) => [...prev, message]);
  };

  const simulateAIResponse = async (userMessage) => {
    setIsTyping(true);
    await new Promise((resolve) => setTimeout(resolve, 800));

    const lowerMessage = userMessage.toLowerCase();

    if (lowerMessage.includes('savings') || lowerMessage.includes('goal')) {
      for (const line of conversationFlows.savingsProgress) {
        addMessage('ai', line, 'text');
        await new Promise((resolve) => setTimeout(resolve, 1200));
      }
    } else if (lowerMessage.includes('budget') || lowerMessage.includes('plan')) {
      for (const line of conversationFlows.budgetHelp) {
        addMessage('ai', line, 'text');
        await new Promise((resolve) => setTimeout(resolve, 1200));
      }
    } else if (lowerMessage.includes('analyze')) {
      addMessage(
        'ai',
        "Upload your latest CSV statement using the + button, and I'll analyze it.",
        'text'
      );
    } else {
      addMessage('ai', 'Let me think about that for a second.', 'text');
      await new Promise((resolve) => setTimeout(resolve, 1000));
      for (const line of conversationFlows.encouragement) {
        addMessage('ai', line, 'text');
        await new Promise((resolve) => setTimeout(resolve, 1000));
      }
    }

    setIsTyping(false);
  };

  const handleSend = async () => {
    if (!input.trim()) return;

    addMessage('user', input);
    const userInput = input;
    setInput('');

    await simulateAIResponse(userInput);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // === CSV UPLOAD + BACKEND CALL ===
  const handleFileChange = async (e) => {
    const file = e.target.files && e.target.files[0];
    if (!file) return;

    const lowerName = file.name.toLowerCase();
    if (!lowerName.endsWith('.csv')) {
      addMessage('ai', 'Please upload a CSV statement file.', 'text');
      return;
    }

    setUploadedFile(file);
    addMessage('user', `Uploaded statement: ${file.name}`, 'text');

    setIsTyping(true);

    try {
      const formData = new FormData();
      formData.append('statement', file);

      const res = await fetch(API_URL, {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        let msg = 'Error analyzing statement.';
        try {
          const body = await res.json();
          if (body.detail) msg = body.detail;
        } catch (_) {}
        addMessage('ai', msg, 'text');
        return;
      }

      const data = await res.json();

      // 1) Show insights in chat
      addMessage(
        'ai',
        "I've analyzed your statement. Here are some key insights:",
        'text'
      );
      (data.insights || []).forEach((insight) => {
        addMessage('ai', insight, 'text');
      });

      // 2) Show spending chart
      if (data.chart) {
        addMessage('ai', 'Spending breakdown for this period:', 'text');
        addMessage('ai', 'spending-chart', 'chart', {
          categories: data.chart.categories,
          amounts: data.chart.amounts,
        });
      }

      // 3) Update right-side insights panel
      if (data.user_profile) {
        setUserProfile((prev) => ({
          ...prev,
          ...data.user_profile,
        }));
      }
    } catch (err) {
      console.error(err);
      addMessage(
        'ai',
        'Something went wrong while contacting the server.',
        'text'
      );
    } finally {
      setIsTyping(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  const QuickAction = ({ icon: Icon, label, onClick }) => (
    <button
      onClick={onClick}
      className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors text-sm"
    >
      <Icon className="w-4 h-4 text-emerald-600" />
      <span className="text-gray-700">{label}</span>
    </button>
  );

  const SpendingChart = ({ data }) => {
    const maxAmount = Math.max(...data.amounts);

    return (
      <div className="bg-white rounded-lg p-4 border border-gray-200">
        <h4 className="text-sm font-semibold text-gray-700 mb-3">
          This Period&apos;s Spending
        </h4>
        <div className="space-y-3">
          {data.categories.map((category, index) => {
            const amount = data.amounts[index];
            const percentage = (amount / maxAmount) * 100;
            const isHigh = amount > 100;

            return (
              <div key={category}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">{category}</span>
                  <span
                    className={`font-semibold ${
                      isHigh ? 'text-amber-600' : 'text-gray-700'
                    }`}
                  >
                    {amount.toFixed(2)} EUR
                  </span>
                </div>
                <div className="w-full bg-gray-100 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all ${
                      isHigh ? 'bg-amber-500' : 'bg-emerald-500'
                    }`}
                    style={{ width: `${percentage}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  const InsightsPanel = () => {
    const savingsProgress = (
      (userProfile.currentSavings / userProfile.savingsGoal) *
      100
    ).toFixed(0);
    const remainingBudget =
      userProfile.monthlyIncome - userProfile.spendingThisMonth;

    const hasRestaurantBaseline = userProfile.restaurantBaseline > 0;
    const deviation = hasRestaurantBaseline
      ? (
          ((userProfile.restaurantSpending - userProfile.restaurantBaseline) /
            userProfile.restaurantBaseline) *
          100
        ).toFixed(0)
      : 0;

    return (
      <div className="bg-white border-l border-gray-200 p-6 overflow-y-auto h-full">
        <h3 className="text-lg font-bold text-gray-800 mb-4">
          Financial Insights
        </h3>

        <div className="space-y-4">
          <div className="bg-emerald-50 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <Target className="w-5 h-5 text-emerald-600" />
              <h4 className="font-semibold text-gray-700">Savings Goal</h4>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">Progress</span>
                <span className="font-semibold text-emerald-600">
                  {isNaN(savingsProgress) ? '0' : savingsProgress}%
                </span>
              </div>
              <div className="w-full bg-emerald-100 rounded-full h-3">
                <div
                  className="bg-emerald-600 h-3 rounded-full transition-all"
                  style={{
                    width: `${
                      isNaN(savingsProgress) ? 0 : Number(savingsProgress)
                    }%`,
                  }}
                />
              </div>
              <p className="text-xs text-gray-600 mt-2">
                {userProfile.currentSavings.toLocaleString()} /{' '}
                {userProfile.savingsGoal.toLocaleString()} EUR
              </p>
            </div>
          </div>

          <div className="bg-blue-50 rounded-lg p-4">
            <div className="flex items-center gap-2 mb-2">
              <DollarSign className="w-5 h-5 text-blue-600" />
              <h4 className="font-semibold text-gray-700">
                Current Period Overview
              </h4>
            </div>
            <p className="text-sm text-gray-600 mb-1">
              Income: {userProfile.monthlyIncome.toFixed(2)} EUR
            </p>
            <p className="text-sm text-gray-600 mb-1">
              Spending: {userProfile.spendingThisMonth.toFixed(2)} EUR
            </p>
            <p className="text-2xl font-bold text-blue-600">
              {remainingBudget.toFixed(2)} EUR left
            </p>
          </div>

          <div className="border-t pt-4">
            <h4 className="font-semibold text-gray-700 mb-3">
              Behavioral Patterns
            </h4>
            <div className="space-y-2 text-sm">
              <div className="flex items-start gap-2">
                <div className="w-2 h-2 bg-emerald-500 rounded-full mt-1.5" />
                <p className="text-gray-600">
                  Upload a new CSV each month to track your habits over time.
                </p>
              </div>
              <div className="flex items-start gap-2">
                <div className="w-2 h-2 bg-blue-500 rounded-full mt-1.5" />
                <p className="text-gray-600">
                  Focus first on your highest category (e.g. Groceries) for easy
                  wins.
                </p>
              </div>
              {hasRestaurantBaseline && (
                <div className="flex items-start gap-2">
                  <div className="w-2 h-2 bg-amber-500 rounded-full mt-1.5" />
                  <p className="text-gray-600">
                    Restaurant spending is {deviation}% vs your baseline.
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="flex h-screen bg-gradient-to-br from-emerald-50 to-blue-50">
      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-emerald-500 to-blue-500 rounded-lg flex items-center justify-center">
              <DollarSign className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-800">
                Financial Assistant
              </h1>
              <p className="text-xs text-gray-500">
                Upload your statement and get insights
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* + button to upload CSV */}
            <button
              onClick={() => fileInputRef.current && fileInputRef.current.click()}
              className="hidden sm:flex items-center gap-1 px-3 py-2 border border-gray-200 rounded-lg text-sm hover:bg-gray-50 transition-colors"
            >
              <Plus className="w-4 h-4 text-emerald-600" />
              <span className="text-gray-700">Upload CSV</span>
            </button>

            {/* Mobile icon-only upload */}
            <button
              onClick={() => fileInputRef.current && fileInputRef.current.click()}
              className="sm:hidden p-2 rounded-lg border border-gray-200 hover:bg-gray-50"
            >
              <Plus className="w-5 h-5 text-emerald-600" />
            </button>

            <button
              onClick={() => setShowInsights(!showInsights)}
              className="lg:hidden p-2 hover:bg-gray-100 rounded-lg"
            >
              {showInsights ? (
                <X className="w-5 h-5" />
              ) : (
                <Menu className="w-5 h-5" />
              )}
            </button>
          </div>
        </div>

        {/* Hidden file input */}
        <input
          type="file"
          accept=".csv"
          ref={fileInputRef}
          onChange={handleFileChange}
          className="hidden"
        />

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-6 py-6 space-y-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${
                message.sender === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              <div
                className={`max-w-[70%] ${
                  message.sender === 'user'
                    ? 'bg-emerald-600 text-white rounded-2xl rounded-tr-sm'
                    : 'bg-white text-gray-800 rounded-2xl rounded-tl-sm border border-gray-200'
                } px-4 py-3 shadow-sm`}
              >
                {message.type === 'chart' && message.data ? (
                  <SpendingChart data={message.data} />
                ) : (
                  <>
                    <p className="text-sm whitespace-pre-line">
                      {message.text}
                    </p>
                    <p
                      className={`text-xs mt-1 ${
                        message.sender === 'user'
                          ? 'text-emerald-100'
                          : 'text-gray-400'
                      }`}
                    >
                      {message.timestamp}
                    </p>
                  </>
                )}
              </div>
            </div>
          ))}

          {isTyping && (
            <div className="flex justify-start">
              <div className="bg-white border border-gray-200 rounded-2xl rounded-tl-sm px-4 py-3">
                <div className="flex gap-1">
                  <div
                    className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                    style={{ animationDelay: '0ms' }}
                  />
                  <div
                    className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                    style={{ animationDelay: '150ms' }}
                  />
                  <div
                    className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                    style={{ animationDelay: '300ms' }}
                  />
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Quick Actions */}
        <div className="px-6 py-3 border-t border-gray-200 bg-white/50 backdrop-blur-sm">
          <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
            <QuickAction
              icon={TrendingUp}
              label="Analyze spending"
              onClick={() => {
                setInput('Can you analyze my spending patterns?');
                setTimeout(() => handleSend(), 100);
              }}
            />
            <QuickAction
              icon={Target}
              label="Savings goal"
              onClick={() => {
                setInput('How is my savings goal progressing?');
                setTimeout(() => handleSend(), 100);
              }}
            />
            <QuickAction
              icon={DollarSign}
              label="Budget plan"
              onClick={() => {
                setInput('Help me create a budget plan');
                setTimeout(() => handleSend(), 100);
              }}
            />
          </div>
        </div>

        {/* Input Area */}
        <div className="bg-white border-t border-gray-200 px-6 py-4">
          <div className="flex gap-3">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything about your finances..."
              className="flex-1 px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
            />
            <button
              onClick={handleSend}
              disabled={!input.trim()}
              className="bg-emerald-600 text-white px-6 py-3 rounded-xl hover:bg-emerald-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Insights Panel */}
      <div className={`w-80 ${showInsights ? 'block' : 'hidden'} lg:block`}>
        <InsightsPanel />
      </div>
    </div>
  );
};

export default FinancialAssistant;
